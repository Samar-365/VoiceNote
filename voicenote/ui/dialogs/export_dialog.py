"""
VoiceNote Export Dialog.
Provides user-facing interface for configuring note export format,
selecting source voice note with full transcription context,
destination path, and included sections (PDF, DOCX, and TXT).
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFrame, QLineEdit,
    QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt

from voicenote.core.export_engine import ExportEngine
try:
    from voicenote.db.database import get_db
except Exception:
    get_db = lambda: None


class ExportDialog(QDialog):
    """Dialog for exporting notes to PDF, DOCX, or TXT formats - Retro Cream Theme."""

    def __init__(
        self,
        note_data: Optional[Union[Dict[str, Any], Any]] = None,
        note_title: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Export Voice Note")
        self.setFixedSize(560, 580)

        # Initialize export engine & database
        self.export_engine = ExportEngine()
        self.db = get_db()
        self.exported_file_path: Optional[str] = None
        self.all_db_notes: List[Dict[str, Any]] = []

        # Load available notes from database
        if self.db:
            try:
                self.all_db_notes = self.db.get_all_notes()
            except Exception:
                self.all_db_notes = []

        # Resolve initial note data
        if note_data is not None:
            if isinstance(note_data, dict):
                self.note_data = dict(note_data)
            elif hasattr(note_data, "__dict__"):
                self.note_data = dict(note_data.__dict__)
            else:
                self.note_data = {"title": str(note_data)}
        elif note_title:
            self.note_data = self._fetch_db_note_data(note_title)
        elif self.all_db_notes:
            self.note_data = self._fetch_db_note_data(self.all_db_notes[0].get("title", ""))
        else:
            self.note_data = self._get_fallback_note_data("Sprint Planning & Local AI Architecture")

        self.note_title = self.note_data.get("title", "Voice Note")
        self.init_ui()

    def _fetch_db_note_data(self, note_title: str) -> Dict[str, Any]:
        """Fetch complete transcript, summary, and tasks for a given note title from DB."""
        if not self.db:
            return self._get_fallback_note_data(note_title)

        try:
            target = next((n for n in self.all_db_notes if n.get("title") == note_title), None)
            if not target:
                all_notes = self.db.get_all_notes()
                target = next((n for n in all_notes if n.get("title") == note_title), None)

            if not target:
                return self._get_fallback_note_data(note_title)

            note_id = target.get("id")
            transcript_data = self.db.get_transcript(note_id) if note_id else None
            summary_data = self.db.get_ai_summary(note_id) if note_id else None
            all_tasks = self.db.get_all_tasks() if note_id else []
            note_tasks = [t for t in all_tasks if t.get("note_id") == note_id]

            tags = target.get("main_topics") or target.get("tags") or [target.get("category", "General")]
            if summary_data and summary_data.get("main_topics"):
                tags = summary_data.get("main_topics")

            raw_t = transcript_data.get("cleaned_text") or transcript_data.get("raw_text") if transcript_data else ""
            if not raw_t:
                raw_t = target.get("summary", "")

            return {
                "id": note_id,
                "title": target.get("title", note_title),
                "created_at": target.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "duration": target.get("duration", "00:00"),
                "category": target.get("category", "General"),
                "tags": tags,
                "summary": summary_data.get("summary", target.get("summary", "")) if summary_data else target.get("summary", ""),
                "key_points": summary_data.get("key_points", target.get("key_points", [])) if summary_data else target.get("key_points", []),
                "sentiment": summary_data.get("sentiment", "Neutral") if summary_data else "Neutral",
                "tasks": note_tasks,
                "transcript": raw_t,
            }
        except Exception:
            return self._get_fallback_note_data(note_title)

    def _get_fallback_note_data(self, title: str) -> Dict[str, Any]:
        """Generate structured note data if standalone note was passed without DB context."""
        return {
            "title": title,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": "04m 32s",
            "category": "Sprint-Planning",
            "tags": ["#Sprint-Planning", "#Architecture", "#Ollama-AI"],
            "summary": (
                "Discussed PySide6 UI responsiveness, QThread background processing for Whisper STT, "
                "and ChromaDB vector store integration for semantic retrieval."
            ),
            "key_points": [
                "Achieved 100% offline transcription capability via faster-whisper.",
                "Structured action item extraction into JSON schema via Ollama/Gemini AI.",
                "Implemented secure PostgreSQL database persistence for user notes.",
                "Added multi-format export capability (PDF, Word DOCX, Plain Text).",
            ],
            "tasks": [
                {"title": "Implement ReportLab PDF note generator", "priority": "High", "assignee": "Samar", "due_date": "Today", "status": "Completed"},
                {"title": "Integrate python-docx Word export module", "priority": "High", "assignee": "Samar", "due_date": "Today", "status": "Completed"},
                {"title": "Run full automated test verification suite", "priority": "Medium", "assignee": "Dev Team", "due_date": "Sprint End", "status": "Pending"},
            ],
            "transcript": (
                "[00:00:05] Host: Welcome team to today's VoiceNote sprint architecture sync.\n"
                "[00:00:22] Samar: We've finished calibrating the Retro Cream Bento Grid desktop UI.\n"
                "[00:01:10] Atharv: Whisper STT and Gemini AI task extraction pipelines are fully hooked into PostgreSQL.\n"
                "[00:01:45] QA Lead: Will end users be able to export notes into PDF, DOCX, and plain text TXT files directly from the main dashboard?\n"
                "[00:02:10] Samar: Yes! Export dialog support for PDF, DOCX, and TXT is built directly into the sidebar and header quick options."
            ),
        }

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header Title
        title = QLabel("Export Note Document")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        layout.addWidget(title)

        # 0. Source Note Selection Box
        note_card = QFrame()
        note_card.setObjectName("cardFrame")
        n_layout = QVBoxLayout(note_card)
        n_layout.setContentsMargins(14, 10, 14, 10)
        n_layout.setSpacing(6)

        n_layout.addWidget(QLabel("<b>1. Select Source Note to Export:</b>"))
        self.combo_notes = QComboBox()
        self.combo_notes.setStyleSheet("background: #FFFFFF; border: 1px solid #E2DDD3; padding: 5px 8px; border-radius: 6px; font-weight: 600; color: #1E2B4B;")

        # Populate note selector
        if self.all_db_notes:
            for n in self.all_db_notes:
                t = n.get("title", "Untitled Note")
                dur = n.get("duration", "00:00")
                date = n.get("created_at", "")
                display = f"{t} ({dur} • {date})"
                self.combo_notes.addItem(display, t)
        else:
            self.combo_notes.addItem(self.note_title, self.note_title)

        # Pre-select matching note
        cur_idx = 0
        for i in range(self.combo_notes.count()):
            if self.combo_notes.itemData(i) == self.note_title or self.note_title in self.combo_notes.itemText(i):
                cur_idx = i
                break
        self.combo_notes.setCurrentIndex(cur_idx)
        self.combo_notes.currentIndexChanged.connect(self._on_note_selection_changed)

        n_layout.addWidget(self.combo_notes)

        self.lbl_preview = QLabel()
        self.lbl_preview.setStyleSheet("color: #5C6479; font-size: 11px;")
        self._update_preview_label()
        n_layout.addWidget(self.lbl_preview)

        layout.addWidget(note_card)

        # 1. Format Picker Radio Buttons
        fmt_card = QFrame()
        fmt_card.setObjectName("cardFrame")
        f_layout = QVBoxLayout(fmt_card)
        f_layout.setContentsMargins(14, 10, 14, 10)
        f_layout.setSpacing(6)

        f_layout.addWidget(QLabel("<b>2. Select Export Format:</b>"))
        
        self.fmt_group = QButtonGroup(self)
        self.rb_pdf = QRadioButton("PDF Document (.pdf) — Publication styled with tables & headers")
        self.rb_docx = QRadioButton("Word Document (.docx) — Editable Microsoft Word document")
        self.rb_txt = QRadioButton("Plain Text (.txt) — Markdown & formatted transcription text")
        self.rb_pdf.setChecked(True)

        self.fmt_group.addButton(self.rb_pdf)
        self.fmt_group.addButton(self.rb_docx)
        self.fmt_group.addButton(self.rb_txt)

        self.rb_pdf.toggled.connect(self._on_format_changed)
        self.rb_docx.toggled.connect(self._on_format_changed)
        self.rb_txt.toggled.connect(self._on_format_changed)

        f_layout.addWidget(self.rb_pdf)
        f_layout.addWidget(self.rb_docx)
        f_layout.addWidget(self.rb_txt)

        layout.addWidget(fmt_card)

        # 2. Content Sections Checkboxes
        sec_card = QFrame()
        sec_card.setObjectName("cardFrame")
        s_layout = QVBoxLayout(sec_card)
        s_layout.setContentsMargins(14, 10, 14, 10)
        s_layout.setSpacing(6)

        s_layout.addWidget(QLabel("<b>3. Sections to Include:</b>"))
        
        self.chk_summary = QCheckBox("Include AI Executive Summary & Context Takeaways")
        self.chk_tasks = QCheckBox("Include Extracted Action Items & Tasks Table")
        self.chk_transcript = QCheckBox("Include Full Audio Transcript with Timestamps")
        self.chk_metadata = QCheckBox("Include Note Metadata (Date, Duration, Category Tags)")
        
        self.chk_summary.setChecked(True)
        self.chk_tasks.setChecked(True)
        self.chk_transcript.setChecked(True)
        self.chk_metadata.setChecked(True)

        s_layout.addWidget(self.chk_summary)
        s_layout.addWidget(self.chk_tasks)
        s_layout.addWidget(self.chk_transcript)
        s_layout.addWidget(self.chk_metadata)

        layout.addWidget(sec_card)

        # 3. Destination File Path Selector
        path_card = QFrame()
        path_card.setObjectName("cardFrame")
        p_layout = QVBoxLayout(path_card)
        p_layout.setContentsMargins(14, 10, 14, 10)
        p_layout.setSpacing(6)

        p_layout.addWidget(QLabel("<b>4. Save Location:</b>"))
        
        path_row = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("Select export destination file...")
        self.txt_path.setText(self._generate_default_filepath("pdf"))
        self.txt_path.setStyleSheet("background: #FFFFFF; border: 1px solid #E2DDD3; padding: 5px 8px; border-radius: 6px;")

        btn_browse = QPushButton("Browse...")
        btn_browse.setStyleSheet("padding: 5px 12px; font-weight: 700; background: #FFFFFF; border: 1px solid #E2DDD3; border-radius: 6px;")
        btn_browse.clicked.connect(self._on_browse_clicked)

        path_row.addWidget(self.txt_path, stretch=1)
        path_row.addWidget(btn_browse)
        p_layout.addLayout(path_row)

        layout.addWidget(path_card)

        # 4. Action Buttons Row
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        self.btn_export = QPushButton("Export Now")
        self.btn_export.setObjectName("primaryBtn")
        self.btn_export.clicked.connect(self._on_export_clicked)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_export)

        layout.addLayout(btn_row)

    def _update_preview_label(self):
        t_len = len(self.note_data.get("transcript", ""))
        s_len = len(self.note_data.get("summary", ""))
        tasks_count = len(self.note_data.get("tasks", []))
        self.lbl_preview.setText(
            f"Context: Transcript ({t_len} chars) • AI Summary ({s_len} chars) • Tasks ({tasks_count} items)"
        )

    def _on_note_selection_changed(self, idx: int):
        selected_title = self.combo_notes.itemData(idx)
        if selected_title:
            self.note_title = selected_title
            self.note_data = self._fetch_db_note_data(selected_title)
            self._update_preview_label()
            fmt = self._get_selected_format()
            self.txt_path.setText(self._generate_default_filepath(fmt))

    def _get_selected_format(self) -> str:
        if self.rb_pdf.isChecked():
            return "pdf"
        elif self.rb_docx.isChecked():
            return "docx"
        else:
            return "txt"

    def _generate_default_filepath(self, ext: str) -> str:
        """Generate a clean default output path in user's Documents or project folder."""
        title_slug = "".join(
            c if c.isalnum() or c in ("-", "_") else "_"
            for c in self.note_title.replace(" ", "_")
        )[:35].strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title_slug}_{timestamp}.{ext}"
        
        docs_dir = Path.home() / "Documents"
        if not docs_dir.exists():
            docs_dir = Path.cwd() / "data" / "exports"
        else:
            docs_dir = docs_dir / "VoiceNote_Exports"

        return str(docs_dir / filename)

    def _on_format_changed(self):
        """Update file path extension when format selection changes."""
        fmt = self._get_selected_format()
        current_text = self.txt_path.text().strip()
        if current_text:
            p = Path(current_text)
            new_path = p.with_suffix(f".{fmt}")
            self.txt_path.setText(str(new_path))
        else:
            self.txt_path.setText(self._generate_default_filepath(fmt))

    def _on_browse_clicked(self):
        """Open native save file dialog."""
        fmt = self._get_selected_format()
        filter_map = {
            "pdf": "PDF Document (*.pdf)",
            "docx": "Word Document (*.docx)",
            "txt": "Plain Text File (*.txt)",
        }
        current = self.txt_path.text().strip() or self._generate_default_filepath(fmt)
        selected_file, _ = QFileDialog.getSaveFileName(
            self,
            "Choose Export Destination",
            current,
            f"{filter_map.get(fmt, 'All Files (*.*)')};;All Files (*.*)"
        )
        if selected_file:
            self.txt_path.setText(selected_file)

    def _on_export_clicked(self):
        """Execute the export via ExportEngine."""
        dest_path = self.txt_path.text().strip()
        if not dest_path:
            QMessageBox.warning(self, "Invalid Destination", "Please specify a destination file path for export.")
            return

        fmt = self._get_selected_format()
        options = {
            "include_summary": self.chk_summary.isChecked(),
            "include_tasks": self.chk_tasks.isChecked(),
            "include_transcript": self.chk_transcript.isChecked(),
            "include_metadata": self.chk_metadata.isChecked(),
        }

        try:
            self.btn_export.setEnabled(False)
            self.btn_export.setText("Generating...")

            output_file = self.export_engine.export(
                format_type=fmt,
                note_data=self.note_data,
                output_path=dest_path,
                options=options,
            )
            self.exported_file_path = output_file

            # Show success dialog with quick action buttons
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Export Complete")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(f"<b>Successfully exported note!</b><br><br>Saved to: <code>{output_file}</code>")
            
            btn_open = msg_box.addButton("Open Document", QMessageBox.ActionRole)
            btn_folder = msg_box.addButton("Open Folder", QMessageBox.ActionRole)
            msg_box.addButton("OK", QMessageBox.AcceptRole)

            msg_box.exec()

            if msg_box.clickedButton() == btn_open:
                self._open_file(output_file)
            elif msg_box.clickedButton() == btn_folder:
                self._open_folder(output_file)

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Failed to export document:\n\n{str(e)}"
            )
            self.btn_export.setEnabled(True)
            self.btn_export.setText("Export Now")

    def _open_file(self, file_path: str):
        """Open the exported document in the system default application."""
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.warning(self, "Open Error", f"Could not open file: {e}")

    def _open_folder(self, file_path: str):
        """Open the directory containing the exported document."""
        try:
            folder = str(Path(file_path).parent)
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{file_path}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            QMessageBox.warning(self, "Open Error", f"Could not open directory: {e}")
