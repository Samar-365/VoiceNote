from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QScrollArea, QDialog, QInputDialog
)
from PySide6.QtCore import Qt

class TranscriptViewWidget(QWidget):
    """Transcript Viewer & Tag Manager UI Component - Retro Cream Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = ["#Sprint-Architecture", "#Ollama-AI", "#Local-Whisper", "#High-Priority"]
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

        top_row = QHBoxLayout()
        title_v = QVBoxLayout()
        
        self.title_label = QLabel("Note: Sprint Planning & Local AI Architecture")
        self.title_label.setObjectName("titleLabel")
        
        sub_info = QLabel("Recorded Today at 02:30 PM  •  Duration: 04m 32s  •  Format: WAV 16kHz Mono  •  Engine: faster-whisper")
        sub_info.setObjectName("subtitleLabel")
        
        title_v.addWidget(self.title_label)
        title_v.addWidget(sub_info)
        top_row.addLayout(title_v)
        top_row.addStretch()

        # Action Buttons
        btn_copy = QPushButton("Copy Text")
        btn_copy.clicked.connect(self.copy_transcript)
        top_row.addWidget(btn_copy)

        card_layout.addLayout(top_row)
        card_layout.addSpacing(10)

        # Tag Manager Row
        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("Tags:"))

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
        self.transcript_edit.setReadOnly(True)
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
        self.transcript_edit.selectAll()
        self.transcript_edit.copy()
        cursor = self.transcript_edit.textCursor()
        cursor.clearSelection()
        self.transcript_edit.setTextCursor(cursor)

    def filter_transcript(self, query: str):
        pass

    def load_sample_transcript(self):
        sample_html = """
        <style>
            .time { color: #6D59A7; font-weight: bold; font-family: monospace; }
            .speaker { color: #1E2B4B; font-weight: bold; }
            .p { margin-bottom: 12px; font-size: 14px; line-height: 1.6; color: #1E2B4B; }
            .highlight { background-color: #FEF6E6; color: #D97706; padding: 2px 4px; border-radius: 0px; font-weight: 600; }
        </style>
        
        <div class="p">
            <span class="time">[00:00:02]</span> <span class="speaker">Samar:</span> 
            Alright team, welcome to the VoiceNote Desktop architecture review. Our main goal today is finalizing the home screen UI and validating our local AI strategy.
        </div>

        <div class="p">
            <span class="time">[00:00:15]</span> <span class="speaker">Lead Engineer:</span> 
            Exactly. We are sticking strictly to local components: faster-whisper for speech-to-text, Ollama running Llama 3 for intelligent summarization and task extraction, and PostgreSQL for note metadata.
        </div>

        <div class="p">
            <span class="time">[00:00:34]</span> <span class="speaker">AI Architect:</span> 
            Also, for semantic search across all voice notes, we'll embed the transcripts using ChromaDB vector store. That way, natural language queries like 'find our discussion on database migration' will instantly return relevant timestamped audio clips.
        </div>

        <div class="p">
            <span class="time">[00:01:10]</span> <span class="speaker">Samar:</span> 
            <span class="highlight">Awesome. Let's make sure the PySide6 UI feels super fast, responsive, and elegant. No lag during Whisper transcription because all STT and Ollama calls run in background QThreads.</span>
        </div>

        <div class="p">
            <span class="time">[00:01:45]</span> <span class="speaker">QA Lead:</span> 
            Will end users be able to export notes into PDF, DOCX, and plain text TXT files directly from the main dashboard?
        </div>

        <div class="p">
            <span class="time">[00:02:10]</span> <span class="speaker">Samar:</span> 
            Yes! Export dialog support for PDF, DOCX, and TXT is built directly into the sidebar and header quick options.
        </div>
        """
        self.transcript_edit.setHtml(sample_html)
