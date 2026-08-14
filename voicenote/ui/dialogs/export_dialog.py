from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QLineEdit, QFileDialog, QFrame
)
from PySide6.QtCore import Qt

class ExportDialog(QDialog):
    """Dialog preview for exporting notes to PDF, DOCX, or TXT formats."""

    def __init__(self, note_title="Sprint Planning & Architecture", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Voice Note")
        self.setFixedSize(480, 420)
        self.note_title = note_title
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Export Note Document")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        
        target = QLabel(f"Exporting: <b>{self.note_title}</b>")
        target.setStyleSheet("color: #94A3B8; font-size: 13px;")

        layout.addWidget(title)
        layout.addWidget(target)

        # Format Picker Radio Buttons
        fmt_card = QFrame()
        fmt_card.setObjectName("cardFrame")
        f_layout = QVBoxLayout(fmt_card)
        f_layout.setContentsMargins(16, 16, 16, 16)

        f_layout.addWidget(QLabel("<b>1. Select Export Format:</b>"))
        
        self.fmt_group = QButtonGroup(self)
        self.rb_pdf = QRadioButton("PDF Document (.pdf) - Formatted with styling & headers")
        self.rb_docx = QRadioButton("Word Document (.docx) - Editable document format")
        self.rb_txt = QRadioButton("Plain Text (.txt) - Raw transcript text file")
        self.rb_pdf.setChecked(True)

        self.fmt_group.addButton(self.rb_pdf)
        self.fmt_group.addButton(self.rb_docx)
        self.fmt_group.addButton(self.rb_txt)

        f_layout.addWidget(self.rb_pdf)
        f_layout.addWidget(self.rb_docx)
        f_layout.addWidget(self.rb_txt)

        layout.addWidget(fmt_card)

        # Content Checkboxes
        sec_card = QFrame()
        sec_card.setObjectName("cardFrame")
        s_layout = QVBoxLayout(sec_card)
        s_layout.setContentsMargins(16, 16, 16, 16)

        s_layout.addWidget(QLabel("<b>2. Sections to Include:</b>"))
        
        self.chk_summary = QCheckBox("Include AI Executive Summary")
        self.chk_tasks = QCheckBox("Include Extracted Action Items & Tasks")
        self.chk_transcript = QCheckBox("Include Full Transcript with Timestamps")
        
        self.chk_summary.setChecked(True)
        self.chk_tasks.setChecked(True)
        self.chk_transcript.setChecked(True)

        s_layout.addWidget(self.chk_summary)
        s_layout.addWidget(self.chk_tasks)
        s_layout.addWidget(self.chk_transcript)

        layout.addWidget(sec_card)

        # Buttons Row
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_export = QPushButton("Export Now")
        btn_export.setObjectName("primaryBtn")
        btn_export.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_export)

        layout.addLayout(btn_row)
