from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QScrollArea, QInputDialog
)
from PySide6.QtCore import Qt

class SummaryTaskWidget(QWidget):
    """AI Summarization & Task Board UI Component - Retro Cream Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = [
            {"desc": "Implement QThread worker for faster-whisper background STT processing", "priority": "HIGH", "assignee": "Lead Eng", "done": True},
            {"desc": "Configure local Ollama structured JSON prompt schema for task extraction", "priority": "HIGH", "assignee": "AI Arch", "done": False},
            {"desc": "Setup ChromaDB collection for transcript vector embeddings and semantic search", "priority": "MEDIUM", "assignee": "Data Eng", "done": False},
            {"desc": "Build PDF & DOCX export generator using ReportLab / python-docx", "priority": "MEDIUM", "assignee": "Dev Team", "done": False},
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
        
        model_badge = QLabel("Ollama • llama3:8b")
        model_badge.setObjectName("badgePurple")

        header_row.addWidget(stitle)
        header_row.addWidget(model_badge)
        header_row.addStretch()

        btn_regen = QPushButton("Re-generate")
        btn_regen.setStyleSheet("background-color: #FFFFFF; font-size: 12px; border: 1px solid #E2DDD3;")
        header_row.addWidget(btn_regen)

        s_layout.addLayout(header_row)
        s_layout.addSpacing(8)

        # Overview Content
        summary_text = QLabel(
            "<b>Overview:</b> The team aligned on building a privacy-first, local-only desktop application using PySide6. "
            "All speech recognition (Whisper) and LLM inference (Ollama) will run locally on client machines.<br><br>"
            "<b>Key Decisions:</b><br>"
            "• Use <b>PySide6 QThreads</b> to prevent UI freeze during audio transcription.<br>"
            "• Utilize <b>ChromaDB</b> for indexing note chunk embeddings for instant semantic search.<br>"
            "• Provide seamless <b>PDF, DOCX, and TXT</b> export options directly from the home dashboard."
        )
        summary_text.setWordWrap(True)
        summary_text.setStyleSheet("color: #5C6479; font-size: 13px; line-height: 1.6;")
        s_layout.addWidget(summary_text)

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
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        completed_count = sum(1 for t in self.tasks if t["done"])
        self.t_count.setText(f"{completed_count} / {len(self.tasks)} Completed")

        for idx, task in enumerate(self.tasks):
            item_frame = QFrame()
            item_frame.setObjectName("glassFrame")
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(12, 10, 12, 10)

            chk = QCheckBox(task["desc"])
            chk.setChecked(task["done"])
            chk.toggled.connect(lambda checked, i=idx: self.toggle_task(i, checked))
            if task["done"]:
                chk.setStyleSheet("text-decoration: line-through; color: #8C93A4;")

            item_layout.addWidget(chk, stretch=1)

            # Priority Badge
            p_lbl = QLabel(task["priority"])
            if task["priority"] == "HIGH":
                p_lbl.setObjectName("badgeActive")
                p_lbl.setStyleSheet("background-color: #FCE8EC; color: #E05A77; border: 1px solid #F5B0C0; border-radius: 0px; padding: 2px 6px; font-weight: 700;")
            elif task["priority"] == "MEDIUM":
                p_lbl.setObjectName("badgeAmber")
            else:
                p_lbl.setObjectName("badgeCyan")
            
            item_layout.addWidget(p_lbl)

            # Assignee
            a_lbl = QLabel(task['assignee'])
            a_lbl.setStyleSheet("color: #5C6479; font-size: 11px; font-weight: 600;")
            item_layout.addWidget(a_lbl)

            self.tasks_layout.addWidget(item_frame)

    def toggle_task(self, idx: int, checked: bool):
        self.tasks[idx]["done"] = checked
        self.render_tasks()

    def add_task_dialog(self):
        text, ok = QInputDialog.getText(self, "Add Task", "Enter action item description:")
        if ok and text.strip():
            self.tasks.append({
                "desc": text.strip(),
                "priority": "MEDIUM",
                "assignee": "Samar",
                "done": False
            })
            self.render_tasks()
