"""
VoiceNote Export Dialog.
Provides user-facing interface for configuring note export format,
destination path, and included sections (PDF, DOCX, and TXT).
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFrame, QLineEdit,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from voicenote.core.export_engine import ExportEngine


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
        self.setFixedSize(540, 520)

        # Initialize export engine
        self.export_engine = ExportEngine()
        self.exported_file_path: Optional[str] = None

        # Resolve note data
        if note_data is not None:
            if isinstance(note_data, dict):
                self.note_data = dict(note_data)
            elif hasattr(note_data, "__dict__"):
                self.note_data = dict(note_data.__dict__)
            else:
                self.note_data = {"title": str(note_data)}
        else:
            title = note_title or "Sprint Planning & Local AI Architecture"
            self.note_data = self._get_fallback_note_data(title)

        if note_title and "title" not in self.note_data:
            self.note_data["title"] = note_title

        self.note_title = self.note_data.get("title", "Voice Note")
        self.init_ui()

    def _get_fallback_note_data(self, title: str) -> Dict[str, Any]:
        """Generate structured sample note data if standalone note was passed without context."""
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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header Title
        title = QLabel("Export Note Document")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        
        target = QLabel(f"Exporting: <b>{self.note_title}</b>")
        target.setStyleSheet("color: #5C6479; font-size: 13px;")

        layout.addWidget(title)
        layout.addWidget(target)

        # 1. Format Picker Radio Buttons
        fmt_card = QFrame()
        fmt_card.setObjectName("cardFrame")
        f_layout = QVBoxLayout(fmt_card)
        f_layout.setContentsMargins(14, 12, 14, 12)
        f_layout.setSpacing(8)

        f_layout.addWidget(QLabel("<b>1. Select Export Format:</b>"))
        
        self.fmt_group = QButtonGroup(self)
        self.rb_pdf = QRadioButton("PDF Document (.pdf) — Formatted publication styling & tables")
        self.rb_docx = QRadioButton("Word Document (.docx) — Editable Microsoft Word document")
        self.rb_txt = QRadioButton("Plain Text (.txt) — Markdown & formatted text file")
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
        s_layout.setContentsMargins(14, 12, 14, 12)
        s_layout.setSpacing(8)

        s_layout.addWidget(QLabel("<b>2. Sections to Include:</b>"))
        
        self.chk_summary = QCheckBox("Include AI Executive Summary & Key Points")
        self.chk_tasks = QCheckBox("Include Extracted Action Items & Tasks")
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
        p_layout.setContentsMargins(14, 12, 14, 12)
        p_layout.setSpacing(6)

        p_layout.addWidget(QLabel("<b>3. Save Location:</b>"))
        
        path_row = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("Select export destination file...")
        self.txt_path.setText(self._generate_default_filepath("pdf"))
        self.txt_path.setStyleSheet("background: #FFFFFF; border: 1px solid #E2DDD3; padding: 6px 10px; border-radius: 6px;")

        btn_browse = QPushButton("Browse...")
        btn_browse.setStyleSheet("padding: 6px 12px; font-weight: 700; background: #FFFFFF; border: 1px solid #E2DDD3; border-radius: 6px;")
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
