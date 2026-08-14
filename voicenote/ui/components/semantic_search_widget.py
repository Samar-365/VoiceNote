from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt

class SemanticSearchWidget(QWidget):
    """Semantic Search UI Component powered by ChromaDB vector store - Retro Cream Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sample_results = [
            {
                "title": "Sprint Planning & Local AI Architecture",
                "match": "96% Match",
                "timestamp": "00:00:34",
                "snippet": "For semantic search across all voice notes, we'll embed the transcripts using ChromaDB vector store. That way, natural language queries will instantly return relevant timestamped audio clips.",
                "tag": "#Architecture"
            },
            {
                "title": "VoiceNote Requirements & Tech Stack",
                "match": "88% Match",
                "timestamp": "00:01:10",
                "snippet": "Let's make sure the PySide6 UI feels super fast, responsive, and elegant. No lag during Whisper transcription because all STT and Ollama calls run in background QThreads.",
                "tag": "#Performance"
            },
            {
                "title": "Database Schema & Persistence Review",
                "match": "81% Match",
                "timestamp": "00:02:45",
                "snippet": "PostgreSQL relational persistence holds users, notes, transcripts, tags, and tasks while local filesystem caches raw audio recordings.",
                "tag": "#PostgreSQL"
            }
        ]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header Search Area
        search_card = QFrame()
        search_card.setObjectName("heroCard")
        s_layout = QVBoxLayout(search_card)
        s_layout.setContentsMargins(24, 24, 24, 24)

        stitle = QLabel("Natural Language Semantic Search")
        stitle.setObjectName("titleLabel")
        ssub = QLabel("Query your voice notes by meaning and context using local ChromaDB vector embeddings.")
        ssub.setObjectName("subtitleLabel")

        s_layout.addWidget(stitle)
        s_layout.addWidget(ssub)
        s_layout.addSpacing(12)

        # Input Row
        input_row = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("e.g. 'Where did we discuss database schema migration and vector search?'")
        self.search_bar.setStyleSheet("font-size: 14px; padding: 10px 14px;")
        
        btn_search = QPushButton("Search Notes")
        btn_search.setObjectName("primaryBtn")
        btn_search.setStyleSheet("padding: 10px 20px; font-size: 14px;")
        btn_search.clicked.connect(self.perform_search)

        input_row.addWidget(self.search_bar, stretch=1)
        input_row.addWidget(btn_search)

        s_layout.addLayout(input_row)

        # Quick Filter Chips
        chips_row = QHBoxLayout()
        chips_row.addWidget(QLabel("Suggested Queries:"))
        
        chips = ["Database Migration", "Ollama LLM", "Whisper STT", "Export Formats"]
        for chip in chips:
            btn_chip = QPushButton(chip)
            btn_chip.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2DDD3; font-size: 11px; padding: 4px 10px; color: #1E2B4B;")
            btn_chip.clicked.connect(lambda _, c=chip: self.apply_chip(c))
            chips_row.addWidget(btn_chip)

        chips_row.addStretch()
        s_layout.addLayout(chips_row)

        layout.addWidget(search_card)

        # Search Results List Container
        self.results_title = QLabel("Top Semantic Matches (3 Results Found)")
        self.results_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
        layout.addWidget(self.results_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(12)

        self.render_results()

        scroll.setWidget(self.results_container)
        layout.addWidget(scroll)

    def apply_chip(self, chip_text: str):
        self.search_bar.setText(f"Find discussions regarding {chip_text}")
        self.perform_search()

    def perform_search(self):
        self.render_results()

    def render_results(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for item in self.sample_results:
            card = QFrame()
            card.setObjectName("cardFrame")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 16, 16, 16)

            h_row = QHBoxLayout()
            title = QLabel(item['title'])
            title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")

            match_lbl = QLabel(item["match"])
            match_lbl.setObjectName("badgeActive")

            tag_lbl = QLabel(item["tag"])
            tag_lbl.setObjectName("badgePurple")

            h_row.addWidget(title)
            h_row.addWidget(match_lbl)
            h_row.addWidget(tag_lbl)
            h_row.addStretch()

            btn_jump = QPushButton(f"Jump to {item['timestamp']}")
            btn_jump.setStyleSheet("background-color: #ECE8E1; color: #6D59A7; font-size: 12px; font-weight: 600; border: 1px solid #E2DDD3;")
            h_row.addWidget(btn_jump)

            c_layout.addLayout(h_row)
            c_layout.addSpacing(6)

            snippet_lbl = QLabel(f'"{item["snippet"]}"')
            snippet_lbl.setWordWrap(True)
            snippet_lbl.setStyleSheet("color: #1E2B4B; font-style: italic; font-size: 13px; background-color: #F7F5F0; padding: 10px; border-radius: 0px; border: 1px solid #E2DDD3;")
            c_layout.addWidget(snippet_lbl)

            self.results_layout.addWidget(card)
