from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from voicenote.config import APP_NAME, APP_SUBTITLE, VERSION
from voicenote.db.database import get_db
from voicenote.services.worker import PipelineWorker
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
    """Main Application Window for VoiceNote Desktop."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - {APP_SUBTITLE}")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(MAIN_STYLE)
        
        self.db = get_db()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
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
        self.status_bar.showMessage(f"{APP_NAME} v{VERSION} • Database Connected • Local & Gemini AI Pipeline Ready")

    def create_home_view(self) -> QWidget:
        """Create the main Home View containing Quick Stats, Live Audio Recorder, and Recent Notes."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        self.home_layout = QVBoxLayout(container)
        self.home_layout.setContentsMargins(0, 0, 0, 0)
        self.home_layout.setSpacing(16)

        # A. Quick Overview Stat Cards Row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        total_notes = self.db.get_note_count()
        tasks_count = len(self.db.get_all_tasks())

        stats_data = [
            ("Total Voice Notes", f"{total_notes} Notes", "+3 Today", "badgePurple"),
            ("Recorded Audio", "15m 27s", "Avg 5m/note", "badgeCyan"),
            ("Pending Tasks", f"{tasks_count} Tasks", "Active", "badgeAmber"),
            ("Local AI Privacy", "Active", "Gemini & Whisper", "badgeActive"),
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

        self.home_layout.addLayout(stats_row)

        # B. Live Audio Recorder Component
        self.recorder_widget = AudioRecorderWidget()
        self.recorder_widget.transcription_requested.connect(self.on_new_recording_finished)
        self.home_layout.addWidget(self.recorder_widget)

        # C. Recent Voice Notes List
        recent_header = QHBoxLayout()
        r_title = QLabel("Recent Voice Notes & Transcripts")
        r_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #1E2B4B;")
        
        btn_view_all = QPushButton("View All Notes ->")
        btn_view_all.setStyleSheet("background-color: transparent; border: none; color: #6D59A7; font-weight: 700;")
        btn_view_all.clicked.connect(lambda: self.switch_view(1))

        recent_header.addWidget(r_title)
        recent_header.addStretch()
        recent_header.addWidget(btn_view_all)

        self.home_layout.addLayout(recent_header)

        # Populate from database
        self.notes_container = QVBoxLayout()
        self.notes_container.setSpacing(12)
        self.home_layout.addLayout(self.notes_container)

        self.refresh_notes_list()

        scroll.setWidget(container)
        return scroll

    def refresh_notes_list(self):
        """Fetch notes from local SQLite database and render NoteCards."""
        # Clear existing cards
        while self.notes_container.count():
            child = self.notes_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        db_notes = self.db.get_all_notes()
        for note in db_notes:
            tags = note.get("main_topics", ["#VoiceNote"])
            if isinstance(tags, list):
                tags = [f"#{t}" if not t.startswith("#") else t for t in tags]

            card = NoteCard(
                title=note.get("title", "Untitled Note"),
                date=note.get("created_at", "Today"),
                duration=note.get("duration", "00:00"),
                summary=note.get("summary", "No AI summary available."),
                tags=tags if tags else ["#VoiceNote"]
            )
            card.view_clicked.connect(self.on_view_note)
            card.export_clicked.connect(self.on_export_note)
            self.notes_container.addWidget(card)

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

    def on_new_recording_finished(self, raw_text_or_path: str):
        self.status_bar.showMessage("Processing Audio & Generating Gemini AI Summary...")
        
        # Start PipelineWorker background thread
        self.worker = PipelineWorker(raw_transcript=raw_text_or_path, title=f"Voice Note ({raw_text_or_path[:20]}...)")
        self.worker.progress.connect(lambda msg: self.status_bar.showMessage(msg))
        self.worker.finished.connect(self.on_pipeline_success)
        self.worker.error.connect(self.on_pipeline_error)
        self.worker.start()

    def on_pipeline_success(self, data: dict):
        self.status_bar.showMessage("AI Processing Complete • Saved to Database")
        self.refresh_notes_list()
        QMessageBox.information(
            self, "Pipeline Complete",
            f"Speech transcription & Gemini AI analysis completed for note:\n\n'{data.get('title')}'"
        )
        self.sidebar.on_nav_click(1)

    def on_pipeline_error(self, err_msg: str):
        self.status_bar.showMessage("Error processing voice note.")
        QMessageBox.critical(self, "Processing Error", f"Failed to process recording:\n\n{err_msg}")

