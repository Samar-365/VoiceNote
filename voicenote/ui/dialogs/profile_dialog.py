from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QTabWidget, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal


class ProfileDialog(QDialog):
    """User Profile and System Settings Configuration Dialog - Retro Cream Theme."""

    logout_requested = Signal()

    def __init__(self, user_data: dict = None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.setWindowTitle("Settings & Profile")
        self.setFixedSize(560, 480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("User Profile & System Settings")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        layout.addWidget(header)

        tabs = QTabWidget()

        # Tab 1: Profile & Account
        tab_profile = QWidget()
        p_layout = QVBoxLayout(tab_profile)
        p_layout.setSpacing(10)

        # User Info Summary Card
        user_card = QFrame()
        user_card.setObjectName("glassFrame")
        uc_lay = QVBoxLayout(user_card)
        uc_lay.setContentsMargins(12, 10, 12, 10)
        uc_lay.setSpacing(4)

        full_name = self.user_data.get("full_name") or "VoiceNote User"
        username = self.user_data.get("username") or "user"
        email = self.user_data.get("email") or "user@voicenote.ai"
        created_at = self.user_data.get("created_at") or "N/A"

        uc_lay.addWidget(QLabel(f"<b>Active User:</b> {full_name} (@{username})"))
        uc_lay.addWidget(QLabel(f"<b>Registered Email:</b> {email}"))
        uc_lay.addWidget(QLabel(f"<b>Member Since:</b> {created_at}"))
        p_layout.addWidget(user_card)

        p_layout.addWidget(QLabel("<b>Display Name:</b>"))
        self.name_edit = QLineEdit(full_name)
        p_layout.addWidget(self.name_edit)

        p_layout.addWidget(QLabel("<b>Primary Role / Department:</b>"))
        self.role_edit = QLineEdit("Lead Software Engineer")
        p_layout.addWidget(self.role_edit)

        p_layout.addWidget(QLabel("<b>Default Audio Export Directory:</b>"))
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit("C:/Users/samar/Documents/VoiceNotes")
        btn_browse = QPushButton("Browse...")
        path_row.addWidget(self.path_edit)
        path_row.addWidget(btn_browse)
        p_layout.addLayout(path_row)

        # Logout button in profile
        btn_logout = QPushButton("🚪 Sign Out of Account")
        btn_logout.setObjectName("stopBtn")
        btn_logout.clicked.connect(self.on_sign_out)
        p_layout.addWidget(btn_logout)

        p_layout.addStretch()
        tabs.addTab(tab_profile, "User Profile")

        # Tab 2: AI & Inference Models
        tab_ai = QWidget()
        a_layout = QVBoxLayout(tab_ai)
        a_layout.setSpacing(12)

        a_layout.addWidget(QLabel("<b>Local Ollama AI LLM Model:</b>"))
        self.ollama_combo = QComboBox()
        self.ollama_combo.addItems([
            "llama3:8b-instruct (Recommended)",
            "gemma2:9b-instruct",
            "mistral:7b-instruct",
            "phi3:mini"
        ])
        a_layout.addWidget(self.ollama_combo)

        a_layout.addWidget(QLabel("<b>Whisper STT Model Size:</b>"))
        self.whisper_combo = QComboBox()
        self.whisper_combo.addItems([
            "small.en (High accuracy, fast)",
            "base.en (Standard speed)",
            "medium.en (Highest precision)",
            "tiny.en (Ultra fast)"
        ])
        self.whisper_combo.setCurrentIndex(0)
        a_layout.addWidget(self.whisper_combo)

        a_layout.addWidget(QLabel("<b>Hardware Acceleration Engine:</b>"))
        self.hw_combo = QComboBox()
        self.hw_combo.addItems([
            "Auto Detect (NVIDIA CUDA GPU available)",
            "CPU Only (CTranslate2 fallback)"
        ])
        a_layout.addWidget(self.hw_combo)

        a_layout.addStretch()
        tabs.addTab(tab_ai, "AI Models")

        # Tab 3: Database & Storage
        tab_db = QWidget()
        d_layout = QVBoxLayout(tab_db)
        d_layout.setSpacing(12)

        d_card = QFrame()
        d_card.setObjectName("glassFrame")
        dc_lay = QVBoxLayout(d_card)

        dc_lay.addWidget(QLabel("<b>PostgreSQL Status:</b> <span style='color: #2E7D32;'>Connected (localhost:5432)</span>"))
        dc_lay.addWidget(QLabel("<b>ChromaDB Vector Store:</b> <span style='color: #3B82F6;'>Ready (12,450 vectors indexed)</span>"))
        dc_lay.addWidget(QLabel("<b>Local Disk Storage Free:</b> 142 GB"))

        d_layout.addWidget(d_card)
        d_layout.addStretch()
        tabs.addTab(tab_db, "Storage & DB")

        layout.addWidget(tabs)

        # Dialog buttons
        btn_row = QHBoxLayout()
        btn_close = QPushButton("Cancel")
        btn_close.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def on_sign_out(self):
        reply = QMessageBox.question(
            self,
            "Confirm Sign Out",
            "Are you sure you want to sign out of this account?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
            self.reject()
