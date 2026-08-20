import unittest
import uuid
from voicenote.db import get_db, User
from voicenote.db.database import hash_password


class TestUserAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.db = get_db()
        except Exception as e:
            cls.db = None
            print(f"PostgreSQL not connected for auth tests: {e}")

    def test_password_hashing(self):
        """Verify that SHA-256 hashing produces predictable and secure digests."""
        raw_pwd = "SuperSecretPassword123!"
        hashed_1 = hash_password(raw_pwd)
        hashed_2 = hash_password(raw_pwd)
        
        self.assertEqual(hashed_1, hashed_2)
        self.assertNotEqual(raw_pwd, hashed_1)
        self.assertEqual(len(hashed_1), 64)  # 256 bits in hex is 64 chars

    def test_create_and_verify_user(self):
        """Verify creating a new user in PostgreSQL and verifying credentials."""
        if self.db is None:
            self.skipTest("PostgreSQL server not running locally or auth failed.")

        unique_suffix = uuid.uuid4().hex[:8]
        username = f"auth_user_{unique_suffix}"
        email = f"auth_{unique_suffix}@voicenote.ai"
        password = "UserPass123!"

        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=f"Auth Test User {unique_suffix}"
        )

        user_id = self.db.create_user(new_user)
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)

        # Retrieve by username
        user_by_name = self.db.get_user_by_username(username)
        self.assertIsNotNone(user_by_name)
        self.assertEqual(user_by_name["username"], username)
        self.assertEqual(user_by_name["email"], email)

        # Retrieve by email
        user_by_email = self.db.get_user_by_email(email)
        self.assertIsNotNone(user_by_email)
        self.assertEqual(user_by_email["id"], user_id)

        # Verify login with username
        verified_by_user = self.db.verify_user_login(username, password)
        self.assertIsNotNone(verified_by_user)
        self.assertEqual(verified_by_user["id"], user_id)

        # Verify login with email
        verified_by_email = self.db.verify_user_login(email, password)
        self.assertIsNotNone(verified_by_email)
        self.assertEqual(verified_by_email["id"], user_id)

        # Verify failed login with wrong password
        failed = self.db.verify_user_login(username, "WrongPassword!")
        self.assertIsNone(failed)

        # Verify failed login with non-existent user
        non_existent = self.db.verify_user_login("non_existent_username_xyz", password)
        self.assertIsNone(non_existent)


if __name__ == "__main__":
    unittest.main()
