"""
VoiceNote AI Meeting Intelligence & Productivity Workspace Component.
Transforms voice notes into actionable structured workspaces:
- Meeting Health & Productivity Overview
- Executive Summary & Key Takeaways
- Key Decisions
- Interactive Action Items (checkbox, priority, owner, status dropdown, overdue indicator, DB persistence)
- Deadlines & Commitments
- Important Numbers (metric cards)
- Risks & Blockers
- Open Questions & Follow-ups
- Your Meeting Plan (Today, Upcoming, Decisions, Follow-ups, Blocked)
- Selective Re-generation (Summary, Actions, Insights)
"""

import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QScrollArea, QInputDialog, QMessageBox,
    QComboBox, QGridLayout, QMenu, QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCursor

from voicenote.db.database import get_db
from voicenote.db.models import Task as DBTask
from voicenote.core.ai_engine import AIEngine


class SummaryTaskWidget(QWidget):
    """AI Meeting Intelligence & Productivity Workspace UI Component."""
    task_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.current_note_id: Optional[int] = None
        self.current_transcript_text: str = ""
        
        # Stored intelligence state
        self.tasks: List[Dict[str, Any]] = []
        self.decisions: List[str] = []
        self.deadlines: List[Dict[str, str]] = []
        self.numbers: List[Dict[str, str]] = []
        self.risks: List[str] = []
        self.questions: List[str] = []
        self.follow_ups: List[str] = []
        self.health_data: Dict[str, Any] = {
            "duration": "00:00",
            "speakers": 1,
            "words": 0,
            "actions": 0,
            "decisions": 0,
            "questions": 0
        }

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(14)

        # Scrollable container for the workspace
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        self.c_layout = QVBoxLayout(container)
        self.c_layout.setContentsMargins(0, 0, 0, 16)
        self.c_layout.setSpacing(16)

        # 1. Meeting Health & Productivity Insights Strip
        self.health_card = QFrame()
        self.health_card.setObjectName("heroCard")
        h_layout = QVBoxLayout(self.health_card)
        h_layout.setContentsMargins(18, 14, 18, 14)
        h_layout.setSpacing(10)

        h_title_row = QHBoxLayout()
        h_title = QLabel("Meeting Intelligence & Health Overview")
        h_title.setObjectName("titleLabel")
        
        self.source_tag = QLabel("AI Meeting Intelligence")
        self.source_tag.setObjectName("badgePurple")

        h_title_row.addWidget(h_title)
        h_title_row.addWidget(self.source_tag)
        h_title_row.addStretch()

        # Selective Re-generate Button with Dropdown Menu
        self.btn_regen = QPushButton("Re-generate ▼")
        self.btn_regen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_regen.setStyleSheet("background-color: #FFFFFF; font-size: 12px; border: 1px solid #CBD5E1; font-weight: 700; color: #1E2B4B; padding: 5px 12px; border-radius: 4px;")
        
        regen_menu = QMenu(self)
        act_all = QAction("Full Analysis (All Sections)", self)
        act_all.triggered.connect(lambda: self.trigger_regenerate("all"))
        act_sum = QAction("Executive Summary Only", self)
        act_sum.triggered.connect(lambda: self.trigger_regenerate("summary"))
        act_tasks = QAction("Action Items & Tasks Only", self)
        act_tasks.triggered.connect(lambda: self.trigger_regenerate("tasks"))
        act_ins = QAction("Decisions & Insights Only", self)
        act_ins.triggered.connect(lambda: self.trigger_regenerate("insights"))
        
        regen_menu.addAction(act_all)
        regen_menu.addAction(act_sum)
        regen_menu.addAction(act_tasks)
        regen_menu.addAction(act_ins)
        self.btn_regen.setMenu(regen_menu)

        h_title_row.addWidget(self.btn_regen)
        h_layout.addLayout(h_title_row)

        # Compact Metric Strip
        self.metrics_row = QHBoxLayout()
        self.metrics_row.setSpacing(12)
        h_layout.addLayout(self.metrics_row)
        self._render_health_metrics()

        self.c_layout.addWidget(self.health_card)

        # 2. Tabbed Workspace: [ Overview & Actions ] [ Meeting Plan ] [ Numbers & Risks ]
        self.tabs = QTabWidget()
        self.tabs.setObjectName("workspaceTabs")
        
        # Tab 1: Overview, Decisions, and Action Items
        self.tab_actions = QWidget()
        tab1_layout = QVBoxLayout(self.tab_actions)
        tab1_layout.setContentsMargins(0, 12, 0, 0)
        tab1_layout.setSpacing(14)

        # Executive Summary Section
        sum_card = QFrame()
        sum_card.setObjectName("cardFrame")
        s_layout = QVBoxLayout(sum_card)
        s_layout.setContentsMargins(18, 16, 18, 16)
        s_layout.setSpacing(8)

        st_lbl = QLabel("Executive Summary")
        st_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")
        s_layout.addWidget(st_lbl)

        self.summary_text_lbl = QLabel()
        self.summary_text_lbl.setWordWrap(True)
        self.summary_text_lbl.setStyleSheet("color: #4A5568; font-size: 13px; line-height: 1.6;")
        s_layout.addWidget(self.summary_text_lbl)
        tab1_layout.addWidget(sum_card)

        # Key Decisions Section
        self.decisions_card = QFrame()
        self.decisions_card.setObjectName("cardFrame")
        d_layout = QVBoxLayout(self.decisions_card)
        d_layout.setContentsMargins(18, 16, 18, 16)
        d_layout.setSpacing(8)

        dt_row = QHBoxLayout()
        dt_lbl = QLabel("Key Decisions Agreed Upon")
        dt_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")
        self.dec_count_badge = QLabel("0 Decisions")
        self.dec_count_badge.setObjectName("badgeActive")
        dt_row.addWidget(dt_lbl)
        dt_row.addWidget(self.dec_count_badge)
        dt_row.addStretch()
        d_layout.addLayout(dt_row)

        self.decisions_box = QVBoxLayout()
        self.decisions_box.setSpacing(6)
        d_layout.addLayout(self.decisions_box)
        tab1_layout.addWidget(self.decisions_card)

        # Action Items Section
        task_card = QFrame()
        task_card.setObjectName("cardFrame")
        t_layout = QVBoxLayout(task_card)
        t_layout.setContentsMargins(18, 16, 18, 16)
        t_layout.setSpacing(10)

        t_header = QHBoxLayout()
        t_title = QLabel("Action Items & Extracted Tasks")
        t_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")

        self.t_count = QLabel("0 / 0 Completed")
        self.t_count.setObjectName("badgeActive")

        t_header.addWidget(t_title)
        t_header.addWidget(self.t_count)
        t_header.addStretch()

        btn_add = QPushButton("+ Add Action Item")
        btn_add.setObjectName("primaryBtn")
        btn_add.clicked.connect(self.add_task_dialog)
        t_header.addWidget(btn_add)

        t_layout.addLayout(t_header)

        # Tasks Container
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(8)
        t_layout.addWidget(self.tasks_widget)

        tab1_layout.addWidget(task_card)
        self.tabs.addTab(self.tab_actions, "Overview & Action Items")

        # Tab 2: Your Meeting Plan (Productivity Planner)
        self.tab_plan = QWidget()
        self._init_plan_tab()
        self.tabs.addTab(self.tab_plan, "Your Meeting Plan")

        # Tab 3: Insights, Metrics & Risks
        self.tab_insights = QWidget()
        self._init_insights_tab()
        self.tabs.addTab(self.tab_insights, "Important Numbers & Risks")

        self.c_layout.addWidget(self.tabs)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self.load_empty_state()

    def _render_health_metrics(self):
        """Render the compact meeting quality strip."""
        while self.metrics_row.count():
            item = self.metrics_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = [
            ("Duration", str(self.health_data.get("duration", "00:00")), "#1E2B4B"),
            ("Speakers", f"{self.health_data.get('speakers', 1)} Active", "#6D59A7"),
            ("Words", f"{self.health_data.get('words', 0):,}", "#1E2B4B"),
            ("Actions", f"{self.health_data.get('actions', 0)} Items", "#10B981"),
            ("Decisions", f"{self.health_data.get('decisions', 0)} Captured", "#2563EB"),
            ("Questions", f"{self.health_data.get('questions', 0)} Open", "#D97706"),
        ]

        for label, val, color in items:
            box = QFrame()
            box.setStyleSheet("QFrame { background: #FFFFFF; border: 1px solid #E5E0D6; border-radius: 6px; padding: 6px 10px; } QLabel { border: none; background: transparent; }")
            b_lay = QVBoxLayout(box)
            b_lay.setContentsMargins(4, 2, 4, 2)
            b_lay.setSpacing(2)
            
            l_lbl = QLabel(label.upper())
            l_lbl.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748B; border: none; background: transparent;")
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {color}; border: none; background: transparent;")
            b_lay.addWidget(l_lbl)
            b_lay.addWidget(v_lbl)
            self.metrics_row.addWidget(box)

    def _init_plan_tab(self):
        """Build the planner-style 'Your Meeting Plan' view (Today, Upcoming, Decisions, Follow-Ups, Blocked)."""
        lay = QVBoxLayout(self.tab_plan)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.setSpacing(12)

        # Plan columns container
        plan_card = QFrame()
        plan_card.setObjectName("cardFrame")
        p_lay = QVBoxLayout(plan_card)
        p_lay.setContentsMargins(18, 16, 18, 16)
        p_lay.setSpacing(12)

        p_title = QLabel("<b>Your Meeting Plan</b> — Structured outcome roadmap derived from discussion")
        p_title.setStyleSheet("font-size: 14px; color: #1E2B4B;")
        p_lay.addWidget(p_title)

        self.plan_content = QVBoxLayout()
        self.plan_content.setSpacing(10)
        p_lay.addLayout(self.plan_content)

        lay.addWidget(plan_card)

    def _init_insights_tab(self):
        """Build the Important Numbers, Risks & Blockers, and Open Questions tab."""
        lay = QVBoxLayout(self.tab_insights)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.setSpacing(14)

        # Deadlines & Commitments
        deadlines_card = QFrame()
        deadlines_card.setObjectName("cardFrame")
        dl_lay = QVBoxLayout(deadlines_card)
        dl_lay.setContentsMargins(18, 16, 18, 16)
        dl_title = QLabel("📅 Deadlines & Commitments")
        dl_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")
        dl_lay.addWidget(dl_title)
        self.deadlines_box = QVBoxLayout()
        self.deadlines_box.setSpacing(6)
        dl_lay.addLayout(self.deadlines_box)
        lay.addWidget(deadlines_card)

        # Important Numbers Grid
        num_card = QFrame()
        num_card.setObjectName("cardFrame")
        n_lay = QVBoxLayout(num_card)
        n_lay.setContentsMargins(18, 16, 18, 16)
        n_title = QLabel("📊 Important Numbers & Metrics")
        n_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")
        n_lay.addWidget(n_title)
        self.numbers_grid = QGridLayout()
        self.numbers_grid.setSpacing(10)
        n_lay.addLayout(self.numbers_grid)
        lay.addWidget(num_card)

        # Risks, Blockers & Open Questions Split
        bot_row = QHBoxLayout()
        bot_row.setSpacing(12)

        # Risks & Blockers
        risks_card = QFrame()
        risks_card.setObjectName("cardFrame")
        r_lay = QVBoxLayout(risks_card)
        r_lay.setContentsMargins(18, 16, 18, 16)
        r_title = QLabel("⚠ Risks & Blockers")
        r_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #D97706;")
        r_lay.addWidget(r_title)
        self.risks_box = QVBoxLayout()
        self.risks_box.setSpacing(6)
        r_lay.addLayout(self.risks_box)
        bot_row.addWidget(risks_card, stretch=1)

        # Open Questions
        q_card = QFrame()
        q_card.setObjectName("cardFrame")
        q_lay = QVBoxLayout(q_card)
        q_lay.setContentsMargins(18, 16, 18, 16)
        q_title = QLabel("❓ Open Questions & Follow-ups")
        q_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #2563EB;")
        q_lay.addWidget(q_title)
        self.questions_box = QVBoxLayout()
        self.questions_box.setSpacing(6)
        q_lay.addLayout(self.questions_box)
        bot_row.addWidget(q_card, stretch=1)

        lay.addLayout(bot_row)

    def load_empty_state(self):
        """Render informative empty state when no note is currently selected."""
        self.summary_text_lbl.setText(
            "<span style='color: #64748B; font-style: italic;'>No conversation selected. Record audio or select a note from the Recent Notes feed to view AI Meeting Intelligence, extracted tasks, and productivity insights.</span>"
        )
        self.tasks = []
        self.decisions = []
        self.deadlines = []
        self.numbers = []
        self.risks = []
        self.questions = []
        self.follow_ups = []
        self.health_data = {"duration": "00:00", "speakers": 1, "words": 0, "actions": 0, "decisions": 0, "questions": 0}
        self._render_health_metrics()
        self.render_all_sections()

    def set_note_context(self, note_id: int, title: str, duration: str, transcript_text: str):
        """Load data from PostgreSQL for a specific note."""
        self.current_note_id = note_id
        self.current_transcript_text = transcript_text
        
        # Calculate words
        word_count = len(transcript_text.split()) if transcript_text else 0
        
        # Calculate distinct speakers
        speaker_set = set()
        for line in transcript_text.split("\n"):
            if ":" in line and "speaker" in line.lower()[:15]:
                speaker_set.add(line.split(":")[0].strip())
        num_speakers = max(1, len(speaker_set))

        summary_data = self.db.get_ai_summary(note_id) if self.db else None
        db_tasks = self.db.get_tasks_by_note(note_id) if self.db else []

        if summary_data:
            summary = summary_data.get("summary", "")
            key_points = summary_data.get("key_points", [])
            self.decisions = summary_data.get("decisions", [])
            self.deadlines = summary_data.get("deadlines", [])
            self.numbers = summary_data.get("important_numbers", [])
            self.risks = summary_data.get("risks_blockers", [])
            self.questions = summary_data.get("open_questions", [])
            self.follow_ups = summary_data.get("follow_ups", [])
        else:
            summary = transcript_text[:250] + ("..." if len(transcript_text) > 250 else "")
            key_points = []
            self.decisions = []
            self.deadlines = []
            self.numbers = []
            self.risks = []
            self.questions = []
            self.follow_ups = []

        # Load tasks
        self.tasks = []
        for t in db_tasks:
            self.tasks.append({
                "id": t.get("id"),
                "desc": t.get("title", ""),
                "priority": (t.get("priority") or "Medium").capitalize(),
                "assignee": t.get("assignee") or "Unassigned",
                "due_date": t.get("due_date") or "TBD",
                "status": t.get("status") or "Not Started",
                "notes": t.get("notes") or "",
                "done": (t.get("status") or "").lower() == "completed"
            })

        # Update Health Data
        self.health_data = {
            "duration": duration or "00:00",
            "speakers": num_speakers,
            "words": word_count,
            "actions": len(self.tasks),
            "decisions": len(self.decisions),
            "questions": len(self.questions)
        }
        self._render_health_metrics()

        # Update Executive Summary HTML
        kp_html = ""
        if key_points:
            kp_items = "".join([f"<li>{kp}</li>" for kp in key_points])
            kp_html = f"<br><b>Key Takeaways:</b><ul>{kp_items}</ul>"
        self.summary_text_lbl.setText(f"<b>Executive Summary:</b> {summary}{kp_html}")

        self.render_all_sections()

    def render_all_sections(self):
        """Render decisions, tasks, planner, deadlines, numbers, risks, and questions."""
        self.render_decisions()
        self.render_tasks()
        self.render_plan()
        self.render_insights()

    def render_decisions(self):
        """Render Key Decisions list."""
        while self.decisions_box.count():
            item = self.decisions_box.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        self.dec_count_badge.setText(f"{len(self.decisions)} Decisions")
        
        if not self.decisions:
            lbl = QLabel("<span style='color: #94A3B8; font-style: italic;'>No explicit decisions captured in this conversation.</span>")
            self.decisions_box.addWidget(lbl)
            return

        for dec in self.decisions:
            row = QFrame()
            row.setStyleSheet("QFrame { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 6px 12px; } QLabel { border: none; background: transparent; }")
            r_lay = QHBoxLayout(row)
            r_lay.setContentsMargins(6, 4, 6, 4)
            r_lay.setSpacing(8)

            check_icon = QLabel("✓")
            check_icon.setStyleSheet("color: #10B981; font-weight: 900; font-size: 14px; border: none; background: transparent;")
            dec_text = QLabel(dec)
            dec_text.setWordWrap(True)
            dec_text.setStyleSheet("color: #166534; font-weight: 600; font-size: 13px; border: none; background: transparent;")

            r_lay.addWidget(check_icon)
            r_lay.addWidget(dec_text, stretch=1)
            self.decisions_box.addWidget(row)

    def render_tasks(self):
        """Render interactive action items with checkbox, status, priority, and overdue badge."""
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        done_count = sum(1 for t in self.tasks if t.get("done"))
        self.t_count.setText(f"{done_count} / {len(self.tasks)} Completed")

        if not self.tasks:
            lbl = QLabel("<span style='color: #94A3B8; font-style: italic;'>No action items found. Click '+ Add Action Item' to create one.</span>")
            self.tasks_layout.addWidget(lbl)
            return

        today_str = date.today().isoformat()

        for idx, task in enumerate(self.tasks):
            t_row = QFrame()
            t_row.setObjectName("glassFrame")
            t_row.setStyleSheet("QFrame#glassFrame { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; } QLabel { border: none; background: transparent; }")
            row_lay = QHBoxLayout(t_row)
            row_lay.setContentsMargins(12, 10, 12, 10)
            row_lay.setSpacing(10)

            # Checkbox
            chk = QCheckBox()
            chk.setChecked(bool(task.get("done")))
            chk.stateChanged.connect(lambda state, i=idx: self.toggle_task_done(i, state))
            row_lay.addWidget(chk)

            # Title / description
            desc_lbl = QLabel(task.get("desc", ""))
            desc_lbl.setWordWrap(True)
            if task.get("done"):
                desc_lbl.setStyleSheet("color: #94A3B8; text-decoration: line-through; font-size: 13px;")
            else:
                desc_lbl.setStyleSheet("color: #1E2B4B; font-weight: 600; font-size: 13px;")
            row_lay.addWidget(desc_lbl, stretch=1)

            # Assignee
            owner_lbl = QLabel(f"👤 {task.get('assignee', 'Unassigned')}")
            owner_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 600; background: #F1F5F9; padding: 3px 8px; border-radius: 4px; border: none;")
            row_lay.addWidget(owner_lbl)

            # Due Date & Overdue Indicator
            due_text = task.get("due_date", "TBD")
            due_lbl = QLabel(f"📅 {due_text}")
            due_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500; border: none; background: transparent;")
            row_lay.addWidget(due_lbl)

            # Check Overdue status
            is_overdue = False
            if not task.get("done") and due_text and due_text.upper() != "TBD":
                # Try simple date match (e.g. 2026-09-20 or Sep 20)
                try:
                    due_d = datetime.strptime(due_text[:10], "%Y-%m-%d").date()
                    if due_d < date.today():
                        is_overdue = True
                except Exception:
                    pass

            if is_overdue:
                overdue_lbl = QLabel("🔴 OVERDUE")
                overdue_lbl.setStyleSheet("color: #DC2626; font-weight: 800; font-size: 10px; background: #FEF2F2; padding: 2px 6px; border-radius: 4px; border: none;")
                row_lay.addWidget(overdue_lbl)

            # Priority Selector Combobox
            prio_combo = QComboBox()
            prio_combo.addItems(["Urgent", "High", "Medium", "Low"])
            cur_prio = (task.get("priority") or "Medium").capitalize()
            prio_idx = prio_combo.findText(cur_prio)
            if prio_idx >= 0:
                prio_combo.setCurrentIndex(prio_idx)
            prio_combo.setStyleSheet("font-size: 11px; font-weight: 700; padding: 2px 6px;")
            prio_combo.currentIndexChanged.connect(lambda p_idx, i=idx, cb=prio_combo: self.on_task_priority_changed(i, cb.currentText()))
            row_lay.addWidget(prio_combo)

            # Status Combobox
            status_combo = QComboBox()
            status_combo.addItems(["Not Started", "In Progress", "Blocked", "Completed"])
            cur_status = task.get("status") or "Not Started"
            st_idx = status_combo.findText(cur_status)
            if st_idx >= 0:
                status_combo.setCurrentIndex(st_idx)
            status_combo.setStyleSheet("font-size: 11px; font-weight: 600; padding: 2px 6px;")
            status_combo.currentIndexChanged.connect(lambda s_idx, i=idx, cb=status_combo: self.on_task_status_changed(i, cb.currentText()))
            row_lay.addWidget(status_combo)

            # Delete button
            btn_del = QPushButton("✕")
            btn_del.setToolTip("Delete task")
            btn_del.setFixedSize(22, 22)
            btn_del.setStyleSheet("color: #94A3B8; font-weight: 800; border: none; background: transparent;")
            btn_del.clicked.connect(lambda _, i=idx: self.delete_task(i))
            row_lay.addWidget(btn_del)

            self.tasks_layout.addWidget(t_row)

    def toggle_task_done(self, idx: int, state: int):
        """Toggle task completion and update database."""
        is_done = bool(state)
        self.tasks[idx]["done"] = is_done
        self.tasks[idx]["status"] = "Completed" if is_done else "In Progress"
        
        task_id = self.tasks[idx].get("id")
        if task_id and self.db:
            self.db.update_task(task_id, status=self.tasks[idx]["status"])

        self.render_tasks()
        self.render_plan()
        self.task_updated.emit()

    def on_task_status_changed(self, idx: int, new_status: str):
        self.tasks[idx]["status"] = new_status
        self.tasks[idx]["done"] = (new_status.lower() == "completed")
        
        task_id = self.tasks[idx].get("id")
        if task_id and self.db:
            self.db.update_task(task_id, status=new_status)

        self.render_tasks()
        self.render_plan()
        self.task_updated.emit()

    def on_task_priority_changed(self, idx: int, new_priority: str):
        self.tasks[idx]["priority"] = new_priority
        task_id = self.tasks[idx].get("id")
        if task_id and self.db:
            self.db.update_task(task_id, priority=new_priority)
        self.task_updated.emit()

    def delete_task(self, idx: int):
        task = self.tasks[idx]
        task_id = task.get("id")
        if task_id and self.db:
            self.db.delete_task(task_id)
        self.tasks.pop(idx)
        self.health_data["actions"] = len(self.tasks)
        self._render_health_metrics()
        self.render_tasks()
        self.render_plan()
        self.task_updated.emit()

    def add_task_dialog(self):
        """Prompt to create a new action item and save to database."""
        desc, ok = QInputDialog.getText(self, "Add Action Item", "Task Description:")
        if ok and desc.strip():
            new_task = {
                "desc": desc.strip(),
                "priority": "High",
                "assignee": "Unassigned",
                "due_date": "Today",
                "status": "Not Started",
                "done": False
            }
            if self.current_note_id and self.db:
                t_obj = DBTask(
                    note_id=self.current_note_id,
                    title=desc.strip(),
                    priority="High",
                    assignee="Unassigned",
                    due_date="Today",
                    status="Not Started"
                )
                new_id = self.db.save_task(t_obj)
                new_task["id"] = new_id

            self.tasks.append(new_task)
            self.health_data["actions"] = len(self.tasks)
            self._render_health_metrics()
            self.render_tasks()
            self.render_plan()
            self.task_updated.emit()

    def render_plan(self):
        """Render 'Your Meeting Plan' categorized into Today, Upcoming, Decisions, Follow-Ups, Blocked."""
        while self.plan_content.count():
            item = self.plan_content.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        # Categorize
        today_tasks = [t for t in self.tasks if "today" in (t.get("due_date") or "").lower() and not t.get("done")]
        upcoming_tasks = [t for t in self.tasks if "today" not in (t.get("due_date") or "").lower() and not t.get("done") and t.get("status") != "Blocked"]
        blocked_tasks = [t for t in self.tasks if t.get("status") == "Blocked"]

        sections = [
            ("⚡ TODAY", today_tasks, "#10B981", "Tasks scheduled for immediate execution today"),
            ("📅 UPCOMING", upcoming_tasks, "#2563EB", "Upcoming commitments and deadlines"),
            ("🎯 DECISIONS", [{"desc": d} for d in self.decisions], "#6D59A7", "Key decisions and strategic alignments"),
            ("🔄 FOLLOW-UPS", [{"desc": f} for f in self.follow_ups], "#D97706", "Follow-up items requiring future review"),
            ("🚫 BLOCKED", blocked_tasks, "#EF4444", "Items blocked by dependencies or hurdles"),
        ]

        for title, items, color, desc_text in sections:
            sec_card = QFrame()
            sec_card.setStyleSheet(f"QFrame {{ background: #FFFFFF; border-left: 4px solid {color}; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 12px; }} QLabel {{ border: none; background: transparent; }}")
            s_lay = QVBoxLayout(sec_card)
            s_lay.setContentsMargins(6, 4, 6, 4)
            s_lay.setSpacing(4)

            hdr = QLabel(f"<b>{title}</b> — <span style='color: #64748B; font-size: 11px;'>{desc_text}</span>")
            hdr.setStyleSheet(f"color: {color}; font-size: 12px; border: none; background: transparent;")
            s_lay.addWidget(hdr)

            if not items:
                none_lbl = QLabel("<span style='color: #94A3B8; font-size: 11px; font-style: italic;'>No items in this category.</span>")
                s_lay.addWidget(none_lbl)
            else:
                for it in items:
                    t_lbl = QLabel(f"• {it.get('desc', '')}")
                    t_lbl.setWordWrap(True)
                    t_lbl.setStyleSheet("color: #334155; font-size: 12px; border: none; background: transparent;")
                    s_lay.addWidget(t_lbl)

            self.plan_content.addWidget(sec_card)

    def render_insights(self):
        """Render Deadlines, Numbers, Risks, and Open Questions."""
        # 1. Deadlines
        while self.deadlines_box.count():
            item = self.deadlines_box.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        if not self.deadlines:
            self.deadlines_box.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No explicit calendar deadlines extracted.</span>"))
        else:
            for dl in self.deadlines:
                d_row = QFrame()
                d_row.setStyleSheet("QFrame { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; } QLabel { border: none; background: transparent; }")
                dl_layout = QHBoxLayout(d_row)
                dl_layout.setContentsMargins(4, 2, 4, 2)
                dt_badge = QLabel(dl.get("date", "Date"))
                dt_badge.setStyleSheet("color: #2563EB; font-weight: 700; font-size: 11px; background: #EFF6FF; border: none; padding: 2px 8px; border-radius: 4px;")
                com_lbl = QLabel(dl.get("commitment", ""))
                com_lbl.setWordWrap(True)
                com_lbl.setStyleSheet("color: #1E293B; font-weight: 500; font-size: 12px; border: none; background: transparent;")
                dl_layout.addWidget(dt_badge)
                dl_layout.addWidget(com_lbl, stretch=1)
                self.deadlines_box.addWidget(d_row)

        # 2. Numbers Grid
        while self.numbers_grid.count():
            item = self.numbers_grid.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        if not self.numbers:
            self.numbers_grid.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No numerical metrics detected in dialogue.</span>"), 0, 0)
        else:
            for idx, num in enumerate(self.numbers):
                n_card = QFrame()
                n_card.setStyleSheet("QFrame { background: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 6px; padding: 8px; } QLabel { border: none; background: transparent; }")
                n_lay = QVBoxLayout(n_card)
                n_lay.setContentsMargins(6, 4, 6, 4)
                n_lay.setSpacing(2)

                val_lbl = QLabel(num.get("value", ""))
                val_lbl.setStyleSheet("color: #6D59A7; font-size: 16px; font-weight: 900; border: none; background: transparent;")
                ctx_lbl = QLabel(num.get("context", ""))
                ctx_lbl.setWordWrap(True)
                ctx_lbl.setStyleSheet("color: #6B21A8; font-size: 11px; border: none; background: transparent;")
                n_lay.addWidget(val_lbl)
                n_lay.addWidget(ctx_lbl)

                r, c = divmod(idx, 3)
                self.numbers_grid.addWidget(n_card, r, c)

        # 3. Risks & Blockers
        while self.risks_box.count():
            item = self.risks_box.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        if not self.risks:
            self.risks_box.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No critical risks or blockers flagged.</span>"))
        else:
            for r in self.risks:
                rf = QFrame()
                rf.setStyleSheet("QFrame { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 6px 10px; } QLabel { border: none; background: transparent; }")
                r_lay = QHBoxLayout(rf)
                r_lay.setContentsMargins(4, 2, 4, 2)
                r_lay.addWidget(QLabel("⚠"))
                rl = QLabel(r)
                rl.setWordWrap(True)
                rl.setStyleSheet("color: #92400E; font-size: 12px; font-weight: 500; border: none; background: transparent;")
                r_lay.addWidget(rl, stretch=1)
                self.risks_box.addWidget(rf)

        # 4. Open Questions
        while self.questions_box.count():
            item = self.questions_box.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

        if not self.questions:
            self.questions_box.addWidget(QLabel("<span style='color: #94A3B8; font-style: italic;'>No unresolved questions identified.</span>"))
        else:
            for q in self.questions:
                qf = QFrame()
                qf.setStyleSheet("QFrame { background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 6px 10px; } QLabel { border: none; background: transparent; }")
                q_lay = QHBoxLayout(qf)
                q_lay.setContentsMargins(4, 2, 4, 2)
                q_lay.addWidget(QLabel("❓"))
                ql = QLabel(q)
                ql.setWordWrap(True)
                ql.setStyleSheet("color: #1E40AF; font-size: 12px; font-weight: 500; border: none; background: transparent;")
                q_lay.addWidget(ql, stretch=1)
                self.questions_box.addWidget(qf)

    def trigger_regenerate(self, section: str):
        """Selectively re-generate chosen section via AIEngine."""
        if not self.current_transcript_text:
            QMessageBox.warning(self, "Re-generate", "No active transcript available to re-generate.")
            return

        try:
            ai = AIEngine()
            if section in ("summary", "all"):
                res = ai.regenerate_summary(self.current_transcript_text)
                sum_text = res.get("summary", "")
                kps = res.get("key_points", [])
                kp_html = "".join([f"<li>{k}</li>" for k in kps])
                self.summary_text_lbl.setText(f"<b>Executive Summary:</b> {sum_text}<br><b>Key Takeaways:</b><ul>{kp_html}</ul>")

            if section in ("tasks", "all"):
                new_tasks = ai.regenerate_tasks(self.current_transcript_text)
                for t in new_tasks:
                    task_dict = {
                        "desc": t.get("task", ""),
                        "priority": (t.get("priority") or "Medium").capitalize(),
                        "assignee": t.get("owner") or "Unassigned",
                        "due_date": t.get("due_date") or "TBD",
                        "status": "Not Started",
                        "done": False
                    }
                    if self.current_note_id and self.db:
                        db_t = DBTask(
                            note_id=self.current_note_id,
                            title=task_dict["desc"],
                            priority=task_dict["priority"],
                            assignee=task_dict["assignee"],
                            due_date=task_dict["due_date"],
                            status="Not Started"
                        )
                        task_dict["id"] = self.db.save_task(db_t)
                    self.tasks.append(task_dict)
                self.health_data["actions"] = len(self.tasks)
                self.render_tasks()

            if section in ("insights", "all"):
                ins = ai.regenerate_insights(self.current_transcript_text)
                self.decisions = ins.get("key_decisions", [])
                self.deadlines = ins.get("deadlines", [])
                self.numbers = ins.get("important_numbers", [])
                self.risks = ins.get("risks_blockers", [])
                self.questions = ins.get("open_questions", [])
                self.follow_ups = ins.get("follow_ups", [])
                self.health_data["decisions"] = len(self.decisions)
                self.health_data["questions"] = len(self.questions)
                self.render_decisions()
                self.render_insights()

            self._render_health_metrics()
            self.render_plan()
            QMessageBox.information(self, "AI Intelligence Updated", f"Successfully re-generated {section} from conversation transcript.")
        except Exception as e:
            QMessageBox.warning(self, "Re-generate Failed", f"Could not re-generate {section}: {e}")

    def set_ai_data(self, summary: str, key_points: list = None, tasks: list = None, model_name: str = "AI Summary"):
        """Compatibility method for direct summary and task setting."""
        kp_html = ""
        if key_points:
            kp_items = "".join([f"<li>{kp}</li>" for kp in key_points])
            kp_html = f"<br><b>Key Takeaways:</b><ul>{kp_items}</ul>"
        self.summary_text_lbl.setText(f"<b>Executive Summary:</b> {summary}{kp_html}")

        if tasks is not None:
            self.tasks = []
            for t in tasks:
                if isinstance(t, dict):
                    self.tasks.append({
                        "id": t.get("id"),
                        "desc": t.get("desc") or t.get("description") or t.get("title") or "Task item",
                        "priority": (t.get("priority") or "Medium").capitalize(),
                        "assignee": t.get("assignee") or t.get("owner") or "Unassigned",
                        "due_date": t.get("due_date") or "TBD",
                        "status": t.get("status") or "Not Started",
                        "done": bool(t.get("done") or (str(t.get("status", "")).lower() == "completed")),
                    })
                elif hasattr(t, "title"):
                    self.tasks.append({
                        "id": getattr(t, "id", None),
                        "desc": getattr(t, "title", "Task item"),
                        "priority": getattr(t, "priority", "Medium").capitalize(),
                        "assignee": getattr(t, "assignee", "Unassigned"),
                        "due_date": getattr(t, "due_date", "TBD"),
                        "status": getattr(t, "status", "Not Started"),
                        "done": getattr(t, "status", "").lower() == "completed",
                    })
            self.health_data["actions"] = len(self.tasks)
            self._render_health_metrics()
            self.render_tasks()
            self.render_plan()

