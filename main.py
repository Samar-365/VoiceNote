#!/usr/bin/env python3
"""
VoiceNote Desktop Application Entrypoint.
Orchestrates PySide6 UI, Database, and AI Background Services.
Developed by: Tejas (Architecture & Integration Lead), Samar (UI/UX Lead), Atharv (AI Lead)
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from voicenote.config import APP_NAME, VERSION
try:
    from voicenote.db.database import get_db
except Exception:
    get_db = None
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
                logger.info(f"Database initialized successfully ({db.get_note_count()} notes loaded).")
        except Exception as db_err:
            logger.warning(f"Database connection not available (running in local offline mode): {db_err}")

    # 3. Instantiate & Launch Main Application Window
    window = MainWindow()
    window.show()
    logger.info("VoiceNote Main Window opened and ready for user interactions.")
    
    # 4. Start Qt Event Loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
