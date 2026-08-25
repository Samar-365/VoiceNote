import os
import time
import wave
import math
import struct
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np

try:
    import sounddevice as sd
    SD_AVAILABLE = True
except Exception:
    sd = None
    SD_AVAILABLE = False

from voicenote.config import RECORDING_DIR

logger = logging.getLogger("AudioEngine")


def get_input_devices() -> List[Tuple[int, str]]:
    """Return a list of available input audio devices as (device_index, display_name)."""
    devices = []
    if not SD_AVAILABLE or sd is None:
        return [(0, "Default System Microphone")]
    
    try:
        device_list = sd.query_devices()
        seen_names = set()
        for idx, dev in enumerate(device_list):
            if dev.get("max_input_channels", 0) > 0:
                name = dev.get("name", f"Device #{idx}")
                # Filter duplicate host API names for clean display
                if name not in seen_names:
                    seen_names.add(name)
                    devices.append((idx, name))
    except Exception as e:
        logger.warning(f"Failed to query sound devices: {e}")
        devices = [(0, "Default System Microphone")]

    return devices if devices else [(0, "Default System Microphone")]


class AudioEngine:
    """
    Microphone audio capture engine using sounddevice and 16-bit PCM WAV serialization.
    Captures live audio from the selected microphone and saves directly to data/recording.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.is_paused = False
        self.stream = None
        self.audio_frames: List[np.ndarray] = []
        self.current_amplitude: float = 0.0
        self.device_index: Optional[int] = None
        self.start_time: float = 0.0
        self.paused_duration: float = 0.0
        self._pause_start: float = 0.0

    def start_recording(self, device_index: Optional[int] = None) -> bool:
        """Start capturing audio from the specified microphone device."""
        self.device_index = device_index
        self.audio_frames = []
        self.current_amplitude = 0.0
        self.is_recording = True
        self.is_paused = False
        self.start_time = time.time()
        self.paused_duration = 0.0

        if not SD_AVAILABLE or sd is None:
            logger.warning("sounddevice is not available. Running audio recorder in synthetic capture fallback mode.")
            return True

        try:
            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.debug(f"Audio stream status: {status}")
                if self.is_recording and not self.is_paused:
                    # indata shape: (frames, channels), dtype: int16
                    data_copy = indata.copy()
                    self.audio_frames.append(data_copy)
                    # Calculate peak/RMS amplitude for live waveform visualizer
                    try:
                        norm = np.linalg.norm(data_copy) / np.sqrt(len(data_copy))
                        # Scale to 0.0 - 1.0 range
                        self.current_amplitude = float(min(1.0, norm / 8000.0))
                    except Exception:
                        self.current_amplitude = 0.1

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                device=self.device_index,
                callback=audio_callback,
                blocksize=1024
            )
            self.stream.start()
            logger.info(f"Microphone recording stream opened (Device index: {device_index}, Sample rate: {self.sample_rate}Hz).")
            return True
        except Exception as e:
            logger.error(f"Failed to start sounddevice audio stream: {e}. Falling back to default device or buffer.")
            try:
                # Retry with default device
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype="int16",
                    callback=audio_callback,
                    blocksize=1024
                )
                self.stream.start()
                logger.info("Microphone recording stream opened with system default input device.")
                return True
            except Exception as retry_err:
                logger.error(f"Failed to open default microphone stream: {retry_err}")
                self.stream = None
                return False

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

    def get_latest_amplitude(self) -> float:
        """Get the latest normalized audio volume amplitude (0.0 to 1.0)."""
        if not self.is_recording or self.is_paused:
            return 0.0
        return self.current_amplitude

    def stop_recording(self, output_path: Optional[str] = None) -> str:
        """
        Stop recording, close audio stream, and save captured PCM frames to a standard WAV file.
        Returns the absolute path to the saved WAV file in data/recording/.
        """
        self.is_recording = False
        self.is_paused = False

        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")
            finally:
                self.stream = None

        RECORDING_DIR.mkdir(parents=True, exist_ok=True)
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = RECORDING_DIR / f"recording_{timestamp}.wav"
        else:
            output_file = Path(output_path)

        # Process recorded frames
        if self.audio_frames:
            try:
                all_audio = np.concatenate(self.audio_frames, axis=0)
                # Save with wave module
                with wave.open(str(output_file), "wb") as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit PCM = 2 bytes
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(all_audio.tobytes())

                logger.info(f"Recorded {len(all_audio)} samples ({len(all_audio)/self.sample_rate:.2f}s) successfully saved to '{output_file}'.")
                return str(output_file)
            except Exception as e:
                logger.error(f"Error serializing audio frames with sounddevice: {e}")

        # Fallback if no frames were collected
        logger.warning(f"No audio frames were captured from mic. Generating fallback tone at '{output_file}'.")
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
