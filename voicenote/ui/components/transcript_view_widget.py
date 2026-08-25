from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QInputDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal

class TranscriptViewWidget(QWidget):
    """Transcript Viewer & Tag Manager UI Component - Retro Cream Theme matching assets/transcript.png."""
    export_clicked = Signal(str)
    delete_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = []
        self.current_title = "No Note Selected"
        self.raw_transcript_text = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header Info Card
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        top_row = QHBoxLayout()
        title_v = QVBoxLayout()
        
        self.title_label = QLabel("No Note Selected")
        self.title_label.setObjectName("titleLabel")
        
        self.sub_info = QLabel("Select a note from the dashboard or record audio to view its transcript.")
        self.sub_info.setObjectName("subtitleLabel")
        
        title_v.addWidget(self.title_label)
        title_v.addWidget(self.sub_info)
        top_row.addLayout(title_v)
        top_row.addStretch()

        # Action Buttons
        btn_delete = QPushButton("Delete Note")
        btn_delete.setStyleSheet("background-color: #FFF5F5; border: 1px solid #FADBD8; font-weight: 700; color: #C0392B; padding: 6px 14px;")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.current_title))
        top_row.addWidget(btn_delete)

        btn_export = QPushButton("Export Note")
        btn_export.setObjectName("primaryBtn")
        btn_export.clicked.connect(lambda: self.export_clicked.emit(self.current_title))
        top_row.addWidget(btn_export)

        btn_copy = QPushButton("Copy Text")
        btn_copy.setStyleSheet("background-color: #F8F6F0; border: 1px solid #E5E0D6; font-weight: 700; color: #4A3980; padding: 6px 14px;")
        btn_copy.clicked.connect(self.copy_transcript)
        top_row.addWidget(btn_copy)

        card_layout.addLayout(top_row)
        card_layout.addSpacing(6)

        # Tag Manager Row
        tag_row = QHBoxLayout()
        tag_lbl = QLabel("Tags:")
        tag_lbl.setStyleSheet("color: #1E2B4B; font-weight: 600;")
        tag_row.addWidget(tag_lbl)

        self.tags_container = QHBoxLayout()
        self.render_tags()
        tag_row.addLayout(self.tags_container)

        btn_add_tag = QPushButton("+ Add Tag")
        btn_add_tag.setStyleSheet("background-color: #ECE8E1; color: #6D59A7; font-size: 11px; padding: 4px 10px; border: 1px solid #E2DDD3;")
        btn_add_tag.clicked.connect(self.add_new_tag)
        tag_row.addWidget(btn_add_tag)
        tag_row.addStretch()

        card_layout.addLayout(tag_row)
        layout.addWidget(card)

        # Search Bar for Transcript
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter transcript text or timestamp...")
        self.search_input.textChanged.connect(self.filter_transcript)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Main Transcript Text Display Panel
        self.transcript_edit = QTextEdit()
        self.transcript_edit.setReadOnly(False)
        self.load_sample_transcript()

        layout.addWidget(self.transcript_edit)

    def render_tags(self):
        while self.tags_container.count():
            item = self.tags_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for tag in self.tags:
            lbl = QLabel(tag)
            lbl.setObjectName("badgePurple")
            self.tags_container.addWidget(lbl)

    def add_new_tag(self):
        text, ok = QInputDialog.getText(self, "Add Tag", "Enter tag name:")
        if ok and text.strip():
            tag_name = text.strip()
            if not tag_name.startswith("#"):
                tag_name = "#" + tag_name
            self.tags.append(tag_name)
            self.render_tags()

    def copy_transcript(self):
        QApplication.clipboard().setText(self.transcript_edit.toPlainText())
        QMessageBox.information(self, "Copied", "Full transcript text copied to clipboard.")

    def filter_transcript(self, text: str):
        if not text.strip():
            self.transcript_edit.setPlainText(self.raw_transcript_text or "No transcript available. Select a voice note or record audio.")
            return
        
        lines = self.raw_transcript_text.split("\n") if self.raw_transcript_text else []
        filtered = [l for l in lines if text.lower() in l.lower()]
        self.transcript_edit.setPlainText("\n\n".join(filtered) if filtered else "No matching dialogue found.")

    def set_note_transcript(self, title: str, transcript_text: str, tags: list = None, metadata_info: str = None):
        """Dynamically load and format a note's real transcript in the viewer."""
        self.current_title = title
        self.raw_transcript_text = transcript_text
        self.title_label.setText(f"Note: {title}")
        if metadata_info:
            self.sub_info.setText(metadata_info)
        if tags is not None:
            self.tags = [f"#{t.lstrip('#')}" for t in tags] if tags else ["#VoiceNote"]
            self.render_tags()

        if not transcript_text or not transcript_text.strip():
            self.transcript_edit.setHtml("<p style='color: #7D8495; font-style: italic;'>No transcript text recorded for this note.</p>")
            return

        # Format transcript lines with styled timestamps
        formatted_html_lines = []
        for line in transcript_text.split("\n"):
            line_str = line.strip()
            if not line_str:
                formatted_html_lines.append("<br>")
                continue
            if line_str.startswith("[") and "]" in line_str:
                idx = line_str.find("]")
                timestamp = line_str[:idx + 1]
                rest = line_str[idx + 1:].strip()
                formatted_html_lines.append(f"<b style='color: #6D59A7;'>{timestamp}</b> {rest}<br><br>")
            else:
                formatted_html_lines.append(f"{line_str}<br><br>")

        html = f"<div style='line-height: 1.8; color: #1E2B4B; font-size: 13px;'>{''.join(formatted_html_lines)}</div>"
        self.transcript_edit.setHtml(html)

    def load_sample_transcript(self):
        self.transcript_edit.setHtml("<p style='color: #7D8495; font-style: italic; font-size: 13px;'>No voice note selected. Select a note from the Recent Notes feed or record audio to view the transcript.</p>")
