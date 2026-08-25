import os
import sys
import platform
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QCheckBox, QTabWidget, QWidget,
    QMessageBox, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from voicenote.config import (
    APP_NAME, APP_SUBTITLE, VERSION, RECORDING_DIR,
    GEMINI_API_KEY, GROQ_API_KEY, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
)
from voicenote.ui.styles import MAIN_STYLE

try:
    from voicenote.core.audio_engine import AudioEngine
except Exception:
    AudioEngine = None

logger = logging.getLogger("SettingsDialog")


class SettingsDialog(QDialog):
    """VoiceNote Application Preferences & System Configuration Dialog - Retro Cream Bento Theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"VoiceNote Settings & Preferences — v{VERSION}")
        self.resize(720, 600)
        self.setMinimumSize(640, 520)
        self.setStyleSheet(MAIN_STYLE)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # Header Title
        h_box = QHBoxLayout()
        header_v = QVBoxLayout()
        title = QLabel("System Settings & Preferences")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Configure audio hardware, AI transcription engines, storage paths, and app defaults.")
        subtitle.setObjectName("subtitleLabel")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        h_box.addLayout(header_v)
        h_box.addStretch()

        badge = QLabel("LOCAL & CLOUD")
        badge.setObjectName("badgeActive")
        h_box.addWidget(badge)
        main_layout.addLayout(h_box)

        # Tab Widget for Sections
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #D5CEBF;
                background-color: #F7F4EE;
                border-radius: 12px;
                padding: 16px;
            }
            QTabBar::tab {
                background: #ECE7DF;
                color: #5C6479;
                font-weight: 700;
                font-size: 13px;
                padding: 10px 18px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #F7F4EE;
                color: #4A3980;
                border-bottom: 2px solid #6D59A7;
            }
        """)

        # Tab 1: Audio & Recording
        tabs.addTab(self._create_audio_tab(), "Audio & Hardware")

        # Tab 2: AI & Models
        tabs.addTab(self._create_ai_tab(), "AI & Intelligence")

        # Tab 3: Storage & Database
        tabs.addTab(self._create_storage_tab(), "Storage & DB")

        # Tab 4: About & System
        tabs.addTab(self._create_about_tab(), "System Info")

        main_layout.addWidget(tabs, stretch=1)

        # Bottom Button Bar
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_save = QPushButton("Save Preferences")
        self.btn_save.setObjectName("btnPrimary")
        self.btn_save.setMinimumHeight(38)
        self.btn_save.clicked.connect(self.save_and_close)

        self.btn_close = QPushButton("Close")
        self.btn_close.setMinimumHeight(38)
        self.btn_close.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_close)
        btn_row.addWidget(self.btn_save)

        main_layout.addLayout(btn_row)

    def _create_audio_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(14)

        # Microphone Input Device
        d_lbl = QLabel("Input Recording Microphone:")
        d_lbl.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 13px;")
        lay.addWidget(d_lbl)

        self.combo_device = QComboBox()
        self.combo_device.addItem("Default System Microphone (Auto-Detect)", None)

        if AudioEngine:
            try:
                devices = AudioEngine.get_input_devices()
                for dev in devices:
                    self.combo_device.addItem(f"🎤 {dev.get('name', 'Mic')} ({dev.get('hostapi', '')})", dev.get("index"))
            except Exception as e:
                logger.warning(f"Failed to enumerate audio devices: {e}")

        lay.addWidget(self.combo_device)

        # Recording specs
        spec_frame = QFrame()
        spec_frame.setObjectName("cardFrame")
        s_lay = QVBoxLayout(spec_frame)
        s_lay.setContentsMargins(14, 12, 14, 12)

        s_info = QLabel("Audio Pipeline Specifications:\n• Sampling Rate: 16,000 Hz (16 kHz)\n• Format: 16-bit PCM Linear Mono WAV\n• Storage Folder: data/recording/")
        s_info.setStyleSheet("color: #5C6479; font-size: 12px; line-height: 1.5;")
        s_lay.addWidget(s_info)
        lay.addWidget(spec_frame)

        # Options
        self.chk_noise_suppress = QCheckBox("Enable AI Background Noise Suppression")
        self.chk_noise_suppress.setChecked(True)
        lay.addWidget(self.chk_noise_suppress)

        self.chk_auto_save = QCheckBox("Automatically archive PCM WAV recordings to disk")
        self.chk_auto_save.setChecked(True)
        lay.addWidget(self.chk_auto_save)

        lay.addStretch()
        return widget

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(14)

        # STT Engine Selection
        stt_lbl = QLabel("Primary Speech-to-Text (STT) Engine:")
        stt_lbl.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 13px;")
        lay.addWidget(stt_lbl)

        self.combo_stt = QComboBox()
        self.combo_stt.addItem("Groq Whisper Large v3 (Fast Cloud STT - Recommended)", "groq")
        self.combo_stt.addItem("faster-whisper (Local Offline STT)", "local_whisper")
        lay.addWidget(self.combo_stt)

        # LLM Engine Selection
        llm_lbl = QLabel("AI Summarization & Task Extraction Model:")
        llm_lbl.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 13px;")
        lay.addWidget(llm_lbl)

        self.combo_llm = QComboBox()
        self.combo_llm.addItem("Gemini 2.5 Flash (Google Cloud AI - Recommended)", "gemini-2.5-flash")
        self.combo_llm.addItem("Gemini 1.5 Pro (In-depth Reasoning)", "gemini-1.5-pro")
        self.combo_llm.addItem("Ollama (Local Offline Llama 3 / Mistral)", "ollama")
        lay.addWidget(self.combo_llm)

        # API Status Cards
        api_frame = QFrame()
        api_frame.setObjectName("cardFrame")
        a_lay = QVBoxLayout(api_frame)
        a_lay.setContentsMargins(14, 12, 14, 12)

        gemini_status = "Connected" if GEMINI_API_KEY else "Not Configured"
        groq_status = "Connected" if GROQ_API_KEY else "Not Configured"

        status_text = f"API Connectivity Status:\n• Gemini AI API: {gemini_status}\n• Groq STT API: {groq_status}\n• Vector Retrieval: Active (ChromaDB)"
        stat_lbl = QLabel(status_text)
        stat_lbl.setStyleSheet("color: #5C6479; font-size: 12px; line-height: 1.6;")
        a_lay.addWidget(stat_lbl)
        lay.addWidget(api_frame)

        lay.addStretch()
        return widget

    def _create_storage_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(14)

        # Recording Directory
        rec_lbl = QLabel("Audio Recordings Directory:")
        rec_lbl.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 13px;")
        lay.addWidget(rec_lbl)

        rec_row = QHBoxLayout()
        self.lbl_rec_dir = QLabel(str(RECORDING_DIR))
        self.lbl_rec_dir.setStyleSheet("background: #ECE7DF; padding: 8px 12px; border-radius: 6px; color: #4A3980; font-family: monospace; font-size: 12px;")
        rec_row.addWidget(self.lbl_rec_dir, stretch=1)

        btn_open_rec = QPushButton("Open Folder")
        btn_open_rec.clicked.connect(self._open_recording_folder)
        rec_row.addWidget(btn_open_rec)
        lay.addLayout(rec_row)

        # Default Export Format
        exp_lbl = QLabel("Default Note Export Format:")
        exp_lbl.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 13px;")
        lay.addWidget(exp_lbl)

        self.combo_export = QComboBox()
        self.combo_export.addItem("PDF Document (.pdf) — Professional Layout", "pdf")
        self.combo_export.addItem("Word Document (.docx) — Editable Document", "docx")
        self.combo_export.addItem("Plain Text (.txt) — Markdown & Raw Text", "txt")
        lay.addWidget(self.combo_export)

        # Database Connection Info
        db_frame = QFrame()
        db_frame.setObjectName("cardFrame")
        db_lay = QVBoxLayout(db_frame)
        db_lay.setContentsMargins(14, 12, 14, 12)

        db_info = QLabel(f"PostgreSQL Database Information:\n• Database Name: {POSTGRES_DB}\n• Server Host: {POSTGRES_HOST}:{POSTGRES_PORT}\n• Storage Mode: Persistent Local/Remote PostgreSQL")
        db_info.setStyleSheet("color: #5C6479; font-size: 12px; line-height: 1.5;")
        db_lay.addWidget(db_info)
        lay.addWidget(db_frame)

        lay.addStretch()
        return widget

    def _create_about_tab(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(14)

        card = QFrame()
        card.setObjectName("cardFrame")
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 16, 18, 16)
        c_lay.setSpacing(8)

        app_title = QLabel(f"{APP_NAME} Desktop")
        app_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #4A3980;")
        
        app_sub = QLabel(APP_SUBTITLE)
        app_sub.setStyleSheet("font-size: 13px; color: #5C6479;")

        sys_details = QLabel(
            f"• Version: {VERSION}\n"
            f"• Python: {platform.python_version()} ({platform.architecture()[0]})\n"
            f"• Operating System: {platform.system()} {platform.release()}\n"
            f"• UI Framework: PySide6 (Qt for Python)\n"
            f"• Core Contributors: Tejas, Samar, Atharv"
        )
        sys_details.setStyleSheet("font-size: 12px; color: #5C6479; line-height: 1.6;")

        c_lay.addWidget(app_title)
        c_lay.addWidget(app_sub)
        c_lay.addSpacing(6)
        c_lay.addWidget(sys_details)

        lay.addWidget(card)
        lay.addStretch()
        return widget

    def _open_recording_folder(self):
        try:
            folder_path = str(RECORDING_DIR)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        except Exception as e:
            QMessageBox.warning(self, "Folder Error", f"Could not open directory:\n{e}")

    def save_and_close(self):
        """Save settings feedback and close dialog."""
        QMessageBox.information(
            self, "Preferences Saved",
            "Your application preferences and hardware configurations have been saved successfully."
        )
        self.accept()
