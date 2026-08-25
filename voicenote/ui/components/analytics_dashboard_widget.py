from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGridLayout, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, Signal

try:
    from voicenote.core.analytics_engine import AnalyticsEngine
except Exception:
    AnalyticsEngine = None


class AnalyticsDashboardWidget(QWidget):
    """Analytics Dashboard UI Component for usage metrics & insights - Retro Cream Theme matching assets/analytics.png."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_engine = AnalyticsEngine() if AnalyticsEngine else None
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #ECE7DF; }")

        container = QWidget()
        container.setStyleSheet("background-color: #ECE7DF;")
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        # Header Title and Refresh Row
        header_row = QHBoxLayout()
        header_v = QVBoxLayout()
        
        title = QLabel("Voice Note Analytics & Insights")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Overview of your recording duration trends, AI processing metrics, and task completion performance.")
        subtitle.setObjectName("subtitleLabel")
        
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        header_row.addLayout(header_v)
        header_row.addStretch()

        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.setFixedWidth(130)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_row.addWidget(self.btn_refresh)

        self.content_layout.addLayout(header_row)

        # Dynamic containers to populate
        self.grid_container = QGridLayout()
        self.grid_container.setSpacing(14)
        self.content_layout.addLayout(self.grid_container)

        self.activity_container = QVBoxLayout()
        self.content_layout.addLayout(self.activity_container)

        self.bottom_row = QHBoxLayout()
        self.bottom_row.setSpacing(14)
        self.content_layout.addLayout(self.bottom_row)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """Fetch latest metrics from AnalyticsEngine and update UI cards."""
        if self.analytics_engine:
            data = self.analytics_engine.get_dashboard_analytics()
        else:
            # Fallback static presentation data
            data = {
                "total_notes": 48,
                "formatted_total_duration": "14h 25m",
                "avg_duration": "18m / note",
                "task_completion_rate_str": "82%",
                "completed_tasks": 37,
                "total_tasks": 45,
                "time_saved_str": "~12.5 hrs",
                "weekly_activity": [
                    ("Mon", 45, 60), ("Tue", 30, 60), ("Wed", 55, 60),
                    ("Thu", 20, 60), ("Fri", 50, 60), ("Sat", 15, 60), ("Sun", 10, 60)
                ],
                "top_tags": [
                    ("#Sprint-Planning", 18), ("#Architecture", 14),
                    ("#Meeting-Notes", 10), ("#Gemini-AI", 6)
                ],
                "sentiment_distribution": {"Positive": 28, "Neutral": 16, "Negative": 4},
                "priority_distribution": {"High": 12, "Medium": 25, "Low": 8}
            }

        self._render_metrics_grid(data)
        self._render_weekly_activity(data.get("weekly_activity", []))
        self._render_bottom_panels(data)

    def _render_metrics_grid(self, data: dict):
        """Render the 4 primary Bento metric cards."""
        # Clear existing grid widgets
        while self.grid_container.count():
            item = self.grid_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_notes = data.get("total_notes", 0)
        tot_dur = data.get("formatted_total_duration", "0m 00s")
        avg_dur = data.get("avg_duration", "0m 00s")
        rate_str = data.get("task_completion_rate_str", "0%")
        comp_tasks = data.get("completed_tasks", 0)
        tot_tasks = data.get("total_tasks", 0)
        time_saved = data.get("time_saved_str", "~0 mins")

        metrics = [
            ("Total Voice Notes", str(total_notes), f"{total_notes} notes indexed", "badgePurple"),
            ("Total Recording Time", tot_dur, f"Avg {avg_dur} / note", "badgePurple"),
            ("Task Completion Rate", rate_str, f"{comp_tasks} of {tot_tasks} completed", "badgeActive"),
            ("Local AI Time Saved", time_saved, "Whisper + Gemini", "badgeAmber"),
        ]

        for i, (m_title, m_val, m_sub, badge_cls) in enumerate(metrics):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setMinimumHeight(115)
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(18, 16, 18, 16)
            c_lay.setSpacing(6)

            t_lbl = QLabel(m_title)
            t_lbl.setStyleSheet("color: #5C6479; font-size: 13px; font-weight: 700;")
            
            val_lbl = QLabel(m_val)
            val_lbl.setStyleSheet("color: #1E2B4B; font-size: 26px; font-weight: 900; line-height: 1.2;")

            badge_row = QHBoxLayout()
            b_lbl = QLabel(m_sub)
            b_lbl.setObjectName(badge_cls)
            badge_row.addWidget(b_lbl)
            badge_row.addStretch()

            c_lay.addWidget(t_lbl)
            c_lay.addWidget(val_lbl)
            c_lay.addLayout(badge_row)

            row, col = divmod(i, 2)
            self.grid_container.addWidget(card, row, col)

    def _render_weekly_activity(self, days: list):
        """Render the Weekly Activity Breakdown Card."""
        while self.activity_container.count():
            item = self.activity_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        act_card = QFrame()
        act_card.setObjectName("cardFrame")
        a_lay = QVBoxLayout(act_card)
        a_lay.setContentsMargins(20, 20, 20, 20)

        a_title = QLabel("Weekly Recording Activity (Minutes / Day)")
        a_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1E2B4B;")
        a_lay.addWidget(a_title)
        a_lay.addSpacing(12)

        for day, val, max_val in days:
            d_row = QHBoxLayout()
            d_lbl = QLabel(day)
            d_lbl.setFixedWidth(40)
            d_lbl.setStyleSheet("font-weight: 700; color: #1E2B4B;")

            p_bar = QProgressBar()
            p_bar.setRange(0, max(1, max_val))
            p_bar.setValue(val)
            pct = int((val / max(1, max_val)) * 100)
            p_bar.setFormat(f"{pct}%")
            p_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

            v_lbl = QLabel(f"{val}m")
            v_lbl.setFixedWidth(45)
            v_lbl.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 600; text-align: right;")

            d_row.addWidget(d_lbl)
            d_row.addWidget(p_bar, stretch=1)
            d_row.addWidget(v_lbl)

            a_lay.addLayout(d_row)

        self.activity_container.addWidget(act_card)

    def _render_bottom_panels(self, data: dict):
        """Render Tag Distribution and Sentiment/Priority Breakdown cards."""
        while self.bottom_row.count():
            item = self.bottom_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Top Tags Breakdown Card
        tag_card = QFrame()
        tag_card.setObjectName("cardFrame")
        t_lay = QVBoxLayout(tag_card)
        t_lay.setContentsMargins(20, 20, 20, 20)

        t_title = QLabel("Top Tag & Topic Breakdown")
        t_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1E2B4B;")
        t_lay.addWidget(t_title)
        t_lay.addSpacing(10)

        tags_data = data.get("top_tags", [])
        if not tags_data:
            empty_lbl = QLabel("No topics extracted yet.")
            empty_lbl.setStyleSheet("color: #7D8495; font-style: italic;")
            t_lay.addWidget(empty_lbl)
        else:
            for tag, count in tags_data[:5]:
                tr_row = QHBoxLayout()
                t_lbl = QLabel(tag)
                t_lbl.setObjectName("badgePurple")
                
                c_lbl = QLabel(f"{count} Notes")
                c_lbl.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 600;")
                
                tr_row.addWidget(t_lbl)
                tr_row.addStretch()
                tr_row.addWidget(c_lbl)
                
                t_lay.addLayout(tr_row)

        self.bottom_row.addWidget(tag_card, stretch=1)

        # 2. Sentiment & Task Priority Distribution Card
        sent_card = QFrame()
        sent_card.setObjectName("cardFrame")
        s_lay = QVBoxLayout(sent_card)
        s_lay.setContentsMargins(20, 20, 20, 20)

        s_title = QLabel("AI Sentiment & Priority Insights")
        s_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1E2B4B;")
        s_lay.addWidget(s_title)
        s_lay.addSpacing(10)

        sentiments = data.get("sentiment_distribution", {"Positive": 0, "Neutral": 0, "Negative": 0})
        priorities = data.get("priority_distribution", {"High": 0, "Medium": 0, "Low": 0})

        # Sentiment row
        s_header = QLabel("Tone Analysis:")
        s_header.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 700;")
        s_lay.addWidget(s_header)

        s_row = QHBoxLayout()
        for s_name, s_count in sentiments.items():
            badge = QLabel(f"{s_name}: {s_count}")
            if s_name == "Positive":
                badge.setObjectName("badgeActive")
            elif s_name == "Negative":
                badge.setObjectName("badgeAmber")
            else:
                badge.setObjectName("badgeCyan")
            s_row.addWidget(badge)
        s_row.addStretch()
        s_lay.addLayout(s_row)
        s_lay.addSpacing(8)

        # Priority row
        p_header = QLabel("Task Priority Load:")
        p_header.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 700;")
        s_lay.addWidget(p_header)

        p_row = QHBoxLayout()
        for p_name, p_count in priorities.items():
            badge = QLabel(f"{p_name}: {p_count}")
            if p_name == "High":
                badge.setObjectName("badgeAmber")
            elif p_name == "Medium":
                badge.setObjectName("badgePurple")
            else:
                badge.setObjectName("badgeCyan")
            p_row.addWidget(badge)
        p_row.addStretch()
        s_lay.addLayout(p_row)

        self.bottom_row.addWidget(sent_card, stretch=1)
