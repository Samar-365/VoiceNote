from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt

class NoteCard(QFrame):
    """Card widget representing a single Voice Note item - Retro Cream Theme."""
    view_clicked = Signal(str)
    export_clicked = Signal(str)

    def __init__(self, title: str, date: str, duration: str, summary: str, tags: list, parent=None):
        super().__init__(parent)
        self.note_title = title
        self.setObjectName("cardFrame")
        self.init_ui(title, date, duration, summary, tags)

    def init_ui(self, title, date, duration, summary, tags):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Header Row
        top_row = QHBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
        
        dur_lbl = QLabel(f"Duration: {duration}")
        dur_lbl.setStyleSheet("color: #6D59A7; font-weight: 700; font-size: 12px;")

        date_lbl = QLabel(date)
        date_lbl.setStyleSheet("color: #8C93A4; font-size: 12px;")

        top_row.addWidget(t_lbl)
        top_row.addWidget(dur_lbl)
        top_row.addStretch()
        top_row.addWidget(date_lbl)

        layout.addLayout(top_row)

        # Summary Snippet
        sum_lbl = QLabel(summary)
        sum_lbl.setWordWrap(True)
        sum_lbl.setStyleSheet("color: #5C6479; font-size: 13px; line-height: 1.4;")
        layout.addWidget(sum_lbl)

        # Footer Row (Tags & Action Buttons)
        bottom_row = QHBoxLayout()
        for tag in tags:
            tag_badge = QLabel(tag)
            tag_badge.setObjectName("badgePurple")
            bottom_row.addWidget(tag_badge)

        bottom_row.addStretch()

        btn_export = QPushButton("Export")
        btn_export.setStyleSheet("padding: 4px 10px; font-size: 11px; background: #FFFFFF; color: #1E2B4B; border: 1px solid #E2DDD3;")
        btn_export.clicked.connect(lambda: self.export_clicked.emit(self.note_title))

        btn_view = QPushButton("View Note")
        btn_view.setObjectName("primaryBtn")
        btn_view.setStyleSheet("padding: 4px 12px; font-size: 11px;")
        btn_view.clicked.connect(lambda: self.view_clicked.emit(self.note_title))

        bottom_row.addWidget(btn_export)
        bottom_row.addWidget(btn_view)

        layout.addLayout(bottom_row)
