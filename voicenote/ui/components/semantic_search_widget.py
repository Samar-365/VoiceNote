import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt

try:
    from voicenote.db.database import get_db
except Exception:
    get_db = lambda: None

try:
    from voicenote.core.vector_engine import VectorEngine
except Exception:
    VectorEngine = None

logger = logging.getLogger("SemanticSearchWidget")


class SemanticSearchWidget(QWidget):
    """Semantic Search UI Component powered by ChromaDB vector store and PostgreSQL - Retro Cream Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.vector_engine = None
        self.init_ui()

    def _get_vector_engine(self):
        if self.vector_engine is None and VectorEngine:
            try:
                self.vector_engine = VectorEngine()
            except Exception as e:
                logger.warning(f"ChromaDB VectorEngine not loaded: {e}")
        return self.vector_engine

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
        self.search_bar.setPlaceholderText("e.g. 'Where did we discuss project architecture or task priorities?'")
        self.search_bar.returnPressed.connect(self.perform_search)

        btn_search = QPushButton("Search Notes")
        btn_search.setObjectName("primaryBtn")
        btn_search.clicked.connect(self.perform_search)

        input_row.addWidget(self.search_bar, stretch=1)
        input_row.addWidget(btn_search)
        s_layout.addLayout(input_row)

        s_layout.addSpacing(8)

        # Quick Search Suggestion Chips
        chips_row = QHBoxLayout()
        chip_label = QLabel("Suggestions:")
        chip_label.setStyleSheet("color: #5C6479; font-size: 11px; font-weight: 700;")
        chips_row.addWidget(chip_label)

        chips = ["Architecture", "Database", "Sprint", "Tasks"]
        for chip in chips:
            btn_chip = QPushButton(chip)
            btn_chip.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2DDD3; font-size: 11px; padding: 4px 10px; color: #1E2B4B; font-weight: 700;")
            btn_chip.clicked.connect(lambda _, c=chip: self.apply_chip(c))
            chips_row.addWidget(btn_chip)

        chips_row.addStretch()
        s_layout.addLayout(chips_row)

        layout.addWidget(search_card)

        # Search Results List Container
        self.results_title = QLabel("Semantic Search Results")
        self.results_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
        layout.addWidget(self.results_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(12)

        self.render_results([])

        scroll.setWidget(self.results_container)
        layout.addWidget(scroll)

    def apply_chip(self, chip_text: str):
        self.search_bar.setText(chip_text)
        self.perform_search()

    def perform_search(self):
        query = self.search_bar.text().strip()
        if not query:
            self.results_title.setText("Semantic Search Results")
            self.render_results([])
            return

        results = []
        
        # 1. Try vector engine semantic search
        v_engine = self._get_vector_engine()
        if v_engine:
            try:
                v_res = v_engine.search(query, n_results=5)
                for item in v_res:
                    meta = item.get("metadata", {})
                    results.append({
                        "title": meta.get("title", "Voice Note Match"),
                        "match": f"{int(item.get('similarity', 0.85) * 100)}% Match",
                        "timestamp": meta.get("start_time", "00:00:00"),
                        "snippet": item.get("text", query),
                        "tag": meta.get("category", "#SemanticMatch")
                    })
            except Exception as e:
                logger.warning(f"Vector search execution error: {e}")

        # 2. Fallback / supplementary DB search
        if not results and self.db:
            try:
                db_matches = self.db.search_notes(query)
                for m in db_matches:
                    results.append({
                        "title": m.get("title", "Voice Note"),
                        "match": "Database Match",
                        "timestamp": m.get("duration", "00:00"),
                        "snippet": m.get("summary") or "Note matching search query.",
                        "tag": f"#{m.get('category', 'General')}"
                    })
            except Exception as e:
                logger.warning(f"DB search error: {e}")

        self.results_title.setText(f"Search Results ({len(results)} Found for '{query}')")
        self.render_results(results, query=query)

    def render_results(self, results, query=None):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not results:
            empty_card = QFrame()
            empty_card.setObjectName("cardFrame")
            e_lay = QVBoxLayout(empty_card)
            e_lay.setContentsMargins(20, 24, 20, 24)
            e_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if query:
                msg_title = f"No semantic matches found for '{query}'"
                msg_sub = "Try searching for broader keywords, topics, or action items."
            else:
                msg_title = "Enter a search query above"
                msg_sub = "Search across transcripts and summaries using natural language or topic tags."

            lbl_t = QLabel(msg_title)
            lbl_t.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")
            lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_s = QLabel(msg_sub)
            lbl_s.setStyleSheet("color: #7D8495; font-size: 12px; margin-top: 4px;")
            lbl_s.setAlignment(Qt.AlignmentFlag.AlignCenter)

            e_lay.addWidget(lbl_t)
            e_lay.addWidget(lbl_s)
            self.results_layout.addWidget(empty_card)
            return

        for res in results:
            card = QFrame()
            card.setObjectName("cardFrame")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(20, 16, 20, 16)
            c_lay.setSpacing(10)

            top_row = QHBoxLayout()
            t_lbl = QLabel(res["title"])
            t_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
            
            m_badge = QLabel(res["match"])
            m_badge.setObjectName("badgeActive")

            tag_badge = QLabel(res["tag"])
            tag_badge.setObjectName("badgePurple")

            top_row.addWidget(t_lbl)
            top_row.addWidget(m_badge)
            top_row.addWidget(tag_badge)
            top_row.addStretch()

            c_lay.addLayout(top_row)

            # Snippet text in italics
            snip_lbl = QLabel(f"\"{res['snippet']}\"")
            snip_lbl.setWordWrap(True)
            snip_lbl.setStyleSheet("color: #5C6479; font-style: italic; font-size: 13px; line-height: 1.5;")
            c_lay.addWidget(snip_lbl)

            self.results_layout.addWidget(card)
