import json
import logging
import hashlib
from typing import List, Optional, Dict, Any

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    psycopg2 = None
    ISOLATION_LEVEL_AUTOCOMMIT = None

from voicenote.config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
)
from voicenote.db.models import Note, Transcript, AISummary, Task, User

logger = logging.getLogger("DatabaseManager")



def hash_password(password: str) -> str:
    """Hash a cleartext password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class DatabaseManager:
    """Strictly PostgreSQL database manager for VoiceNote."""

    def __init__(self):
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is not installed. Please install psycopg2-binary to use PostgreSQL.")
        self._ensure_database_exists()
        self.init_db()


    def _ensure_database_exists(self):
        """Connect to default 'postgres' database and create target database if missing."""
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            conn.close()
        except psycopg2.OperationalError as e:
            err_msg = str(e)
            if f'database "{POSTGRES_DB}" does not exist' in err_msg or "does not exist" in err_msg:
                logger.info(f"Database '{POSTGRES_DB}' does not exist. Creating database on PostgreSQL server...")
                conn = psycopg2.connect(
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT,
                    dbname="postgres",
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                cursor.execute(f'CREATE DATABASE "{POSTGRES_DB}";')
                cursor.close()
                conn.close()
                logger.info(f"Database '{POSTGRES_DB}' created successfully.")
            else:
                logger.error(f"PostgreSQL connection error: {e}")
                raise e

    def get_connection(self):
        """Get PostgreSQL connection."""
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
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255) DEFAULT 'VoiceNote User',
                        created_at VARCHAR(100) NOT NULL,
                        avatar_url TEXT
                    );

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

        if self.get_user_count() == 0:
            self._seed_default_user()

    def get_user_count(self) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users;")
                res = cursor.fetchone()
                return res["count"]

    def _seed_default_user(self):
        """Seed initial default admin user for login authentication."""
        demo_user = User(
            username="admin",
            email="admin@voicenote.ai",
            password_hash=hash_password("admin123"),
            full_name="Tejas Rawool"
        )
        self.create_user(demo_user)
        logger.info("Default demo user ('admin' / 'admin123') created successfully.")

    def create_user(self, user: User) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, full_name, created_at, avatar_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (user.username, user.email, user.password_hash, user.full_name, user.created_at, user.avatar_url)
                )
                new_id = cursor.fetchone()["id"]
            conn.commit()
            return new_id

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
                row = cursor.fetchone()
                return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
                row = cursor.fetchone()
                return dict(row) if row else None

    def verify_user_login(self, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify login credentials by checking username/email and hashed password."""
        hashed_pwd = hash_password(password)
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE (username = %s OR email = %s) AND password_hash = %s;",
                    (username_or_email, username_or_email, hashed_pwd)
                )
                row = cursor.fetchone()
                return dict(row) if row else None

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
                Transcript(raw_text="Defined JSON structured outputs for Groq and Gemini task extraction, priority categorization, and assignee mapping.", cleaned_text="Defined JSON structured outputs for Groq and Gemini task extraction, priority categorization, and assignee mapping."),
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

    def delete_note(self, note_id: int) -> bool:
        """Delete a note and its cascading relations (transcripts, summaries, tasks) from database."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT audio_path FROM notes WHERE id = %s;", (note_id,))
                    row = cursor.fetchone()
                    if row and row.get("audio_path"):
                        try:
                            import os
                            if os.path.exists(row["audio_path"]):
                                os.remove(row["audio_path"])
                        except Exception as e:
                            logger.warning(f"Could not remove audio file: {e}")
                    cursor.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete note {note_id}: {e}")
            return False

    def delete_note_by_title(self, title: str) -> bool:
        """Delete a note by its title and remove its audio file if present."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, audio_path FROM notes WHERE title = %s;", (title,))
                    row = cursor.fetchone()
                    if not row:
                        return False
                    note_id = row["id"]
                    if row.get("audio_path"):
                        try:
                            import os
                            if os.path.exists(row["audio_path"]):
                                os.remove(row["audio_path"])
                        except Exception as e:
                            logger.warning(f"Could not remove audio file: {e}")
                    cursor.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete note with title '{title}': {e}")
            return False

    def delete_all_notes(self) -> int:
        """Delete all notes, cascade relational tables, and purge recording files from disk."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get all audio paths to clean up recording files
                    cursor.execute("SELECT audio_path FROM notes WHERE audio_path IS NOT NULL;")
                    rows = cursor.fetchall()
                    for r in rows:
                        path = r.get("audio_path")
                        if path:
                            try:
                                import os
                                if os.path.exists(path):
                                    os.remove(path)
                            except Exception as e:
                                logger.warning(f"Could not remove file '{path}': {e}")
                    
                    cursor.execute("SELECT COUNT(*) FROM notes;")
                    count = cursor.fetchone()["count"]
                    cursor.execute("DELETE FROM notes;")
                conn.commit()
            return count
        except Exception as e:
            logger.error(f"Failed to delete all notes: {e}")
            return 0

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


def get_db() -> Optional[DatabaseManager]:
    global _db_instance
    if psycopg2 is None:
        logger.warning("psycopg2 is not installed in current Python environment. Running in offline mode.")
        return None
    if _db_instance is None:
        try:
            _db_instance = DatabaseManager()
        except Exception as e:
            logger.warning(f"Unable to connect to PostgreSQL database: {e}")
            return None
    return _db_instance



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Initializing VoiceNote PostgreSQL Database...")
    db = get_db()
    print("PostgreSQL Database initialized successfully!")
    print(f"Total Users: {db.get_user_count()}")
    print(f"Total Notes: {db.get_note_count()}")
    print(f"Total Tasks: {len(db.get_all_tasks())}")
