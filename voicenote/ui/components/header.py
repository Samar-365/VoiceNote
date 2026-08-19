from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame
)
from PySide6.QtCore import Signal, Qt

class HeaderWidget(QFrame):
    """Header Bar Component with Omni-Search & AI Pipeline Status."""
    profile_clicked = Signal()
    search_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setFixedHeight(64)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Global Quick Search LineEdit
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍  Search notes, transcripts, or ask AI... (Ctrl+K)")
        self.search_bar.setFixedWidth(360)
        self.search_bar.returnPressed.connect(lambda: self.search_triggered.emit(self.search_bar.text()))
        layout.addWidget(self.search_bar)

        layout.addStretch()

        # Engine Status Indicators
        st_whisper = QLabel("🟢 Whisper STT: Ready")
        st_whisper.setObjectName("badgeActive")
        
        st_chroma = QLabel("🔵 ChromaDB: Synced")
        st_chroma.setObjectName("badgeCyan")

        st_gemini = QLabel("🟣 Gemini / Ollama: Active")
        st_gemini.setObjectName("badgePurple")

        layout.addWidget(st_whisper)
        layout.addWidget(st_chroma)
        layout.addWidget(st_gemini)

        layout.addSpacing(8)

        # User Profile Avatar Button
        btn_profile = QPushButton("👤 Samar S. (Admin)")
        btn_profile.setObjectName("primaryBtn")
        btn_profile.clicked.connect(self.profile_clicked.emit)
        layout.addWidget(btn_profile)
