import sys
import unittest
from PySide6.QtWidgets import QApplication

from voicenote.core.diarization_engine import DiarizationEngine, SPEAKER_COLORS
from voicenote.ui.components.transcript_view_widget import TranscriptViewWidget


class TestDiarizationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.engine = DiarizationEngine(ai_engine=None)  # Test deterministic core logic

    def test_timestamp_stripping(self):
        """Verify all variants of timestamp tokens are cleanly removed."""
        raw = "[00:00] Good morning. [00:12.34] Quick update. (01:05) Launch plan. [0.0s -> 7.1s]: Final check."
        cleaned = self.engine.strip_timestamps(raw)
        self.assertNotIn("[00:00]", cleaned)
        self.assertNotIn("[00:12.34]", cleaned)
        self.assertNotIn("(01:05)", cleaned)
        self.assertNotIn("[0.0s -> 7.1s]", cleaned)
        self.assertEqual(cleaned, "Good morning. Quick update. Launch plan. Final check.")

    def test_merge_consecutive_speaker_segments(self):
        """Consecutive utterances from the same speaker must be merged into one paragraph."""
        dialogue = """Speaker 1: Good morning team.
Speaker 1: Quick update on NovaFlow. We are 82% complete.
Speaker 2: Backend development should finish by September 24th.
Speaker 2: I can reduce costs by ₹22,000.
Speaker 1: Perfect. Let's proceed."""

        turns = self.engine.parse_speaker_turns(dialogue)
        self.assertEqual(len(turns), 3)
        self.assertEqual(turns[0]["speaker"], "Speaker 1")
        self.assertEqual(turns[0]["text"], "Good morning team. Quick update on NovaFlow. We are 82% complete.")
        self.assertEqual(turns[1]["speaker"], "Speaker 2")
        self.assertEqual(turns[1]["text"], "Backend development should finish by September 24th. I can reduce costs by ₹22,000.")
        self.assertEqual(turns[2]["speaker"], "Speaker 1")
        self.assertEqual(turns[2]["text"], "Perfect. Let's proceed.")

    def test_consistent_speaker_colors(self):
        """The same speaker must always receive the exact same color throughout the session."""
        color_spk1_first = self.engine.get_color_for_speaker("Speaker 1")
        color_spk2 = self.engine.get_color_for_speaker("Speaker 2")
        color_spk1_second = self.engine.get_color_for_speaker("Speaker 1")

        self.assertEqual(color_spk1_first, color_spk1_second)
        self.assertNotEqual(color_spk1_first, color_spk2)
        self.assertEqual(color_spk1_first, SPEAKER_COLORS[0])
        self.assertEqual(color_spk2, SPEAKER_COLORS[1])

    def test_short_utterance_preservation(self):
        """Short acknowledgments like 'Got it.', 'Done.' must be preserved in turns."""
        dialogue = """Speaker 1: Rahul, complete the AI test by September 23rd.
Speaker 2: Got it.
Speaker 3: Done.
Speaker 1: Perfect. Let's proceed."""

        turns = self.engine.parse_speaker_turns(dialogue)
        self.assertEqual(len(turns), 4)
        self.assertEqual(turns[1]["speaker"], "Speaker 2")
        self.assertEqual(turns[1]["text"], "Got it.")
        self.assertEqual(turns[2]["speaker"], "Speaker 3")
        self.assertEqual(turns[2]["text"], "Done.")
        self.assertEqual(turns[3]["speaker"], "Speaker 1")
        self.assertEqual(turns[3]["text"], "Perfect. Let's proceed.")

    def test_heuristic_diarization_conversational_flow(self):
        """Heuristic fallback should separate questions, addresses, and short answers into Speaker 1, 2, 3."""
        raw = ("Good morning. Rahul, where are we technically? "
               "Backend development should finish by September 24th. "
               "From finance, our total budget is ₹18,50,000. "
               "Got it. Done. Perfect.")

        turns = self.engine._heuristic_diarize(raw)
        self.assertGreaterEqual(len(turns), 3)
        speakers = [t["speaker"] for t in turns]
        self.assertIn("Speaker 1", speakers)
        self.assertIn("Speaker 2", speakers)

    def test_transcript_view_widget_renders_speaker_colors_no_timestamps(self):
        """Verify TranscriptViewWidget renders HTML with colored speaker spans and zero timestamps."""
        widget = TranscriptViewWidget()
        text_with_ts = "[00:00] Speaker 1: Hello team.\n\n[00:15] Speaker 2: Hi there."
        widget.set_note_transcript("Test Meeting", text_with_ts)

        html = widget.transcript_edit.toHtml()
        self.assertNotIn("[00:00]", html)
        self.assertNotIn("[00:15]", html)
        self.assertIn("Speaker 1:", html)
        self.assertIn("Speaker 2:", html)
        html_lower = html.lower()
        self.assertIn(SPEAKER_COLORS[0].lower(), html_lower)  # Speaker 1 color (#5e35b1)
        self.assertIn(SPEAKER_COLORS[1].lower(), html_lower)  # Speaker 2 color (#0d9488)


if __name__ == "__main__":
    unittest.main()
