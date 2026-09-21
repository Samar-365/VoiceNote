import sys
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from voicenote.ui.dialogs.login_dialog import LoginDialog


class TestLoginFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure a single QApplication instance exists for GUI tests
        cls.app = QApplication.instance()
        if not cls.app:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.dialog = LoginDialog()
        self.dialog.show()
        self.app.processEvents()

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()
        self.app.processEvents()

    def test_initial_state(self):
        """Verify initial UI state has inputs enabled and loading widgets hidden."""
        self.assertFalse(self.dialog.is_authenticating)
        self.assertTrue(self.dialog.login_user_input.isEnabled())
        self.assertTrue(self.dialog.login_pwd_input.isEnabled())
        self.assertTrue(self.dialog.btn_login.isEnabled())
        self.assertTrue(self.dialog.btn_demo.isEnabled())
        self.assertTrue(self.dialog.signin_progress.isHidden())
        self.assertTrue(self.dialog.signin_status.isHidden())
        self.assertTrue(self.dialog.signin_error_label.isHidden())

    def test_empty_credentials_validation(self):
        """Empty credentials should display an error and not start loading."""
        self.dialog.login_user_input.setText("")
        self.dialog.login_pwd_input.setText("")
        self.dialog.handle_login()

        self.assertFalse(self.dialog.is_authenticating)
        self.assertFalse(self.dialog.signin_error_label.isHidden())
        self.assertIn("Please enter both", self.dialog.signin_error_label.text())

    def test_set_signin_loading_toggles_inputs(self):
        """set_signin_loading(True) should disable inputs and show progress indicators."""
        self.dialog.set_signin_loading(True, "Authenticating credentials...")
        self.assertTrue(self.dialog.is_authenticating)
        self.assertFalse(self.dialog.login_user_input.isEnabled())
        self.assertFalse(self.dialog.login_pwd_input.isEnabled())
        self.assertFalse(self.dialog.btn_login.isEnabled())
        self.assertFalse(self.dialog.btn_demo.isEnabled())
        self.assertFalse(self.dialog.signin_progress.isHidden())
        self.assertFalse(self.dialog.signin_status.isHidden())
        self.assertTrue(self.dialog.spinner_timer.isActive())

        # Resetting loading should restore controls
        self.dialog.set_signin_loading(False)
        self.assertFalse(self.dialog.is_authenticating)
        self.assertTrue(self.dialog.login_user_input.isEnabled())
        self.assertTrue(self.dialog.login_pwd_input.isEnabled())
        self.assertTrue(self.dialog.btn_login.isEnabled())
        self.assertTrue(self.dialog.signin_progress.isHidden())
        self.assertFalse(self.dialog.spinner_timer.isActive())

    def test_set_signin_success_state(self):
        """Success state should display verified badge and keep progress bar active."""
        self.dialog.set_signin_success("Preparing workspace...")
        self.assertIn("Authenticated", self.dialog.btn_login.text())
        self.assertFalse(self.dialog.signin_progress.isHidden())
        self.assertFalse(self.dialog.signin_status.isHidden())
        self.assertIn("Preparing workspace", self.dialog.signin_status.text())
        self.assertFalse(self.dialog.spinner_timer.isActive())

    def test_auth_signal_emission_on_success(self):
        """Verifying that valid login emits the user_authenticated signal."""
        emitted_payloads = []
        self.dialog.user_authenticated.connect(lambda u: emitted_payloads.append(u))

        class MockDB:
            def verify_user_login(self, username, password):
                return {"id": 1, "username": username, "email": "test@voicenote.ai"}

        self.dialog.db = MockDB()
        self.dialog.login_user_input.setText("test_user")
        self.dialog.login_pwd_input.setText("test_pass")
        self.dialog._perform_login()

        self.assertEqual(len(emitted_payloads), 1)
        self.assertEqual(emitted_payloads[0]["username"], "test_user")
        self.assertIn("Authenticated", self.dialog.btn_login.text())

    def test_auth_failure_handling(self):
        """Verifying that failed login displays error banner and re-enables controls."""
        class MockFailingDB:
            def verify_user_login(self, username, password):
                return None

        self.dialog.db = MockFailingDB()
        self.dialog.login_user_input.setText("invalid_user")
        self.dialog.login_pwd_input.setText("wrong_pass")
        self.dialog.set_signin_loading(True)
        self.dialog._perform_login()

        self.assertFalse(self.dialog.is_authenticating)
        self.assertFalse(self.dialog.signin_error_label.isHidden())
        self.assertIn("Invalid credentials", self.dialog.signin_error_label.text())
        self.assertTrue(self.dialog.login_user_input.isEnabled())
        self.assertTrue(self.dialog.btn_login.isEnabled())
        self.assertTrue(self.dialog.signin_progress.isHidden())


if __name__ == "__main__":
    unittest.main()
