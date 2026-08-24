"""
Unit tests for VoiceNote Export Engine (PDF, Word DOCX, and TXT).
"""

import os
import unittest
import tempfile
from pathlib import Path

from voicenote.core.export_engine import ExportEngine
from voicenote.db.models import Note, Transcript, AISummary, Task


class TestExportEngine(unittest.TestCase):
    """Test suite for ExportEngine functionality."""

    def setUp(self):
        self.engine = ExportEngine()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.sample_note = {
            "title": "VoiceNote Architecture & AI Sync",
            "created_at": "2026-08-24 18:30:00",
            "duration": "06m 45s",
            "category": "Engineering",
            "tags": ["#Architecture", "#PySide6", "#ExportEngine"],
            "summary": "Reviewed desktop UI responsiveness, local STT models, and document export pipeline.",
            "key_points": [
                "100% local speech-to-text with faster-whisper.",
                "Styled PDF generation via ReportLab.",
                "Custom Word DOCX generation via python-docx.",
            ],
            "tasks": [
                {"title": "Implement PDF Export Engine", "priority": "High", "assignee": "Samar", "due_date": "Today", "status": "Completed"},
                {"title": "Implement DOCX Word Generator", "priority": "High", "assignee": "Samar", "due_date": "Today", "status": "Completed"},
                {"title": "Verify comprehensive test suite", "priority": "Medium", "assignee": "Dev Team", "due_date": "Sprint End", "status": "Pending"},
            ],
            "transcript": (
                "[00:00:00] Tejas: Let's begin the architecture review.\n"
                "[00:00:15] Samar: The export engine supports PDF, DOCX, and TXT.\n"
                "[00:01:00] Atharv: AI summary and tasks will automatically populate in the exported document."
            ),
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_pdf_generation(self):
        """Test PDF generation produces a valid, non-empty PDF file."""
        out_file = str(self.temp_path / "test_note.pdf")
        result_path = self.engine.export("pdf", self.sample_note, output_path=out_file)

        self.assertTrue(os.path.exists(result_path))
        self.assertGreater(os.path.getsize(result_path), 500)

        # Check PDF file signature
        with open(result_path, "rb") as f:
            header = f.read(5)
            self.assertEqual(header, b"%PDF-")

    def test_export_docx_generation(self):
        """Test DOCX generation produces a valid Word document."""
        out_file = str(self.temp_path / "test_note.docx")
        result_path = self.engine.export("docx", self.sample_note, output_path=out_file)

        self.assertTrue(os.path.exists(result_path))
        self.assertGreater(os.path.getsize(result_path), 500)

        # Verify python-docx can open and read the file
        import docx
        doc = docx.Document(result_path)
        doc_text = " ".join(p.text for p in doc.paragraphs)
        self.assertIn("VOICENOTE AI", doc_text)
        self.assertIn("VoiceNote Architecture & AI Sync", doc_text)

    def test_export_txt_generation(self):
        """Test Plain Text generation produces readable formatted text."""
        out_file = str(self.temp_path / "test_note.txt")
        result_path = self.engine.export("txt", self.sample_note, output_path=out_file)

        self.assertTrue(os.path.exists(result_path))
        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("VOICENOTE ARCHITECTURE & AI SYNC", content)
        self.assertIn("[ METADATA ]", content)
        self.assertIn("[ AI EXECUTIVE SUMMARY ]", content)
        self.assertIn("[ EXTRACTED ACTION ITEMS & TASKS ]", content)
        self.assertIn("[ COMPLETE AUDIO TRANSCRIPT ]", content)
        self.assertIn("Implement PDF Export Engine", content)
        self.assertIn("[X]", content)  # Completed task
        self.assertIn("[ ]", content)  # Pending task

    def test_section_filtering_options(self):
        """Test options to exclude specific sections (summary, tasks, transcript)."""
        out_file = str(self.temp_path / "filtered_note.txt")
        options = {
            "include_summary": False,
            "include_tasks": False,
            "include_transcript": True,
            "include_metadata": True,
        }
        result_path = self.engine.export("txt", self.sample_note, output_path=out_file, options=options)

        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertNotIn("[ AI EXECUTIVE SUMMARY ]", content)
        self.assertNotIn("[ EXTRACTED ACTION ITEMS & TASKS ]", content)
        self.assertIn("[ COMPLETE AUDIO TRANSCRIPT ]", content)
        self.assertIn("[ METADATA ]", content)

    def test_dataclass_models_input(self):
        """Test exporting when input is structured with domain model objects."""
        note = Note(
            id=1,
            title="Dataclass Note Test",
            duration="02m 10s",
            category="Models",
        )
        out_file = str(self.temp_path / "dataclass_test.pdf")
        result = self.engine.export("pdf", note, output_path=out_file)
        self.assertTrue(os.path.exists(result))

    def test_unsupported_format_raises_error(self):
        """Test that requesting an unknown format raises a ValueError."""
        with self.assertRaises(ValueError):
            self.engine.export("unsupported_xyz", self.sample_note)

    def test_unicode_and_special_characters(self):
        """Test document export with multi-lingual and unicode strings."""
        unicode_note = {
            "title": "Marathi & Hindi Notes — मराठी आणि हिंदी नोट",
            "created_at": "2026-08-24 19:00:00",
            "duration": "03m 15s",
            "tags": ["#MultiLingual", "#Unicode"],
            "summary": "VoiceNote handles diverse multi-lingual transcriptions accurately.",
            "tasks": [
                {"title": "Verify unicode serialization & display", "priority": "High", "assignee": "Samar", "status": "Completed"}
            ],
            "transcript": "[00:00:05] Speaker: VoiceNote supports smart note exports seamlessly."
        }
        out_file = str(self.temp_path / "unicode_test.docx")
        result = self.engine.export("docx", unicode_note, output_path=out_file)
        self.assertTrue(os.path.exists(result))


if __name__ == "__main__":
    unittest.main()
