from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QScrollArea, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt

class SummaryTaskWidget(QWidget):
    """AI Summarization & Task Board UI Component - Retro Cream Theme matching assets/ai summary.png."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = [
            {"desc": "Implement QThread worker for faster-whisper background STT processing", "priority": "HIGH", "assignee": "Lead Eng", "done": True},
            {"desc": "Configure local Ollama structured JSON prompt schema for task extraction", "priority": "HIGH", "assignee": "AI Arch", "done": False},
            {"desc": "Setup ChromaDB collection for transcript vector embeddings and semantic search", "priority": "MEDIUM", "assignee": "Data Eng", "done": False},
            {"desc": "Build PDF  DOCX export generator using ReportLab / python-docx", "priority": "MEDIUM", "assignee": "Dev Team", "done": False},
            {"desc": "Integrate PostgreSQL database schema with SQLAlchemy models", "priority": "LOW", "assignee": "Backend Eng", "done": True},
        ]
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # AI Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("heroCard")
        s_layout = QVBoxLayout(summary_card)
        s_layout.setContentsMargins(20, 20, 20, 20)

        header_row = QHBoxLayout()
        stitle = QLabel("AI Executive Summary")
        stitle.setObjectName("titleLabel")
        
        self.model_badge = QLabel("Gemini • 2.5 Flash")
        self.model_badge.setObjectName("badgePurple")

        header_row.addWidget(stitle)
        header_row.addWidget(self.model_badge)
        header_row.addStretch()

        btn_regen = QPushButton("Re-generate")
        btn_regen.setStyleSheet("background-color: #FFFFFF; font-size: 12px; border: 1px solid #E2DDD3; font-weight: 700; color: #1E2B4B;")
        btn_regen.clicked.connect(self.reanalyze)
        header_row.addWidget(btn_regen)

        s_layout.addLayout(header_row)
        s_layout.addSpacing(8)

        # Overview Content
        self.summary_text_lbl = QLabel()
        self.summary_text_lbl.setWordWrap(True)
        self.summary_text_lbl.setStyleSheet("color: #5C6479; font-size: 13px; line-height: 1.6;")
        self.load_sample_summary()
        s_layout.addWidget(self.summary_text_lbl)

        main_layout.addWidget(summary_card)

        # Task Extraction Board Section
        task_card = QFrame()
        task_card.setObjectName("cardFrame")
        t_layout = QVBoxLayout(task_card)
        t_layout.setContentsMargins(20, 20, 20, 20)

        t_header = QHBoxLayout()
        t_title = QLabel("Extracted Action Items & Tasks")
        t_title.setObjectName("titleLabel")

        self.t_count = QLabel("2 / 5 Completed")
        self.t_count.setObjectName("badgeActive")

        t_header.addWidget(t_title)
        t_header.addWidget(self.t_count)
        t_header.addStretch()

        btn_add = QPushButton("+ Add Action Item")
        btn_add.setObjectName("primaryBtn")
        btn_add.clicked.connect(self.add_task_dialog)
        t_header.addWidget(btn_add)

        t_layout.addLayout(t_header)
        t_layout.addSpacing(12)

        # Task List Container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(10)

        self.render_tasks()

        scroll.setWidget(self.tasks_widget)
        t_layout.addWidget(scroll)

        main_layout.addWidget(task_card)

    def render_tasks(self):
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        done_count = sum(1 for t in self.tasks if t["done"])
        self.t_count.setText(f"{done_count} / {len(self.tasks)} Completed")

        for idx, task in enumerate(self.tasks):
            t_row = QFrame()
            t_row.setObjectName("glassFrame")
            row_lay = QHBoxLayout(t_row)
            row_lay.setContentsMargins(14, 12, 14, 12)
            row_lay.setSpacing(12)

            chk = QCheckBox()
            chk.setChecked(task["done"])
            chk.stateChanged.connect(lambda state, i=idx: self.toggle_task_done(i, state))
            row_lay.addWidget(chk)

            desc_lbl = QLabel(task["desc"])
            if task["done"]:
                desc_lbl.setStyleSheet("color: #5C6479; text-decoration: line-through;")
            else:
                desc_lbl.setStyleSheet("color: #1E2B4B; font-weight: 600;")
            row_lay.addWidget(desc_lbl, stretch=1)

            # Priority Badge (Styled as outline boxes per assets/ai summary.png)
            p_badge = QLabel(task["priority"])
            if task["priority"] == "HIGH":
                p_badge.setStyleSheet("color: #E05A77; border: 1px solid #F5B0C0; background: #FDF2F4; padding: 4px 10px; font-weight: 700; font-size: 11px;")
            elif task["priority"] == "MEDIUM":
                p_badge.setStyleSheet("color: #D97706; border: 1px solid #FCD34D; background: #FEF6E6; padding: 4px 10px; font-weight: 700; font-size: 11px;")
            else:
                p_badge.setStyleSheet("color: #4A3980; border: 1px solid #D8D0EB; background: #F2EFF9; padding: 4px 10px; font-weight: 700; font-size: 11px;")

            row_lay.addWidget(p_badge)

            # Assignee chip
            assignee_lbl = QLabel(task["assignee"])
            assignee_lbl.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 600; min-width: 60px;")
            row_lay.addWidget(assignee_lbl)

            self.tasks_layout.addWidget(t_row)

    def toggle_task_done(self, idx: int, state: int):
        self.tasks[idx]["done"] = bool(state)
        self.render_tasks()

    def add_task_dialog(self):
        text, ok = QInputDialog.getText(self, "Add Action Item", "Enter task description:")
        if ok and text.strip():
            self.tasks.append({
                "desc": text.strip(),
                "priority": "HIGH",
                "assignee": "Lead Eng",
                "done": False
            })
            self.render_tasks()

    def load_sample_summary(self):
        self.summary_text_lbl.setText(
            "<b>Overview:</b> The team aligned on building a privacy-first, local-only desktop application using PySide6. "
            "All speech recognition (Whisper) and LLM inference (Ollama) will run locally on client machines.<br><br>"
            "<b>Key Decisions:</b><br>"
            "• Use <b>PySide6 QThreads</b> to prevent UI freeze during audio transcription.<br>"
            "• Utilize <b>ChromaDB</b> for indexing note chunk embeddings for instant semantic search.<br>"
            "• Provide seamless <b>PDF, DOCX, and TXT</b> export options directly from the home dashboard."
        )

    def set_ai_data(self, summary: str, key_points: list = None, tasks: list = None, model_name: str = "Gemini 2.5 Flash"):
        """Dynamically load AI summary and extracted tasks for a note."""
        self.model_badge.setText(f"AI • {model_name}")
        
        kp_html = ""
        if key_points:
            kp_items = "".join([f"<li>{kp}</li>" for kp in key_points])
            kp_html = f"<br><br><b>Key Takeaways:</b><ul>{kp_items}</ul>"

        self.summary_text_lbl.setText(
            f"<b>Executive Summary:</b> {summary}{kp_html}"
        )

        if tasks is not None:
            self.tasks = []
            for t in tasks:
                if isinstance(t, dict):
                    self.tasks.append({
                        "desc": t.get("desc") or t.get("description") or t.get("title") or "Task item",
                        "priority": (t.get("priority") or "MEDIUM").upper(),
                        "assignee": t.get("assignee") or t.get("owner") or "Unassigned",
                        "done": t.get("done") or (t.get("status", "").lower() == "completed"),
                    })
                elif hasattr(t, "title"):
                    self.tasks.append({
                        "desc": getattr(t, "title", "Task item"),
                        "priority": getattr(t, "priority", "MEDIUM").upper(),
                        "assignee": getattr(t, "assignee", "Unassigned"),
                        "done": getattr(t, "status", "").lower() == "completed",
                    })
            self.render_tasks()

    def reanalyze(self):
        QMessageBox.information(self, "AI Summary", "Summary and action items re-generated via Gemini AI.")
