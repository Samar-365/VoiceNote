from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QInputDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal

class TranscriptViewWidget(QWidget):
    """Transcript Viewer & Tag Manager UI Component - Retro Cream Theme matching assets/transcript.png."""
    export_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = ["#Sprint-Architecture", "#Ollama-AI", "#Local-Whisper", "#High-Priority"]
        self.current_title = "Sprint Planning & Local AI Architecture"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header Info Card
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        top_row = QHBoxLayout()
        title_v = QVBoxLayout()
        
        self.title_label = QLabel("Note: Sprint Planning & Local AI Architecture")
        self.title_label.setObjectName("titleLabel")
        
        self.sub_info = QLabel("Recorded Today at 02:30 PM  •  Duration: 04m 32s  •  Format: WAV 16kHz Mono  •  Engine: faster-whisper")
        self.sub_info.setObjectName("subtitleLabel")
        
        title_v.addWidget(self.title_label)
        title_v.addWidget(self.sub_info)
        top_row.addLayout(title_v)
        top_row.addStretch()

        # Action Buttons
        btn_export = QPushButton("Export Note")
        btn_export.setObjectName("primaryBtn")
        btn_export.clicked.connect(lambda: self.export_clicked.emit(self.current_title))
        top_row.addWidget(btn_export)

        btn_copy = QPushButton("Copy Text")
        btn_copy.setStyleSheet("background-color: #F8F6F0; border: 1px solid #E5E0D6; font-weight: 700; color: #4A3980; padding: 6px 14px;")
        btn_copy.clicked.connect(self.copy_transcript)
        top_row.addWidget(btn_copy)

        card_layout.addLayout(top_row)
        card_layout.addSpacing(6)

        # Tag Manager Row
        tag_row = QHBoxLayout()
        tag_lbl = QLabel("Tags:")
        tag_lbl.setStyleSheet("color: #1E2B4B; font-weight: 600;")
        tag_row.addWidget(tag_lbl)

        self.tags_container = QHBoxLayout()
        self.render_tags()
        tag_row.addLayout(self.tags_container)

        btn_add_tag = QPushButton("+ Add Tag")
        btn_add_tag.setStyleSheet("background-color: #ECE8E1; color: #6D59A7; font-size: 11px; padding: 4px 10px; border: 1px solid #E2DDD3;")
        btn_add_tag.clicked.connect(self.add_new_tag)
        tag_row.addWidget(btn_add_tag)
        tag_row.addStretch()

        card_layout.addLayout(tag_row)
        layout.addWidget(card)

        # Search Bar for Transcript
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter transcript text or timestamp...")
        self.search_input.textChanged.connect(self.filter_transcript)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Main Transcript Text Display Panel
        self.transcript_edit = QTextEdit()
        self.transcript_edit.setReadOnly(False)
        self.load_sample_transcript()

        layout.addWidget(self.transcript_edit)

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

    def copy_transcript(self):
        QApplication.clipboard().setText(self.transcript_edit.toPlainText())
        QMessageBox.information(self, "Copied", "Full transcript text copied to clipboard.")

    def filter_transcript(self, text: str):
        if not text.strip():
            self.load_sample_transcript()
            return
        
        full_text = self.sample_full_html()
        # Filter paragraphs
        lines = [
            "[00:00:02] Samar: Alright team, welcome to the VoiceNote Desktop architecture review. Our main goal today is finalizing the home screen UI and validating our local AI strategy.",
            "[00:00:15] Lead Engineer: Exactly. We are sticking strictly to local components: faster-whisper for speech-to-text, Ollama running Llama 3 for intelligent summarization and task extraction, and PostgreSQL for note metadata.",
            "[00:00:34] AI Architect: Also, for semantic search across all voice notes, we'll embed the transcripts using ChromaDB vector store. That way, natural language queries like 'find our discussion on database migration' will instantly return relevant timestamped audio clips.",
            "[00:01:10] Samar: Awesome. Let's make sure the PySide6 UI feels super fast, responsive, and elegant. No lag during Whisper transcription because all STT and Ollama calls run in background QThreads.",
            "[00:01:45] QA Lead: Will end users be able to export notes into PDF, DOCX, and plain text TXT files directly from the main dashboard?",
            "[00:02:10] Samar: Yes! Export dialog support for PDF, DOCX, and TXT is built directly into the sidebar and header quick options."
        ]
        filtered = [l for l in lines if text.lower() in l.lower()]
        self.transcript_edit.setPlainText("\n\n".join(filtered) if filtered else "No matching dialogue found.")

    def set_note_transcript(self, title: str, transcript_text: str, tags: list = None, metadata_info: str = None):
        """Dynamically load and format a note's real transcript in the viewer."""
        self.current_title = title
        self.title_label.setText(f"Note: {title}")
        if metadata_info:
            self.sub_info.setText(metadata_info)
        if tags is not None:
            self.tags = [f"#{t.lstrip('#')}" for t in tags] if tags else ["#VoiceNote"]
            self.render_tags()

        # Format transcript lines with styled timestamps
        formatted_html_lines = []
        for line in transcript_text.split("\n"):
            line_str = line.strip()
            if not line_str:
                formatted_html_lines.append("<br>")
                continue
            if line_str.startswith("[") and "]" in line_str:
                idx = line_str.find("]")
                timestamp = line_str[:idx + 1]
                rest = line_str[idx + 1:].strip()
                formatted_html_lines.append(f"<b style='color: #6D59A7;'>{timestamp}</b> {rest}<br><br>")
            else:
                formatted_html_lines.append(f"{line_str}<br><br>")

        html = f"<div style='line-height: 1.8; color: #1E2B4B; font-size: 13px;'>{''.join(formatted_html_lines)}</div>"
        self.transcript_edit.setHtml(html)

    def sample_full_html(self) -> str:
        return """<p style='line-height: 1.8; color: #1E2B4B;'>
<b style='color: #6D59A7;'>[00:00:02] Samar:</b> Alright team, welcome to the VoiceNote Desktop architecture review. Our main goal today is finalizing the home screen UI and validating our local AI strategy.<br><br>
<b style='color: #6D59A7;'>[00:00:15] Lead Engineer:</b> Exactly. We are sticking strictly to local components: faster-whisper for speech-to-text, Ollama running Llama 3 for intelligent summarization and task extraction, and PostgreSQL for note metadata.<br><br>
<b style='color: #6D59A7;'>[00:00:34] AI Architect:</b> Also, for semantic search across all voice notes, we'll embed the transcripts using ChromaDB vector store. That way, natural language queries like 'find our discussion on database migration' will instantly return relevant timestamped audio clips.<br><br>
<b style='color: #6D59A7;'>[00:01:10] Samar:</b> <span style='color: #D97706; font-weight: bold;'>Awesome. Let's make sure the PySide6 UI feels super fast, responsive, and elegant. No lag during Whisper transcription because all STT and Ollama calls run in background QThreads.</span><br><br>
<b style='color: #6D59A7;'>[00:01:45] QA Lead:</b> Will end users be able to export notes into PDF, DOCX, and plain text TXT files directly from the main dashboard?<br><br>
<b style='color: #6D59A7;'>[00:02:10] Samar:</b> Yes! Export dialog support for PDF, DOCX, and TXT is built directly into the sidebar and header quick options.
</p>"""

    def load_sample_transcript(self):
        self.transcript_edit.setHtml(self.sample_full_html())
