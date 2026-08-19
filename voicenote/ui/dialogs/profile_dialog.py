from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QTabWidget, QWidget
)
from PySide6.QtCore import Qt

class ProfileDialog(QDialog):
    """User Profile and System Settings Configuration Dialog - Retro Cream Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings & Profile")
        self.setFixedSize(540, 440)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("User Profile & System Settings")
        header.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        layout.addWidget(header)

        tabs = QTabWidget()

        # Tab 1: Profile & Preferences
        tab_profile = QWidget()
        p_layout = QVBoxLayout(tab_profile)
        p_layout.setSpacing(12)

        p_layout.addWidget(QLabel("<b>User Display Name:</b>"))
        self.name_edit = QLineEdit("Samar")
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
