from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt

class SidebarWidget(QFrame):
    """Navigation Sidebar Widget - Modern Dark Bento Theme."""
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
        layout.setContentsMargins(14, 20, 14, 20)
        layout.setSpacing(6)

        # App Brand Header
        brand_v = QVBoxLayout()
        brand_v.setSpacing(4)
        
        brand_row = QHBoxLayout()
        logo_icon = QLabel("🎙️")
        logo_icon.setStyleSheet("font-size: 20px;")
        
        brand_name = QLabel("VoiceNote AI")
        brand_name.setStyleSheet("font-size: 17px; font-weight: 900; color: #FFFFFF; letter-spacing: 0.5px;")
        
        brand_row.addWidget(logo_icon)
        brand_row.addWidget(brand_name)
        brand_row.addStretch()
        brand_v.addLayout(brand_row)

        sub_label = QLabel("Desktop Studio v2.0")
        sub_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600; padding-left: 28px;")
        brand_v.addWidget(sub_label)
        
        privacy_badge = QLabel("🛡️ LOCAL PRIVACY FIRST")
        privacy_badge.setObjectName("badgeActive")
        privacy_badge.setStyleSheet("margin-top: 6px; padding: 4px 8px; font-size: 10px; font-weight: 800;")
        brand_v.addWidget(privacy_badge)

        layout.addLayout(brand_v)
        layout.addSpacing(18)

        # Nav Section Title
        sec_lbl = QLabel("MAIN WORKSPACE")
        sec_lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 800; letter-spacing: 1px; padding: 0 4px;")
        layout.addWidget(sec_lbl)

        # Nav Buttons
        nav_items = [
            ("⚡ Studio Recorder", 0),
            ("📝 Transcripts & Notes", 1),
            ("🧠 AI Summaries & Tasks", 2),
            ("🔍 Semantic Vector Search", 3),
            ("📊 Analytics Dashboard", 4),
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
        sep.setStyleSheet("background-color: #1E293B;")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Bottom Actions
        btn_export = QPushButton("📤 Export Notes Hub")
        btn_export.setObjectName("navBtn")
        btn_export.clicked.connect(self.export_clicked.emit)
        layout.addWidget(btn_export)

        btn_settings = QPushButton("⚙️ Settings & AI Config")
        btn_settings.setObjectName("navBtn")
        btn_settings.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(btn_settings)

    def on_nav_click(self, index: int):
        for idx, btn in enumerate(self.buttons):
            btn.setProperty("active", "true" if idx == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.nav_changed.emit(index)
