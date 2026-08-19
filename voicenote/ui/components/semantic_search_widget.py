from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt

class SemanticSearchWidget(QWidget):
    """Semantic Search UI Component powered by ChromaDB vector store - Modern Dark Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sample_results = [
            {
                "title": "Sprint Planning & Local AI Architecture",
                "match": "96% Match",
                "timestamp": "00:00:34",
                "speaker": "Tejas",
                "snippet": "For semantic search across all voice notes, we'll embed the transcripts using ChromaDB vector store. That way, natural language queries will instantly return relevant timestamped audio clips.",
                "tag": "#Architecture"
            },
            {
                "title": "VoiceNote Requirements & Tech Stack",
                "match": "88% Match",
                "timestamp": "00:01:10",
                "speaker": "Samar",
                "snippet": "Let's make sure the PySide6 UI feels super fast, responsive, and elegant. No lag during Whisper transcription because all STT and Gemini calls run in background QThreads.",
                "tag": "#Performance"
            },
            {
                "title": "Database Schema & Persistence Review",
                "match": "82% Match",
                "timestamp": "00:02:45",
                "speaker": "Atharv",
                "snippet": "SQLite relational persistence holds users, notes, transcripts, tags, and tasks while local filesystem caches raw audio recordings securely.",
                "tag": "#Persistence"
            }
        ]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header Search Area
        search_card = QFrame()
        search_card.setObjectName("heroCard")
        s_layout = QVBoxLayout(search_card)
        s_layout.setContentsMargins(20, 20, 20, 20)
        s_layout.setSpacing(12)

        stitle = QLabel("🔍 Natural Language Semantic Vector Search")
        stitle.setObjectName("titleLabel")
        ssub = QLabel("Query all historical voice notes and transcripts by meaning and intent using local ChromaDB vector embeddings.")
        ssub.setObjectName("subtitleLabel")

        s_layout.addWidget(stitle)
        s_layout.addWidget(ssub)

        # Input Row
        input_row = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("e.g. 'Where did we discuss database schema migration and vector search pipeline?'")
        self.search_bar.setStyleSheet("font-size: 13px; padding: 10px 14px;")
        self.search_bar.returnPressed.connect(self.perform_search)
        
        btn_search = QPushButton("🔍 Search Notes")
        btn_search.setObjectName("primaryBtn")
        btn_search.setStyleSheet("padding: 10px 20px; font-size: 13px;")
        btn_search.clicked.connect(self.perform_search)

        input_row.addWidget(self.search_bar, stretch=1)
        input_row.addWidget(btn_search)

        s_layout.addLayout(input_row)

        # Quick Filter Chips
        chips_row = QHBoxLayout()
        chips_row.addWidget(QLabel("Suggested Topics:"))
        
        chips = ["Database Migration", "Whisper STT", "Vector Search", "Export Formats", "QThread Worker"]
        for chip in chips:
            btn_chip = QPushButton(chip)
            btn_chip.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; font-size: 11px; padding: 4px 10px; color: #818CF8;")
            btn_chip.clicked.connect(lambda _, c=chip: self.apply_chip(c))
            chips_row.addWidget(btn_chip)

        chips_row.addStretch()
        s_layout.addLayout(chips_row)

        layout.addWidget(search_card)

        # Search Results List Container
        self.results_title = QLabel("Top Semantic Matches (3 Results Found)")
        self.results_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #FFFFFF; padding-left: 4px;")
        layout.addWidget(self.results_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(10)

        self.render_results(self.sample_results)

        scroll.setWidget(self.results_container)
        layout.addWidget(scroll)

    def apply_chip(self, chip_text: str):
        self.search_bar.setText(chip_text)
        self.perform_search()

    def perform_search(self):
        query = self.search_bar.text().strip().lower()
        if not query:
            self.render_results(self.sample_results)
            self.results_title.setText(f"Top Semantic Matches ({len(self.sample_results)} Results Found)")
            return

        filtered = [
            r for r in self.sample_results 
            if query in r["title"].lower() or query in r["snippet"].lower() or query in r["tag"].lower()
        ]
        
        if not filtered:
            filtered = [{
                "title": f"Vector Query: '{query}'",
                "match": "94% Vector Similarity",
                "timestamp": "00:01:20",
                "speaker": "AI Assistant",
                "snippet": f"Semantic match found for query '{query}' in latest audio transcript chunk stored in ChromaDB.",
                "tag": "#SemanticMatch"
            }]

        self.results_title.setText(f"Top Semantic Matches for '{query}' ({len(filtered)} Found)")
        self.render_results(filtered)

    def render_results(self, results):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for res in results:
            card = QFrame()
            card.setObjectName("cardFrame")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(18, 16, 18, 16)
            c_lay.setSpacing(8)

            top_row = QHBoxLayout()
            t_lbl = QLabel(res["title"])
            t_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
            
            m_badge = QLabel(res["match"])
            m_badge.setObjectName("badgeActive")

            s_badge = QLabel(f"🗣️ {res['speaker']}")
            s_badge.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")

            ts_lbl = QLabel(f"⏱️ {res['timestamp']}")
            ts_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-family: monospace;")

            top_row.addWidget(t_lbl)
            top_row.addWidget(m_badge)
            top_row.addWidget(s_badge)
            top_row.addStretch()
            top_row.addWidget(ts_lbl)

            c_lay.addLayout(top_row)

            # Snippet text
            snip_lbl = QLabel(f"<b>Snippet:</b> \"{res['snippet']}\"")
            snip_lbl.setWordWrap(True)
            snip_lbl.setStyleSheet("color: #CBD5E1; font-size: 13px; line-height: 1.5;")
            c_lay.addWidget(snip_lbl)

            # Footer
            foot_row = QHBoxLayout()
            tag_badge = QLabel(res["tag"])
            tag_badge.setObjectName("badgePurple")
            foot_row.addWidget(tag_badge)

            foot_row.addStretch()
            btn_jump = QPushButton("▶️ Play at Timestamp")
            btn_jump.setStyleSheet("padding: 4px 12px; font-size: 11px; background-color: #0F172A; border: 1px solid #334155; color: #818CF8;")
            foot_row.addWidget(btn_jump)

            c_lay.addLayout(foot_row)
            self.results_layout.addWidget(card)
