"""
VoiceNote Intelligence Analytics Dashboard UI Component.
Provides multi-metric workspace answering:
"What is happening across all my meetings and conversations?"
100% data-driven metrics from actual recordings, transcripts, tasks, and AI summaries.
"""

from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGridLayout, QScrollArea, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from voicenote.core.analytics_engine import AnalyticsEngine


class AnalyticsDashboardWidget(QWidget):
    """Voice Note Intelligence Dashboard Component - Retro Cream Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_engine = AnalyticsEngine()
        self.selected_days_filter = 30
        self.init_ui()
        self.refresh_data()

    def set_time_filter(self, days: int):
        self.selected_days_filter = days
        self._update_filter_buttons()
        self.refresh_data()

    def _update_filter_buttons(self):
        active_style = "background-color: #6D59A7; color: #FFFFFF; font-weight: 700; border: 1px solid #5B4896; border-radius: 4px; padding: 5px 12px;"
        inactive_style = "background-color: #FFFFFF; color: #1E2B4B; font-weight: 600; border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px 12px;"
        
        self.btn_7d.setStyleSheet(active_style if self.selected_days_filter == 7 else inactive_style)
        self.btn_30d.setStyleSheet(active_style if self.selected_days_filter == 30 else inactive_style)
        self.btn_90d.setStyleSheet(active_style if self.selected_days_filter == 90 else inactive_style)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #ECE7DF; }")

        container = QWidget()
        container.setStyleSheet("background-color: #ECE7DF;")
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(0, 0, 0, 20)
        self.content_layout.setSpacing(16)

        # Header Title and Filter Bar Row
        header_row = QHBoxLayout()
        header_v = QVBoxLayout()
        
        title = QLabel("Voice Note Intelligence")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Comprehensive metrics and meeting intelligence across all your recorded conversations.")
        subtitle.setObjectName("subtitleLabel")
        
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        header_row.addLayout(header_v)
        header_row.addStretch()

        # Time range filter buttons
        filter_box = QHBoxLayout()
        filter_box.setSpacing(4)
        
        self.btn_7d = QPushButton("7 Days")
        self.btn_7d.clicked.connect(lambda: self.set_time_filter(7))
        self.btn_30d = QPushButton("30 Days")
        self.btn_30d.clicked.connect(lambda: self.set_time_filter(30))
        self.btn_90d = QPushButton("90 Days")
        self.btn_90d.clicked.connect(lambda: self.set_time_filter(90))
        
        filter_box.addWidget(self.btn_7d)
        filter_box.addWidget(self.btn_30d)
        filter_box.addWidget(self.btn_90d)
        header_row.addLayout(filter_box)

        # Refresh Data button
        self.btn_refresh = QPushButton("↻ Refresh")
        self.btn_refresh.setFixedWidth(100)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet("background-color: #FFFFFF; font-weight: 700; border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px 12px; color: #1E2B4B;")
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_row.addWidget(self.btn_refresh)

        self.content_layout.addLayout(header_row)

        # Dynamic Content Containers
        self.empty_state_frame = QFrame()
        self.empty_state_frame.setObjectName("cardFrame")
        self._init_empty_state()
        self.content_layout.addWidget(self.empty_state_frame)

        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(12)
        self.content_layout.addLayout(self.metrics_grid)

        # Activity & Productivity Row
        self.mid_row = QHBoxLayout()
        self.mid_row.setSpacing(14)
        self.content_layout.addLayout(self.mid_row)

        # Speakers & Themes Row
        self.insights_row = QHBoxLayout()
        self.insights_row.setSpacing(14)
        self.content_layout.addLayout(self.insights_row)

        # Decisions & Questions Row
        self.bottom_row = QHBoxLayout()
        self.bottom_row.setSpacing(14)
        self.content_layout.addLayout(self.bottom_row)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self._update_filter_buttons()

    def _init_empty_state(self):
        """Construct encouraging empty state for zero conversation data."""
        es_lay = QVBoxLayout(self.empty_state_frame)
        es_lay.setContentsMargins(32, 32, 32, 32)
        es_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        from voicenote.ui.icon_helper import get_svg_pixmap
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_svg_pixmap("mic", color="#6D59A7", size=36))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        t_lbl = QLabel("<b>No conversation data yet.</b>")
        t_lbl.setStyleSheet("font-size: 16px; color: #1E2B4B; margin-top: 8px;")
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("Record your first VoiceNote to start building meeting insights, tracking decisions, and viewing intelligence analytics.")
        sub_lbl.setStyleSheet("color: #64748B; font-size: 13px; margin-top: 4px;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        es_lay.addWidget(icon_lbl)
        es_lay.addWidget(t_lbl)
        es_lay.addWidget(sub_lbl)
        self.empty_state_frame.hide()

    def refresh_data(self):
        """Fetch real data from AnalyticsEngine and update UI."""
        data = self.analytics_engine.get_dashboard_analytics(days_filter=self.selected_days_filter)
        
        has_data = data.get("has_data", False)
        if not has_data:
            self.empty_state_frame.show()
        else:
            self.empty_state_frame.hide()

        self._render_metrics_grid(data)
        self._render_mid_panels(data)
        self._render_insights_panels(data)
        self._render_bottom_panels(data)

    def _render_metrics_grid(self, data: dict):
        """Render the 8 core overview cards."""
        while self.metrics_grid.count():
            item = self.metrics_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cards = [
            ("Total Conversations", str(data.get("total_notes", 0)), f"Last {self.selected_days_filter} days", "badgePurple"),
            ("Total Recording Time", data.get("formatted_total_duration", "0m 00s"), f"Avg {data.get('avg_duration', '0m 00s')}", "badgePurple"),
            ("Total Speakers", f"{data.get('total_speakers', 0)} Detected", "Voice separation", "badgeActive"),
            ("Words Transcribed", f"{data.get('total_words', 0):,}", f"~{data.get('words_per_minute', 0)} WPM", "badgeActive"),
            ("Action Items", f"{data.get('completed_tasks', 0)} / {data.get('total_tasks', 0)}", f"{data.get('task_completion_rate_str', '0%')} Completed", "badgeActive"),
            ("Actions / Meeting", str(data.get("actions_per_meeting", 0.0)), "Average productivity", "badgePurple"),
            ("Decisions Captured", str(data.get("decisions_count", 0)), "Explicit alignments", "badgePurple"),
            ("Open Questions", str(data.get("questions_count", 0)), "Pending follow-ups", "badgeAmber"),
        ]

        for i, (title, val, sub, badge_cls) in enumerate(cards):
            card = QFrame()
            card.setObjectName("cardFrame")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(16, 14, 16, 14)
            c_lay.setSpacing(4)

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700; text-transform: uppercase; border: none; background: transparent;")
            
            val_lbl = QLabel(val)
            val_lbl.setStyleSheet("color: #1E2B4B; font-size: 22px; font-weight: 900; border: none; background: transparent;")

            badge_row = QHBoxLayout()
            b_lbl = QLabel(sub)
            b_lbl.setObjectName(badge_cls)
            badge_row.addWidget(b_lbl)
            badge_row.addStretch()

            c_lay.addWidget(t_lbl)
            c_lay.addWidget(val_lbl)
            c_lay.addLayout(badge_row)

            r, c = divmod(i, 4)
            self.metrics_grid.addWidget(card, r, c)

    def _render_mid_panels(self, data: dict):
        """Render Weekly Recording Activity and Action Item Overview."""
        while self.mid_row.count():
            item = self.mid_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Weekly Recording Activity Card
        act_card = QFrame()
        act_card.setObjectName("cardFrame")
        a_lay = QVBoxLayout(act_card)
        a_lay.setContentsMargins(18, 16, 18, 16)
        a_lay.setSpacing(10)

        act_hdr = QHBoxLayout()
        act_title = QLabel("Weekly Recording Activity")
        act_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B; border: none; background: transparent;")
        most_active = data.get("most_active_day", "None")
        badge_act = QLabel(f"Peak: {most_active}")
        badge_act.setObjectName("badgePurple")
        act_hdr.addWidget(act_title)
        act_hdr.addWidget(badge_act)
        act_hdr.addStretch()
        a_lay.addLayout(act_hdr)

        days = data.get("weekly_activity", [])
        for day_name, minutes, max_scale in days:
            d_row = QHBoxLayout()
            lbl_d = QLabel(day_name)
            lbl_d.setFixedWidth(35)
            lbl_d.setStyleSheet("color: #475569; font-weight: 600; font-size: 11px; border: none; background: transparent;")

            bar = QProgressBar()
            bar.setRange(0, max_scale if max_scale > 0 else 30)
            bar.setValue(minutes)
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            bar.setStyleSheet("QProgressBar { background: #F1F5F9; border: none; border-radius: 5px; } QProgressBar::chunk { background: #6D59A7; border-radius: 5px; }")

            lbl_val = QLabel(f"{minutes}m")
            lbl_val.setFixedWidth(40)
            lbl_val.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600; border: none; background: transparent;")

            d_row.addWidget(lbl_d)
            d_row.addWidget(bar, stretch=1)
            d_row.addWidget(lbl_val)
            a_lay.addLayout(d_row)

        self.mid_row.addWidget(act_card, stretch=1)

        # 2. Action Item Overview Card
        task_card = QFrame()
        task_card.setObjectName("cardFrame")
        t_lay = QVBoxLayout(task_card)
        t_lay.setContentsMargins(18, 16, 18, 16)
        t_lay.setSpacing(10)

        t_title = QLabel("Action Item & Productivity Status")
        t_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B; border: none; background: transparent;")
        t_lay.addWidget(t_title)

        statuses = [
            ("Completed", data.get("completed_tasks", 0), "#10B981", "#ECFDF5"),
            ("In Progress", data.get("in_progress_tasks", 0), "#2563EB", "#EFF6FF"),
            ("Blocked", data.get("blocked_tasks", 0), "#EF4444", "#FEF2F2"),
            ("Overdue", data.get("overdue_tasks", 0), "#DC2626", "#FEF2F2"),
            ("Total Tasks", data.get("total_tasks", 0), "#1E2B4B", "#F8FAFC"),
        ]

        total = max(1, data.get("total_tasks", 0))
        for s_name, s_count, color, bg in statuses:
            s_row = QHBoxLayout()
            s_lbl = QLabel(s_name)
            s_lbl.setFixedWidth(100)
            s_lbl.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 12px; border: none; background: transparent;")

            s_bar = QProgressBar()
            s_bar.setRange(0, total)
            s_bar.setValue(s_count)
            s_bar.setTextVisible(False)
            s_bar.setFixedHeight(8)
            s_bar.setStyleSheet(f"QProgressBar {{ background: #F1F5F9; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}")

            c_lbl = QLabel(f"{s_count}")
            c_lbl.setFixedWidth(30)
            c_lbl.setStyleSheet("color: #1E2B4B; font-weight: 800; font-size: 12px; border: none; background: transparent;")

            s_row.addWidget(s_lbl)
            s_row.addWidget(s_bar, stretch=1)
            s_row.addWidget(c_lbl)
            t_lay.addLayout(s_row)

        self.mid_row.addWidget(task_card, stretch=1)

    def _render_insights_panels(self, data: dict):
        """Render Speaker Insights & Conversation Themes."""
        while self.insights_row.count():
            item = self.insights_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Speaker Insights Panel
        spk_card = QFrame()
        spk_card.setObjectName("cardFrame")
        s_lay = QVBoxLayout(spk_card)
        s_lay.setContentsMargins(18, 16, 18, 16)
        s_lay.setSpacing(10)

        st_title = QLabel("Speaker Activity Distribution")
        st_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B; border: none; background: transparent;")
        s_lay.addWidget(st_title)

        spk_dist = data.get("speaker_distribution", [])
        if not spk_dist:
            s_lay.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No speaker diarization data available yet.</span>"))
        else:
            colors = ["#6D59A7", "#10B981", "#2563EB", "#D97706", "#EC4899"]
            for idx, (spk, pct, words) in enumerate(spk_dist):
                c = colors[idx % len(colors)]
                row = QHBoxLayout()
                name_lbl = QLabel(spk)
                name_lbl.setFixedWidth(80)
                name_lbl.setStyleSheet("color: #1E2B4B; font-weight: 600; font-size: 12px; border: none; background: transparent;")

                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(int(pct))
                bar.setTextVisible(False)
                bar.setFixedHeight(8)
                bar.setStyleSheet(f"QProgressBar {{ background: #F1F5F9; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background: {c}; border-radius: 4px; }}")

                pct_lbl = QLabel(f"{pct}% ({words:,} words)")
                pct_lbl.setFixedWidth(110)
                pct_lbl.setStyleSheet(f"color: {c}; font-weight: 700; font-size: 11px; border: none; background: transparent;")

                row.addWidget(name_lbl)
                row.addWidget(bar, stretch=1)
                row.addWidget(pct_lbl)
                s_lay.addLayout(row)

        self.insights_row.addWidget(spk_card, stretch=1)

        # 2. Conversation Themes Card
        theme_card = QFrame()
        theme_card.setObjectName("cardFrame")
        t_lay = QVBoxLayout(theme_card)
        t_lay.setContentsMargins(18, 16, 18, 16)
        t_lay.setSpacing(10)

        tt_title = QLabel("Conversation Themes & Topics")
        tt_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B; border: none; background: transparent;")
        t_lay.addWidget(tt_title)

        themes = data.get("conversation_themes", [])
        if not themes:
            t_lay.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>Topics and categories will appear as more notes are indexed.</span>"))
        else:
            for topic, count in themes[:6]:
                r = QHBoxLayout()
                t_lbl = QLabel(f"• #{topic}")
                t_lbl.setStyleSheet("color: #1E2B4B; font-weight: 600; font-size: 12px; border: none; background: transparent;")
                cnt_lbl = QLabel(f"{count} {'note' if count == 1 else 'notes'}")
                cnt_lbl.setStyleSheet("color: #6D59A7; font-weight: 700; font-size: 11px; background: #F5F3FF; border: none; padding: 2px 8px; border-radius: 4px;")
                r.addWidget(t_lbl)
                r.addStretch()
                r.addWidget(cnt_lbl)
                t_lay.addLayout(r)

        self.insights_row.addWidget(theme_card, stretch=1)

    def _render_bottom_panels(self, data: dict):
        """Render Decisions Captured and Open Questions."""
        while self.bottom_row.count():
            item = self.bottom_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Decisions Captured Panel
        dec_card = QFrame()
        dec_card.setObjectName("cardFrame")
        d_lay = QVBoxLayout(dec_card)
        d_lay.setContentsMargins(18, 16, 18, 16)
        d_lay.setSpacing(10)

        d_title = QLabel("Decisions Captured Across Meetings")
        d_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B; border: none; background: transparent;")
        d_lay.addWidget(d_title)

        decs = data.get("decisions_captured", [])
        if not decs:
            d_lay.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No decisions captured yet. Decisions identified in conversations will appear here.</span>"))
        else:
            for d in decs[:5]:
                df = QFrame()
                df.setStyleSheet("QFrame { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; } QLabel { border: none; background: transparent; }")
                dl = QHBoxLayout(df)
                dl.setContentsMargins(10, 6, 10, 6)
                check = QLabel("✓")
                check.setStyleSheet("color: #10B981; font-weight: 800; border: none; background: transparent;")
                dt = QLabel(d.get("decision", ""))
                dt.setWordWrap(True)
                dt.setStyleSheet("color: #166534; font-size: 12px; font-weight: 600; border: none; background: transparent;")
                dl.addWidget(check)
                dl.addWidget(dt, stretch=1)
                d_lay.addWidget(df)

        self.bottom_row.addWidget(dec_card, stretch=1)

        # 2. Open Questions Panel
        q_card = QFrame()
        q_card.setObjectName("cardFrame")
        q_lay = QVBoxLayout(q_card)
        q_lay.setContentsMargins(18, 16, 18, 16)
        q_lay.setSpacing(10)

        q_title = QLabel("Open Questions & Unresolved Items")
        q_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B; border: none; background: transparent;")
        q_lay.addWidget(q_title)

        qs = data.get("open_questions", [])
        if not qs:
            q_lay.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No open questions detected. Unresolved questions will appear here for follow-up.</span>"))
        else:
            for q in qs[:5]:
                qf = QFrame()
                qf.setStyleSheet("QFrame { background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; } QLabel { border: none; background: transparent; }")
                ql = QHBoxLayout(qf)
                ql.setContentsMargins(10, 6, 10, 6)
                qmark = QLabel("❓")
                qmark.setStyleSheet("border: none; background: transparent;")
                qt = QLabel(q.get("question", ""))
                qt.setWordWrap(True)
                qt.setStyleSheet("color: #1E40AF; font-size: 12px; font-weight: 600; border: none; background: transparent;")
                ql.addWidget(qmark)
                ql.addWidget(qt, stretch=1)
                q_lay.addWidget(qf)

        self.bottom_row.addWidget(q_card, stretch=1)
