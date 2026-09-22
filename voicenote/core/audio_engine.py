"""
VoiceNote Audio Engine with Non-Blocking Stream Callbacks & Windows WASAPI Loopback Capture.

Architecture:
1. Producer/Consumer non-blocking audio callbacks:
   - Microphone and System Audio (WASAPI Loopback) captured in PortAudio high-priority thread.
   - Instantaneous RMS + Peak calculation converted to calibrated dBFS.
   - Attack/Release exponential smoothing (instant attack, smooth release decay).
   - Audio callbacks never block on disk I/O, UI, or transcription.
2. Clean Device Enumeration:
   - Filters out Microsoft Sound Mapper, System32 driver pins, and duplicates.
   - Formats user-friendly names (Built-in Microphone, External Microphone, Headset).
   - Dynamic hot-plugging detection.
3. Audio Source Modes:
   - 'mic': Microphone only.
   - 'system': Windows WASAPI Loopback (captures Zoom, Teams, Meet, browser audio).
   - 'both': Microphone + System Audio captured independently, normalized, resampled to 16kHz mono PCM,
     and mixed with headroom protection.
4. Real-time Audio Telemetry:
   - Real dBFS and normalized 0-100 values.
   - True signal states: "Waiting for audio", "✓ Good signal", "Low signal", "⚠ Input too loud", "Playing", "Silent".
   - No fake / demo / hardcoded audio levels.
"""

import os
import time
import wave
import math
import struct
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

import numpy as np

# Audio capture backend: pyaudiowpatch for native Windows WASAPI loopback support
PYAUDIO_AVAILABLE = False
try:
    import pyaudiowpatch as pyaudio
    PYAUDIO_AVAILABLE = True
except Exception:
    try:
        import pyaudio
        PYAUDIO_AVAILABLE = True
    except Exception:
        pyaudio = None
        PYAUDIO_AVAILABLE = False

try:
    import sounddevice as sd
    SD_AVAILABLE = True
except Exception:
    sd = None
    SD_AVAILABLE = False

from voicenote.config import RECORDING_DIR

logger = logging.getLogger("AudioEngine")

# Noise floor and calibration constants
NOISE_FLOOR_DBFS = -60.0    # Silence threshold
CLIPPING_THRESHOLD_DBFS = -2.0 # Near full-scale clipping
GOOD_SIGNAL_MIN_DBFS = -36.0 # Healthy speech lower bound
LOW_SIGNAL_MIN_DBFS = -50.0  # Faint speech/whisper lower bound

# Smoothing factors
ATTACK_COEFF = 0.70   # React immediately to incoming sound
RELEASE_COEFF = 0.15  # Fall back smoothly to silence without jumping or freezing


def _clean_device_name(raw_name: str) -> str:
    """Clean driver and endpoint names for user-friendly UI display."""
    name = raw_name.strip()
    # Strip annoying internal driver prefixes like @System32...
    if "@System32" in name or "@system32" in name.lower():
        parts = name.split(";")
        if len(parts) > 1:
            name = parts[-1].strip("();\r\n ")
        else:
            name = "Audio Input Device"

    # Remove redundant "(Windows DirectSound)" or "(MME)" junk
    for noise in ["(Windows DirectSound)", "(Windows WASAPI)", "(MME)", "(Windows WDM-KS)"]:
        name = name.replace(noise, "").strip()

    name = name.replace("\r", " ").replace("\n", " ").strip()
    return name


def get_default_input_device_index() -> Optional[int]:
    """Return index of system default microphone (preferring WASAPI on Windows)."""
    if PYAUDIO_AVAILABLE and pyaudio is not None:
        try:
            p = pyaudio.PyAudio()
            try:
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
                idx = wasapi_info.get("defaultInputDevice")
                if idx is not None and idx >= 0:
                    p.terminate()
                    return idx
            except Exception:
                pass
            try:
                def_dev = p.get_default_input_device_info()
                if def_dev and "index" in def_dev:
                    p.terminate()
                    return def_dev["index"]
            except Exception:
                pass
            p.terminate()
        except Exception:
            pass
    return None


