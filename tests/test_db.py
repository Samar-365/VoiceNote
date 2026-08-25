import unittest
from voicenote.db import get_db, Note, Transcript, AISummary, Task


class TestPostgreSQLDatabaseManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.db = get_db()
        except Exception as e:
            cls.db = None
            print(f"PostgreSQL not connected: {e}")

    def test_database_initialization(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        self.assertIsNotNone(self.db)

    def test_get_note_count(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        count = self.db.get_note_count()
        self.assertGreaterEqual(count, 0)

    def test_add_and_retrieve_note(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        new_note = Note(
            title="PostgreSQL Unit Test Note",
            duration="01:30",
            category="Testing"
        )
        note_id = self.db.add_note(new_note)
        self.assertIsNotNone(note_id)

        retrieved = self.db.get_note_by_id(note_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["title"], "PostgreSQL Unit Test Note")

    def test_save_and_retrieve_transcript(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        note = Note(title="PostgreSQL Transcript Note")
        note_id = self.db.add_note(note)

        transcript = Transcript(
            note_id=note_id,
            raw_text="PostgreSQL raw transcript text.",
            cleaned_text="PostgreSQL raw transcript text.",
            language="en"
        )
        t_id = self.db.save_transcript(transcript)
        self.assertIsNotNone(t_id)

        retrieved_t = self.db.get_transcript(note_id)
        self.assertIsNotNone(retrieved_t)
        self.assertEqual(retrieved_t["raw_text"], "PostgreSQL raw transcript text.")

    def test_save_and_retrieve_ai_summary(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        note = Note(title="PostgreSQL AI Summary Note")
        note_id = self.db.add_note(note)

        summary = AISummary(
            note_id=note_id,
            summary="PostgreSQL summary text",
            key_points=["Point A", "Point B"],
            sentiment="Positive",
            main_topics=["Testing", "PostgreSQL"]
        )
        s_id = self.db.save_ai_summary(summary)
        self.assertIsNotNone(s_id)

        retrieved_s = self.db.get_ai_summary(note_id)
        self.assertIsNotNone(retrieved_s)
        self.assertEqual(retrieved_s["summary"], "PostgreSQL summary text")

    def test_save_and_retrieve_tasks(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        note = Note(title="PostgreSQL Task Note")
        note_id = self.db.add_note(note)

        task = Task(
            note_id=note_id,
            title="Complete PostgreSQL testing",
            priority="High",
            assignee="Tejas",
            due_date="Today",
            status="Pending"
        )
        task_id = self.db.save_task(task)
        self.assertIsNotNone(task_id)

        tasks = self.db.get_all_tasks()
        self.assertTrue(any(t["id"] == task_id for t in tasks))


    def test_user_auth_flow(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        import uuid
        from voicenote.db.database import hash_password
        from voicenote.db import User

        unique_id = uuid.uuid4().hex[:6]
        u_name = f"test_user_{unique_id}"
        u_email = f"test_{unique_id}@voicenote.ai"

        new_user = User(
            username=u_name,
            email=u_email,
            password_hash=hash_password("secret123"),
            full_name="Test User"
        )
        user_id = self.db.create_user(new_user)
        self.assertIsNotNone(user_id)

        user_by_name = self.db.get_user_by_username(u_name)
        self.assertIsNotNone(user_by_name)
        self.assertEqual(user_by_name["email"], u_email)

        verified = self.db.verify_user_login(u_name, "secret123")
        self.assertIsNotNone(verified)
        self.assertEqual(verified["username"], u_name)

        invalid = self.db.verify_user_login(u_name, "wrongpassword")
        self.assertIsNone(invalid)

    def test_delete_note(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        note = Note(title="Temporary Delete Test Note", duration="00:30")
        note_id = self.db.add_note(note)
        self.assertIsNotNone(note_id)

        # Save relations
        self.db.save_transcript(Transcript(note_id=note_id, raw_text="Temp text"))
        self.db.save_ai_summary(AISummary(note_id=note_id, summary="Temp summary"))
        self.db.save_task(Task(note_id=note_id, title="Temp task"))

        # Verify exists
        self.assertIsNotNone(self.db.get_note_by_id(note_id))

        # Delete note
        success = self.db.delete_note(note_id)
        self.assertTrue(success)

        # Verify deleted
        self.assertIsNone(self.db.get_note_by_id(note_id))
        self.assertIsNone(self.db.get_transcript(note_id))
        self.assertIsNone(self.db.get_ai_summary(note_id))

    def test_delete_all_notes(self):
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")
        # Add 2 temporary notes
        n1 = self.db.add_note(Note(title="Bulk Delete Note 1", duration="00:10"))
        n2 = self.db.add_note(Note(title="Bulk Delete Note 2", duration="00:20"))
        self.assertIsNotNone(n1)
        self.assertIsNotNone(n2)
        
        # Test delete all
        deleted_count = self.db.delete_all_notes()
        self.assertGreaterEqual(deleted_count, 2)
        self.assertEqual(self.db.get_note_count(), 0)


if __name__ == "__main__":
    unittest.main()

