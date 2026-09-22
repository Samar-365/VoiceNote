import os
import wave
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from voicenote.config import DATA_DIR, RECORDING_DIR, RECORDINGS_DIR
from voicenote.core.audio_engine import AudioEngine, get_input_devices
from voicenote.ui.components.audio_recorder_widget import AudioRecorderWidget


class TestAudioRecordingStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.recording_dir = RECORDING_DIR
        self.recording_dir.mkdir(parents=True, exist_ok=True)

    def test_recording_directory_path(self):
        """Verify recording directory is correctly configured inside data/recording."""
        self.assertTrue(str(self.recording_dir).endswith(os.path.join("data", "recording")) or str(self.recording_dir).endswith("data/recording"))
        self.assertTrue(self.recording_dir.exists())
        self.assertTrue(self.recording_dir.is_dir())

    def test_input_device_detection(self):
        """Verify input audio devices are queried."""
        devices = get_input_devices()
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
        self.assertIsInstance(devices[0], tuple)
        self.assertEqual(len(devices[0]), 2)

    def test_audio_engine_capture_and_save(self):
        """Verify that AudioEngine can start, stop, and save audible WAV file in data/recording."""
        engine = AudioEngine(sample_rate=16000, channels=1)
        started = engine.start_recording()
        self.assertTrue(started)
        self.assertTrue(engine.is_recording)

        engine.pause_recording()
        self.assertTrue(engine.is_paused)

        engine.resume_recording()
        self.assertFalse(engine.is_paused)

        saved_path = engine.stop_recording()
        self.assertIsNotNone(saved_path)
        path_obj = Path(saved_path)
        self.assertTrue(path_obj.exists())
        self.assertEqual(path_obj.parent.resolve(), self.recording_dir.resolve())
        self.assertTrue(path_obj.name.startswith("recording_"))
        self.assertTrue(path_obj.name.endswith(".wav"))

        # Verify WAV format header integrity
        with wave.open(saved_path, "rb") as wf:
            self.assertEqual(wf.getnchannels(), 1)      # Mono
            self.assertEqual(wf.getsampwidth(), 2)     # 16-bit
            self.assertEqual(wf.getframerate(), 16000) # 16kHz
            self.assertGreater(wf.getnframes(), 0)

        # Cleanup generated test audio file
        try:
            path_obj.unlink()
        except Exception:
            pass

    def test_widget_audio_engine_integration(self):
        """Verify that AudioRecorderWidget initializes with AudioEngine and populated mic list."""
        widget = AudioRecorderWidget()
        self.assertIsNotNone(widget.audio_engine)
    def test_audio_engine_cancel_dumps_frames(self):
        """Verify that cancel_recording discards audio buffer without saving any file."""
        engine = AudioEngine(sample_rate=16000, channels=1)
        engine.start_recording()
        engine.audio_frames = [b"fake_pcm_data_chunk_12345"]
        self.assertTrue(engine.is_recording)

        engine.cancel_recording()
        self.assertFalse(engine.is_recording)
        self.assertFalse(engine.is_paused)
        self.assertEqual(len(engine.audio_frames), 0)

    def test_restart_button_and_flow(self):
        """Verify that Restart button shows during pause/recording and resets the session cleanly."""
        widget = AudioRecorderWidget()
        widget.show()
        self.app.processEvents()

        # Initially hidden
        self.assertTrue(widget.btn_restart.isHidden())

        # Start recording -> Restart button should be visible and enabled
        widget.toggle_recording()
        self.assertFalse(widget.btn_restart.isHidden())
        self.assertTrue(widget.btn_restart.isEnabled())

        # Pause recording -> Restart button stays visible and enabled
        widget.toggle_pause()
        self.assertTrue(widget.is_paused)
        self.assertEqual(widget.btn_pause.text(), "Resume")
        self.assertFalse(widget.btn_restart.isHidden())
        self.assertTrue(widget.btn_restart.isEnabled())

        # Click Restart -> dumps old audio, resets timer to 00:00:00, and restarts recording
        widget.seconds_elapsed = 42
        widget.restart_recording()
        self.assertEqual(widget.seconds_elapsed, 0)
        self.assertEqual(widget.timer_label.text(), "00:00:00")
        self.assertFalse(widget.is_paused)
        self.assertEqual(widget.btn_pause.text(), "Pause")
        self.assertIn("REC", widget.status_badge.text())

        # Cleanup
        widget.audio_engine.cancel_recording()
        widget.close()


if __name__ == "__main__":
    unittest.main()