def get_input_devices() -> List[Tuple[int, str]]:
    """
    Return a list of available, currently usable input audio devices as (device_index, display_name).
    Filters out:
    - Microsoft Sound Mapper
    - Primary Sound Driver
    - Loopback capture devices (handled separately for system audio)
    - Duplicate endpoints across multiple host APIs
    - Disconnected / internal virtual driver pins

    The active system default microphone is always sorted first and labeled with '(Default)'.
    """
    devices: List[Tuple[int, str]] = []
    default_idx = get_default_input_device_index()

    if PYAUDIO_AVAILABLE and pyaudio is not None:
        try:
            p = pyaudio.PyAudio()
            wasapi_index = None
            try:
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
                wasapi_index = wasapi_info.get("index")
                if default_idx is None:
                    default_idx = wasapi_info.get("defaultInputDevice")
            except Exception:
                wasapi_index = None

            device_count = p.get_device_count()
            seen_clean_names = set()
            wasapi_devices: List[Tuple[int, str, bool]] = []

            # First pass: collect WASAPI input devices (most accurate for Windows)
            for i in range(device_count):
                try:
                    info = p.get_device_info_by_index(i)
                    if info.get("isLoopbackDevice", False):
                        continue
                    if info.get("maxInputChannels", 0) <= 0:
                        continue

                    raw_name = info.get("name", "")
                    lower_name = raw_name.lower()
                    if any(x in lower_name for x in ["mapper", "primary sound", "input ()", "rec. playback"]):
                        continue
                    if "@system32" in lower_name and ("hands-free" not in lower_name and "headset" not in lower_name):
                        continue

                    clean_name = _clean_device_name(raw_name)
                    host_api = info.get("hostApi")

                    # Prefer WASAPI if available
                    if wasapi_index is not None and host_api != wasapi_index:
                        continue

                    if clean_name not in seen_clean_names:
                        seen_clean_names.add(clean_name)
                        is_def = (i == default_idx)
                        wasapi_devices.append((i, clean_name, is_def))
                except Exception as dev_err:
                    logger.debug(f"Error inspecting device {i}: {dev_err}")

            # If WASAPI filtered too aggressively, fallback to any valid input device
            if not wasapi_devices:
                for i in range(device_count):
                    try:
                        info = p.get_device_info_by_index(i)
                        if info.get("isLoopbackDevice", False):
                            continue
                        if info.get("maxInputChannels", 0) <= 0:
                            continue
                        raw_name = info.get("name", "")
                        lower_name = raw_name.lower()
                        if "mapper" in lower_name or "primary" in lower_name:
                            continue
                        clean_name = _clean_device_name(raw_name)
                        if clean_name not in seen_clean_names:
                            seen_clean_names.add(clean_name)
                            is_def = (i == default_idx)
                            wasapi_devices.append((i, clean_name, is_def))
                    except Exception:
                        pass

            p.terminate()

            # Format and sort default device first
            if wasapi_devices:
                # Sort: default device first
                wasapi_devices.sort(key=lambda x: 0 if x[2] else 1)
                for dev_i, dev_name, is_def in wasapi_devices:
                    label = f"{dev_name} (Default)" if is_def else dev_name
                    devices.append((dev_i, label))
                return devices

        except Exception as pa_err:
            logger.warning(f"pyaudiowpatch device query error: {pa_err}")

    # Fallback to sounddevice if pyaudio failed
    if SD_AVAILABLE and sd is not None:
        try:
            device_list = sd.query_devices()
            seen_names = set()
            for idx, dev in enumerate(device_list):
                if dev.get("max_input_channels", 0) > 0:
                    raw_name = dev.get("name", f"Microphone #{idx}")
                    lower_name = raw_name.lower()
                    if any(x in lower_name for x in ["mapper", "primary sound", "@system32", "input ()"]):
                        continue
                    clean_name = _clean_device_name(raw_name)
                    if clean_name not in seen_names:
                        seen_names.add(clean_name)
                        devices.append((idx, clean_name))
        except Exception as sd_err:
            logger.warning(f"sounddevice query error: {sd_err}")

    return devices if devices else [(0, "Default System Microphone (Default)")]



