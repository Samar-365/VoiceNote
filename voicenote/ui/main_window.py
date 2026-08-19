from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from voicenote.ui.styles import MAIN_STYLE
from voicenote.ui.components.sidebar import SidebarWidget
from voicenote.ui.components.header import HeaderWidget
from voicenote.ui.components.audio_recorder_widget import AudioRecorderWidget
from voicenote.ui.components.note_card import NoteCard
from voicenote.ui.components.transcript_view_widget import TranscriptViewWidget
from voicenote.ui.components.summary_task_widget import SummaryTaskWidget
from voicenote.ui.components.semantic_search_widget import SemanticSearchWidget
from voicenote.ui.components.analytics_dashboard_widget import AnalyticsDashboardWidget
from voicenote.ui.dialogs.export_dialog import ExportDialog
from voicenote.ui.dialogs.profile_dialog import ProfileDialog

class MainWindow(QMainWindow):
    """Main Application Window for VoiceNote Desktop matching assets/home.png."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceNote Desktop - AI-Powered Local Voice Intelligence")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(MAIN_STYLE)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # 1. Left Sidebar Navigation
        self.sidebar = SidebarWidget()
        self.sidebar.nav_changed.connect(self.switch_view)
        self.sidebar.export_clicked.connect(self.show_export_dialog)
        self.sidebar.settings_clicked.connect(self.show_profile_dialog)
        main_layout.addWidget(self.sidebar)

        # Right Main Content Container
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # 2. Header Bar
        self.header = HeaderWidget()
        self.header.profile_clicked.connect(self.show_profile_dialog)
        self.header.search_triggered.connect(self.on_header_search)
        right_layout.addWidget(self.header)

        # 3. Stacked Pages Area
        self.stack = QStackedWidget()

        # View 0: Home / Recorder View
        self.home_view = self.create_home_view()
        self.stack.addWidget(self.home_view)

        # View 1: Transcript & Tag Manager View
        self.transcript_view = TranscriptViewWidget()
        self.stack.addWidget(self.transcript_view)

        # View 2: AI Summary & Task Board View
        self.summary_task_view = SummaryTaskWidget()
        self.stack.addWidget(self.summary_task_view)

        # View 3: Semantic Search View
        self.semantic_search_view = SemanticSearchWidget()
        self.stack.addWidget(self.semantic_search_view)

        # View 4: Analytics Dashboard View
        self.analytics_view = AnalyticsDashboardWidget()
        self.stack.addWidget(self.analytics_view)

        right_layout.addWidget(self.stack)
        main_layout.addWidget(right_container, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("VoiceNote Desktop v0.1.0 • All Local AI Services Active (Whisper, Ollama, Postgres, ChromaDB)")

    def create_home_view(self) -> QWidget:
        """Create the main Home View containing Quick Stats, Live Audio Recorder, and Recent Notes."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # A. Quick Overview Stat Cards Row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        stats_data = [
            ("Total Voice Notes", "24 Notes", "+4 Today", "badgePurple"),
            ("Recorded Audio", "4h 32m", "Avg 11m/note", "badgeCyan"),
            ("Pending Tasks", "5 Pending", "18 Completed", "badgeAmber"),
            ("Local AI Privacy", "100% Offline", "Zero Cloud", "badgeActive"),
        ]

        for title, val, sub, badge_cls in stats_data:
            card = QFrame()
            card.setObjectName("cardFrame")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(16, 14, 16, 14)

            v_lbl = QLabel(val)
            v_lbl.setStyleSheet("color: #1E2B4B; font-size: 24px; font-weight: 900; margin: 2px 0;")

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 700;")

            s_lbl = QLabel(sub)
            s_lbl.setObjectName(badge_cls)

            c_lay.addWidget(v_lbl)
            c_lay.addWidget(t_lbl)
            c_lay.addWidget(s_lbl)

            stats_row.addWidget(card)

        layout.addLayout(stats_row)

        # B. Live Audio Recorder Component
        self.recorder_widget = AudioRecorderWidget()
        self.recorder_widget.transcription_requested.connect(self.on_new_recording_finished)
        layout.addWidget(self.recorder_widget)

        # C. Recent Voice Notes List
        recent_header = QHBoxLayout()
        r_title = QLabel("Recent Voice Notes & Transcripts")
        r_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #1E2B4B;")
        
        btn_view_all = QPushButton("View All Notes ->")
        btn_view_all.setStyleSheet("background-color: transparent; border: none; color: #6D59A7; font-weight: 700;")
        btn_view_all.clicked.connect(lambda: self.sidebar.on_nav_click(1))

        recent_header.addWidget(r_title)
        recent_header.addStretch()
        recent_header.addWidget(btn_view_all)

        layout.addLayout(recent_header)

        # Sample recent notes matching assets/home.png
        sample_notes = [
            {
                "title": "Sprint Planning & Local AI Architecture",
                "date": "Today, 02:30 PM",
                "duration": "04m 32s",
                "summary": "Discussed PySide6 UI responsiveness, QThread background processing for Whisper STT, and ChromaDB vector store integration.",
                "tags": ["#Sprint-Planning", "#Architecture", "#Ollama-AI"]
            },
            {
                "title": "PostgreSQL Schema & Persistence Review",
                "date": "Yesterday, 04:15 PM",
                "duration": "12m 40s",
                "summary": "Reviewed user profiles, transcript relational tables, tag associations, and SQLAlchemy model migrations.",
                "tags": ["#PostgreSQL", "#Database"]
            },
            {
                "title": "Task Extraction & AI Prompt Formatting",
                "date": "Aug 12, 11:00 AM",
                "duration": "08m 15s",
                "summary": "Defined JSON structured outputs for Ollama task extraction, priority categorization, and assignee mapping.",
                "tags": ["#Tasks", "#Ollama-AI", "#High-Priority"]
            }
        ]

        for note in sample_notes:
            card = NoteCard(
                title=note["title"],
                date=note["date"],
                duration=note["duration"],
                summary=note["summary"],
                tags=note["tags"]
            )
            card.view_clicked.connect(self.on_view_note)
            card.export_clicked.connect(self.on_export_note)
            layout.addWidget(card)

        scroll.setWidget(container)
        return scroll

    def switch_view(self, index: int):
        self.stack.setCurrentIndex(index)
        views = ["Home & Recorder", "Transcripts & Notes", "AI Summary & Tasks", "Semantic Search", "Analytics Dashboard"]
        self.status_bar.showMessage(f"Active View: {views[index]}")

    def on_header_search(self, query: str):
        if query.strip():
            self.sidebar.on_nav_click(3)
            self.semantic_search_view.search_bar.setText(query)
            self.semantic_search_view.perform_search()

    def on_view_note(self, note_title: str):
        self.sidebar.on_nav_click(1)
        self.transcript_view.title_label.setText(f"Note: {note_title}")

    def on_export_note(self, note_title: str):
        dialog = ExportDialog(note_title=note_title, parent=self)
        if dialog.exec():
            QMessageBox.information(self, "Export Success", f"Successfully exported '{note_title}' to file.")

    def show_export_dialog(self):
        dialog = ExportDialog(parent=self)
        if dialog.exec():
            QMessageBox.information(self, "Export Success", "Successfully exported selected note.")

    def show_profile_dialog(self):
        dialog = ProfileDialog(parent=self)
        dialog.exec()

    def on_new_recording_finished(self, name: str):
        QMessageBox.information(
            self, "Transcription Complete",
            "Whisper speech recognition & Ollama AI summary processing completed successfully!\n\nNote added to your dashboard."
        )
        self.sidebar.on_nav_click(1)
