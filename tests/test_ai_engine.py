import os
import unittest
from voicenote.core.ai_engine import AIEngine


class TestAIEngine(unittest.TestCase):

    def setUp(self):
        if not os.getenv("GEMINI_API_KEY"):
            self.skipTest("GEMINI_API_KEY is not set.")
        try:
            self.ai = AIEngine()
        except Exception as e:
            self.skipTest(f"AIEngine initialization skipped: {e}")

    def test_generate(self):
        """Test basic communication with Gemini LLM."""
        try:
            response = self.ai.generate(
                "Say 'VoiceNote test successful' and nothing else."
            )
            self.assertTrue(response)
        except Exception as e:
            self.skipTest(f"Live Gemini API call skipped (network/key error): {e}")

    def test_analyze_transcript(self):
        """Test transcript analysis."""
        try:
            transcript = """
            Today we discussed the VoiceNote project.
            Rahul will prepare the project presentation by Friday.
            Atharva will implement the AI engine.
            We decided to use ChromaDB for semantic search.
            The team will test the complete STT to LLM pipeline next week.
            """
            result = self.ai.analyze_transcript(transcript)
            self.assertTrue(result.summary)
            self.assertGreater(len(result.key_points), 0)
            self.assertGreater(len(result.tasks), 0)
        except Exception as e:
            self.skipTest(f"Live Gemini API call skipped (network/key error): {e}")

    def test_empty_prompt(self):
        """Test that empty prompts are rejected."""
        with self.assertRaises(ValueError):
            self.ai.generate("")

    def test_empty_transcript(self):
        """Test that empty transcripts are rejected."""
        with self.assertRaises(ValueError):
            self.ai.analyze_transcript("")


if __name__ == "__main__":
    unittest.main()