from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QScrollArea, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt

class SummaryTaskWidget(QWidget):
    """AI Summarization, Task Extraction & Semantic Cross-Reference UI Component - Modern Dark Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = [
            {"desc": "Implement QThread worker for faster-whisper background STT processing", "priority": "HIGH", "assignee": "Atharv", "done": True, "date": "Today"},
            {"desc": "Design Bento Grid layout with live audio waveform in PySide6", "priority": "HIGH", "assignee": "Samar", "done": True, "date": "Today"},
            {"desc": "Setup ChromaDB vector indexing for transcript chunk retrieval", "priority": "HIGH", "assignee": "Atharv", "done": False, "date": "Tomorrow"},
            {"desc": "Build PDF, DOCX, and TXT export generator with ReportLab", "priority": "MEDIUM", "assignee": "Samar", "done": False, "date": "Aug 22"},
            {"desc": "App lifecycle orchestration, session persistence & SQLite schema", "priority": "MEDIUM", "assignee": "Tejas", "done": True, "date": "Yesterday"},
            {"desc": "Stress test local Whisper vs Groq cloud STT fallback", "priority": "LOW", "assignee": "Tejas", "done": False, "date": "Aug 25"},
        ]
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

        # 1. AI Executive Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("heroCard")
        s_layout = QVBoxLayout(summary_card)
        s_layout.setContentsMargins(20, 18, 20, 18)
        s_layout.setSpacing(10)

        header_row = QHBoxLayout()
        stitle = QLabel("🧠 AI Executive Summary & Key Insights")
        stitle.setObjectName("titleLabel")
        
        model_badge = QLabel("Gemini 1.5 Flash • faster-whisper")
        model_badge.setObjectName("badgePurple")

        header_row.addWidget(stitle)
        header_row.addWidget(model_badge)
        header_row.addStretch()

        btn_regen = QPushButton("🔄 Re-analyze with AI")
        btn_regen.setObjectName("primaryBtn")
        btn_regen.setStyleSheet("font-size: 11px; padding: 4px 12px;")
        btn_regen.clicked.connect(self.reanalyze)
        header_row.addWidget(btn_regen)

        s_layout.addLayout(header_row)

        summary_text = QLabel(
            "<b>TL;DR:</b> The team conducted an architectural sync on the VoiceNote Desktop product. "
            "Ownership boundaries were locked between <b>Tejas</b> (Core Backbone & Orchestration), <b>Samar</b> (Modern PySide6 UX, Export & Analytics), "
            "and <b>Atharv</b> (AI Pipeline, STT, Vector DB & Persistence).<br><br>"
            "<b>Key Architectural Decisions:</b><br>"
            "• <b>Non-blocking UI:</b> Audio capture and Whisper speech recognition execute strictly in background QThreads.<br>"
            "• <b>Vector Search:</b> ChromaDB indexes chunked transcript embeddings for sub-millisecond semantic retrieval.<br>"
            "• <b>Multi-Format Export:</b> Support PDF, DOCX, Markdown, and TXT direct generation with customizable sections."
        )
        summary_text.setWordWrap(True)
        summary_text.setStyleSheet("color: #E2E8F0; font-size: 13px; line-height: 1.6;")
        s_layout.addWidget(summary_text)

        layout.addWidget(summary_card)

        # 2. Extracted Action Items Section
        task_card = QFrame()
        task_card.setObjectName("cardFrame")
        t_layout = QVBoxLayout(task_card)
        t_layout.setContentsMargins(20, 18, 20, 18)
        t_layout.setSpacing(12)

        t_header = QHBoxLayout()
        t_title = QLabel("✅ Extracted Action Items & Deliverables")
        t_title.setObjectName("titleLabel")

        self.t_count = QLabel("3 / 6 Completed")
        self.t_count.setObjectName("badgeActive")

        t_header.addWidget(t_title)
        t_header.addWidget(self.t_count)
        t_header.addStretch()

        btn_add = QPushButton("+ Add Action Item")
        btn_add.setObjectName("primaryBtn")
        btn_add.clicked.connect(self.add_task_dialog)
        t_header.addWidget(btn_add)

        t_layout.addLayout(t_header)

        # Task list layout
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setContentsMargins(0, 0, 0, 0)
        self.tasks_layout.setSpacing(8)

        self.render_tasks()
        t_layout.addWidget(self.tasks_widget)
        layout.addWidget(task_card)

        # 3. Semantic Cross-References (Vector Connections)
        cross_card = QFrame()
        cross_card.setObjectName("cardFrame")
        c_layout = QVBoxLayout(cross_card)
        c_layout.setContentsMargins(20, 18, 20, 18)
        c_layout.setSpacing(10)

        c_title = QLabel("🔗 Semantic Cross-References (ChromaDB Vector Match)")
        c_title.setObjectName("titleLabel")
        c_sub = QLabel("Past voice notes related to this topic based on embedding similarity:")
        c_sub.setObjectName("subtitleLabel")
        c_layout.addWidget(c_title)
        c_layout.addWidget(c_sub)

        cross_refs = [
            ("Sprint 12 Architecture & Pipeline Planning", "94% Match", "Discussed QThread worker design and SQLite persistence schema.", "#Architecture"),
            ("VoiceNote SRS & UI Specifications Review", "88% Match", "Defined export dialog formats (PDF, DOCX) and dark slate Bento grid.", "#UI-Design")
        ]

        for r_title, r_match, r_desc, r_tag in cross_refs:
            rf = QFrame()
            rf.setObjectName("glassFrame")
            rf_lay = QVBoxLayout(rf)
            rf_lay.setContentsMargins(14, 12, 14, 12)
            rf_lay.setSpacing(4)

            rf_top = QHBoxLayout()
            rt = QLabel(r_title)
            rt.setStyleSheet("color: #FFFFFF; font-weight: 700; font-size: 14px;")
            
            rm = QLabel(r_match)
            rm.setObjectName("badgeCyan")
            
            rtag = QLabel(r_tag)
            rtag.setObjectName("badgePurple")

            rf_top.addWidget(rt)
            rf_top.addWidget(rm)
            rf_top.addWidget(rtag)
            rf_top.addStretch()
            rf_lay.addLayout(rf_top)

            rd = QLabel(r_desc)
            rd.setStyleSheet("color: #94A3B8; font-size: 12px;")
            rf_lay.addWidget(rd)

            c_layout.addWidget(rf)

        layout.addWidget(cross_card)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

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
            row_lay.setContentsMargins(14, 10, 14, 10)
            row_lay.setSpacing(12)

            chk = QCheckBox()
            chk.setChecked(task["done"])
            chk.stateChanged.connect(lambda state, i=idx: self.toggle_task_done(i, state))
            row_lay.addWidget(chk)

            desc_lbl = QLabel(task["desc"])
            if task["done"]:
                desc_lbl.setStyleSheet("text-decoration: line-through; color: #64748B;")
            else:
                desc_lbl.setStyleSheet("color: #F8FAFC; font-weight: 600;")
            row_lay.addWidget(desc_lbl, stretch=1)

            # Assignee chip
            assignee_lbl = QLabel(f"👤 {task['assignee']}")
            assignee_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600;")
            row_lay.addWidget(assignee_lbl)

            # Due Date chip
            date_lbl = QLabel(f"📅 {task['date']}")
            date_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            row_lay.addWidget(date_lbl)

            # Priority Badge
            p_badge = QLabel(task["priority"])
            if task["priority"] == "HIGH":
                p_badge.setObjectName("badgeRose")
            elif task["priority"] == "MEDIUM":
                p_badge.setObjectName("badgeAmber")
            else:
                p_badge.setObjectName("badgeActive")

            row_lay.addWidget(p_badge)
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
                "assignee": "Samar",
                "done": False,
                "date": "Today"
            })
            self.render_tasks()

    def reanalyze(self):
        QMessageBox.information(self, "AI Analysis", "AI summary and action item extractor successfully refreshed.")
