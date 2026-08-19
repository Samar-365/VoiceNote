from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QFileDialog, QProgressBar, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from voicenote.ui.components.waveform_widget import WaveformWidget

class AudioRecorderWidget(QWidget):
    """Audio Recording and Upload Widget Component - Modern Dark Bento Grid Theme."""
    transcription_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.seconds_elapsed = 0
        self.is_paused = False
        self.stream_index = 0
        self.streaming_tokens = [
            "We are reviewing", " the architecture for", " the local STT pipeline",
            " and ChromaDB vector engine.", " Tejas is orchestrating",
            " the background QThread workers,", " while Samar finalizes",
            " the modern PySide6 UI.", " Atharv has connected", " faster-whisper and",
            " Gemini LLM for automatic", " action items and summaries."
        ]
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(14)

        # Hero Recorder Card
        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(20, 20, 20, 20)
        hero_layout.setSpacing(14)

        # Header Row inside Hero
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        title = QLabel("Live Voice Studio & Audio Processing")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Record microphone stream or import audio for local AI transcription, summaries, and vector indexing.")
        subtitle.setObjectName("subtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)

        header_row.addStretch()

        # Input Device Selector & Noise Reduction
        self.chk_noise = QCheckBox("AI Noise Suppression")
        self.chk_noise.setChecked(True)
        header_row.addWidget(self.chk_noise)
        header_row.addSpacing(10)

        self.mic_combo = QComboBox()
        self.mic_combo.addItems([
            "🎙️ Studio USB Mic (48kHz 24-bit)",
            "🎧 Realtek High Definition Audio",
            "🔊 Stereo Mix (System Audio)"
        ])
        self.mic_combo.setFixedWidth(260)
        header_row.addWidget(self.mic_combo)

        hero_layout.addLayout(header_row)

        # Timer & Waveform Display Area
        waveform_box = QFrame()
        waveform_box.setObjectName("glassFrame")
        wf_layout = QVBoxLayout(waveform_box)
        wf_layout.setContentsMargins(16, 14, 16, 14)
        wf_layout.setSpacing(10)

        timer_row = QHBoxLayout()
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 26px; font-weight: 800; font-family: monospace; color: #FFFFFF;")
        
        self.status_badge = QLabel("IDLE")
        self.status_badge.setObjectName("badgeActive")
        
        timer_row.addWidget(self.timer_label)
        timer_row.addWidget(self.status_badge)
        timer_row.addStretch()

        # Format info
        fmt_label = QLabel("PCM 16-bit | 16000 Hz Mono | Whisper STT Ready")
        fmt_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600;")
        timer_row.addWidget(fmt_label)

        wf_layout.addLayout(timer_row)

        # Waveform Canvas
        self.waveform = WaveformWidget()
        wf_layout.addWidget(self.waveform)

        hero_layout.addWidget(waveform_box)

        # Live Streaming Transcript Preview (visible during recording)
        self.stream_box = QFrame()
        self.stream_box.setObjectName("glassFrame")
        sb_lay = QVBoxLayout(self.stream_box)
        sb_lay.setContentsMargins(12, 10, 12, 10)
        
        sb_title = QLabel("⚡ Live Streaming Speech Recognition (Whisper STT)")
        sb_title.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 700;")
        self.stream_text = QLabel("Listening for voice activity...")
        self.stream_text.setStyleSheet("color: #E2E8F0; font-size: 13px; font-style: italic;")
        self.stream_text.setWordWrap(True)
        
        sb_lay.addWidget(sb_title)
        sb_lay.addWidget(self.stream_text)
        hero_layout.addWidget(self.stream_box)
        self.stream_box.hide()

        # Recording Control Buttons Row
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        self.btn_record = QPushButton("🎙️ Start Recording")
        self.btn_record.setObjectName("recordBtn")
        self.btn_record.clicked.connect(self.toggle_recording)

        self.btn_pause = QPushButton("⏸️ Pause")
        self.btn_pause.setObjectName("pauseBtn")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_stop = QPushButton("⏹️ Stop & Transcribe")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_recording)

        self.btn_upload = QPushButton("📂 Import Audio File")
        self.btn_upload.setObjectName("primaryBtn")
        self.btn_upload.clicked.connect(self.browse_audio_file)

        controls_row.addWidget(self.btn_record)
        controls_row.addWidget(self.btn_pause)
        controls_row.addWidget(self.btn_stop)
        controls_row.addSpacing(14)
        controls_row.addWidget(self.btn_upload)
        controls_row.addStretch()

        hero_layout.addLayout(controls_row)
        main_layout.addWidget(hero_card)

        # Processing progress bar
        self.progress_box = QFrame()
        self.progress_box.setObjectName("cardFrame")
        p_layout = QVBoxLayout(self.progress_box)
        p_layout.setContentsMargins(16, 14, 16, 14)
        self.progress_label = QLabel("⚡ Running faster-whisper STT transcription & Gemini AI summary pipeline...")
        self.progress_label.setStyleSheet("color: #818CF8; font-weight: 700;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(70)
        p_layout.addWidget(self.progress_label)
        p_layout.addWidget(self.progress_bar)
        self.progress_box.hide()
        main_layout.addWidget(self.progress_box)

        # Timer & Stream Update Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.stream_timer = QTimer(self)
        self.stream_timer.timeout.connect(self.update_stream_text)

    def toggle_recording(self):
        if not self.waveform.is_recording and not self.is_paused:
            self.waveform.set_recording(True)
            self.timer.start(1000)
            self.stream_timer.start(800)
            self.btn_record.setText("🔴 Recording Live...")
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.status_badge.setText("RECORDING")
            self.status_badge.setObjectName("badgeRose")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            self.stream_box.show()
            self.stream_index = 0
            self.stream_text.setText("Listening...")
        elif self.is_paused:
            self.is_paused = False
            self.waveform.set_recording(True)
            self.timer.start(1000)
            self.stream_timer.start(800)
            self.btn_pause.setText("⏸️ Pause")
            self.status_badge.setText("RECORDING")
            self.status_badge.setObjectName("badgeRose")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def toggle_pause(self):
        if self.waveform.is_recording:
            self.waveform.set_recording(False)
            self.timer.stop()
            self.stream_timer.stop()
            self.is_paused = True
            self.btn_pause.setText("▶️ Resume")
            self.status_badge.setText("PAUSED")
            self.status_badge.setObjectName("badgeAmber")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def stop_recording(self):
        self.waveform.set_recording(False)
        self.timer.stop()
        self.stream_timer.stop()
        self.is_paused = False
        self.btn_record.setText("🎙️ Start Recording")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.status_badge.setText("IDLE")
        self.status_badge.setObjectName("badgeActive")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.stream_box.hide()
        
        self.progress_box.show()
        QTimer.singleShot(2200, self.finish_processing)

    def update_stream_text(self):
        if self.stream_index < len(self.streaming_tokens):
            cur = self.stream_text.text()
            if cur == "Listening...":
                cur = ""
            self.stream_text.setText(cur + " " + self.streaming_tokens[self.stream_index])
            self.stream_index += 1

    def finish_processing(self):
        self.progress_box.hide()
        self.transcription_requested.emit(self.stream_text.text() if self.stream_index > 0 else "New Recording Session")

    def update_timer(self):
        self.seconds_elapsed += 1
        mins, secs = divmod(self.seconds_elapsed, 60)
        hrs, mins = divmod(mins, 60)
        self.timer_label.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")

    def browse_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.m4a *.mp4)"
        )
        if file_path:
            self.progress_box.show()
            QTimer.singleShot(2000, self.finish_processing)
