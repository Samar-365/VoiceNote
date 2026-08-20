from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame
)
from PySide6.QtCore import Signal, Qt

class HeaderWidget(QFrame):
    """Header Bar Component displaying status indicators & user avatar matching assets/."""
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
        self.search_bar.setPlaceholderText("Search notes, transcripts, or tasks...")
        self.search_bar.setFixedWidth(320)
        self.search_bar.returnPressed.connect(lambda: self.search_triggered.emit(self.search_bar.text()))
        layout.addWidget(self.search_bar)

        layout.addStretch()

        # Engine Status Indicators
        st_ollama = QLabel("Ollama: llama3:8b")
        st_ollama.setObjectName("badgePurple")
        
        st_whisper = QLabel("Whisper: Small.en")
        st_whisper.setObjectName("badgePurple")

        st_db = QLabel("Postgres: Online")
        st_db.setObjectName("badgeActive")

        layout.addWidget(st_ollama)
        layout.addWidget(st_whisper)
        layout.addWidget(st_db)

        layout.addSpacing(12)

        # User Profile Avatar Button
        self.btn_profile = QPushButton("User (Admin)")
        self.btn_profile.setObjectName("primaryBtn")
        self.btn_profile.clicked.connect(self.profile_clicked.emit)
        layout.addWidget(self.btn_profile)

    def set_user(self, user: dict):
        """Update header profile button text with current user info."""
        if not user:
            self.btn_profile.setText("Guest")
            return
        name = user.get("full_name") or user.get("username") or "User"
        username = user.get("username", "")
        self.btn_profile.setText(f"👤 {name} (@{username})" if username else f"👤 {name}")

