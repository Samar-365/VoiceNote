import re
import datetime
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("AnalyticsEngine")


class AnalyticsEngine:
    """Core computational engine for calculating VoiceNote usage metrics,

    trends, AI performance statistics, and task completion insights.
    """

    def __init__(self, db=None):
        self.db = db

    def _get_db(self):
        if self.db:
            return self.db
        try:
            from voicenote.db.database import get_db
            return get_db()
        except Exception as e:
            logger.warning(f"Could not connect to database: {e}")
            return None

    @staticmethod
    def parse_duration_to_seconds(duration_str: Any) -> float:
        """Parse various duration string formats into seconds.

        Supported formats:
        - "04m 32s" -> 272
        - "14h 25m" -> 51900
        - "01:23:45" -> 5025
        - "04:32" -> 272
        - "45s" -> 45
        - 120 (int/float) -> 120.0
        """
        if duration_str is None:
            return 0.0
        if isinstance(duration_str, (int, float)):
            return float(duration_str)

        text = str(duration_str).strip().lower()
        if not text or text == "00:00":
            return 0.0

        # Pattern: 1h 20m 30s or 4m 32s
        hours = 0.0
        minutes = 0.0
        seconds = 0.0

        h_match = re.search(r"(\d+(?:\.\d+)?)\s*h", text)
        m_match = re.search(r"(\d+(?:\.\d+)?)\s*m", text)
        s_match = re.search(r"(\d+(?:\.\d+)?)\s*s", text)

        if h_match or m_match or s_match:
            if h_match:
                hours = float(h_match.group(1))
            if m_match:
                minutes = float(m_match.group(1))
            if s_match:
                seconds = float(s_match.group(1))
            return hours * 3600 + minutes * 60 + seconds

        # Pattern: HH:MM:SS or MM:SS
        parts = text.split(":")
        try:
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 1:
                return float(parts[0])
        except ValueError:
            pass

        return 0.0

    @staticmethod
    def format_seconds_to_human(seconds: float) -> str:
        """Format seconds into human readable duration string (e.g. '14h 25m', '4m 32s', or '45s')."""
        sec = int(round(seconds))
        if sec <= 0:
            return "0m 00s"

        hrs = sec // 3600
        mins = (sec % 3600) // 60
        rem_sec = sec % 60

        if hrs > 0:
            return f"{hrs}h {mins:02d}m"
        elif mins > 0:
            return f"{mins:02d}m {rem_sec:02d}s"
        else:
            return f"{rem_sec}s"

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Compute and aggregate all primary metrics for the Analytics Dashboard."""
        db = self._get_db()
        notes = []
        tasks = []
        summaries = []

        if db:
            try:
                notes = db.get_all_notes() or []
                tasks = db.get_all_tasks() or []
                for n in notes:
                    n_id = n.get("id")
                    if n_id:
                        s = db.get_ai_summary(n_id)
                        if s:
                            summaries.append(s)
            except Exception as e:
                logger.error(f"Error fetching analytics data from DB: {e}")

        return self.compute_analytics(notes=notes, tasks=tasks, summaries=summaries)

    def compute_analytics(
        self,
        notes: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        summaries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Compute metrics given raw lists of notes, tasks, and summaries."""
        summaries = summaries or []

        # 1. Note & Duration Metrics
        total_notes = len(notes)
        total_seconds = sum(self.parse_duration_to_seconds(n.get("duration")) for n in notes)
        formatted_total_duration = self.format_seconds_to_human(total_seconds)

        avg_seconds = (total_seconds / total_notes) if total_notes > 0 else 0.0
        formatted_avg_duration = self.format_seconds_to_human(avg_seconds)

        # 2. Task Completion Metrics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if str(t.get("status", "")).lower() == "completed")
        pending_tasks = total_tasks - completed_tasks
        
        completion_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0
        completion_rate_str = f"{int(round(completion_rate))}%"

        # 3. AI Time Saved Calculation
        # Estimated: Human manual transcription + note organization takes ~4x the audio length.
        # Whisper + Gemini takes seconds. Estimated savings = ~3.5x recording time + 5m per note.
        time_saved_hours = (total_seconds * 3.5 + total_notes * 300) / 3600.0
        if time_saved_hours >= 1.0:
            time_saved_str = f"~{time_saved_hours:.1f} hrs"
        else:
            time_saved_mins = int(time_saved_hours * 60)
            time_saved_str = f"~{time_saved_mins} mins"

        # 4. Weekly Activity Breakdown (Mon - Sun)
        weekly_activity = self._compute_weekly_activity(notes)

        # 5. Top Tags Breakdown
        top_tags = self._compute_top_tags(notes, summaries)

        # 6. Sentiment Distribution
        sentiment_dist = self._compute_sentiment_distribution(summaries)

        # 7. Task Priority Breakdown
        priority_dist = {"High": 0, "Medium": 0, "Low": 0}
        for t in tasks:
            p = str(t.get("priority", "Medium")).capitalize()
            if p in priority_dist:
                priority_dist[p] += 1
            else:
                priority_dist["Medium"] += 1

        # 8. Category Breakdown
        category_dist: Dict[str, int] = {}
        for n in notes:
            cat = str(n.get("category", "General")).strip() or "General"
            category_dist[cat] = category_dist.get(cat, 0) + 1

        return {
            "total_notes": total_notes,
            "total_recording_seconds": total_seconds,
            "formatted_total_duration": formatted_total_duration,
            "avg_duration": formatted_avg_duration,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "task_completion_rate": completion_rate,
            "task_completion_rate_str": completion_rate_str,
            "time_saved_hours": time_saved_hours,
            "time_saved_str": time_saved_str,
            "weekly_activity": weekly_activity,
            "top_tags": top_tags,
            "sentiment_distribution": sentiment_dist,
            "priority_distribution": priority_dist,
            "category_distribution": category_dist,
        }

    def _compute_weekly_activity(self, notes: List[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
        """Group recording duration in minutes by day of week (Mon-Sun).

        Returns list of tuples: [("Mon", minutes, max_scale), ("Tue", ...), ...]
        """
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_minutes = {name: 0.0 for name in day_names}

        for n in notes:
            dur_sec = self.parse_duration_to_seconds(n.get("duration"))
            dur_min = dur_sec / 60.0

            created = str(n.get("created_at", "")).strip()
            matched_day = None

            # Check if day name is directly in timestamp string (e.g. 'Monday', 'Mon')
            for idx, d_name in enumerate(day_names):
                full_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                if d_name.lower() in created.lower() or full_names[idx] in created.lower():
                    matched_day = d_name
                    break

            if not matched_day:
                if "today" in created.lower():
                    today_idx = datetime.datetime.now().weekday()
                    matched_day = day_names[today_idx]
                elif "yesterday" in created.lower():
                    yesterday_idx = (datetime.datetime.now().weekday() - 1) % 7
                    matched_day = day_names[yesterday_idx]
                else:
                    # Attempt standard date parsing
                    try:
                        # Try parsing ISO or common format
                        dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
                        matched_day = day_names[dt.weekday()]
                    except Exception:
                        # Default distribute or place on today
                        today_idx = datetime.datetime.now().weekday()
                        matched_day = day_names[today_idx]

            day_minutes[matched_day] += dur_min

        # Determine scaling maximum for progress bars
        max_recorded = max(day_minutes.values()) if day_minutes else 0.0
        max_scale = max(60, int(round(max_recorded * 1.25)))

        result = []
        for name in day_names:
            val_m = int(round(day_minutes[name]))
            result.append((name, val_m, max_scale))

        return result

    def _compute_top_tags(
        self, notes: List[Dict[str, Any]], summaries: List[Dict[str, Any]]
    ) -> List[Tuple[str, int]]:
        """Extract and count topic tags across notes and summaries."""
        tag_counts: Dict[str, int] = {}

        def process_tags(items):
            if not items:
                return
            if isinstance(items, str):
                # May be JSON string or comma-separated
                if items.startswith("[") and items.endswith("]"):
                    try:
                        import json
                        items = json.loads(items)
                    except Exception:
                        items = [t.strip() for t in items.replace("[", "").replace("]", "").replace('"', "").split(",")]
                else:
                    items = [t.strip() for t in items.split(",") if t.strip()]

            if isinstance(items, list):
                for t in items:
                    tag_str = str(t).strip()
                    if not tag_str:
                        continue
                    if not tag_str.startswith("#"):
                        tag_str = f"#{tag_str}"
                    # Normalize formatting
                    tag_str = tag_str.replace(" ", "-")
                    tag_counts[tag_str] = tag_counts.get(tag_str, 0) + 1

        for n in notes:
            process_tags(n.get("main_topics"))
            process_tags(n.get("tags"))

        for s in summaries:
            process_tags(s.get("main_topics"))

        # Sort tags by frequency descending
        sorted_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
        if not sorted_tags:
            # Fallback default topic breakdown if none exist
            return [
                ("#VoiceNote", len(notes)),
                ("#Architecture", max(1, len(notes) // 3)),
                ("#Sprint-Planning", max(1, len(notes) // 4)),
                ("#AI-Summary", max(1, len(notes) // 5)),
            ]
        return sorted_tags[:8]

    def _compute_sentiment_distribution(self, summaries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate sentiment distribution from AI summaries."""
        counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for s in summaries:
            sent = str(s.get("sentiment", "Neutral")).capitalize().strip()
            if sent in counts:
                counts[sent] += 1
            else:
                counts["Neutral"] += 1
        return counts
