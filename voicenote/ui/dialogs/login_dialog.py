import re
import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QTabWidget, QWidget, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal

from voicenote.config import APP_NAME, VERSION
from voicenote.db.models import User
from voicenote.db.database import hash_password, get_db
from voicenote.ui.styles import MAIN_STYLE

logger = logging.getLogger("LoginDialog")


class LoginDialog(QDialog):
    """
    Full-Window Bento Grid Authentication & Registration Portal.
    Matches the exact 1280x840 window size, warm cream canvas (#ECE7DF),
    and Bento card layout of the VoiceNote Home UI.
    """

    user_authenticated = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} Desktop - AI-Powered Local Voice Intelligence • Account Authentication")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 700)
        self.setStyleSheet(MAIN_STYLE)
        self.setModal(True)

        self.authenticated_user: Optional[Dict[str, Any]] = None
        self.db = None
        try:
            self.db = get_db()
        except Exception as e:
            logger.warning(f"Database unavailable during login initialization: {e}")

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # 1. Top Header Bar (Matching Home Page Header)
        top_header = QFrame()
        top_header.setObjectName("cardFrame")
        top_header.setFixedHeight(64)
        th_layout = QHBoxLayout(top_header)
        th_layout.setContentsMargins(20, 8, 20, 8)
        th_layout.setSpacing(12)

        # Logo & App Title
        brand_title = QLabel(f"🎙️ {APP_NAME} <span style='color: #6D59A7; font-size: 13px; font-weight: 600;'>Desktop Studio v{VERSION}</span>")
        brand_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        th_layout.addWidget(brand_title)

        th_layout.addStretch()

        # Engine & DB Status Badges
        st_whisper = QLabel("Whisper: Small.en")
        st_whisper.setObjectName("badgePurple")

        st_ai = QLabel("Gemini: 2.5 Flash")
        st_ai.setObjectName("badgeCyan")

        if self.db:
            st_db = QLabel("Postgres: Online")
            st_db.setObjectName("badgeActive")
        else:
            st_db = QLabel("Postgres: Offline (Demo Mode)")
            st_db.setObjectName("badgeAmber")

        th_layout.addWidget(st_whisper)
        th_layout.addWidget(st_ai)
        th_layout.addWidget(st_db)

        main_layout.addWidget(top_header)

        # 2. Main Bento Grid Content Area (Split Left Showcase & Right Authentication)
        bento_layout = QHBoxLayout()
        bento_layout.setSpacing(16)

        # =====================================================================
        # LEFT COLUMN: STUDIO SHOWCASE & CAPABILITIES BENTO CARDS
        # =====================================================================
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)

        # Hero Bento Card
        hero_card = QFrame()
        hero_card.setObjectName("cardFrame")
        hc_layout = QVBoxLayout(hero_card)
        hc_layout.setContentsMargins(24, 22, 24, 22)
        hc_layout.setSpacing(10)

        hero_badge = QLabel("LOCAL VOICE INTELLIGENCE ENGINE")
        hero_badge.setObjectName("badgePurple")
        hero_badge.setFixedWidth(240)
        hc_layout.addWidget(hero_badge)

        hero_h1 = QLabel("Transform Spoken Meetings into Structured Actionable Notes")
        hero_h1.setStyleSheet("font-size: 22px; font-weight: 800; color: #1E2B4B; line-height: 1.3;")
        hero_h1.setWordWrap(True)
        hc_layout.addWidget(hero_h1)

        hero_desc = QLabel(
            "VoiceNote combines on-device Whisper speech-to-text, Gemini AI semantic summarization, "
            "and PostgreSQL enterprise persistence for seamless meeting productivity and timestamped search."
        )
        hero_desc.setObjectName("subtitleLabel")
        hero_desc.setWordWrap(True)
        hc_layout.addWidget(hero_desc)

        left_layout.addWidget(hero_card)

        # Bento 2-Card Row (Features)
        features_row = QHBoxLayout()
        features_row.setSpacing(14)

        # Feature 1: Real-time Audio STT
        f1_card = QFrame()
        f1_card.setObjectName("glassFrame")
        f1_lay = QVBoxLayout(f1_card)
        f1_lay.setContentsMargins(18, 16, 18, 16)
        f1_lay.setSpacing(6)

        f1_tag = QLabel("SPEECH-TO-TEXT")
        f1_tag.setObjectName("badgeCyan")
        f1_tag.setFixedWidth(120)
        f1_title = QLabel("🎙️ Real-time Transcription")
        f1_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
        f1_body = QLabel("Whisper transcription with dynamic waveform visualization and microphone gain controls.")
        f1_body.setObjectName("subtitleLabel")
        f1_body.setWordWrap(True)

        f1_lay.addWidget(f1_tag)
        f1_lay.addWidget(f1_title)
        f1_lay.addWidget(f1_body)
        features_row.addWidget(f1_card)

        # Feature 2: AI Summaries & Tasks
        f2_card = QFrame()
        f2_card.setObjectName("glassFrame")
        f2_lay = QVBoxLayout(f2_card)
        f2_lay.setContentsMargins(18, 16, 18, 16)
        f2_lay.setSpacing(6)

        f2_tag = QLabel("AI INTELLIGENCE")
        f2_tag.setObjectName("badgeAmber")
        f2_tag.setFixedWidth(120)
        f2_title = QLabel("🧠 Automated Task Extraction")
        f2_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
        f2_body = QLabel("Structured key points, action items with assignees, sentiment analysis, and topic tagging.")
        f2_body.setObjectName("subtitleLabel")
        f2_body.setWordWrap(True)

        f2_lay.addWidget(f2_tag)
        f2_lay.addWidget(f2_title)
        f2_lay.addWidget(f2_body)
        features_row.addWidget(f2_card)

        left_layout.addLayout(features_row)

        # Feature 3: Vector & DB Persistence Card
        f3_card = QFrame()
        f3_card.setObjectName("cardFrame")
        f3_lay = QVBoxLayout(f3_card)
        f3_lay.setContentsMargins(20, 16, 20, 16)
        f3_lay.setSpacing(6)

        f3_tag = QLabel("PERSISTENCE & SECURITY")
        f3_tag.setObjectName("badgeActive")
        f3_tag.setFixedWidth(160)
        f3_title = QLabel("🔒 PostgreSQL & ChromaDB Vector Store")
        f3_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E2B4B;")
        f3_body = QLabel("Strict PostgreSQL relational database with SHA-256 password security, cascading note associations, and sub-second semantic search.")
        f3_body.setObjectName("subtitleLabel")
        f3_body.setWordWrap(True)

        f3_lay.addWidget(f3_tag)
        f3_lay.addWidget(f3_title)
        f3_lay.addWidget(f3_body)
        left_layout.addWidget(f3_card)

        # Team & Project Footer Pill
        footer_card = QFrame()
        footer_card.setObjectName("glassFrame")
        ft_lay = QHBoxLayout(footer_card)
        ft_lay.setContentsMargins(16, 10, 16, 10)
        ft_lbl = QLabel("VoiceNote Desktop • Samar (UI/UX) • Tejas (Architecture) • Atharv (AI Lead)")
        ft_lbl.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 600;")
        ft_lay.addWidget(ft_lbl)
        left_layout.addWidget(footer_card)

        left_layout.addStretch()
        bento_layout.addWidget(left_column, stretch=6)

        # =====================================================================
        # RIGHT COLUMN: AUTHENTICATION CARD (SIGN IN / REGISTER)
        # =====================================================================
        right_container = QFrame()
        right_container.setObjectName("cardFrame")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(28, 24, 28, 24)
        right_layout.setSpacing(14)

        # Auth Header
        auth_title = QLabel("Account Authentication")
        auth_title.setObjectName("titleLabel")
        auth_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1E2B4B;")

        auth_sub = QLabel("Sign in to your account or create a new profile in PostgreSQL.")
        auth_sub.setObjectName("subtitleLabel")
        auth_sub.setWordWrap(True)

        right_layout.addWidget(auth_title)
        right_layout.addWidget(auth_sub)
        right_layout.addSpacing(4)

        # Tab Widget for Sign In vs Create Account
        self.tabs = QTabWidget()

        # Tab 1: Sign In
        self.tab_signin = QWidget()
        self.init_signin_tab()
        self.tabs.addTab(self.tab_signin, "Sign In")

        # Tab 2: Create Account
        self.tab_register = QWidget()
        self.init_register_tab()
        self.tabs.addTab(self.tab_register, "Create Account")

        right_layout.addWidget(self.tabs, stretch=1)

        bento_layout.addWidget(right_container, stretch=5)
        main_layout.addLayout(bento_layout, stretch=1)

    # =========================================================================
    # TAB 1: SIGN IN FORM
    # =========================================================================
    def init_signin_tab(self):
        layout = QVBoxLayout(self.tab_signin)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)

        # Username / Email
        layout.addWidget(QLabel("<b>Username or Email:</b>"))
        self.login_user_input = QLineEdit()
        self.login_user_input.setPlaceholderText("e.g. admin or samar@voicenote.ai")
        self.login_user_input.setText("admin")
        self.login_user_input.setFixedHeight(38)
        layout.addWidget(self.login_user_input)

        # Password
        layout.addWidget(QLabel("<b>Password:</b>"))
        self.login_pwd_input = QLineEdit()
        self.login_pwd_input.setEchoMode(QLineEdit.Password)
        self.login_pwd_input.setPlaceholderText("Enter your password")
        self.login_pwd_input.setText("admin123")
        self.login_pwd_input.setFixedHeight(38)
        self.login_pwd_input.returnPressed.connect(self.handle_login)

        pwd_row = QHBoxLayout()
        pwd_row.addWidget(self.login_pwd_input)
        self.btn_toggle_login_pwd = QPushButton("👁")
        self.btn_toggle_login_pwd.setFixedSize(42, 38)
        self.btn_toggle_login_pwd.setToolTip("Show/Hide Password")
        self.btn_toggle_login_pwd.clicked.connect(
            lambda: self.toggle_password_visibility(self.login_pwd_input, self.btn_toggle_login_pwd)
        )
        pwd_row.addWidget(self.btn_toggle_login_pwd)
        layout.addLayout(pwd_row)

        # Error banner
        self.signin_error_label = QLabel("")
        self.signin_error_label.setStyleSheet("color: #E05A77; font-weight: 700; font-size: 12px;")
        self.signin_error_label.setWordWrap(True)
        self.signin_error_label.hide()
        layout.addWidget(self.signin_error_label)

        layout.addSpacing(6)

        # Sign In Submit Button
        btn_login = QPushButton("Sign In to Studio")
        btn_login.setObjectName("primaryBtn")
        btn_login.setFixedHeight(42)
        btn_login.clicked.connect(self.handle_login)
        layout.addWidget(btn_login)

        # Quick Demo Button
        btn_demo = QPushButton("Quick Demo Sign In (Admin)")
        btn_demo.setFixedHeight(36)
        btn_demo.clicked.connect(self.handle_demo_login)
        layout.addWidget(btn_demo)

        # Default Credentials Hint Card
        hint_card = QFrame()
        hint_card.setObjectName("glassFrame")
        hc_lay = QVBoxLayout(hint_card)
        hc_lay.setContentsMargins(12, 10, 12, 10)
        hint_txt = QLabel("<b>Default Admin:</b> <code>admin</code> • <b>Password:</b> <code>admin123</code>")
        hint_txt.setStyleSheet("font-size: 11px; color: #5C6479;")
        hc_lay.addWidget(hint_txt)
        layout.addWidget(hint_card)

        layout.addStretch()

    # =========================================================================
    # TAB 2: CREATE ACCOUNT FORM
    # =========================================================================
    def init_register_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Full Name
        layout.addWidget(QLabel("<b>Full Name:</b>"))
        self.reg_fullname_input = QLineEdit()
        self.reg_fullname_input.setPlaceholderText("e.g. Samar Saxena")
        self.reg_fullname_input.setFixedHeight(36)
        layout.addWidget(self.reg_fullname_input)

        # Username
        layout.addWidget(QLabel("<b>Username:</b>"))
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("e.g. samar")
        self.reg_username_input.setFixedHeight(36)
        layout.addWidget(self.reg_username_input)

        # Email
        layout.addWidget(QLabel("<b>Email Address:</b>"))
        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("e.g. samar@voicenote.ai")
        self.reg_email_input.setFixedHeight(36)
        layout.addWidget(self.reg_email_input)

        # Password
        layout.addWidget(QLabel("<b>Password:</b>"))
        self.reg_pwd_input = QLineEdit()
        self.reg_pwd_input.setEchoMode(QLineEdit.Password)
        self.reg_pwd_input.setPlaceholderText("Minimum 4 characters")
        self.reg_pwd_input.setFixedHeight(36)
        layout.addWidget(self.reg_pwd_input)

        # Confirm Password
        layout.addWidget(QLabel("<b>Confirm Password:</b>"))
        self.reg_confirm_input = QLineEdit()
        self.reg_confirm_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_input.setPlaceholderText("Re-enter password")
        self.reg_confirm_input.setFixedHeight(36)
        self.reg_confirm_input.returnPressed.connect(self.handle_register)
        layout.addWidget(self.reg_confirm_input)

        # Error banner
        self.reg_error_label = QLabel("")
        self.reg_error_label.setStyleSheet("color: #E05A77; font-weight: 700; font-size: 12px;")
        self.reg_error_label.setWordWrap(True)
        self.reg_error_label.hide()
        layout.addWidget(self.reg_error_label)

        layout.addSpacing(6)

        # Register Submit Button
        btn_register = QPushButton("Create Account & Sign In")
        btn_register.setObjectName("primaryBtn")
        btn_register.setFixedHeight(42)
        btn_register.clicked.connect(self.handle_register)
        layout.addWidget(btn_register)

        reg_info = QLabel("New accounts are securely persisted directly in PostgreSQL.")
        reg_info.setStyleSheet("font-size: 11px; color: #5C6479;")
        layout.addWidget(reg_info)

        layout.addStretch()
        scroll.setWidget(container)

        tab_lay = QVBoxLayout(self.tab_register)
        tab_lay.setContentsMargins(0, 0, 0, 0)
        tab_lay.addWidget(scroll)

    # =========================================================================
    # ACTIONS & VALIDATION
    # =========================================================================
    def toggle_password_visibility(self, input_field: QLineEdit, button: QPushButton):
        if input_field.echoMode() == QLineEdit.Password:
            input_field.setEchoMode(QLineEdit.Normal)
            button.setText("🔒")
        else:
            input_field.setEchoMode(QLineEdit.Password)
            button.setText("👁")

    def show_signin_error(self, message: str):
        self.signin_error_label.setText(f"⚠️ {message}")
        self.signin_error_label.show()

    def show_register_error(self, message: str):
        self.reg_error_label.setText(f"⚠️ {message}")
        self.reg_error_label.show()

    def handle_login(self):
        self.signin_error_label.hide()
        ident = self.login_user_input.text().strip()
        pwd = self.login_pwd_input.text()

        if not ident or not pwd:
            self.show_signin_error("Please enter both username/email and password.")
            return

        if not self.db:
            # Fallback offline mode if PostgreSQL server is down
            logger.warning("PostgreSQL server offline. Using fallback local authentication.")
            self.authenticated_user = {
                "id": 1,
                "username": ident,
                "email": f"{ident}@voicenote.local",
                "full_name": ident.capitalize(),
                "role": "Local User"
            }
            self.user_authenticated.emit(self.authenticated_user)
            self.accept()
            return

        try:
            user = self.db.verify_user_login(ident, pwd)
            if user:
                logger.info(f"User '{user['username']}' authenticated successfully.")
                self.authenticated_user = user
                self.user_authenticated.emit(self.authenticated_user)
                self.accept()
            else:
                self.show_signin_error("Invalid credentials. Please check your username and password.")
        except Exception as err:
            logger.error(f"Authentication query error: {err}")
            self.show_signin_error(f"Database error during login: {err}")

    def handle_demo_login(self):
        """Quickly sign in as the default admin user."""
        self.login_user_input.setText("admin")
        self.login_pwd_input.setText("admin123")
        self.handle_login()

    def handle_register(self):
        self.reg_error_label.hide()
        full_name = self.reg_fullname_input.text().strip()
        username = self.reg_username_input.text().strip().lower()
        email = self.reg_email_input.text().strip().lower()
        pwd = self.reg_pwd_input.text()
        confirm = self.reg_confirm_input.text()

        # Validation
        if not full_name:
            self.show_register_error("Full Name cannot be empty.")
            return

        if not username or len(username) < 3:
            self.show_register_error("Username must be at least 3 characters.")
            return

        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            self.show_register_error("Username can only contain letters, numbers, underscores, and hyphens.")
            return

        if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            self.show_register_error("Please enter a valid email address.")
            return

        if not pwd or len(pwd) < 4:
            self.show_register_error("Password must be at least 4 characters long.")
            return

        if pwd != confirm:
            self.show_register_error("Passwords do not match.")
            return

        if not self.db:
            self.show_register_error("Database is offline. Unable to persist new user registration.")
            return

        try:
            # Check unique username
            existing_user = self.db.get_user_by_username(username)
            if existing_user:
                self.show_register_error(f"Username '{username}' is already taken.")
                return

            # Check unique email
            existing_email = self.db.get_user_by_email(email)
            if existing_email:
                self.show_register_error(f"Email '{email}' is already registered.")
                return

            # Create User instance
            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(pwd),
                full_name=full_name
            )

            new_id = self.db.create_user(new_user)
            logger.info(f"New user registered successfully with ID {new_id}: {username}")

            # Auto authenticate user and close dialog
            self.authenticated_user = {
                "id": new_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "password_hash": new_user.password_hash,
                "created_at": new_user.created_at
            }
            self.user_authenticated.emit(self.authenticated_user)

            QMessageBox.information(
                self,
                "Account Created",
                f"Welcome, {full_name}!\nYour account was created successfully in the PostgreSQL database."
            )
            self.accept()

        except Exception as err:
            logger.error(f"Registration error: {err}")
            self.show_register_error(f"Failed to register account: {err}")

    def get_user(self) -> Optional[Dict[str, Any]]:
        """Return the authenticated user dictionary."""
        return self.authenticated_user
