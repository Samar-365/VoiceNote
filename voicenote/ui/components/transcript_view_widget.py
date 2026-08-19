from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QSlider, QInputDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer

class TranscriptViewWidget(QWidget):
    """Transcript Viewer, Audio Scrubber & Tag Manager UI Component - Modern Dark Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.playback_speed = 1.0
        self.tags = ["#Sprint-Architecture", "#Gemini-AI", "#Local-Whisper", "#High-Priority"]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header Info Card
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        top_row = QHBoxLayout()
        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        
        self.title_label = QLabel("Note: Sprint Planning & Local AI Architecture")
        self.title_label.setObjectName("titleLabel")
        
        sub_info = QLabel("Recorded Today at 02:30 PM  •  Duration: 04m 32s  •  Format: WAV 16kHz Mono  •  STT: faster-whisper  •  Confidence: 98.4%")
        sub_info.setObjectName("subtitleLabel")
        
        title_v.addWidget(self.title_label)
        title_v.addWidget(sub_info)
        top_row.addLayout(title_v)
        top_row.addStretch()

        # Action Buttons
        btn_copy = QPushButton("📋 Copy Raw Text")
        btn_copy.clicked.connect(self.copy_transcript)
        top_row.addWidget(btn_copy)

        card_layout.addLayout(top_row)

        # Audio Scrubber Player Bar
        player_frame = QFrame()
        player_frame.setObjectName("glassFrame")
        pf_layout = QHBoxLayout(player_frame)
        pf_layout.setContentsMargins(14, 10, 14, 10)
        pf_layout.setSpacing(12)

        self.btn_play_pause = QPushButton("▶️ Play")
        self.btn_play_pause.setFixedWidth(80)
        self.btn_play_pause.clicked.connect(self.toggle_play_audio)
        pf_layout.addWidget(self.btn_play_pause)

        self.time_current = QLabel("00:15")
        self.time_current.setStyleSheet("color: #818CF8; font-weight: 700; font-family: monospace;")
        pf_layout.addWidget(self.time_current)

        self.scrub_slider = QSlider(Qt.Orientation.Horizontal)
        self.scrub_slider.setRange(0, 272)
        self.scrub_slider.setValue(15)
        pf_layout.addWidget(self.scrub_slider, stretch=1)

        self.time_total = QLabel("04:32")
        self.time_total.setStyleSheet("color: #64748B; font-weight: 600; font-family: monospace;")
        pf_layout.addWidget(self.time_total)

        # Speed button
        self.btn_speed = QPushButton("1.0x")
        self.btn_speed.setFixedWidth(60)
        self.btn_speed.clicked.connect(self.cycle_speed)
        pf_layout.addWidget(self.btn_speed)

        card_layout.addWidget(player_frame)

        # Tag Manager Row
        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("🏷️ Topics & Tags:"))

        self.tags_container = QHBoxLayout()
        self.render_tags()
        tag_row.addLayout(self.tags_container)

        btn_add_tag = QPushButton("+ Add Tag")
        btn_add_tag.setStyleSheet("background-color: #1E293B; color: #818CF8; font-size: 11px; padding: 4px 10px; border: 1px solid #334155;")
        btn_add_tag.clicked.connect(self.add_new_tag)
        tag_row.addWidget(btn_add_tag)
        tag_row.addStretch()

        card_layout.addLayout(tag_row)
        layout.addWidget(card)

        # Search Bar for Transcript
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter transcript by keyword, speaker, or timestamp...")
        self.search_input.textChanged.connect(self.filter_transcript)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Main Transcript Text Display Panel
        self.transcript_edit = QTextEdit()
        self.transcript_edit.setReadOnly(False)
        self.load_sample_transcript()

        layout.addWidget(self.transcript_edit)

        # Timer for simulated playback
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.advance_playback)

    def render_tags(self):
        while self.tags_container.count():
            item = self.tags_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for tag in self.tags:
            lbl = QLabel(tag)
            lbl.setObjectName("badgePurple")
            self.tags_container.addWidget(lbl)

    def add_new_tag(self):
        text, ok = QInputDialog.getText(self, "Add Tag", "Enter tag name:")
        if ok and text.strip():
            tag_name = text.strip()
            if not tag_name.startswith("#"):
                tag_name = "#" + tag_name
            self.tags.append(tag_name)
            self.render_tags()

    def toggle_play_audio(self):
        if not self.is_playing:
            self.is_playing = True
            self.btn_play_pause.setText("⏸️ Pause")
            self.play_timer.start(int(1000 / self.playback_speed))
        else:
            self.is_playing = False
            self.btn_play_pause.setText("▶️ Play")
            self.play_timer.stop()

    def cycle_speed(self):
        speeds = [1.0, 1.25, 1.5, 2.0]
        curr_idx = speeds.index(self.playback_speed) if self.playback_speed in speeds else 0
        next_idx = (curr_idx + 1) % len(speeds)
        self.playback_speed = speeds[next_idx]
        self.btn_speed.setText(f"{self.playback_speed}x")
        if self.is_playing:
            self.play_timer.setInterval(int(1000 / self.playback_speed))

    def advance_playback(self):
        val = self.scrub_slider.value() + 1
        if val > self.scrub_slider.maximum():
            val = 0
            self.toggle_play_audio()
        self.scrub_slider.setValue(val)
        mins, secs = divmod(val, 60)
        self.time_current.setText(f"{mins:02d}:{secs:02d}")

    def copy_transcript(self):
        QApplication.clipboard().setText(self.transcript_edit.toPlainText())
        QMessageBox.information(self, "Copied", "Full transcript text copied to clipboard.")

    def filter_transcript(self, text: str):
        if not text.strip():
            self.load_sample_transcript()
            return
        
        full_text = self.sample_full_text()
        lines = full_text.split("\n\n")
        filtered = [l for l in lines if text.lower() in l.lower()]
        self.transcript_edit.setText("\n\n".join(filtered) if filtered else "No matching dialogue or timestamp found.")

    def sample_full_text(self) -> str:
        return (
            "[00:00:04] Speaker 1 (Tejas): Alright team, let's align on the VoiceNote desktop architecture. "
            "We are using PySide6 for the entire desktop frontend, backed by SQLite and ChromaDB for local vector embeddings.\n\n"
            "[00:00:22] Speaker 2 (Samar): Perfect. On the UI side, I have designed the Bento Grid layout with the "
            "live audio recorder, interactive waveform visualizer, and multi-format export for PDF, DOCX, and TXT.\n\n"
            "[00:00:48] Speaker 3 (Atharv): From the AI side, the STT pipeline with faster-whisper is running in a background "
            "QThread so the UI stays 100% responsive. LLM summaries and action item extraction via Gemini and Ollama are fully connected.\n\n"
            "[00:01:15] Speaker 1 (Tejas): Great. Let's make sure the database integration and vector indexing run smoothly "
            "after every new note is recorded. Privacy-first local storage is our core strength."
        )

    def load_sample_transcript(self):
        self.transcript_edit.setText(self.sample_full_text())
