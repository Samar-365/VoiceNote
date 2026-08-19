import json
import logging
from typing import List, Optional, Dict, Any

import psycopg2
import psycopg2.extras

from voicenote.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
)
from voicenote.db.models import Note, Transcript, AISummary, Task

logger = logging.getLogger("DatabaseManager")


class DatabaseManager:
    """Thread-safe PostgreSQL database manager for VoiceNote."""

    def __init__(self):
        self.init_db()

    def get_connection(self):
        return psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    def init_db(self):
        """Create PostgreSQL tables if they do not exist."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        created_at VARCHAR(100) NOT NULL,
                        duration VARCHAR(50) DEFAULT '00:00',
                        audio_path TEXT,
                        category VARCHAR(100) DEFAULT 'General'
                    );

                    CREATE TABLE IF NOT EXISTS transcripts (
                        id SERIAL PRIMARY KEY,
                        note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
                        raw_text TEXT NOT NULL,
                        cleaned_text TEXT,
                        language VARCHAR(20) DEFAULT 'en'
                    );

                    CREATE TABLE IF NOT EXISTS ai_summaries (
                        id SERIAL PRIMARY KEY,
                        note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
                        summary TEXT NOT NULL,
                        key_points TEXT,
                        sentiment VARCHAR(50) DEFAULT 'Neutral',
                        main_topics TEXT
                    );

                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        priority VARCHAR(50) DEFAULT 'Medium',
                        assignee VARCHAR(100) DEFAULT 'Unassigned',
                        due_date VARCHAR(100) DEFAULT 'TBD',
                        status VARCHAR(50) DEFAULT 'Pending'
                    );
                """)
            conn.commit()

        if self.get_note_count() == 0:
            self._seed_sample_data()

    def get_note_count(self) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM notes;")
                res = cursor.fetchone()
                return res["count"]

    def _seed_sample_data(self):
        """Seed initial sample voice notes into PostgreSQL."""
        samples = [
            (
                Note(title="Sprint Planning & Local AI Architecture", duration="04m 32s", category="Architecture"),
                Transcript(raw_text="Discussed PySide6 UI responsiveness, QThread background processing for Whisper STT, and ChromaDB vector store integration.", cleaned_text="Discussed PySide6 UI responsiveness, QThread background processing for Whisper STT, and ChromaDB vector store integration."),
                AISummary(summary="Team aligned on desktop architecture using PySide6 and background threading for STT and Gemini LLM pipeline.", key_points=["PySide6 UI theme setup", "QThread background processing", "Gemini API integration"], sentiment="Positive", main_topics=["PySide6", "Whisper", "Gemini AI"]),
                [Task(title="Build QThread worker pool for STT pipeline", priority="High", assignee="Tejas", due_date="Tomorrow", status="Pending")]
            ),
            (
                Note(title="PostgreSQL Persistence Review", duration="12m 40s", category="Database"),
                Transcript(raw_text="Reviewed user profiles, transcript relational tables, tag associations, and PostgreSQL database model migrations.", cleaned_text="Reviewed user profiles, transcript relational tables, tag associations, and PostgreSQL database model migrations."),
                AISummary(summary="Finalized PostgreSQL storage schema and relational note-to-task relationships.", key_points=["Database schema approved", "Cascading deletes on notes", "JSON serialization for lists"], sentiment="Neutral", main_topics=["Database", "PostgreSQL", "Models"]),
                [Task(title="Implement PostgreSQL CRUD operations", priority="Medium", assignee="Tejas", due_date="Aug 20", status="Completed")]
            ),
            (
                Note(title="Task Extraction & AI Prompt Formatting", duration="08m 15s", category="AI Intelligence"),
                Transcript(raw_text="Defined JSON structured outputs for Ollama and Gemini task extraction, priority categorization, and assignee mapping.", cleaned_text="Defined JSON structured outputs for Ollama and Gemini task extraction, priority categorization, and assignee mapping."),
                AISummary(summary="Established Pydantic output schemas for Gemini AI task extraction.", key_points=["Structured JSON output format", "Task priority mapping", "Sentiment analysis tagging"], sentiment="Positive", main_topics=["Gemini API", "Task Extraction", "Pydantic"]),
                [Task(title="Verify Pydantic models with Gemini API outputs", priority="High", assignee="Atharv", due_date="Today", status="Completed")]
            )
        ]

        for note, transcript, summary, tasks in samples:
            note_id = self.add_note(note)
            transcript.note_id = note_id
            self.save_transcript(transcript)
            summary.note_id = note_id
            self.save_ai_summary(summary)
            for t in tasks:
                t.note_id = note_id
                self.save_task(t)

    def add_note(self, note: Note) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO notes (title, created_at, duration, audio_path, category) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (note.title, note.created_at, note.duration, note.audio_path, note.category)
                )
                new_id = cursor.fetchone()["id"]
            conn.commit()
            return new_id

    def get_all_notes(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT n.*, 
                           s.summary, s.key_points, s.sentiment, s.main_topics
                    FROM notes n
                    LEFT JOIN ai_summaries s ON n.id = s.note_id
                    ORDER BY n.id DESC;
                """)
                rows = cursor.fetchall()
                result = []
                for r in rows:
                    row_dict = dict(r)
                    if row_dict.get("key_points"):
                        try:
                            row_dict["key_points"] = json.loads(row_dict["key_points"])
                        except Exception:
                            row_dict["key_points"] = []
                    if row_dict.get("main_topics"):
                        try:
                            row_dict["main_topics"] = json.loads(row_dict["main_topics"])
                        except Exception:
                            row_dict["main_topics"] = []
                    result.append(row_dict)
                return result

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM notes WHERE id = %s;", (note_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

    def save_transcript(self, transcript: Transcript) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO transcripts (note_id, raw_text, cleaned_text, language) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (transcript.note_id, transcript.raw_text, transcript.cleaned_text, transcript.language)
                )
                new_id = cursor.fetchone()["id"]
            conn.commit()
            return new_id

    def get_transcript(self, note_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM transcripts WHERE note_id = %s;", (note_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

    def save_ai_summary(self, summary: AISummary) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ai_summaries (note_id, summary, key_points, sentiment, main_topics) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (
                        summary.note_id,
                        summary.summary,
                        json.dumps(summary.key_points),
                        summary.sentiment,
                        json.dumps(summary.main_topics)
                    )
                )
                new_id = cursor.fetchone()["id"]
            conn.commit()
            return new_id

    def get_ai_summary(self, note_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM ai_summaries WHERE note_id = %s;", (note_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                res = dict(row)
                res["key_points"] = json.loads(res["key_points"]) if res.get("key_points") else []
                res["main_topics"] = json.loads(res["main_topics"]) if res.get("main_topics") else []
                return res

    def save_task(self, task: Task) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tasks (note_id, title, description, priority, assignee, due_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                    (task.note_id, task.title, task.description, task.priority, task.assignee, task.due_date, task.status)
                )
                new_id = cursor.fetchone()["id"]
            conn.commit()
            return new_id

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, n.title as note_title
                    FROM tasks t
                    LEFT JOIN notes n ON t.note_id = n.id
                    ORDER BY t.id DESC;
                """)
                return [dict(r) for r in cursor.fetchall()]

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                q = f"%{query}%"
                cursor.execute("""
                    SELECT DISTINCT n.*, s.summary
                    FROM notes n
                    LEFT JOIN transcripts t ON n.id = t.note_id
                    LEFT JOIN ai_summaries s ON n.id = s.note_id
                    WHERE n.title ILIKE %s OR t.raw_text ILIKE %s OR s.summary ILIKE %s;
                """, (q, q, q))
                return [dict(r) for r in cursor.fetchall()]


_db_instance: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
