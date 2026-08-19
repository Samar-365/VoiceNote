from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt

class AnalyticsDashboardWidget(QWidget):
    """Analytics Dashboard UI Component for usage metrics & insights - Modern Dark Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header Title
        title = QLabel("📊 Voice Note Analytics & AI Productivity Insights")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Overview of your recording duration trends, AI summarization metrics, and action item completion rates.")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Metric Summary Cards Grid
        grid = QGridLayout()
        grid.setSpacing(12)

        metrics = [
            ("Total Voice Notes", "48", "+12 this week", "badgePurple"),
            ("Total Audio Processed", "14h 25m", "Avg 18m / note", "badgeCyan"),
            ("Task Completion Rate", "82%", "37 of 45 completed", "badgeActive"),
            ("Local AI Time Saved", "~12.5 hrs", "Whisper + Gemini", "badgeAmber"),
        ]

        for i, (m_title, m_val, m_sub, badge_cls) in enumerate(metrics):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setMinimumHeight(105)
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(18, 16, 18, 16)
            c_lay.setSpacing(4)

            t_lbl = QLabel(m_title)
            t_lbl.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 700;")
            
            val_lbl = QLabel(m_val)
            val_lbl.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: 900;")

            badge_row = QHBoxLayout()
            b_lbl = QLabel(m_sub)
            b_lbl.setObjectName(badge_cls)
            badge_row.addWidget(b_lbl)
            badge_row.addStretch()

            c_lay.addWidget(t_lbl)
            c_lay.addWidget(val_lbl)
            c_lay.addLayout(badge_row)

            row, col = divmod(i, 2)
            grid.addWidget(card, row, col)

        layout.addLayout(grid)

        # Weekly Activity Visual Breakdown Card
        act_card = QFrame()
        act_card.setObjectName("cardFrame")
        a_lay = QVBoxLayout(act_card)
        a_lay.setContentsMargins(20, 18, 20, 18)
        a_lay.setSpacing(10)

        a_title = QLabel("📈 Weekly Audio Capture Activity (Minutes / Day)")
        a_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #FFFFFF;")
        a_lay.addWidget(a_title)

        days = [
            ("Mon", 45, 60),
            ("Tue", 30, 60),
            ("Wed", 55, 60),
            ("Thu", 20, 60),
            ("Fri", 50, 60),
            ("Sat", 15, 60),
            ("Sun", 10, 60),
        ]

        for day, val, max_val in days:
            d_row = QHBoxLayout()
            d_lbl = QLabel(day)
            d_lbl.setFixedWidth(40)
            d_lbl.setStyleSheet("font-weight: 700; color: #E2E8F0;")

            p_bar = QProgressBar()
            p_bar.setRange(0, max_val)
            p_bar.setValue(val)

            v_lbl = QLabel(f"{val}m")
            v_lbl.setFixedWidth(45)
            v_lbl.setStyleSheet("color: #818CF8; font-size: 12px; font-weight: 600; font-family: monospace;")

            d_row.addWidget(d_lbl)
            d_row.addWidget(p_bar, stretch=1)
            d_row.addWidget(v_lbl)

            a_lay.addLayout(d_row)

        layout.addWidget(act_card)

        # Tag Distribution Card
        tag_card = QFrame()
        tag_card.setObjectName("cardFrame")
        t_lay = QVBoxLayout(tag_card)
        t_lay.setContentsMargins(20, 18, 20, 18)
        t_lay.setSpacing(10)

        t_title = QLabel("🏷️ Topic & Category Distribution")
        t_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #FFFFFF;")
        t_lay.addWidget(t_title)

        tags_data = [
            ("#Sprint-Planning", 18),
            ("#Architecture", 14),
            ("#Meeting-Notes", 10),
            ("#Gemini-AI", 6)
        ]

        for tag, count in tags_data:
            tr_row = QHBoxLayout()
            t_lbl = QLabel(tag)
            t_lbl.setObjectName("badgePurple")
            
            c_lbl = QLabel(f"{count} Notes")
            c_lbl.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
            
            tr_row.addWidget(t_lbl)
            tr_row.addStretch()
            tr_row.addWidget(c_lbl)
            
            t_lay.addLayout(tr_row)

        layout.addWidget(tag_card)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)