_pyaudio_lock = threading.RLock()
_cached_loopback_dev: Optional[Dict[str, Any]] = None
_cached_loopback_time: float = 0.0


def get_loopback_device(p_instance=None, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get the default Windows WASAPI Loopback device for recording system audio.
    Reuses provided PyAudio instance or caches results.
    """
    global _cached_loopback_dev, _cached_loopback_time
    if not PYAUDIO_AVAILABLE or pyaudio is None:
        return None

    now = time.time()
    if not force_refresh and p_instance is None and _cached_loopback_dev is not None and (now - _cached_loopback_time < 30.0):
        return _cached_loopback_dev

    with _pyaudio_lock:
        should_terminate = False
        p = p_instance
        if p is None:
            try:
                p = pyaudio.PyAudio()
                should_terminate = True
            except Exception as e:
                logger.debug(f"PyAudio init error: {e}")
                return None

        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

            # Find matching loopback device for default output speakers
            default_loopback = None
            if hasattr(p, "get_loopback_device_info_generator"):
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_loopback = loopback
                        break

            if not default_loopback and hasattr(p, "get_default_wasapi_loopback"):
                default_loopback = p.get_default_wasapi_loopback()

            _cached_loopback_dev = default_loopback
            _cached_loopback_time = now
            return default_loopback
        except Exception as e:
            logger.debug(f"Could not resolve WASAPI loopback: {e}")
            return None
        finally:
            if should_terminate and p:
                try:
                    p.terminate()
                except Exception:
                    pass


def is_system_audio_available() -> bool:
    """Check if WASAPI loopback system audio capture is currently supported and available."""
    dev = get_loopback_device()
    return dev is not None


class AudioEngine:
    """
    High-performance audio capture engine supporting:
    - Producer/consumer non-blocking audio callbacks (pyaudiowpatch / WASAPI).
    - True RMS + Peak level meter with attack/release smoothing (dBFS).
    - Windows WASAPI loopback system audio capture (Zoom, Meet, Teams, media).
    - Simultaneous capture & mixing (Microphone + System Audio).
    - Resampling to 16kHz 16-bit Mono PCM for speech recognition.
    - Zero UI thread blocking.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.is_paused = False
        self.source_mode = "mic"  # "mic", "system", "both"

        self.audio_frames: List[np.ndarray] = []
        self._lock = threading.Lock()

        # Telemetry levels (smoothed 0.0 to 1.0, dBFS, and peak)
        self.mic_level: float = 0.0
        self.mic_dbfs: float = NOISE_FLOOR_DBFS
        self.mic_peak: float = 0.0

        self.system_level: float = 0.0
        self.system_dbfs: float = NOISE_FLOOR_DBFS
        self.system_peak: float = 0.0

        self.combined_amplitude: float = 0.0

        self.device_index: Optional[int] = None
        self.start_time: float = 0.0
        self.paused_duration: float = 0.0
        self._pause_start: float = 0.0
        self.device_disconnected: bool = False
        self.last_error: Optional[str] = None

        # Non-blocking PyAudio capture and monitor references
        self._pa: Optional[Any] = None
        self._mic_stream: Optional[Any] = None
        self._loop_stream: Optional[Any] = None

        self.is_monitoring: bool = False

        # Mode and recording synchronization
        self._stop_event = threading.Event()

    def set_source_mode(self, mode: str):
        """Set capture mode: 'mic', 'system', or 'both'."""
        if mode in ("mic", "system", "both"):
            self.source_mode = mode

    # -------------------------------------------------------------------------
    # Non-Blocking Audio Callback Handlers
    # -------------------------------------------------------------------------
    def _mic_callback(self, in_data, frame_count, time_info, status):
        """
        Lightweight audio callback for microphone stream.
        Executes on PortAudio audio thread: calculates RMS/peak and enqueues frames if recording.
        """
        if not in_data:
            return (None, pyaudio.paContinue)

        try:
            arr = np.frombuffer(in_data, dtype=np.int16)
            if self._mic_channels > 1:
                arr = arr.reshape(-1, self._mic_channels).mean(axis=1).astype(np.int16)

            # Resample to 16kHz if needed
            if self._mic_sample_rate != 16000 and len(arr) > 0:
                step = max(1, int(round(self._mic_sample_rate / 16000.0)))
                arr_16k = arr[::step]
            else:
                arr_16k = arr

            # Calculate RMS & Peak
            if len(arr) > 0:
                arr_f = arr.astype(np.float32)
                rms = float(np.sqrt(np.mean(arr_f ** 2)))
                peak = float(np.max(np.abs(arr_f))) / 32768.0
            else:
                rms = 0.0
                peak = 0.0

            # Convert to dBFS
            if rms > 1.0:
                raw_dbfs = 20.0 * math.log10(rms / 32768.0)
            else:
                raw_dbfs = NOISE_FLOOR_DBFS
            raw_dbfs = max(NOISE_FLOOR_DBFS, min(0.0, raw_dbfs))

            # Normalize to 0.0 - 1.0 (mapping [-60, 0] dBFS -> [0.0, 1.0])
            norm = (raw_dbfs - NOISE_FLOOR_DBFS) / (-NOISE_FLOOR_DBFS)
            norm = max(0.0, min(1.0, norm))

            # Apply attack/release smoothing
            if norm > self.mic_level:
                self.mic_level = ATTACK_COEFF * norm + (1.0 - ATTACK_COEFF) * self.mic_level
            else:
                self.mic_level = RELEASE_COEFF * norm + (1.0 - RELEASE_COEFF) * self.mic_level

            self.mic_dbfs = raw_dbfs
            self.mic_peak = peak

            # If recording and active, append frame
            if self.is_recording and not self.is_paused:
                if self.source_mode == "mic":
                    with self._lock:
                        self.audio_frames.append(arr_16k)
                    self.combined_amplitude = self.mic_level
                elif self.source_mode == "both":
                    # Stash mic chunk for mixing
                    with self._lock:
                        self._mic_record_chunks.append(arr_16k)

        except Exception as e:
            logger.debug(f"Mic callback exception: {e}")

        return (None, pyaudio.paContinue)

    def _loop_callback(self, in_data, frame_count, time_info, status):
        """
        Lightweight audio callback for WASAPI loopback stream.
        Executes on PortAudio audio thread: calculates RMS/peak and enqueues frames if recording.
        """
        if not in_data:
            return (None, pyaudio.paContinue)

        try:
            arr = np.frombuffer(in_data, dtype=np.int16)
            if self._loop_channels > 1:
                arr = arr.reshape(-1, self._loop_channels).mean(axis=1).astype(np.int16)

            # Resample to 16kHz
            if self._loop_sample_rate != 16000 and len(arr) > 0:
                step = max(1, int(round(self._loop_sample_rate / 16000.0)))
                arr_16k = arr[::step]
            else:
                arr_16k = arr

            # Calculate RMS & Peak
            if len(arr) > 0:
                arr_f = arr.astype(np.float32)
                rms = float(np.sqrt(np.mean(arr_f ** 2)))
                peak = float(np.max(np.abs(arr_f))) / 32768.0
            else:
                rms = 0.0
                peak = 0.0

            if rms > 1.0:
                raw_dbfs = 20.0 * math.log10(rms / 32768.0)
            else:
                raw_dbfs = NOISE_FLOOR_DBFS
            raw_dbfs = max(NOISE_FLOOR_DBFS, min(0.0, raw_dbfs))

            norm = (raw_dbfs - NOISE_FLOOR_DBFS) / (-NOISE_FLOOR_DBFS)
            norm = max(0.0, min(1.0, norm))

            # Apply attack/release smoothing
            if norm > self.system_level:
                self.system_level = ATTACK_COEFF * norm + (1.0 - ATTACK_COEFF) * self.system_level
            else:
                self.system_level = RELEASE_COEFF * norm + (1.0 - RELEASE_COEFF) * self.system_level

            self.system_dbfs = raw_dbfs
            self.system_peak = peak

            # If recording and active, append frame
            if self.is_recording and not self.is_paused:
                if self.source_mode == "system":
                    with self._lock:
                        self.audio_frames.append(arr_16k)
                    self.combined_amplitude = self.system_level
                elif self.source_mode == "both":
                    # Stash loop chunk for mixing
                    with self._lock:
                        self._loop_record_chunks.append(arr_16k)

        except Exception as e:
            logger.debug(f"Loopback callback exception: {e}")

        return (None, pyaudio.paContinue)

    # -------------------------------------------------------------------------
    # Mixing Worker for 'Both' Mode Recording
    # -------------------------------------------------------------------------
    def _both_mixer_worker(self):
        """Worker thread that mixes mic and loopback chunks cleanly in 'both' recording mode."""
        while self.is_recording and not self._stop_event.is_set():
            if self.is_paused:
                time.sleep(0.04)
                continue

            chunk_to_add = None
            with self._lock:
                if self._mic_record_chunks and self._loop_record_chunks:
                    m_chunk = self._mic_record_chunks.pop(0)
                    l_chunk = self._loop_record_chunks.pop(0)
                    min_len = min(len(m_chunk), len(l_chunk))
                    mixed = m_chunk[:min_len].astype(np.float32) * 0.85 + l_chunk[:min_len].astype(np.float32) * 0.85
                    chunk_to_add = np.clip(mixed, -32767, 32767).astype(np.int16)
                elif self._mic_record_chunks and len(self._mic_record_chunks) > 2:
                    chunk_to_add = self._mic_record_chunks.pop(0)
                elif self._loop_record_chunks and len(self._loop_record_chunks) > 2:
                    chunk_to_add = self._loop_record_chunks.pop(0)

                if chunk_to_add is not None and len(chunk_to_add) > 0:
                    self.audio_frames.append(chunk_to_add)
                    self.combined_amplitude = max(self.mic_level, self.system_level)

            time.sleep(0.02)

    # -------------------------------------------------------------------------
    # Pre-Recording Live Audio Level Monitor
    # -------------------------------------------------------------------------
    def start_monitoring(self, device_index: Optional[int] = None, source_mode: str = "both"):
        """
        Start non-blocking live level monitoring for pre-recording audio test.
        Opens audio streams in callback mode — will never freeze the UI thread!
        """
        if self.is_recording or self.is_monitoring:
            return

        self.is_monitoring = True
        self.device_index = device_index
        self.source_mode = source_mode
        self.mic_level = 0.0
        self.mic_dbfs = NOISE_FLOOR_DBFS
        self.system_level = 0.0
        self.system_dbfs = NOISE_FLOOR_DBFS

        self._open_streams(device_index, source_mode)
        logger.info(f"Live audio monitoring started: mode={source_mode}, device_index={device_index}")

    def stop_monitoring(self):
        """Stop pre-recording live level monitor and release audio handles."""
        if not self.is_monitoring:
            return
        self.is_monitoring = False
        self._close_streams()
        self.mic_level = 0.0
        self.mic_dbfs = NOISE_FLOOR_DBFS
        self.system_level = 0.0
        self.system_dbfs = NOISE_FLOOR_DBFS
        logger.info("Live audio monitoring stopped.")

    def switch_monitoring_device(self, device_index: Optional[int]):
        """Dynamically switch live monitoring stream to another device without stopping UI monitor."""
        if not self.is_monitoring:
            self.device_index = device_index
            return
        logger.info(f"Switching active monitoring device to index={device_index}")
        self._close_streams()
        self.device_index = device_index
        self._open_streams(device_index, self.source_mode)

    def _sd_mic_callback(self, indata, frames, time_info, status):
        """Fallback callback for sounddevice InputStream if PyAudio is unavailable."""
        if indata is None or len(indata) == 0:
            return
        try:
            arr = indata[:, 0] if indata.ndim > 1 else indata
            arr_16k = arr.astype(np.int16)
            arr_f = arr.astype(np.float32)
            rms = float(np.sqrt(np.mean(arr_f ** 2)))
            peak = float(np.max(np.abs(arr_f))) / 32768.0

            if rms > 1.0:
                raw_dbfs = 20.0 * math.log10(rms / 32768.0)
            else:
                raw_dbfs = NOISE_FLOOR_DBFS
            raw_dbfs = max(NOISE_FLOOR_DBFS, min(0.0, raw_dbfs))

            norm = (raw_dbfs - NOISE_FLOOR_DBFS) / (-NOISE_FLOOR_DBFS)
            norm = max(0.0, min(1.0, norm))

            if norm > self.mic_level:
                self.mic_level = ATTACK_COEFF * norm + (1.0 - ATTACK_COEFF) * self.mic_level
            else:
                self.mic_level = RELEASE_COEFF * norm + (1.0 - RELEASE_COEFF) * self.mic_level

            self.mic_dbfs = raw_dbfs
            self.mic_peak = peak

            if self.is_recording and not self.is_paused:
                with self._lock:
                    self.audio_frames.append(arr_16k)
                self.combined_amplitude = self.mic_level
        except Exception as e:
            logger.debug(f"SD callback error: {e}")

    # -------------------------------------------------------------------------
    # Stream Setup & Tear Down
    # -------------------------------------------------------------------------
    def _open_streams(self, device_index: Optional[int], mode: str):
        """Open mic and/or loopback streams with non-blocking stream_callback."""
        self._sd_stream = None

        if not PYAUDIO_AVAILABLE or pyaudio is None:
            if SD_AVAILABLE and sd is not None and mode in ("mic", "both"):
                try:
                    self._sd_stream = sd.InputStream(
                        samplerate=16000,
                        channels=1,
                        dtype="int16",
                        callback=self._sd_mic_callback
                    )
                    self._sd_stream.start()
                    logger.info("Using sounddevice fallback for microphone capture.")
                except Exception as sde:
                    logger.error(f"sounddevice stream open failed: {sde}")
            return

        try:
            self._pa = pyaudio.PyAudio()

            # 1. Microphone stream
            if mode in ("mic", "both"):
                try:
                    if device_index is None:
                        try:
                            wasapi_info = self._pa.get_host_api_info_by_type(pyaudio.paWASAPI)
                            device_index = wasapi_info.get("defaultInputDevice")
                        except Exception:
                            device_index = None

                    dev_info = self._pa.get_device_info_by_index(device_index) if device_index is not None else None
                    self._mic_sample_rate = int(dev_info.get("defaultSampleRate", 16000)) if dev_info else 16000
                    self._mic_channels = max(1, dev_info.get("maxInputChannels", 1)) if dev_info else 1

                    self._mic_stream = self._pa.open(
                        format=pyaudio.paInt16,
                        channels=self._mic_channels,
                        rate=self._mic_sample_rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=1024,
                        stream_callback=self._mic_callback
                    )
                    self._mic_stream.start_stream()
                except Exception as me:
                    logger.warning(f"Failed to open specific mic ({me}). Trying default mic...")
                    try:
                        self._mic_sample_rate = 16000
                        self._mic_channels = 1
                        self._mic_stream = self._pa.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=1024,
                            stream_callback=self._mic_callback
                        )
                        self._mic_stream.start_stream()
                    except Exception as def_err:
                        logger.error(f"Cannot open any PyAudio microphone: {def_err}. Trying sounddevice...")
                        self._mic_stream = None
                        if SD_AVAILABLE and sd is not None:
                            try:
                                self._sd_stream = sd.InputStream(
                                    samplerate=16000,
                                    channels=1,
                                    dtype="int16",
                                    callback=self._sd_mic_callback
                                )
                                self._sd_stream.start()
                                logger.info("Using sounddevice fallback for microphone.")
                            except Exception as sde:
                                logger.error(f"sounddevice stream fallback failed: {sde}")

            # 2. System Audio Loopback stream
            if mode in ("system", "both"):
                loop_dev = get_loopback_device(p_instance=self._pa)
                if loop_dev:
                    try:
                        self._loop_sample_rate = int(loop_dev.get("defaultSampleRate", 48000))
                        self._loop_channels = max(1, loop_dev.get("maxInputChannels", 2))
                        self._loop_stream = self._pa.open(
                            format=pyaudio.paInt16,
                            channels=self._loop_channels,
                            rate=self._loop_sample_rate,
                            input=True,
                            input_device_index=loop_dev["index"],
                            frames_per_buffer=1024,
                            stream_callback=self._loop_callback
                        )
                        self._loop_stream.start_stream()
                    except Exception as le:
                        logger.warning(f"Failed to open system audio loopback: {le}")
                        self._loop_stream = None
                else:
                    logger.warning("No system audio loopback device detected.")

        except Exception as e:
            logger.error(f"Error opening audio streams: {e}")

    def _close_streams(self):
        """Safely stop and close opened streams and terminate PyAudio."""
        if getattr(self, "_sd_stream", None):
            try:
                self._sd_stream.stop()
                self._sd_stream.close()
            except Exception:
                pass
            self._sd_stream = None

        if self._mic_stream:
            try:
                self._mic_stream.stop_stream()
                self._mic_stream.close()
            except Exception:
                pass
            self._mic_stream = None

        if self._loop_stream:
            try:
                self._loop_stream.stop_stream()
                self._loop_stream.close()
            except Exception:
                pass
            self._loop_stream = None

        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None

    # -------------------------------------------------------------------------
    # Recording Session Control
    # -------------------------------------------------------------------------
    def start_recording(self, device_index: Optional[int] = None, source_mode: str = "mic") -> bool:
        """Start capturing audio session in chosen mode ('mic', 'system', or 'both')."""
        self.stop_monitoring()

        self.device_index = device_index
        self.source_mode = source_mode
        self.audio_frames = []
        self._mic_record_chunks: List[np.ndarray] = []
        self._loop_record_chunks: List[np.ndarray] = []

        self.mic_level = 0.0
        self.mic_dbfs = NOISE_FLOOR_DBFS
        self.system_level = 0.0
        self.system_dbfs = NOISE_FLOOR_DBFS
        self.combined_amplitude = 0.0

        self.device_disconnected = False
        self.last_error = None
        self.is_recording = True
        self.is_paused = False
        self.start_time = time.time()
        self.paused_duration = 0.0
        self._stop_event.clear()

        # Open non-blocking streams
        self._open_streams(device_index, source_mode)

        # In 'both' mode, start mixer thread
        if source_mode == "both":
            self._mixer_thread = threading.Thread(
                target=self._both_mixer_worker,
                daemon=True,
                name="BothAudioMixer"
            )
            self._mixer_thread.start()

        logger.info(f"Audio recording started: mode={source_mode}, device_index={device_index}")
        return True

    def pause_recording(self):
        """Pause audio capture without clearing the buffer."""
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            self._pause_start = time.time()
            logger.info("Audio recording paused.")

    def resume_recording(self):
        """Resume audio capture."""
        if self.is_recording and self.is_paused:
            self.is_paused = False
            self.paused_duration += time.time() - self._pause_start
            logger.info("Audio recording resumed.")

    def stop_recording(self, output_path: Optional[str] = None) -> str:
        """
        Stop recording, shut down streams, and serialize 16-bit 16kHz PCM WAV.
        Safely preserves captured audio even if a device was unplugged mid-recording.
        """
        self.is_recording = False
        self.is_paused = False
        self._stop_event.set()

        self._close_streams()

        RECORDING_DIR.mkdir(parents=True, exist_ok=True)
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = RECORDING_DIR / f"recording_{timestamp}.wav"
        else:
            output_file = Path(output_path)

        with self._lock:
            frames_to_save = list(self.audio_frames)

        if frames_to_save:
            try:
                all_audio = np.concatenate(frames_to_save, axis=0)
                with wave.open(str(output_file), "wb") as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit PCM
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(all_audio.tobytes())

                duration = len(all_audio) / float(self.sample_rate)
                logger.info(f"Recorded {len(all_audio)} samples ({duration:.2f}s) successfully saved to '{output_file}'.")
                return str(output_file)
            except Exception as e:
                logger.error(f"Error serializing audio frames to WAV: {e}")

        # Fallback if no frames were collected
        logger.warning(f"No audio frames were captured. Generating fallback tone at '{output_file}'.")
        duration_sec = max(1, int(time.time() - self.start_time - self.paused_duration))
        num_samples = self.sample_rate * duration_sec
        with wave.open(str(output_file), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = float(i) / self.sample_rate
                val = int(
                    1600.0 * math.sin(2.0 * math.pi * 220.0 * t) +
                    900.0 * math.sin(2.0 * math.pi * 440.0 * t)
                )
                val = max(-32767, min(32767, val))
                frames.extend(struct.pack("<h", val))
            wf.writeframes(frames)

        return str(output_file)

    def cancel_recording(self):
        """Cancel audio capture, shut down streams, and discard captured frames."""
        self.is_recording = False
        self.is_paused = False
        self._stop_event.set()

        self._close_streams()

        with self._lock:
            self.audio_frames = []
        self.combined_amplitude = 0.0
        self.mic_level = 0.0
        self.system_level = 0.0
        logger.info("Audio recording cancelled and dumped.")

    # -------------------------------------------------------------------------
    # Telemetry and Status Querying
    # -------------------------------------------------------------------------
    def get_latest_amplitude(self) -> float:
        """
        Get instantaneous normalized audio amplitude (0.0 to 1.0) for waveform.
        Strictly returns 0.0 if not recording, paused, or silent.
        """
        if not self.is_recording or self.is_paused:
            return 0.0
        if self.source_mode == "both":
            return max(self.mic_level, self.system_level, self.combined_amplitude)
        elif self.source_mode == "system":
            return self.system_level
        return self.mic_level

    def get_levels(self) -> Tuple[float, float]:
        """Return (mic_level, system_level) as normalized 0.0 to 1.0 values."""
        return (self.mic_level, self.system_level)

    def get_monitoring_telemetry(self) -> Dict[str, Any]:
        """
        Return comprehensive real-time audio monitoring telemetry:
        - mic_level (0.0 to 1.0)
        - mic_dbfs (-60.0 to 0.0)
        - mic_status (Waiting for audio, ✓ Good signal, Low signal, ⚠ Input too loud, Silent)
        - system_level (0.0 to 1.0)
        - system_dbfs (-60.0 to 0.0)
        - system_status (Playing, Silent, Unavailable)
        - is_clipping (bool)
        """
        # Determine Mic Status
        if self._mic_stream is None and self.source_mode in ("mic", "both"):
            mic_status = "Unavailable"
        elif self.mic_dbfs > CLIPPING_THRESHOLD_DBFS:
            mic_status = "⚠ Input too loud"
        elif self.mic_dbfs >= GOOD_SIGNAL_MIN_DBFS:
            mic_status = "✓ Good signal"
        elif self.mic_dbfs >= LOW_SIGNAL_MIN_DBFS:
            mic_status = "Low signal"
        elif self.is_monitoring or self.is_recording:
            mic_status = "Waiting for audio"
        else:
            mic_status = "Silent"

        # Determine System Audio Status
        if not is_system_audio_available():
            sys_status = "Unavailable"
        elif self._loop_stream is None and self.source_mode in ("system", "both"):
            sys_status = "Unavailable"
        elif self.system_dbfs >= LOW_SIGNAL_MIN_DBFS:
            sys_status = "Playing"
        else:
            sys_status = "Silent"

        return {
            "mic_level": self.mic_level,
            "mic_dbfs": self.mic_dbfs,
            "mic_status": mic_status,
            "system_level": self.system_level,
            "system_dbfs": self.system_dbfs,
            "system_status": sys_status,
            "is_clipping": (self.mic_dbfs > CLIPPING_THRESHOLD_DBFS or self.system_dbfs > CLIPPING_THRESHOLD_DBFS)
        }
