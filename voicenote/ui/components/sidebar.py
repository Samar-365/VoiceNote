from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt

class SidebarWidget(QFrame):
    """Navigation Sidebar Widget - Retro Warm Cream Theme matching assets/."""
    nav_changed = Signal(int)       # Tab index
    export_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setFixedWidth(240)
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        # App Brand Header
        brand_v = QVBoxLayout()
        brand_name = QLabel("VoiceNote")
        brand_name.setStyleSheet("font-size: 18px; font-weight: 800; color: #4A3980;")
        
        privacy_badge = QLabel("LOCAL AI [SECURE]")
        privacy_badge.setObjectName("badgeActive")
        privacy_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        brand_v.addWidget(brand_name)
        brand_v.addWidget(privacy_badge)

        layout.addLayout(brand_v)
        layout.addSpacing(20)

        # Nav Buttons
        nav_items = [
            ("Home  Recorder", 0),
            ("Transcripts  Notes", 1),
            ("AI Summary  Tasks", 2),
            ("Semantic Search", 3),
            ("Analytics Dashboard", 4),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.setProperty("active", "true" if index == 0 else "false")
            btn.clicked.connect(lambda _, idx=index: self.on_nav_click(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #E5E0D6;")
        layout.addWidget(sep)
        layout.addSpacing(10)

        # Quick Actions & Settings
        btn_export = QPushButton("Export Notes")
        btn_export.clicked.connect(self.export_clicked.emit)
        layout.addWidget(btn_export)

        btn_settings = QPushButton("Settings  Profile")
        btn_settings.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(btn_settings)

    def on_nav_click(self, index: int):
        for idx, btn in enumerate(self.buttons):
            btn.setProperty("active", "true" if idx == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.nav_changed.emit(index)
