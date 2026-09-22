"""
VoiceNote Analytics Computational Engine.
Calculates 100% real, data-driven intelligence across stored conversations,
transcripts, tasks, and AI summaries with support for:
- 7, 30, and 90-day time filtering
- Speaker activity percentage distribution
- Conversation themes and topics frequency
- Action items breakdown (Completed, In Progress, Blocked, Overdue)
- Captured decisions and open questions
- ZERO fake or hardcoded values
"""

import re
from datetime import datetime, date, timedelta
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("AnalyticsEngine")


class AnalyticsEngine:
    """Core computational engine for calculating VoiceNote usage metrics,
    trends, speaker distributions, and task completion insights from real data.
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
        """Parse various duration string formats into seconds."""
        if duration_str is None:
            return 0.0
        if isinstance(duration_str, (int, float)):
            return float(duration_str)

        text = str(duration_str).strip().lower()
        if not text or text == "00:00":
            return 0.0

        h_match = re.search(r"(\d+(?:\.\d+)?)\s*h", text)
        m_match = re.search(r"(\d+(?:\.\d+)?)\s*m", text)
        s_match = re.search(r"(\d+(?:\.\d+)?)\s*s", text)

        if h_match or m_match or s_match:
            hours = float(h_match.group(1)) if h_match else 0.0
            minutes = float(m_match.group(1)) if m_match else 0.0
            seconds = float(s_match.group(1)) if s_match else 0.0
            return hours * 3600 + minutes * 60 + seconds

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
        """Format seconds into human readable duration string."""
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

    @staticmethod
    def parse_date(date_str: Any) -> Optional[datetime]:
        """Try parsing various date formats from database records."""
        if not date_str:
            return None
        text = str(date_str).strip()
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%d/%m/%Y",
            "%m/%d/%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(text[:19], fmt)
            except Exception:
                pass
        return None

    def get_dashboard_analytics(self, days_filter: Optional[int] = 30) -> Dict[str, Any]:
        """Fetch real data from database and compute metrics for the chosen time range."""
        db = self._get_db()
        notes = []
        tasks = []
        summaries = []
        transcripts = []

        if db:
            try:
                all_notes = db.get_all_notes() or []
                all_tasks = db.get_all_tasks() or []
                
                # Apply date filter if specified
                cutoff = None
                if days_filter:
                    cutoff = datetime.now() - timedelta(days=days_filter)

                valid_note_ids = set()
                for n in all_notes:
                    d = self.parse_date(n.get("created_at"))
                    if cutoff and d and d < cutoff:
                        continue
                    notes.append(n)
                    n_id = n.get("id")
                    if n_id:
                        valid_note_ids.add(n_id)

                for t in all_tasks:
                    # Only include tasks belonging to filtered notes (or all if note_id is unassigned)
                    if not valid_note_ids or t.get("note_id") in valid_note_ids:
                        tasks.append(t)

                for n_id in valid_note_ids:
                    s = db.get_ai_summary(n_id)
                    if s:
                        s["note_title"] = next((n["title"] for n in notes if n["id"] == n_id), "Voice Note")
                        s["note_date"] = next((n["created_at"] for n in notes if n["id"] == n_id), "")
                        summaries.append(s)
                    tr = db.get_transcript(n_id)
                    if tr:
                        transcripts.append(tr)

            except Exception as e:
                logger.error(f"Error fetching analytics data from DB: {e}")

        return self.compute_analytics(notes=notes, tasks=tasks, summaries=summaries, transcripts=transcripts, days_filter=days_filter)

    def compute_analytics(
        self,
        notes: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        summaries: Optional[List[Dict[str, Any]]] = None,
        transcripts: Optional[List[Dict[str, Any]]] = None,
        days_filter: Optional[int] = 30
    ) -> Dict[str, Any]:
        """Compute 100% data-driven metrics from active records."""
        summaries = summaries or []
        transcripts = transcripts or []

        # 1. Core Overview
        total_notes = len(notes)
        total_seconds = sum(self.parse_duration_to_seconds(n.get("duration")) for n in notes)
        formatted_total_duration = self.format_seconds_to_human(total_seconds)

        avg_seconds = (total_seconds / total_notes) if total_notes > 0 else 0.0
        formatted_avg_duration = self.format_seconds_to_human(avg_seconds)

        # Total Words
        total_words = 0
        speaker_word_counts: Dict[str, int] = {}
        for tr in transcripts:
            txt = tr.get("cleaned_text") or tr.get("raw_text") or ""
            words = txt.split()
            total_words += len(words)

            # Speaker diarization breakdown
            cur_spk = "Speaker 1"
            for line in txt.split("\n"):
                line_str = line.strip()
                if not line_str:
                    continue
                if ":" in line_str and "speaker" in line_str.lower()[:15]:
                    parts = line_str.split(":", 1)
                    cur_spk = parts[0].strip()
                    line_words = len(parts[1].split()) if len(parts) > 1 else 0
                else:
                    line_words = len(line_str.split())
                speaker_word_counts[cur_spk] = speaker_word_counts.get(cur_spk, 0) + line_words

        total_speakers = max(1, len(speaker_word_counts)) if total_notes > 0 else 0

        # Speaker Percentage Distribution
        speaker_distribution: List[Tuple[str, float, int]] = []
        if total_words > 0:
            for spk, cnt in sorted(speaker_word_counts.items()):
                pct = round((cnt / total_words) * 100.0, 1)
                speaker_distribution.append((spk, pct, cnt))

        # Words per minute
        wpm = int(round(total_words / (total_seconds / 60.0))) if total_seconds > 0 else 0

        # 2. Action Items & Productivity Overview
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if str(t.get("status", "")).lower() == "completed")
        in_progress_tasks = sum(1 for t in tasks if str(t.get("status", "")).lower() == "in progress")
        blocked_tasks = sum(1 for t in tasks if str(t.get("status", "")).lower() == "blocked")
        pending_tasks = total_tasks - completed_tasks

        # Overdue tasks
        today_val = date.today()
        overdue_tasks = 0
        for t in tasks:
            if str(t.get("status", "")).lower() != "completed":
                due = t.get("due_date", "")
                if due and due.upper() != "TBD":
                    try:
                        d = datetime.strptime(due[:10], "%Y-%m-%d").date()
                        if d < today_val:
                            overdue_tasks += 1
                    except Exception:
                        pass

        completion_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0
        completion_rate_str = f"{int(round(completion_rate))}%"
        actions_per_meeting = round(total_tasks / total_notes, 1) if total_notes > 0 else 0.0

        # 3. Decisions & Questions Extracted
        decisions_captured: List[Dict[str, str]] = []
        open_questions: List[Dict[str, str]] = []

        for s in summaries:
            s_decs = s.get("decisions", [])
            note_title = s.get("note_title", "Meeting")
            note_date = s.get("note_date", "")
            if isinstance(s_decs, list):
                for d in s_decs:
                    if d and str(d).strip():
                        decisions_captured.append({
                            "decision": str(d).strip(),
                            "meeting": note_title,
                            "date": note_date
                        })
            
            s_qs = s.get("open_questions", [])
            if isinstance(s_qs, list):
                for q in s_qs:
                    if q and str(q).strip():
                        open_questions.append({
                            "question": str(q).strip(),
                            "meeting": note_title
                        })

        # 4. Conversation Themes (Most Discussed Topics & Counts)
        theme_counts: Dict[str, int] = {}
        for n in notes:
            cat = str(n.get("category", "")).strip()
            if cat and cat.lower() != "general":
                theme_counts[cat] = theme_counts.get(cat, 0) + 1
        
        for s in summaries:
            topics = s.get("main_topics", [])
            if isinstance(topics, list):
                for t in topics:
                    clean_t = str(t).replace("#", "").strip()
                    if clean_t and clean_t.lower() not in ("voicenote", "general"):
                        theme_counts[clean_t] = theme_counts.get(clean_t, 0) + 1

        conversation_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Top tags (combined notes and summaries for backward compatibility)
        tag_counts: Dict[str, int] = {}
        for n in notes:
            for t in (n.get("main_topics") or []):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        for s in summaries:
            for t in (s.get("main_topics") or []):
                tag_counts[t] = tag_counts.get(t, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        if not top_tags:
            top_tags = [("#General", 0)]

        # Sentiment distribution
        sentiment_distribution = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for s in summaries:
            sent = str(s.get("sentiment", "Neutral")).capitalize()
            if sent in sentiment_distribution:
                sentiment_distribution[sent] += 1
            else:
                sentiment_distribution["Neutral"] += 1

        # Priority distribution
        priority_distribution = {"High": 0, "Medium": 0, "Low": 0}
        for t in tasks:
            p = str(t.get("priority", "Medium")).capitalize()
            if p in priority_distribution:
                priority_distribution[p] += 1
            else:
                priority_distribution["Medium"] += 1

        # 5. Weekly Recording Activity (Monday - Sunday)
        weekly_activity = self._compute_weekly_activity(notes)

        # Most active day
        most_active_day = "None"
        if weekly_activity:
            sorted_by_dur = sorted(weekly_activity, key=lambda x: x[1], reverse=True)
            if sorted_by_dur[0][1] > 0:
                most_active_day = sorted_by_dur[0][0]

        return {
            "has_data": total_notes > 0,
            "days_filter": days_filter,
            "total_notes": total_notes,
            "total_recording_seconds": total_seconds,
            "formatted_total_duration": formatted_total_duration,
            "avg_duration": formatted_avg_duration,
            "total_words": total_words,
            "total_speakers": total_speakers,
            "speaker_distribution": speaker_distribution,
            "words_per_minute": wpm,
            "actions_per_meeting": actions_per_meeting,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "overdue_tasks": overdue_tasks,
            "pending_tasks": pending_tasks,
            "task_completion_rate": completion_rate,
            "task_completion_rate_str": completion_rate_str,
            "decisions_captured": decisions_captured,
            "decisions_count": len(decisions_captured),
            "open_questions": open_questions,
            "questions_count": len(open_questions),
            "conversation_themes": conversation_themes,
            "top_tags": top_tags,
            "sentiment_distribution": sentiment_distribution,
            "priority_distribution": priority_distribution,
            "weekly_activity": weekly_activity,
            "most_active_day": most_active_day
        }

    def _compute_weekly_activity(self, notes: List[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
        """Group recording duration in minutes by day of week (Mon-Sun) from actual timestamps."""
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_minutes = {name: 0.0 for name in day_names}

        for n in notes:
            dur_sec = self.parse_duration_to_seconds(n.get("duration"))
            dur_min = dur_sec / 60.0

            created_str = str(n.get("created_at", "")).strip()
            d = self.parse_date(created_str)
            if d:
                day_name = day_names[d.weekday()]
                day_minutes[day_name] += dur_min
            else:
                for idx, name in enumerate(day_names):
                    if name.lower() in created_str.lower():
                        day_minutes[name] += dur_min
                        break

        max_recorded = max(day_minutes.values()) if day_minutes else 0.0
        max_scale = max(30, int(round(max_recorded * 1.25))) if max_recorded > 0 else 30

        result = []
        for name in day_names:
            val_m = int(round(day_minutes[name]))
            result.append((name, val_m, max_scale))

        return result
