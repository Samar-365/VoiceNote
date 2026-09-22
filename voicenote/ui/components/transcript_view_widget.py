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
        btn_delete.setStyleSheet("background-color: #FFF5F5; border: none; font-weight: 700; color: #C0392B; padding: 6px 14px; border-radius: 6px;")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.current_title))
        top_row.addWidget(btn_delete)

        btn_export = QPushButton("Export Note")
        btn_export.setObjectName("primaryBtn")
        btn_export.setStyleSheet("border-radius: 6px; padding: 6px 16px;")
        btn_export.clicked.connect(lambda: self.export_clicked.emit(self.current_title))
        top_row.addWidget(btn_export)

        btn_copy = QPushButton("Copy Text")
        btn_copy.setStyleSheet("background-color: #F8F6F0; border: 1px solid #E5E0D6; font-weight: 700; color: #4A3980; padding: 6px 14px; border-radius: 6px;")
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
        btn_add_tag.setStyleSheet("background-color: #ECE8E1; color: #6D59A7; font-size: 11px; padding: 4px 10px; border: none; border-radius: 4px; font-weight: 700;")
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
            self._render_dialogue(self.raw_transcript_text or "")
            return

        lines = self.raw_transcript_text.split("\n\n") if self.raw_transcript_text else []
        filtered = [l for l in lines if text.lower() in l.lower()]
        self._render_dialogue("\n\n".join(filtered) if filtered else "No matching dialogue found.")

    def set_note_transcript(self, title: str, transcript_text: str, tags: list = None, metadata_info: str = None):
        """Dynamically load and format a note's real transcript in the viewer with speaker colors and no timestamps."""
        self.current_title = title
        self.raw_transcript_text = transcript_text
        self.title_label.setText(f"Note: {title}")
        if metadata_info:
            self.sub_info.setText(metadata_info)
        if tags is not None:
            self.tags = [f"#{t.lstrip('#')}" for t in tags] if tags else ["#VoiceNote"]
            self.render_tags()

        self._render_dialogue(transcript_text)

    def _render_dialogue(self, text: str):
        if not text or not text.strip():
            self.transcript_edit.setHtml(
                "<p style='color: #7D8495; font-style: italic; font-size: 13px;'>No transcript text recorded for this note.</p>"
            )
            return

        # Distinct, accessible palette for speakers matching VoiceNote's retro cream aesthetic
        palette = [
            "#5E35B1",  # Speaker 1: Deep Indigo / Purple
            "#0D9488",  # Speaker 2: Vibrant Teal / Cyan
            "#D97706",  # Speaker 3: Warm Amber / Terracotta
            "#BE185D",  # Speaker 4: Vivid Berry / Crimson
            "#15803D",  # Speaker 5: Emerald Green
            "#1E40AF",  # Speaker 6: Steel Blue
            "#7C3AED",  # Speaker 7: Electric Violet
            "#B45309",  # Speaker 8: Russet Brown
        ]

        speaker_colors = {}
        formatted_html_blocks = []

        import re
        speaker_regex = re.compile(r"^(Speaker\s*\d+)\s*:\s*(.*)", re.IGNORECASE)

        # Split into blocks (separated by empty lines or newline breaks)
        raw_blocks = text.split("\n")
        current_speaker = None
        current_dialogue = []

        def flush_block():
            nonlocal current_speaker, current_dialogue
            if current_speaker and current_dialogue:
                content = " ".join(current_dialogue).strip()
                # Strip timestamps
                content = re.sub(r"\[\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*\]", "", content)
                content = re.sub(r"\(\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*\)", "", content).strip()
                if content:
                    color = speaker_colors[current_speaker]
                    formatted_html_blocks.append(
                        f"<div style='margin-bottom: 16px;'>"
                        f"<b style='color: {color}; font-size: 13.5px;'>{current_speaker}:</b> "
                        f"<span style='color: {color}; font-size: 13px; line-height: 1.7;'>{content}</span>"
                        f"</div>"
                    )
            current_dialogue = []

        for line in raw_blocks:
            line_str = line.strip()
            # Strip any stray timestamps from line
            line_str = re.sub(r"\[\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*\]", "", line_str)
            line_str = re.sub(r"\(\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*\)", "", line_str).strip()

            if not line_str:
                flush_block()
                current_speaker = None
                continue

            match = speaker_regex.match(line_str)
            if match:
                flush_block()
                raw_spk = match.group(1).title()
                spk = re.sub(r"Speaker\s*(\d+)", r"Speaker \1", raw_spk)
                if spk not in speaker_colors:
                    speaker_colors[spk] = palette[len(speaker_colors) % len(palette)]
                current_speaker = spk
                dialogue_text = match.group(2).strip()
                if dialogue_text:
                    current_dialogue.append(dialogue_text)
            else:
                if current_speaker:
                    current_dialogue.append(line_str)
                else:
                    # Generic line without speaker prefix
                    formatted_html_blocks.append(
                        f"<div style='margin-bottom: 14px; color: #1E2B4B; font-size: 13px; line-height: 1.6;'>"
                        f"{line_str}"
                        f"</div>"
                    )

        flush_block()

        html = f"<div style='padding: 6px; font-family: \"Noto Sans Devanagari\", \"Nirmala UI\", \"Segoe UI\", system-ui, sans-serif;'>{''.join(formatted_html_blocks)}</div>"
        self.transcript_edit.setHtml(html)

    def load_sample_transcript(self):
        self.transcript_edit.setHtml("<p style='color: #7D8495; font-style: italic; font-size: 13px;'>No voice note selected. Select a note from the Recent Notes feed or record audio to view the transcript.</p>")

