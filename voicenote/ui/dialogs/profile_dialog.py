from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QTabWidget, QWidget
)
from PySide6.QtCore import Qt

class ProfileDialog(QDialog):
    """User Profile and AI Engine Settings Configuration Dialog - Modern Dark Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings & AI Pipeline Configuration")
        self.setFixedSize(560, 460)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("⚙️ User Profile & AI Pipeline Configuration")
        header.setStyleSheet("font-size: 17px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(header)

        tabs = QTabWidget()

        # Tab 1: Profile & Preferences
        tab_profile = QWidget()
        p_layout = QVBoxLayout(tab_profile)
        p_layout.setContentsMargins(14, 14, 14, 14)
        p_layout.setSpacing(12)

        p_layout.addWidget(QLabel("<b>User Display Name:</b>"))
        self.name_edit = QLineEdit("Samar S.")
        p_layout.addWidget(self.name_edit)

        p_layout.addWidget(QLabel("<b>Primary Role / Ownership:</b>"))
        self.role_edit = QLineEdit("UI/UX, Recording, Export & Analytics Lead")
        p_layout.addWidget(self.role_edit)

        p_layout.addWidget(QLabel("<b>Default Audio & Export Directory:</b>"))
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit("C:/Users/samar/Documents/VoiceNotes")
        btn_browse = QPushButton("Browse...")
        path_row.addWidget(self.path_edit)
        path_row.addWidget(btn_browse)
        p_layout.addLayout(path_row)

        p_layout.addStretch()
        tabs.addTab(tab_profile, "👤 Profile")

        # Tab 2: AI & Inference Models
        tab_ai = QWidget()
        a_layout = QVBoxLayout(tab_ai)
        a_layout.setContentsMargins(14, 14, 14, 14)
        a_layout.setSpacing(12)

        a_layout.addWidget(QLabel("<b>LLM Summarization & Task Engine:</b>"))
        self.ollama_combo = QComboBox()
        self.ollama_combo.addItems([
            "Gemini 1.5 Flash (Cloud - Ultra Fast)",
            "Ollama: llama3:8b-instruct (Local Privacy)",
            "Groq: llama-3.3-70b-versatile (Cloud Fast)",
            "Ollama: gemma2:9b-instruct (Local)"
        ])
        a_layout.addWidget(self.ollama_combo)

        a_layout.addWidget(QLabel("<b>Whisper STT Model Size:</b>"))
        self.whisper_combo = QComboBox()
        self.whisper_combo.addItems([
            "small.en (Local faster-whisper - High accuracy)",
            "base.en (Local faster-whisper - Standard)",
            "Groq Whisper-large-v3 (Cloud STT - Realtime)",
            "medium.en (Local faster-whisper - Highest precision)"
        ])
        self.whisper_combo.setCurrentIndex(0)
        a_layout.addWidget(self.whisper_combo)

        a_layout.addWidget(QLabel("<b>Hardware Acceleration Engine:</b>"))
        self.hw_combo = QComboBox()
        self.hw_combo.addItems([
            "Auto Detect (NVIDIA CUDA GPU Available)",
            "DirectML (Windows GPU Acceleration)",
            "CPU Only (CTranslate2 Int8 Optimized)"
        ])
        a_layout.addWidget(self.hw_combo)

        a_layout.addStretch()
        tabs.addTab(tab_ai, "🧠 AI Pipeline")

        # Tab 3: Database & Storage
        tab_db = QWidget()
        d_layout = QVBoxLayout(tab_db)
        d_layout.setContentsMargins(14, 14, 14, 14)
        d_layout.setSpacing(12)

        d_card = QFrame()
        d_card.setObjectName("glassFrame")
        dc_lay = QVBoxLayout(d_card)
        dc_lay.setSpacing(8)

        dc_lay.addWidget(QLabel("<b>SQLite Relational DB:</b> <span style='color: #34D399;'>Connected (voicenote.db)</span>"))
        dc_lay.addWidget(QLabel("<b>ChromaDB Vector Store:</b> <span style='color: #67E8F9;'>Ready (48 note embeddings indexed)</span>"))
        dc_lay.addWidget(QLabel("<b>Local Disk Cache:</b> 142 GB Free"))
        dc_lay.addWidget(QLabel("<b>Privacy Mode:</b> <span style='color: #34D399;'>100% Local-First Storage</span>"))

        d_layout.addWidget(d_card)
        d_layout.addStretch()
        tabs.addTab(tab_db, "💾 Database & Storage")

        layout.addWidget(tabs)

        # Dialog buttons
        btn_row = QHBoxLayout()
        btn_close = QPushButton("Cancel")
        btn_close.clicked.connect(self.reject)

        btn_save = QPushButton("💾 Save Settings")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)
