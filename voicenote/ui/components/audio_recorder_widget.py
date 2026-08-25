import os
import wave
import struct
import math
import shutil
from datetime import datetime
from pathlib import Path
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QFileDialog, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal
from voicenote.config import RECORDING_DIR
from voicenote.core.audio_engine import AudioEngine, get_input_devices
from voicenote.ui.components.waveform_widget import WaveformWidget

logger = logging.getLogger("AudioRecorder")

class AudioRecorderWidget(QWidget):
    """Audio Recording and Upload Widget Component - Retro Cream Theme matching assets/home.png."""
    transcription_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.seconds_elapsed = 0
        self.is_paused = False
        self.active_audio_payload = "Live Voice Recording"
        self.audio_engine = AudioEngine()
        self.init_ui()

    def refresh_input_devices(self):
        self.mic_combo.clear()
        devices = get_input_devices()
        for idx, name in devices:
            self.mic_combo.addItem(name, idx)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Hero Recorder Card
        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(16)

        # Header Row inside Hero
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Live Voice Capture")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Record mic input or upload audio files for instant local AI processing.")
        subtitle.setObjectName("subtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)

        header_row.addStretch()

        # Input Device Selector
        self.mic_combo = QComboBox()
        self.refresh_input_devices()
        self.mic_combo.setFixedWidth(280)
        header_row.addWidget(self.mic_combo)

        hero_layout.addLayout(header_row)

        # Timer & Waveform Display Area
        waveform_box = QFrame()
        waveform_box.setObjectName("glassFrame")
        wf_layout = QVBoxLayout(waveform_box)
        wf_layout.setContentsMargins(16, 16, 16, 16)

        timer_row = QHBoxLayout()
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 28px; font-weight: 800; font-family: monospace; color: #1E2B4B;")
        
        self.status_badge = QLabel("IDLE")
        self.status_badge.setObjectName("badgeActive")
        
        timer_row.addWidget(self.timer_label)
        timer_row.addWidget(self.status_badge)
        timer_row.addStretch()

        # Sample Rate / Format info
        fmt_label = QLabel("PCM 16-bit | 16000 Hz Mono")
        fmt_label.setStyleSheet("color: #5C6479; font-size: 12px;")
        timer_row.addWidget(fmt_label)

        wf_layout.addLayout(timer_row)

        # Waveform Canvas
        self.waveform = WaveformWidget()
        wf_layout.addWidget(self.waveform)

        hero_layout.addWidget(waveform_box)

        # Recording Control Buttons Row
        controls_row = QHBoxLayout()

        self.btn_record = QPushButton("Start Recording")
        self.btn_record.setObjectName("recordBtn")
        self.btn_record.clicked.connect(self.toggle_recording)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setObjectName("pauseBtn")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_stop = QPushButton("Stop Transcribe")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_recording)

        self.btn_upload = QPushButton("Import Audio File")
        self.btn_upload.setObjectName("primaryBtn")
        self.btn_upload.clicked.connect(self.browse_audio_file)

        controls_row.addWidget(self.btn_record)
        controls_row.addWidget(self.btn_pause)
        controls_row.addWidget(self.btn_stop)
        controls_row.addSpacing(16)
        controls_row.addWidget(self.btn_upload)
        controls_row.addStretch()

        hero_layout.addLayout(controls_row)

        main_layout.addWidget(hero_card)

        # Drop Zone & Progress Indicator Area
        drop_card = QFrame()
        drop_card.setObjectName("cardFrame")
        drop_layout = QVBoxLayout(drop_card)
        drop_layout.setContentsMargins(20, 20, 20, 20)

        drop_label = QLabel("Drag and drop audio files here (WAV, MP3, M4A, MP4)")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_label.setStyleSheet("color: #5C6479; font-size: 14px; padding: 12px; border: 2px dashed #CBD5E1; border-radius: 0px; background: #FFFFFF;")
        drop_layout.addWidget(drop_label)

        # Processing progress bar
        self.progress_box = QWidget()
        p_layout = QVBoxLayout(self.progress_box)
        p_layout.setContentsMargins(0, 8, 0, 0)
        self.progress_label = QLabel("Running speech transcription & Gemini AI summary...")
        self.progress_label.setStyleSheet("color: #6D59A7; font-weight: 600;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(65)
        p_layout.addWidget(self.progress_label)
        p_layout.addWidget(self.progress_bar)
        self.progress_box.hide()

        drop_layout.addWidget(self.progress_box)

        main_layout.addWidget(drop_card)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def toggle_recording(self):
        if not self.waveform.is_recording and not self.is_paused:
            selected_idx = self.mic_combo.currentData()
            logger.info(f"Live audio recording session started on device index {selected_idx}.")
            self.seconds_elapsed = 0
            self.timer_label.setText("00:00:00")
            
            # Start hardware microphone capture
            self.audio_engine.start_recording(device_index=selected_idx)
            
            self.waveform.set_recording(True)
            self.timer.start(1000)
            self.btn_record.setText("Recording...")
            self.btn_record.setStyleSheet("background-color: #D04966; border: 1px solid #B93854; color: #FFFFFF;")
            self.btn_record.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_pause.setText("Pause")
            self.btn_stop.setEnabled(True)
            self.status_badge.setText("RECORDING")
            self.status_badge.setObjectName("badgeRose")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def toggle_pause(self):
        if self.is_paused:
            logger.info("Audio recording resumed from pause.")
            self.is_paused = False
            self.audio_engine.resume_recording()
            self.waveform.set_recording(True)
            self.timer.start(1000)
            self.btn_pause.setText("Pause")
            self.status_badge.setText("RECORDING")
            self.status_badge.setObjectName("badgeRose")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
        elif self.waveform.is_recording:
            logger.info(f"Audio recording paused at {self.timer_label.text()}.")
            self.waveform.set_recording(False)
            self.audio_engine.pause_recording()
            self.timer.stop()
            self.is_paused = True
            self.btn_pause.setText("Resume")
            self.status_badge.setText("PAUSED")
            self.status_badge.setObjectName("badgeAmber")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def stop_recording(self):
        total_time = self.timer_label.text()
        logger.info(f"Audio recording stopped permanently. Total duration: {total_time}. Storing recording in data/recording folder...")
        
        # Stop mic capture and save real audible WAV to data/recording
        try:
            saved_wav = self.audio_engine.stop_recording()
            self.active_audio_payload = saved_wav
            logger.info(f"Audio recording successfully stored at: {saved_wav}")
        except Exception as e:
            logger.error(f"Failed to save audio recording: {e}")
            self.active_audio_payload = f"Voice Recording ({total_time})"
        
        # 1. Halt all recording activities
        self.waveform.set_recording(False)
        self.timer.stop()
        self.is_paused = False
        self.seconds_elapsed = 0
        
        # 2. Fully lock and reset buttons
        self.btn_record.setText("Start Recording")
        self.btn_record.setStyleSheet("")
        self.btn_record.setEnabled(False)
        self.btn_pause.setText("Pause")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        # 3. Reset status and timer display
        self.timer_label.setText("00:00:00")
        self.status_badge.setText("PROCESSING")
        self.status_badge.setObjectName("badgePurple")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        
        # 4. Trigger processing progress
        self.progress_box.show()
        QTimer.singleShot(2200, self.finish_processing)

    def finish_processing(self):
        logger.info(f"Speech transcription and summarization ready for: '{self.active_audio_payload}'.")
        self.progress_box.hide()
        self.status_badge.setText("IDLE")
        self.status_badge.setObjectName("badgeActive")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.btn_record.setEnabled(True)
        self.transcription_requested.emit(self.active_audio_payload)

    def update_timer(self):
        self.seconds_elapsed += 1
        mins, secs = divmod(self.seconds_elapsed, 60)
        hrs, mins = divmod(mins, 60)
        self.timer_label.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")
        
        # Stream live audio amplitude into dynamic waveform visualizer
        latest_amp = self.audio_engine.get_latest_amplitude()
        self.waveform.set_live_amplitude(latest_amp)

    def browse_audio_file(self):
        logger.info("Opening system audio file picker dialog...")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.m4a *.mp4)"
        )
        if file_path:
            src_path = Path(file_path)
            file_name = src_path.name
            file_ext = src_path.suffix.upper()
            try:
                file_size_kb = round(os.path.getsize(file_path) / 1024, 1)
            except Exception:
                file_size_kb = "N/A"

            # Copy imported audio file to data/recording folder
            RECORDING_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = RECORDING_DIR / f"imported_{timestamp}_{src_path.name}"
            try:
                shutil.copy2(src_path, dest_file)
                saved_audio_path = str(dest_file)
                logger.info(f"Imported audio file stored in recording directory: '{dest_file}'")
            except Exception as copy_err:
                logger.warning(f"Could not copy to data/recording folder ({copy_err}), using original path: {file_path}")
                saved_audio_path = file_path
            
            self.active_audio_payload = saved_audio_path
            logger.info(f"Audio payload ready: '{file_name}' (Format: {file_ext}, Size: {file_size_kb} KB). Sending to STT pipeline...")
            
            self.status_badge.setText("PROCESSING")
            self.status_badge.setObjectName("badgePurple")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            self.progress_box.show()
            QTimer.singleShot(2000, self.finish_processing)
        else:
            logger.info("Audio file import cancelled by user.")
