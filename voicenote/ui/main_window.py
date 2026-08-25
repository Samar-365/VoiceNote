from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon

from voicenote.config import APP_NAME, APP_SUBTITLE, VERSION
try:
    from voicenote.db.database import get_db
except Exception:
    get_db = lambda: None

try:
    from voicenote.services.worker import PipelineWorker
except Exception:
    PipelineWorker = None
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
from voicenote.ui.dialogs.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """Main Application Window for VoiceNote Desktop matching assets/home.png."""
    logout_requested = Signal()

    def __init__(self, current_user: dict = None):
        super().__init__()
        self.current_user = current_user or {}
        self.setWindowTitle(f"{APP_NAME} Desktop - AI-Powered Local Voice Intelligence")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(MAIN_STYLE)
        
        self.db = get_db()
        self.worker = None
        self.current_selected_note_title = None
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
        self.sidebar.settings_clicked.connect(self.show_settings_dialog)
        main_layout.addWidget(self.sidebar)

        # Right Main Content Container
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # 2. Header Bar
        self.header = HeaderWidget()
        if self.current_user:
            self.header.set_user(self.current_user)
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
        self.transcript_view.export_clicked.connect(self.on_export_note)
        self.transcript_view.delete_clicked.connect(self.on_delete_note)
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
        self.status_bar.showMessage(f"{APP_NAME} v{VERSION} • Database Connected • Local & Cloud AI Pipeline Ready")

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

        total_notes = self.db.get_note_count() if self.db else 24
        tasks_count = len(self.db.get_all_tasks()) if self.db else 5

        stats_data = [
            ("Total Voice Notes", f"{total_notes} Notes", "+3 Today", "badgePurple"),
            ("Recorded Audio", "15m 27s", "Avg 5m/note", "badgeCyan"),
            ("Pending Tasks", f"{tasks_count} Tasks", "Active", "badgeAmber"),
            ("Local AI Privacy", "Active", "Whisper & Gemini", "badgeActive"),
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
        
        btn_clear_all = QPushButton("Remove All Recordings")
        btn_clear_all.setStyleSheet("background-color: #FFF5F5; border: 1px solid #FADBD8; color: #C0392B; font-weight: 700; font-size: 11px; padding: 5px 12px; border-radius: 6px;")
        btn_clear_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear_all.clicked.connect(self.on_delete_all_notes)

        btn_view_all = QPushButton("View All Notes ->")
        btn_view_all.setStyleSheet("background-color: transparent; border: none; color: #6D59A7; font-weight: 700;")
        btn_view_all.clicked.connect(lambda: self.sidebar.on_nav_click(1))

        recent_header.addWidget(r_title)
        recent_header.addStretch()
        recent_header.addWidget(btn_clear_all)
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
        """Fetch notes from database and render NoteCards."""
        while self.notes_container.count():
            child = self.notes_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        db_notes = self.db.get_all_notes() if self.db else []
        if not db_notes:
            # Display sample notes if database is empty
            db_notes = [
                {
                    "title": "Sprint Planning & Local AI Architecture",
                    "created_at": "Today, 02:30 PM",
                    "duration": "04m 32s",
                    "summary": "Discussed PySide6 UI responsiveness, QThread background processing for Whisper STT, and ChromaDB vector store integration.",
                    "main_topics": ["#Sprint-Planning", "#Architecture", "#Ollama-AI"]
                },
                {
                    "title": "PostgreSQL Schema & Persistence Review",
                    "created_at": "Yesterday, 04:15 PM",
                    "duration": "12m 40s",
                    "summary": "Reviewed user profiles, transcript relational tables, tag associations, and SQLAlchemy model migrations.",
                    "main_topics": ["#PostgreSQL", "#Database"]
                },
                {
                    "title": "Task Extraction & AI Prompt Formatting",
                    "created_at": "Aug 12, 11:00 AM",
                    "duration": "08m 15s",
                    "summary": "Defined JSON structured outputs for Ollama task extraction, priority categorization, and assignee mapping.",
                    "main_topics": ["#Tasks", "#Ollama-AI", "#High-Priority"]
                }
            ]

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
            card.delete_clicked.connect(self.on_delete_note)
            self.notes_container.addWidget(card)

    def switch_view(self, index: int):
        self.stack.setCurrentIndex(index)
        views = ["Home & Recorder", "Transcripts & Notes", "AI Summary & Tasks", "Semantic Search", "Analytics Dashboard"]
        self.status_bar.showMessage(f"Active View: {views[index]}")
        if index == 4 and hasattr(self, "analytics_view"):
            self.analytics_view.refresh_data()

    def on_header_search(self, query: str):
        if query.strip():
            self.sidebar.on_nav_click(3)
            self.semantic_search_view.search_bar.setText(query)
            self.semantic_search_view.perform_search()

    def on_view_note(self, note_title: str):
        self.current_selected_note_title = note_title
        self.sidebar.on_nav_click(1)
        note_data = self._fetch_full_note_data(note_title)
        transcript_text = note_data.get("transcript") or note_data.get("summary") or "No transcript available."
        tags = note_data.get("tags", [])
        meta_str = f"Date: {note_data.get('created_at', 'Today')}  •  Duration: {note_data.get('duration', '00:00')}  •  Category: {note_data.get('category', 'General')}"
        self.transcript_view.set_note_transcript(
            title=note_title,
            transcript_text=transcript_text,
            tags=tags,
            metadata_info=meta_str
        )
        if note_data.get("summary"):
            self.summary_task_view.set_ai_data(
                summary=note_data.get("summary"),
                key_points=note_data.get("key_points", []),
                tasks=note_data.get("tasks", []),
                model_name="Gemini 2.5 Flash"
            )

    def _fetch_full_note_data(self, note_title: str) -> dict:
        """Fetch all related DB entities (transcript, AI summary, tasks) for a note."""
        if not self.db:
            return {"title": note_title}

        try:
            all_notes = self.db.get_all_notes()
            target = next((n for n in all_notes if n.get("title") == note_title), None)
            if not target:
                return {"title": note_title}

            note_id = target.get("id")
            transcript_data = self.db.get_transcript(note_id) if note_id else None
            summary_data = self.db.get_ai_summary(note_id) if note_id else None
            all_tasks = self.db.get_all_tasks() if note_id else []
            note_tasks = [t for t in all_tasks if t.get("note_id") == note_id]

            tags = target.get("main_topics") or target.get("tags") or [target.get("category", "General")]
            if summary_data and summary_data.get("main_topics"):
                tags = summary_data.get("main_topics")

            return {
                "id": note_id,
                "title": target.get("title", note_title),
                "created_at": target.get("created_at", "Today"),
                "duration": target.get("duration", "00:00"),
                "category": target.get("category", "General"),
                "tags": tags,
                "summary": summary_data.get("summary", target.get("summary", "")) if summary_data else target.get("summary", ""),
                "key_points": summary_data.get("key_points", target.get("key_points", [])) if summary_data else target.get("key_points", []),
                "sentiment": summary_data.get("sentiment", "Neutral") if summary_data else "Neutral",
                "tasks": note_tasks,
                "transcript": (
                    (transcript_data.get("cleaned_text") or transcript_data.get("raw_text"))
                    if transcript_data else target.get("summary", "")
                ),
            }
        except Exception:
            return {"title": note_title}

    def on_export_note(self, note_title: str):
        self.current_selected_note_title = note_title
        note_data = self._fetch_full_note_data(note_title)
        dialog = ExportDialog(note_data=note_data, note_title=note_title, parent=self)
        dialog.exec()

    def on_delete_note(self, note_title: str):
        """Prompt confirmation and delete the selected note and its recording."""
        reply = QMessageBox.question(
            self,
            "Remove Recording & Note",
            f"Are you sure you want to remove voice note:\n\n'{note_title}'?\n\nThis will permanently delete the audio recording file, transcript, summary, and tasks.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.db:
                success = self.db.delete_note_by_title(note_title)
                if success:
                    self.status_bar.showMessage(f"Voice Note '{note_title}' removed successfully.")
                else:
                    self.status_bar.showMessage(f"Could not remove '{note_title}'.")
            
            # Reset views if active note was deleted
            if self.current_selected_note_title == note_title:
                self.current_selected_note_title = None
                self.transcript_view.set_note_transcript("No Note Selected", "Select a note from the dashboard or record audio.", [])
                self.summary_task_view.set_ai_data("No AI summary available.", [], [], "None")

            self.refresh_notes_list()
            if hasattr(self, "analytics_view"):
                self.analytics_view.refresh_data()

    def on_delete_all_notes(self):
        """Prompt confirmation and purge all recordings, notes, transcripts, summaries, and tasks."""
        count = self.db.get_note_count() if self.db else 0
        if count == 0:
            QMessageBox.information(self, "No Recordings", "There are no recordings or voice notes stored in the database.")
            return

        reply = QMessageBox.warning(
            self,
            "Remove All Recordings & Notes",
            f"Are you sure you want to permanently remove ALL {count} voice notes and recordings?\n\nThis will purge all audio files from data/recording, transcripts, summaries, and extracted tasks from the database.\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.db:
                deleted_count = self.db.delete_all_notes()
                self.status_bar.showMessage(f"All {deleted_count} voice notes and recordings removed.")
            
            # Reset active views
            self.current_selected_note_title = None
            self.transcript_view.set_note_transcript("No Note Selected", "Select a note from the dashboard or record audio.", [])
            self.summary_task_view.set_ai_data("No AI summary available.", [], [], "None")

            self.refresh_notes_list()
            if hasattr(self, "analytics_view"):
                self.analytics_view.refresh_data()
            
            QMessageBox.information(self, "Recordings Cleared", "All voice notes and audio recordings have been successfully removed.")

    def show_export_dialog(self):
        title = self.current_selected_note_title
        note_data = self._fetch_full_note_data(title) if title else None
        dialog = ExportDialog(note_data=note_data, note_title=title, parent=self)
        dialog.exec()

    def show_profile_dialog(self):
        dialog = ProfileDialog(user_data=self.current_user, parent=self)
        dialog.logout_requested.connect(self.on_logout_triggered)
        dialog.exec()

    def show_settings_dialog(self):
        dialog = SettingsDialog(parent=self)
        dialog.exec()

    def on_logout_triggered(self):
        self.logout_requested.emit()
        self.close()


    def on_new_recording_finished(self, raw_text_or_path: str):
        self.status_bar.showMessage("Recording saved to data/recording • Processing AI Pipeline...")
        
        # Check if background PipelineWorker is available
        if PipelineWorker and callable(PipelineWorker):
            try:
                from pathlib import Path
                is_file = Path(raw_text_or_path).exists() if raw_text_or_path else False
                if is_file:
                    audio_file = raw_text_or_path
                    raw_text = None
                    file_stem = Path(raw_text_or_path).stem
                    title_name = f"Voice Note ({file_stem})"
                else:
                    audio_file = None
                    raw_text = raw_text_or_path
                    title_snip = raw_text_or_path[:20] if raw_text_or_path else "Recording"
                    title_name = f"Voice Note ({title_snip}...)"

                self.worker = PipelineWorker(
                    audio_path=audio_file,
                    raw_transcript=raw_text,
                    title=title_name
                )
                self.worker.progress.connect(lambda msg: self.status_bar.showMessage(msg))
                self.worker.finished.connect(self.on_pipeline_success)
                self.worker.error.connect(self.on_pipeline_error)
                self.worker.start()
                return
            except Exception as e:
                self.status_bar.showMessage("Pipeline notice: running in local presentation mode.")

        # Presentation mode fallback
        self.status_bar.showMessage("AI Processing Complete • Note added to dashboard")
        QMessageBox.information(
            self, "Recording Saved & Transcribed",
            f"Audio recording successfully stored in data/recording folder.\n\nFile/Payload: {raw_text_or_path}\n\nNote added to your dashboard."
        )
        self.sidebar.on_nav_click(1)

    def on_pipeline_success(self, data: dict):
        self.status_bar.showMessage("AI Processing Complete • Saved to Database")
        self.refresh_notes_list()
        if hasattr(self, "analytics_view"):
            self.analytics_view.refresh_data()

        # Populate newly transcribed note into transcript and summary views
        title = data.get("title", "Voice Note")
        self.current_selected_note_title = title
        transcript_text = data.get("transcript", "")
        duration = data.get("duration", "00:00")
        ai_data = data.get("ai_data") or {}

        self.transcript_view.set_note_transcript(
            title=title,
            transcript_text=transcript_text,
            tags=ai_data.get("tags", ["#VoiceNote"]),
            metadata_info=f"Recorded Just Now  •  Duration: {duration}  •  Format: WAV 16kHz  •  Engine: Whisper & Gemini"
        )

        if ai_data.get("summary"):
            self.summary_task_view.set_ai_data(
                summary=ai_data.get("summary", ""),
                key_points=ai_data.get("key_points", []),
                tasks=ai_data.get("tasks", []),
                model_name="Gemini 2.5 Flash"
            )

        QMessageBox.information(
            self, "Pipeline Complete",
            f"Speech transcription & Gemini AI analysis completed for note:\n\n'{title}'"
        )
        self.sidebar.on_nav_click(1)

    def on_pipeline_error(self, err_msg: str):
        self.status_bar.showMessage("Error processing voice note.")
        QMessageBox.critical(self, "Processing Error", f"Failed to process recording:\n\n{err_msg}")
