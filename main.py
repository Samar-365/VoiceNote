#!/usr/bin/env python3
"""
VoiceNote Desktop Application Entrypoint.
Orchestrates PySide6 UI, Authentication, Database, and AI Background Services.
Developed by: Tejas (Architecture & Integration Lead), Samar (UI/UX Lead), Atharv (AI Lead)
"""

import sys
import logging
from typing import Optional
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QObject, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup

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


class AppSessionController(QObject):
    """
    Manages user sessions, authentication flows, and seamless cross-fade
    transitions between LoginDialog and MainWindow with zero blank screens.
    """

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.login_dlg: Optional[LoginDialog] = None
        self.main_window: Optional[MainWindow] = None
        self.anim_group: Optional[QParallelAnimationGroup] = None

    def start(self):
        self.show_login()

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_dlg = LoginDialog()
        self.login_dlg.user_authenticated.connect(self.on_user_authenticated)
        self.login_dlg.rejected.connect(self.on_login_rejected)
        self.login_dlg.show()
        logger.info("VoiceNote Login Portal ready.")

    def on_login_rejected(self):
        if not self.login_dlg or not self.login_dlg.authenticated_user:
            logger.info("Login closed or cancelled by user. Exiting application.")
            self.app.quit()

    def on_user_authenticated(self, user: dict):
        logger.info(f"User authenticated: '{user.get('username')}'. Launching main workspace with smooth transition...")
        self.app.processEvents()

        if self.login_dlg:
            self.login_dlg.is_transitioning = True

        # Pre-warm and instantiate MainWindow while login_dlg remains completely visible
        self.main_window = MainWindow(current_user=user)
        self.main_window.logout_requested.connect(self.on_logout_requested)

        # Smooth cross-fade transition: MainWindow fades in, LoginDialog fades out
        self.transition_windows(from_window=self.login_dlg, to_window=self.main_window)

    def transition_windows(self, from_window: Optional[QWidget], to_window: QWidget):
        to_window.setWindowOpacity(0.0)
        to_window.show()
        to_window.raise_()
        to_window.activateWindow()

        if from_window and from_window.isVisible():
            self.anim_group = QParallelAnimationGroup()

            fade_out = QPropertyAnimation(from_window, b"windowOpacity")
            fade_out.setDuration(300)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.anim_group.addAnimation(fade_out)

            fade_in = QPropertyAnimation(to_window, b"windowOpacity")
            fade_in.setDuration(300)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.anim_group.addAnimation(fade_in)

            def on_finished():
                from_window.hide()
                from_window.setWindowOpacity(1.0)
                logger.info("Workspace transition completed successfully.")

            self.anim_group.finished.connect(on_finished)
            self.anim_group.start()
        else:
            to_window.setWindowOpacity(1.0)

    def on_logout_requested(self):
        logger.info("User signed out. Smoothly transitioning back to Login Dialog...")
        old_window = self.main_window
        self.login_dlg = LoginDialog()
        self.login_dlg.user_authenticated.connect(self.on_user_authenticated)
        self.login_dlg.rejected.connect(self.on_login_rejected)

        self.transition_windows(from_window=old_window, to_window=self.login_dlg)
        if old_window:
            def close_old():
                old_window.close()
                self.main_window = None
            if self.anim_group:
                self.anim_group.finished.connect(close_old)
            else:
                close_old()


def main():
    logger.info(f"Starting {APP_NAME} Desktop v{VERSION}...")
    
    # 1. Initialize PySide6 Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("VoiceNote")

    # Register bundled Unicode fonts (Devanagari + Latin support)
    from pathlib import Path
    from PySide6.QtGui import QFontDatabase
    fonts_dir = Path(__file__).resolve().parent / "assets" / "fonts"
    if fonts_dir.exists():
        for font_file in fonts_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id != -1:
                logger.debug(f"Loaded application font: {font_file.name}")

    # 2. Initialize Database Connection & Migrations (if available)
    if callable(get_db):
        try:
            db = get_db()
            if db:
                logger.info(f"Database initialized successfully ({db.get_user_count()} users, {db.get_note_count()} notes loaded).")
        except Exception as db_err:
            logger.warning(f"Database connection not available (running in local offline mode): {db_err}")

    # 3. Start Application with AppSessionController
    controller = AppSessionController(app)
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
