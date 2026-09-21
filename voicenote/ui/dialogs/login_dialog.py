import os
import re
import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QTabWidget, QWidget, QMessageBox, QScrollArea,
    QProgressBar, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QEvent, QPoint
from PySide6.QtGui import QPixmap, QIcon

from voicenote.config import APP_NAME, VERSION
from voicenote.db.models import User
from voicenote.db.database import hash_password, get_db
from voicenote.ui.styles import MAIN_STYLE
from voicenote.ui.components.login_showcase_widgets import (
    render_svg_pixmap,
    AnimatedWaveformWidget,
    PulseMicWidget,
    AnimatedPipelineWidget,
    FloatingParticlesOverlay,
    InteractiveFeatureCard,
    CapabilityChip,
    PrivacyTrustBadge,
    TitleBarButton
)

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
        self.setWindowTitle(f"{APP_NAME} Desktop — AI-Powered Local Voice Intelligence")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 700)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(MAIN_STYLE)
        self.setModal(False)
        self._drag_pos = None

        self.authenticated_user: Optional[Dict[str, Any]] = None
        self.is_authenticating = False
        self.is_transitioning = False

        # Animated Spinner Setup
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0
        self.active_loading_btn: Optional[QPushButton] = None
        self.active_loading_text: str = ""
        self.spinner_timer = QTimer(self)
        self.spinner_timer.setInterval(80)
        self.spinner_timer.timeout.connect(self._update_spinner_frame)

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

        # 1. Top Header Bar (Modern Title Bar with Official Logo, Product Tagline, & Window Controls)
        self.top_header = QFrame()
        self.top_header.setObjectName("cardFrame")
        self.top_header.setFixedHeight(64)
        th_layout = QHBoxLayout(self.top_header)
        th_layout.setContentsMargins(18, 8, 14, 8)
        th_layout.setSpacing(14)

        # Brand Logo + App Title
        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)

        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(40, 40)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "voicenote_logo.png"))
        if not os.path.exists(logo_path):
            logo_path = os.path.abspath("assets/voicenote_logo.png")
            
        if os.path.exists(logo_path):
            orig_pix = QPixmap(logo_path)
            if not orig_pix.isNull():
                scaled_pix = orig_pix.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_lbl.setPixmap(scaled_pix)
            else:
                self.logo_lbl.setPixmap(render_svg_pixmap("microphone", color="#6D59A7", size=24))
        else:
            self.logo_lbl.setPixmap(render_svg_pixmap("microphone", color="#6D59A7", size=24))

        brand_row.addWidget(self.logo_lbl)

        brand_title = QLabel(f"{APP_NAME} <span style='color: #6D59A7; font-size: 13px; font-weight: 700;'>Desktop Studio v{VERSION}</span>")
        brand_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E2B4B;")
        brand_row.addWidget(brand_title)
        th_layout.addLayout(brand_row)

        th_layout.addStretch()

        # Product-Related Tagline: "LISTEN. UNDERSTAND. ORGANIZE. ACT."
        tagline_container = QWidget()
        tagline_lay = QHBoxLayout(tagline_container)
        tagline_lay.setContentsMargins(0, 0, 0, 0)
        tagline_lay.setSpacing(8)

        sparkle_left = QLabel()
        sparkle_left.setFixedSize(16, 16)
        sparkle_left.setPixmap(render_svg_pixmap("sparkles", color="#6D59A7", size=14))
        tagline_lay.addWidget(sparkle_left)

        product_tagline = QLabel("LISTEN. UNDERSTAND. ORGANIZE. ACT.")
        product_tagline.setStyleSheet("""
            font-size: 14px;
            font-weight: 900;
            font-style: italic;
            color: #1E2B4B;
            letter-spacing: 1.5px;
        """)
        tagline_lay.addWidget(product_tagline)

        sparkle_right = QLabel()
        sparkle_right.setFixedSize(16, 16)
        sparkle_right.setPixmap(render_svg_pixmap("waveform", color="#3B82F6", size=14))
        tagline_lay.addWidget(sparkle_right)

        th_layout.addWidget(tagline_container)
        th_layout.addSpacing(16)

        # Window Controls: Minimize, Maximize / Restore, Close
        win_controls = QWidget()
        wc_lay = QHBoxLayout(win_controls)
        wc_lay.setContentsMargins(0, 0, 0, 0)
        wc_lay.setSpacing(6)

        self.btn_minimize = TitleBarButton("win_minimize", is_close=False)
        self.btn_minimize.setToolTip("Minimize")
        self.btn_minimize.clicked.connect(self.showMinimized)
        wc_lay.addWidget(self.btn_minimize)

        self.btn_maximize = TitleBarButton("win_maximize", is_close=False)
        self.btn_maximize.setToolTip("Maximize")
        self.btn_maximize.clicked.connect(self.toggle_maximize_restore)
        wc_lay.addWidget(self.btn_maximize)

        self.btn_close_win = TitleBarButton("win_close", is_close=True)
        self.btn_close_win.setToolTip("Close")
        self.btn_close_win.clicked.connect(self.close)
        wc_lay.addWidget(self.btn_close_win)

        th_layout.addWidget(win_controls)

        main_layout.addWidget(self.top_header)

        # 2. Main Bento Grid Content Area (Split Left Showcase & Right Authentication)
        bento_layout = QHBoxLayout()
        bento_layout.setSpacing(16)

        # =====================================================================
        # LEFT COLUMN: LIVING VOICE INTELLIGENCE SHOWCASE
        # =====================================================================
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Floating Particles & Sparkles Overlay (background)
        self.particles_overlay = FloatingParticlesOverlay(left_column)
        self.particles_overlay.resize(left_column.size())
        self.particles_overlay.lower()

        # Hero Bento Showcase Card
        hero_card = QFrame()
        hero_card.setObjectName("cardFrame")
        hc_layout = QVBoxLayout(hero_card)
        hc_layout.setContentsMargins(20, 16, 20, 16)
        hc_layout.setSpacing(8)

        # Eyebrow Tag
        eyebrow_row = QHBoxLayout()
        eyebrow_row.setSpacing(6)
        eyebrow_badge = QLabel("✦ AI-POWERED VOICE INTELLIGENCE")
        eyebrow_badge.setObjectName("badgePurple")
        eyebrow_badge.setStyleSheet("""
            QLabel {
                background-color: #F2EFF9;
                color: #6D59A7;
                border: 1px solid #D8D0EB;
                border-radius: 4px;
                padding: 3px 10px;
                font-weight: 800;
                font-size: 10px;
                letter-spacing: 0.5px;
            }
        """)
        eyebrow_row.addWidget(eyebrow_badge)
        eyebrow_row.addStretch()
        hc_layout.addLayout(eyebrow_row)

        # Main Heading
        hero_h1 = QLabel("Turn conversations into useful knowledge.")
        hero_h1.setStyleSheet("font-size: 21px; font-weight: 800; color: #1E2B4B; line-height: 1.25;")
        hero_h1.setWordWrap(True)
        hc_layout.addWidget(hero_h1)

        # Supporting Text
        hero_desc = QLabel(
            "Record meetings, capture ideas, and transform voice into structured transcripts, "
            "insights, summaries, and actionable tasks — with a privacy-first desktop experience."
        )
        hero_desc.setObjectName("subtitleLabel")
        hero_desc.setStyleSheet("color: #5C6479; font-size: 12px; line-height: 1.35;")
        hero_desc.setWordWrap(True)
        hc_layout.addWidget(hero_desc)

        # Workflow Ribbon with Pulsing Mic & Harmonic Waveform
        wf_container = QFrame()
        wf_container.setObjectName("glassFrame")
        wf_container.setStyleSheet("""
            QFrame#glassFrame {
                background-color: #F8F6F0;
                border: 1px solid #E5E0D6;
                border-radius: 8px;
            }
        """)
        wf_lay = QVBoxLayout(wf_container)
        wf_lay.setContentsMargins(12, 8, 12, 8)
        wf_lay.setSpacing(6)

        # Workflow Step Row
        wf_row = QHBoxLayout()
        wf_row.setSpacing(10)
        
        self.pulse_mic = PulseMicWidget(size=44)
        wf_row.addWidget(self.pulse_mic)

        wf_seq_lbl = QLabel(
            "<span style='color: #6D59A7; font-weight: 800;'>RECORD</span> "
            "<span style='color: #A39C90;'>➔</span> "
            "<span style='color: #3B82F6; font-weight: 800;'>TRANSCRIBE</span> "
            "<span style='color: #A39C90;'>➔</span> "
            "<span style='color: #0D9488; font-weight: 800;'>UNDERSTAND</span> "
            "<span style='color: #A39C90;'>➔</span> "
            "<span style='color: #2E7D32; font-weight: 800;'>ACT</span>"
        )
        wf_seq_lbl.setStyleSheet("font-size: 11px; letter-spacing: 0.5px;")
        wf_row.addWidget(wf_seq_lbl)
        wf_row.addStretch()
        wf_lay.addLayout(wf_row)

        # Continuous Harmonic Waveform Visualizer
        self.waveform_widget = AnimatedWaveformWidget(height=34, bar_count=42)
        wf_lay.addWidget(self.waveform_widget)

        hc_layout.addWidget(wf_container)
        left_layout.addWidget(hero_card)

        # AI Processing Traveling-Dot Pipeline
        self.pipeline_widget = AnimatedPipelineWidget()
        left_layout.addWidget(self.pipeline_widget)

        # 4 Interactive Feature Cards in 2x2 Bento Grid (Generic User-Facing Benefits)
        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)

        self.card_rec = InteractiveFeatureCard(
            icon_name="microphone",
            title="Smart Recording",
            description="Capture meetings, conversations & voice notes.",
            tag_text="RECORD",
            tag_color="#6D59A7",
            tag_bg="#F2EFF9",
            tag_border="#D8D0EB"
        )
        self.card_stt = InteractiveFeatureCard(
            icon_name="waveform",
            title="AI Transcription",
            description="Convert speech into accurate structured text.",
            tag_text="TRANSCRIBE",
            tag_color="#2563EB",
            tag_bg="#EFF6FF",
            tag_border="#BFDBFE"
        )
        self.card_spk = InteractiveFeatureCard(
            icon_name="users",
            title="Speaker Detection",
            description="Separate and organize multi-speaker conversations.",
            tag_text="SPEAKERS",
            tag_color="#0D9488",
            tag_bg="#F0FDFA",
            tag_border="#99F6E4"
        )
        self.card_ins = InteractiveFeatureCard(
            icon_name="sparkles",
            title="AI Insights",
            description="Extract summaries, topics and actionable information.",
            tag_text="INSIGHTS",
            tag_color="#7C3AED",
            tag_bg="#F5F3FF",
            tag_border="#DDD6FE"
        )

        cards_grid.addWidget(self.card_rec, 0, 0)
        cards_grid.addWidget(self.card_stt, 0, 1)
        cards_grid.addWidget(self.card_spk, 1, 0)
        cards_grid.addWidget(self.card_ins, 1, 1)
        left_layout.addLayout(cards_grid)

        # Compact Capabilities Chips Section
        chips_box = QFrame()
        chips_box.setObjectName("glassFrame")
        chips_box.setStyleSheet("""
            QFrame#glassFrame {
                background-color: #F8F6F0;
                border: 1px solid #E5E0D6;
                border-radius: 8px;
            }
        """)
        chips_lay = QVBoxLayout(chips_box)
        chips_lay.setContentsMargins(12, 8, 12, 8)
        chips_lay.setSpacing(6)

        chips_row1 = QHBoxLayout()
        chips_row1.setSpacing(6)
        chips_row1.addWidget(CapabilityChip("microphone", "Smart Recording"))
        chips_row1.addWidget(CapabilityChip("waveform", "AI Transcription"))
        chips_row1.addWidget(CapabilityChip("users", "Speaker Detection"))
        chips_row1.addWidget(CapabilityChip("sparkles", "AI Insights"))
        chips_row1.addStretch()

        chips_row2 = QHBoxLayout()
        chips_row2.setSpacing(6)
        chips_row2.addWidget(CapabilityChip("check_circle", "Action Items"))
        chips_row2.addWidget(CapabilityChip("search", "Semantic Search"))
        chips_row2.addWidget(CapabilityChip("cpu", "Local Processing"))
        chips_row2.addWidget(CapabilityChip("database", "Secure Storage"))
        chips_row2.addStretch()

        chips_lay.addLayout(chips_row1)
        chips_lay.addLayout(chips_row2)
        left_layout.addWidget(chips_box)

        # Privacy Trust Badge
        self.trust_badge = PrivacyTrustBadge()
        left_layout.addWidget(self.trust_badge)

        # Team & Project Footer Pill
        footer_card = QFrame()
        footer_card.setObjectName("glassFrame")
        footer_card.setStyleSheet("background-color: #F8F6F0; border: 1px solid #E5E0D6; border-radius: 6px;")
        ft_lay = QHBoxLayout(footer_card)
        ft_lay.setContentsMargins(14, 6, 14, 6)
        ft_lbl = QLabel("VoiceNote Desktop Studio • Samar (UI/UX) • Tejas (Architecture) • Atharv (AI Lead)")
        ft_lbl.setStyleSheet("color: #7A8299; font-size: 11px; font-weight: 600;")
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
        self.btn_login = QPushButton("Sign In to Studio")
        self.btn_login.setObjectName("primaryBtn")
        self.btn_login.setFixedHeight(42)
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

        # Loading Progress Bar & Status (Option A)
        self.signin_progress = QProgressBar()
        self.signin_progress.setRange(0, 0)
        self.signin_progress.setFixedHeight(6)
        self.signin_progress.setTextVisible(False)
        self.signin_progress.setStyleSheet("""
            QProgressBar {
                background-color: #E2DDD3;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6D59A7, stop:0.5 #8E74D5, stop:1 #6D59A7);
                border-radius: 3px;
            }
        """)
        self.signin_progress.hide()
        layout.addWidget(self.signin_progress)

        self.signin_status = QLabel("")
        self.signin_status.setStyleSheet("font-size: 12px; font-weight: 600; color: #6D59A7;")
        self.signin_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.signin_status.hide()
        layout.addWidget(self.signin_status)

        # Quick Demo Button
        self.btn_demo = QPushButton("Quick Demo Sign In (Admin)")
        self.btn_demo.setFixedHeight(36)
        self.btn_demo.clicked.connect(self.handle_demo_login)
        layout.addWidget(self.btn_demo)

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
        self.btn_register = QPushButton("Create Account & Sign In")
        self.btn_register.setObjectName("primaryBtn")
        self.btn_register.setFixedHeight(42)
        self.btn_register.clicked.connect(self.handle_register)
        layout.addWidget(self.btn_register)

        # Loading Progress Bar & Status (Option A)
        self.reg_progress = QProgressBar()
        self.reg_progress.setRange(0, 0)
        self.reg_progress.setFixedHeight(6)
        self.reg_progress.setTextVisible(False)
        self.reg_progress.setStyleSheet("""
            QProgressBar {
                background-color: #E2DDD3;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6D59A7, stop:0.5 #8E74D5, stop:1 #6D59A7);
                border-radius: 3px;
            }
        """)
        self.reg_progress.hide()
        layout.addWidget(self.reg_progress)

        self.reg_status = QLabel("")
        self.reg_status.setStyleSheet("font-size: 12px; font-weight: 600; color: #6D59A7;")
        self.reg_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reg_status.hide()
        layout.addWidget(self.reg_status)

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
    def _update_spinner_frame(self):
        if self.active_loading_btn:
            self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner_frames)
            frame = self.spinner_frames[self.spinner_idx]
            self.active_loading_btn.setText(f"{frame}  {self.active_loading_text}")

    def start_button_spinner(self, button: QPushButton, text: str):
        self.active_loading_btn = button
        self.active_loading_text = text
        self.spinner_idx = 0
        button.setText(f"{self.spinner_frames[0]}  {text}")
        self.spinner_timer.start()

    def stop_button_spinner(self):
        self.spinner_timer.stop()
        self.active_loading_btn = None
        self.active_loading_text = ""

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

    def set_signin_loading(self, is_loading: bool, status_text: str = "Authenticating..."):
        self.is_authenticating = is_loading
        self.login_user_input.setEnabled(not is_loading)
        self.login_pwd_input.setEnabled(not is_loading)
        self.btn_toggle_login_pwd.setEnabled(not is_loading)
        self.btn_login.setEnabled(not is_loading)
        self.btn_demo.setEnabled(not is_loading)
        self.tabs.tabBar().setEnabled(not is_loading)

        if is_loading:
            self.signin_error_label.hide()
            self.start_button_spinner(self.btn_login, "Authenticating...")
            self.signin_progress.show()
            self.signin_status.setText(status_text)
            self.signin_status.setStyleSheet("font-size: 12px; font-weight: 600; color: #6D59A7;")
            self.signin_status.show()
        else:
            self.stop_button_spinner()
            self.btn_login.setText("Sign In to Studio")
            self.btn_login.setStyleSheet("")
            self.signin_progress.hide()
            self.signin_status.hide()

    def set_signin_success(self, status_text: str = "Preparing workspace..."):
        self.stop_button_spinner()
        self.btn_login.setText("✓  Authenticated!")
        self.btn_login.setStyleSheet(
            "background-color: #2E7D32; color: #FFFFFF; font-weight: 800; border: none;"
        )
        self.signin_status.setText(f"🚀  {status_text}")
        self.signin_status.setStyleSheet("color: #2E7D32; font-size: 12px; font-weight: 700;")
        self.signin_status.show()
        self.signin_progress.show()

    def set_register_loading(self, is_loading: bool, status_text: str = "Creating account..."):
        self.is_authenticating = is_loading
        self.reg_fullname_input.setEnabled(not is_loading)
        self.reg_username_input.setEnabled(not is_loading)
        self.reg_email_input.setEnabled(not is_loading)
        self.reg_pwd_input.setEnabled(not is_loading)
        self.reg_confirm_input.setEnabled(not is_loading)
        self.btn_register.setEnabled(not is_loading)
        self.tabs.tabBar().setEnabled(not is_loading)

        if is_loading:
            self.reg_error_label.hide()
            self.start_button_spinner(self.btn_register, "Creating account...")
            self.reg_progress.show()
            self.reg_status.setText(status_text)
            self.reg_status.setStyleSheet("font-size: 12px; font-weight: 600; color: #6D59A7;")
            self.reg_status.show()
        else:
            self.stop_button_spinner()
            self.btn_register.setText("Create Account & Sign In")
            self.btn_register.setStyleSheet("")
            self.reg_progress.hide()
            self.reg_status.hide()

    def set_register_success(self, status_text: str = "Preparing workspace..."):
        self.stop_button_spinner()
        self.btn_register.setText("✓  Account Created!")
        self.btn_register.setStyleSheet(
            "background-color: #2E7D32; color: #FFFFFF; font-weight: 800; border: none;"
        )
        self.reg_status.setText(f"🚀  {status_text}")
        self.reg_status.setStyleSheet("color: #2E7D32; font-size: 12px; font-weight: 700;")
        self.reg_status.show()
        self.reg_progress.show()

    def reset_form(self):
        """Reset the form to a clean signin state (used e.g. after logout)."""
        self.is_authenticating = False
        self.is_transitioning = False
        self.authenticated_user = None
        self.stop_button_spinner()

        self.login_user_input.setEnabled(True)
        self.login_pwd_input.setEnabled(True)
        self.btn_toggle_login_pwd.setEnabled(True)
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Sign In to Studio")
        self.btn_login.setStyleSheet("")
        self.btn_demo.setEnabled(True)
        self.signin_progress.hide()
        self.signin_status.hide()
        self.signin_error_label.hide()

        self.reg_fullname_input.setEnabled(True)
        self.reg_username_input.setEnabled(True)
        self.reg_email_input.setEnabled(True)
        self.reg_pwd_input.setEnabled(True)
        self.reg_confirm_input.setEnabled(True)
        self.btn_register.setEnabled(True)
        self.btn_register.setText("Create Account & Sign In")
        self.btn_register.setStyleSheet("")
        self.reg_progress.hide()
        self.reg_status.hide()
        self.reg_error_label.hide()

        self.tabs.tabBar().setEnabled(True)
        self.tabs.setCurrentIndex(0)

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            if hasattr(self, "btn_maximize"):
                self.btn_maximize.update_icon("win_maximize")
                self.btn_maximize.setToolTip("Maximize")
        else:
            self.showMaximized()
            if hasattr(self, "btn_maximize"):
                self.btn_maximize.update_icon("win_restore")
                self.btn_maximize.setToolTip("Restore")

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if hasattr(self, "btn_maximize"):
                if self.isMaximized():
                    self.btn_maximize.update_icon("win_restore")
                    self.btn_maximize.setToolTip("Restore")
                else:
                    self.btn_maximize.update_icon("win_maximize")
                    self.btn_maximize.setToolTip("Maximize")
        super().changeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, "top_header") and self.top_header:
                header_rect = self.top_header.geometry()
                pos = event.position().toPoint()
                if header_rect.contains(pos):
                    child = self.top_header.childAt(self.top_header.mapFromParent(pos))
                    if not isinstance(child, QPushButton):
                        self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                        event.accept()
                        return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos") and self._drag_pos is not None:
            if not self.isMaximized():
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, "top_header") and self.top_header:
                header_rect = self.top_header.geometry()
                pos = event.position().toPoint()
                if header_rect.contains(pos):
                    child = self.top_header.childAt(self.top_header.mapFromParent(pos))
                    if not isinstance(child, QPushButton):
                        self.toggle_maximize_restore()
                        event.accept()
                        return
        super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "particles_overlay") and self.particles_overlay:
            self.particles_overlay.resize(self.width(), self.height())

    def showEvent(self, event):
        super().showEvent(event)
        self._start_all_animations()

    def hideEvent(self, event):
        self._stop_all_animations()
        super().hideEvent(event)

    def closeEvent(self, event):
        if self.is_transitioning:
            self._stop_all_animations()
            event.accept()
            return
        if self.is_authenticating:
            # Prevent closing while in the middle of auth
            event.ignore()
            return
        self._stop_all_animations()
        super().closeEvent(event)

    def _start_all_animations(self):
        if hasattr(self, "waveform_widget") and self.waveform_widget:
            self.waveform_widget.start_animation()
        if hasattr(self, "pulse_mic") and self.pulse_mic:
            self.pulse_mic.start_animation()
        if hasattr(self, "pipeline_widget") and self.pipeline_widget:
            self.pipeline_widget.start_animation()
        if hasattr(self, "particles_overlay") and self.particles_overlay:
            self.particles_overlay.start_animation()

    def _stop_all_animations(self):
        if hasattr(self, "waveform_widget") and self.waveform_widget:
            self.waveform_widget.stop_animation()
        if hasattr(self, "pulse_mic") and self.pulse_mic:
            self.pulse_mic.stop_animation()
        if hasattr(self, "pipeline_widget") and self.pipeline_widget:
            self.pipeline_widget.stop_animation()
        if hasattr(self, "particles_overlay") and self.particles_overlay:
            self.particles_overlay.stop_animation()
        self.stop_button_spinner()

    def handle_login(self):
        if self.is_authenticating:
            return

        self.signin_error_label.hide()
        ident = self.login_user_input.text().strip()
        pwd = self.login_pwd_input.text()

        if not ident or not pwd:
            self.show_signin_error("Please enter both username/email and password.")
            return

        # Start loading state immediately
        self.set_signin_loading(True, "Verifying credentials...")

        # Non-blocking auth call via QTimer so spinner and progress bar render smoothly first
        QTimer.singleShot(80, self._perform_login)

    def _perform_login(self):
        ident = self.login_user_input.text().strip()
        pwd = self.login_pwd_input.text()

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
            self.set_signin_success("Authenticated! Preparing workspace...")
            self.user_authenticated.emit(self.authenticated_user)
            return

        try:
            user = self.db.verify_user_login(ident, pwd)
            if user:
                logger.info(f"User '{user['username']}' authenticated successfully.")
                self.authenticated_user = user
                self.set_signin_success("Authenticated! Preparing workspace...")
                self.user_authenticated.emit(self.authenticated_user)
            else:
                self.set_signin_loading(False)
                self.show_signin_error("Invalid credentials. Please check your username and password.")
        except Exception as err:
            logger.error(f"Authentication query error: {err}")
            self.set_signin_loading(False)
            self.show_signin_error(f"Database error during login: {err}")

    def handle_demo_login(self):
        """Quickly sign in as the default admin user."""
        if self.is_authenticating:
            return
        self.login_user_input.setText("admin")
        self.login_pwd_input.setText("admin123")
        self.handle_login()

    def handle_register(self):
        if self.is_authenticating:
            return

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

        # Start loading animation
        self.set_register_loading(True, "Creating account in PostgreSQL...")
        QTimer.singleShot(80, self._perform_register)

    def _perform_register(self):
        full_name = self.reg_fullname_input.text().strip()
        username = self.reg_username_input.text().strip().lower()
        email = self.reg_email_input.text().strip().lower()
        pwd = self.reg_pwd_input.text()

        try:
            # Check unique username
            existing_user = self.db.get_user_by_username(username)
            if existing_user:
                self.set_register_loading(False)
                self.show_register_error(f"Username '{username}' is already taken.")
                return

            # Check unique email
            existing_email = self.db.get_user_by_email(email)
            if existing_email:
                self.set_register_loading(False)
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

            self.authenticated_user = {
                "id": new_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "password_hash": new_user.password_hash,
                "created_at": new_user.created_at
            }

            self.set_register_success("Account created! Launching workspace...")
            self.user_authenticated.emit(self.authenticated_user)

        except Exception as err:
            logger.error(f"Registration error: {err}")
            self.set_register_loading(False)
            self.show_register_error(f"Failed to register account: {err}")

    def get_user(self) -> Optional[Dict[str, Any]]:
        """Return the authenticated user dictionary."""
        return self.authenticated_user

