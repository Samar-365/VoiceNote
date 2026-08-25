from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from voicenote.ui.styles import MAIN_STYLE


class ProcessingDialog(QDialog):
    """Modern Bento Loader Dialog shown while audio is being transcribed and analyzed by the AI pipeline."""

    def __init__(self, parent=None, title="AI Speech & Intelligence Pipeline"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(480, 220)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setModal(True)
        self.setStyleSheet(MAIN_STYLE)
        self.init_ui(title)

    def init_ui(self, title_text: str):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Card container
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)

        # Header Row with Icon & Title
        header_row = QHBoxLayout()
        icon_lbl = QLabel("🎙️")
        icon_lbl.setStyleSheet("font-size: 24px;")
        
        title_v = QVBoxLayout()
        self.lbl_title = QLabel(title_text)
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #1E2B4B;")
        
        self.lbl_sub = QLabel("Speech recognition & Gemini AI analysis in progress...")
        self.lbl_sub.setStyleSheet("font-size: 12px; color: #5C6479;")
        
        title_v.addWidget(self.lbl_title)
        title_v.addWidget(self.lbl_sub)

        header_row.addWidget(icon_lbl)
        header_row.addSpacing(6)
        header_row.addLayout(title_v)
        header_row.addStretch()

        badge = QLabel("PROCESSING")
        badge.setObjectName("badgePurple")
        header_row.addWidget(badge)

        card_layout.addLayout(header_row)
        card_layout.addSpacing(6)

        # Animated Indeterminate Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate animation
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E2DDD3;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6D59A7, stop:0.5 #8E74D5, stop:1 #6D59A7);
                border-radius: 4px;
            }
        """)
        card_layout.addWidget(self.progress_bar)

        # Dynamic Status Message
        self.lbl_status = QLabel("Transcribing speech with Whisper STT engine...")
        self.lbl_status.setStyleSheet("font-size: 13px; font-weight: 600; color: #4A3980; margin-top: 4px;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.lbl_status)

        main_layout.addWidget(card)

    def set_status(self, message: str):
        """Update live status message during AI pipeline execution."""
        if message:
            self.lbl_status.setText(message)
