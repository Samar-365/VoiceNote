import unittest
from voicenote.core.analytics_engine import AnalyticsEngine


class TestAnalyticsEngine(unittest.TestCase):
    """Unit tests for the AnalyticsEngine metrics computation layer."""

    def setUp(self):
        self.engine = AnalyticsEngine(db=None)

    def test_duration_parsing(self):
        """Test parsing of different duration string formats to seconds."""
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("04m 32s"), 272.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("14h 25m"), 51900.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("1h 10m 20s"), 4220.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("01:23:45"), 5025.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("04:32"), 272.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("45s"), 45.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds(120), 120.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds("00:00"), 0.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds(None), 0.0)
        self.assertEqual(AnalyticsEngine.parse_duration_to_seconds(""), 0.0)

    def test_duration_formatting(self):
        """Test converting seconds into human-readable strings."""
        self.assertEqual(AnalyticsEngine.format_seconds_to_human(51900), "14h 25m")
        self.assertEqual(AnalyticsEngine.format_seconds_to_human(272), "04m 32s")
        self.assertEqual(AnalyticsEngine.format_seconds_to_human(45), "45s")
        self.assertEqual(AnalyticsEngine.format_seconds_to_human(0), "0m 00s")

    def test_compute_analytics_with_data(self):
        """Test computation of full analytics payload from mock records."""
        mock_notes = [
            {"id": 1, "title": "Meeting 1", "duration": "10m 00s", "created_at": "Monday, 10:00 AM", "category": "Meetings", "main_topics": ["#Sprint-Planning", "#Architecture"]},
            {"id": 2, "title": "Meeting 2", "duration": "20m 00s", "created_at": "Tuesday, 02:00 PM", "category": "Development", "main_topics": ["#Architecture", "#Backend"]},
            {"id": 3, "title": "Meeting 3", "duration": "30m 00s", "created_at": "Wednesday, 04:00 PM", "category": "Meetings", "main_topics": ["#Sprint-Planning", "#Testing"]},
        ]
        mock_tasks = [
            {"id": 1, "note_id": 1, "title": "Task 1", "priority": "High", "status": "Completed"},
            {"id": 2, "note_id": 1, "title": "Task 2", "priority": "Medium", "status": "Completed"},
            {"id": 3, "note_id": 2, "title": "Task 3", "priority": "High", "status": "Pending"},
            {"id": 4, "note_id": 3, "title": "Task 4", "priority": "Low", "status": "Pending"},
        ]
        mock_summaries = [
            {"id": 1, "note_id": 1, "sentiment": "Positive", "main_topics": ["#Sprint-Planning"]},
            {"id": 2, "note_id": 2, "sentiment": "Neutral", "main_topics": ["#Backend"]},
            {"id": 3, "note_id": 3, "sentiment": "Positive", "main_topics": ["#Testing"]},
        ]

        result = self.engine.compute_analytics(notes=mock_notes, tasks=mock_tasks, summaries=mock_summaries)

        # 1. Notes & Durations
        self.assertEqual(result["total_notes"], 3)
        self.assertEqual(result["total_recording_seconds"], 3600.0) # 60 minutes
        self.assertEqual(result["formatted_total_duration"], "1h 00m")
        self.assertEqual(result["avg_duration"], "20m 00s")

        # 2. Tasks
        self.assertEqual(result["total_tasks"], 4)
        self.assertEqual(result["completed_tasks"], 2)
        self.assertEqual(result["pending_tasks"], 2)
        self.assertEqual(result["task_completion_rate"], 50.0)
        self.assertEqual(result["task_completion_rate_str"], "50%")

        # 3. Weekly activity (Mon to Sun: 7 entries)
        self.assertEqual(len(result["weekly_activity"]), 7)
        # Check Monday (10m), Tuesday (20m), Wednesday (30m)
        act_dict = {day: mins for day, mins, _ in result["weekly_activity"]}
        self.assertEqual(act_dict["Mon"], 10)
        self.assertEqual(act_dict["Tue"], 20)
        self.assertEqual(act_dict["Wed"], 30)

        # 4. Top tags
        top_tags_dict = dict(result["top_tags"])
        self.assertIn("#Sprint-Planning", top_tags_dict)
        self.assertIn("#Architecture", top_tags_dict)
        self.assertEqual(top_tags_dict["#Sprint-Planning"], 3) # note1, note3, summary1
        self.assertEqual(top_tags_dict["#Architecture"], 2) # note1, note2

        # 5. Sentiments
        self.assertEqual(result["sentiment_distribution"]["Positive"], 2)
        self.assertEqual(result["sentiment_distribution"]["Neutral"], 1)

        # 6. Task Priorities
        self.assertEqual(result["priority_distribution"]["High"], 2)
        self.assertEqual(result["priority_distribution"]["Medium"], 1)
        self.assertEqual(result["priority_distribution"]["Low"], 1)

    def test_compute_analytics_empty_data(self):
        """Test analytics calculation on empty database without division by zero errors."""
        result = self.engine.compute_analytics(notes=[], tasks=[], summaries=[])

        self.assertEqual(result["total_notes"], 0)
        self.assertEqual(result["total_recording_seconds"], 0.0)
        self.assertEqual(result["formatted_total_duration"], "0m 00s")
        self.assertEqual(result["avg_duration"], "0m 00s")
        self.assertEqual(result["total_tasks"], 0)
        self.assertEqual(result["completed_tasks"], 0)
        self.assertEqual(result["pending_tasks"], 0)
        self.assertEqual(result["task_completion_rate"], 0.0)
        self.assertEqual(result["task_completion_rate_str"], "0%")
        self.assertEqual(len(result["weekly_activity"]), 7)
        self.assertTrue(len(result["top_tags"]) > 0)


if __name__ == "__main__":
    unittest.main()
