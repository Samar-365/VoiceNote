#!/usr/bin/env python3
"""
VoiceNote Desktop Application Entrypoint.
Orchestrates PySide6 UI, Authentication, Database, and AI Background Services.
Developed by: Tejas (Architecture & Integration Lead), Samar (UI/UX Lead), Atharv (AI Lead)
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt

from voicenote.config import APP_NAME, VERSION
try:
    from voicenote.db.database import get_db
except Exception:
    get_db = None
from voicenote.ui.dialogs.login_dialog import LoginDialog
from voicenote.ui.main_window import MainWindow

# Configure immediate, unbuffered standard output logging
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger("VoiceNote")


def main():
    logger.info(f"Starting {APP_NAME} Desktop v{VERSION}...")
    
    # 1. Initialize PySide6 Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("VoiceNote")

    # 2. Initialize Database Connection & Migrations (if available)
    if callable(get_db):
        try:
            db = get_db()
            if db:
                logger.info(f"Database initialized successfully ({db.get_user_count()} users, {db.get_note_count()} notes loaded).")
        except Exception as db_err:
            logger.warning(f"Database connection not available (running in local offline mode): {db_err}")

    # 3. Authentication & Main Application Session Loop
    while True:
        login_dlg = LoginDialog()
        if login_dlg.exec() != QDialog.Accepted:
            logger.info("Login closed or cancelled by user. Exiting application.")
            break

        current_user = login_dlg.get_user() or {}
        logger.info(f"Launching main window for authenticated user: '{current_user.get('username')}'")

        window = MainWindow(current_user=current_user)
        session_state = {"logged_out": False}

        def on_logout():
            session_state["logged_out"] = True

        window.logout_requested.connect(on_logout)
        window.show()
        logger.info("VoiceNote Main Window opened and ready for user interactions.")

        # Run event loop for this session
        app.exec()

        if not session_state["logged_out"]:
            # User closed window normally, quit
            break

        logger.info("User signed out. Re-opening Login Dialog...")

    logger.info("VoiceNote Desktop session ended.")


if __name__ == "__main__":
    main()
