import os
import shutil
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QFileDialog, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon

from voicenote.config import RECORDING_DIR
from voicenote.core.audio_engine import (
    AudioEngine, get_input_devices, is_system_audio_available, get_loopback_device
)
from voicenote.ui.components.waveform_widget import WaveformWidget
from voicenote.ui.icon_helper import get_svg_icon, get_svg_pixmap

logger = logging.getLogger("AudioRecorder")


class AudioRecorderWidget(QWidget):
    """
    Professional Audio Recording and Ingestion Component:
    - Vector SVG icons (replacing Unicode emojis).
    - Producer/consumer callback-driven live audio monitoring (25-30 fps).
    - Calibrated dBFS meters with attack/release smoothing and clipping warnings.
    - True signal states: Waiting for audio, Good signal, Low signal, Input too loud, Playing, Silent.
    - Real-amplitude reactive waveform (flat baseline on silence, dynamic on speech/playback).
    - Multilingual selection (Auto Detect, Marathi, Hindi, English).
    - Dynamic device enumeration & hot-plugging.
    - Clean Windows WASAPI loopback capture.
    """
    transcription_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.seconds_elapsed = 0
        self.is_paused = False
        self.active_audio_payload = "Live Voice Recording"
        self.audio_engine = AudioEngine()
        self.source_mode = "both" if is_system_audio_available() else "mic"
        self.is_testing_audio = False
        self.selected_language: Optional[str] = None  # None = Auto Detect

        self.init_ui()

        # Periodic background check to detect newly plugged or unplugged devices
        self.device_check_timer = QTimer(self)
        self.device_check_timer.setInterval(4000)
        self.device_check_timer.timeout.connect(self._background_device_check)
        self.device_check_timer.start()

        # Real-time audio monitor timer (~30 fps / 33 ms)
        self.monitor_timer = QTimer(self)
        self.monitor_timer.setInterval(33)
        self.monitor_timer.timeout.connect(self._update_realtime_monitor)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_input_devices()

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.is_testing_audio:
            self.toggle_audio_test()

    def _on_mic_device_changed(self, index: int):
        """Handle user changing microphone in dropdown."""
        selected_idx = self.mic_combo.currentData()
        name = self.mic_combo.currentText()
        logger.info(f"Microphone selection changed: index={selected_idx}, name='{name}'")
        if hasattr(self, "telemetry_dev_label"):
            self.telemetry_dev_label.setText(f"Mic: {name}")
        if self.is_testing_audio:
            self.audio_engine.switch_monitoring_device(selected_idx)

    def refresh_input_devices(self, notify: bool = False):
        """Refresh the microphone list while preserving current selection if still valid, or selecting default."""
        cur_id = self.mic_combo.currentData()
        self.mic_combo.blockSignals(True)
        self.mic_combo.clear()

        devices = get_input_devices()
        selected_idx = 0
        for i, (idx, name) in enumerate(devices):
            # Use headphones or mic icon
            is_headset = any(x in name.lower() for x in ["headset", "airpods", "earbuds", "headphones", "bluetooth"])
            icon_name = "headphones" if is_headset else "mic"
            self.mic_combo.addItem(get_svg_icon(icon_name, size=16), name, idx)
            if cur_id is not None and idx == cur_id:
                selected_idx = i

        if self.mic_combo.count() > 0:
            self.mic_combo.setCurrentIndex(selected_idx)
        self.mic_combo.blockSignals(False)

        # Update active telemetry label if initialized
        if hasattr(self, "telemetry_dev_label") and self.mic_combo.count() > 0:
            self.telemetry_dev_label.setText(f"Mic: {self.mic_combo.currentText()}")

        # If currently testing, dynamically switch monitoring to the active device
        if self.is_testing_audio:
            self.audio_engine.switch_monitoring_device(self.mic_combo.currentData())

        # Update system audio status tag
        sys_avail = is_system_audio_available()
        if sys_avail:
            self.sys_audio_tag.setText("✓ System Audio Loopback Ready")
            self.sys_audio_tag.setStyleSheet("color: #10B981; font-weight: 700; font-size: 11px;")
            self.btn_mode_sys.setEnabled(True)
            self.btn_mode_both.setEnabled(True)
        else:
            self.sys_audio_tag.setText("⚠ System Audio Unavailable")
            self.sys_audio_tag.setStyleSheet("color: #D97706; font-weight: 700; font-size: 11px;")
            self.btn_mode_sys.setEnabled(False)
            self.btn_mode_both.setEnabled(False)
            if self.source_mode in ("system", "both"):
                self.set_source_mode("mic")

        if notify:
            active_name = self.mic_combo.currentText()
            logger.info(f"Audio capture devices refreshed. Active: {active_name}")

    def _background_device_check(self):
        """Background device scan to detect new headphones/USB mics without restarting."""
        if self.waveform.is_recording or self.is_testing_audio:
            return

        devices = get_input_devices()
        current_names = [self.mic_combo.itemText(i) for i in range(self.mic_combo.count())]
        new_names = [name for _, name in devices]

        if current_names != new_names:
            logger.info("Detected audio hardware change. Updating device list...")
            self.refresh_input_devices()

    def set_source_mode(self, mode: str):
        """Toggle source mode between 'mic', 'system', and 'both'."""
        self.source_mode = mode
        self.audio_engine.set_source_mode(mode)

        active_style = (
            "QPushButton { background-color: #6D59A7; color: #FFFFFF; font-weight: 700; "
            "border: 1px solid #5B4896; border-radius: 6px; padding: 6px 14px; text-align: center; } "
            "QPushButton:hover { background-color: #5B4896; }"
        )
        inactive_style = (
            "QPushButton { background-color: #FFFFFF; color: #1E2B4B; font-weight: 600; "
            "border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 14px; text-align: center; } "
            "QPushButton:hover { background-color: #F8FAFC; border-color: #94A3B8; }"
        )

        self.btn_mode_mic.setStyleSheet(active_style if mode == "mic" else inactive_style)
        self.btn_mode_mic.setIcon(get_svg_icon("mic", color="#FFFFFF" if mode == "mic" else "#1E2B4B", size=16))

        self.btn_mode_sys.setStyleSheet(active_style if mode == "system" else inactive_style)
        self.btn_mode_sys.setIcon(get_svg_icon("monitor-speaker", color="#FFFFFF" if mode == "system" else "#1E2B4B", size=16))

        self.btn_mode_both.setStyleSheet(active_style if mode == "both" else inactive_style)
        self.btn_mode_both.setIcon(get_svg_icon("activity", color="#FFFFFF" if mode == "both" else "#1E2B4B", size=16))

        # Show/hide relevant meters in test panel
        if mode == "mic":
            self.mic_meter_row.show()
            self.sys_meter_row.hide()
        elif mode == "system":
            self.mic_meter_row.hide()
            self.sys_meter_row.show()
        else:
            self.mic_meter_row.show()
            self.sys_meter_row.show()

    def on_language_changed(self, index: int):
        """Handle target transcription language selection."""
        lang_data = self.lang_combo.currentData()
        self.selected_language = lang_data
        logger.info(f"Target transcription language set to: {lang_data or 'Auto Detect'}")

    def toggle_audio_test(self):
        """Start or stop the pre-recording live audio level test."""
        if not self.is_testing_audio:
            self.is_testing_audio = True
            self.btn_test_audio.setText("Stop Test")
            self.btn_test_audio.setIcon(get_svg_icon("square", color="#FFFFFF", size=14))
            self.btn_test_audio.setStyleSheet(
                "QPushButton { background-color: #D04966; color: #FFFFFF; font-weight: 700; "
                "border: 1px solid #B93854; border-radius: 6px; padding: 6px 14px; } "
                "QPushButton:hover { background-color: #B93854; }"
            )
            self.test_panel.show()
            self.waveform.set_testing(True)
            selected_idx = self.mic_combo.currentData()
            self.audio_engine.start_monitoring(device_index=selected_idx, source_mode=self.source_mode)
            self.monitor_timer.start()

            if hasattr(self, "live_indicator"):
                self.live_indicator.setText("● AUDIO TEST ACTIVE")
                self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #10B981;")
        else:
            self.is_testing_audio = False
            self.btn_test_audio.setText("Test Audio")
            self.btn_test_audio.setIcon(get_svg_icon("activity", color="#1E2B4B", size=16))
            self.btn_test_audio.setStyleSheet(
                "QPushButton { background-color: #FFFFFF; color: #1E2B4B; font-weight: 700; "
                "border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 14px; } "
                "QPushButton:hover { background-color: #F8FAFC; border-color: #94A3B8; }"
            )
            self.waveform.set_testing(False)
            if not self.waveform.is_recording:
                self.monitor_timer.stop()
                self.audio_engine.stop_monitoring()
                if hasattr(self, "live_indicator"):
                    self.live_indicator.setText("○ READY")
                    self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748B;")
                if hasattr(self, "live_level_bar"):
                    self.live_level_bar.setValue(0)
                if hasattr(self, "live_signal_label"):
                    self.live_signal_label.setText("-∞ dBFS • Standby")
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #64748B;")
            self.test_panel.hide()

    def _update_realtime_monitor(self):
        """
        Runs ~30 times/sec from UI timer.
        Reads thread-safe atomic audio telemetry from non-blocking AudioEngine.
        """
        telemetry = self.audio_engine.get_monitoring_telemetry()

        mic_val = int(telemetry["mic_level"] * 100)
        sys_val = int(telemetry["system_level"] * 100)
        mic_dbfs = telemetry["mic_dbfs"]
        sys_dbfs = telemetry["system_dbfs"]
        mic_status = telemetry["mic_status"]
        sys_status = telemetry["system_status"]

        # Update test panel visual progress meters
        self.mic_meter.setValue(mic_val)
        self.sys_meter.setValue(sys_val)

        # Update test panel dBFS labels
        self.mic_db_label.setText(f"{mic_dbfs:.0f} dBFS" if mic_val > 0 else "-∞ dBFS")
        self.sys_db_label.setText(f"{sys_dbfs:.0f} dBFS" if sys_val > 0 else "-∞ dBFS")

        # Dynamic mic status badge styling
        self.mic_meter_status.setText(mic_status)
        if "loud" in mic_status or "clipping" in mic_status.lower():
            self.mic_meter_status.setStyleSheet("color: #E11D48; font-weight: 700; font-size: 11px;")
        elif "Good" in mic_status:
            self.mic_meter_status.setStyleSheet("color: #10B981; font-weight: 700; font-size: 11px;")
        elif "Low" in mic_status:
            self.mic_meter_status.setStyleSheet("color: #D97706; font-weight: 600; font-size: 11px;")
        else:
            self.mic_meter_status.setStyleSheet("color: #94A3B8; font-size: 11px;")

        # Dynamic system audio status badge styling
        self.sys_meter_status.setText(sys_status)
        if sys_status == "Playing":
            self.sys_meter_status.setStyleSheet("color: #6D59A7; font-weight: 700; font-size: 11px;")
        elif sys_status == "Unavailable":
            self.sys_meter_status.setStyleSheet("color: #D97706; font-size: 11px;")
        else:
            self.sys_meter_status.setStyleSheet("color: #94A3B8; font-size: 11px;")

        # Update Live Audio Telemetry Strip (visible on hero card during recording/testing)
        if hasattr(self, "live_indicator"):
            display_val = max(mic_val, sys_val) if self.source_mode == "both" else (sys_val if self.source_mode == "system" else mic_val)
            display_dbfs = max(mic_dbfs, sys_dbfs) if self.source_mode == "both" else (sys_dbfs if self.source_mode == "system" else mic_dbfs)

            if self.waveform.is_recording and not self.is_paused:
                self.live_indicator.setText("● LIVE CAPTURE ACTIVE")
                self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #E11D48;")
                self.live_level_bar.setValue(display_val)
                self.live_signal_label.setText(f"{display_dbfs:.0f} dBFS • {mic_status}")
                if "Good" in mic_status:
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #10B981;")
                elif "loud" in mic_status or "clipping" in mic_status.lower():
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #E11D48;")
                elif "Low" in mic_status:
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #D97706;")
                else:
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #64748B;")
            elif self.is_testing_audio:
                self.live_indicator.setText("● AUDIO TEST ACTIVE")
                self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #10B981;")
                self.live_level_bar.setValue(display_val)
                self.live_signal_label.setText(f"{display_dbfs:.0f} dBFS • {mic_status}")
                if "Good" in mic_status:
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #10B981;")
                else:
                    self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #64748B;")
                self.waveform.set_live_amplitude(telemetry["mic_level"])

        # If recording is active, feed real combined amplitude directly to waveform visualizer
        if self.waveform.is_recording and not self.is_paused:
            amp = self.audio_engine.get_latest_amplitude()
            self.waveform.set_live_amplitude(amp)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Hero Card
        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(16)

        # ---------------------------------------------------------------------
        # Header Row: Title & Audio Source Selector
        # ---------------------------------------------------------------------
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Live Voice & Meeting Capture")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Capture microphone, system meeting audio (Zoom, Teams, Meet), or both with multilingual AI intelligence.")
        subtitle.setObjectName("subtitleLabel")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)

        header_row.addStretch()

        # Audio Source Mode Buttons
        source_box = QVBoxLayout()
        source_label = QLabel("Audio Source:")
        source_label.setStyleSheet("font-size: 11px; font-weight: 700; color: #5C6479;")
        source_box.addWidget(source_label)

        modes_row = QHBoxLayout()
        modes_row.setSpacing(6)

        self.btn_mode_mic = QPushButton("Microphone")
        self.btn_mode_mic.setIcon(get_svg_icon("mic", size=16))
        self.btn_mode_mic.clicked.connect(lambda: self.set_source_mode("mic"))

        self.btn_mode_sys = QPushButton("System Audio")
        self.btn_mode_sys.setIcon(get_svg_icon("monitor-speaker", size=16))
        self.btn_mode_sys.clicked.connect(lambda: self.set_source_mode("system"))

        self.btn_mode_both = QPushButton("Both")
        self.btn_mode_both.setIcon(get_svg_icon("activity", size=16))
        self.btn_mode_both.clicked.connect(lambda: self.set_source_mode("both"))

        modes_row.addWidget(self.btn_mode_mic)
        modes_row.addWidget(self.btn_mode_sys)
        modes_row.addWidget(self.btn_mode_both)
        source_box.addLayout(modes_row)
        header_row.addLayout(source_box)

        hero_layout.addLayout(header_row)

        # ---------------------------------------------------------------------
        # Device Selection & Language Row
        # ---------------------------------------------------------------------
        dev_row = QHBoxLayout()
        dev_row.setSpacing(10)

        dev_label = QLabel("Input Device:")
        dev_label.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 12px;")
        dev_row.addWidget(dev_label)

        self.mic_combo = QComboBox()
        self.mic_combo.setMinimumWidth(260)
        self.mic_combo.currentIndexChanged.connect(self._on_mic_device_changed)
        dev_row.addWidget(self.mic_combo)

        # Refresh button (Vector SVG)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setIcon(get_svg_icon("refresh-cw", size=14))
        btn_refresh.setToolTip("Scan for newly connected USB or Bluetooth audio devices")
        btn_refresh.setStyleSheet(
            "QPushButton { background-color: #FFFFFF; font-weight: 700; border: 1px solid #CBD5E1; "
            "border-radius: 6px; padding: 6px 12px; color: #1E2B4B; } "
            "QPushButton:hover { background-color: #F8FAFC; border-color: #94A3B8; }"
        )
        btn_refresh.clicked.connect(lambda: self.refresh_input_devices(notify=True))
        dev_row.addWidget(btn_refresh)

        # Pre-recording Test Audio button (Vector SVG)
        self.btn_test_audio = QPushButton("Test Audio")
        self.btn_test_audio.setIcon(get_svg_icon("activity", size=16))
        self.btn_test_audio.setToolTip("Verify microphone and system audio levels before recording")
        self.btn_test_audio.setStyleSheet(
            "QPushButton { background-color: #FFFFFF; font-weight: 700; border: 1px solid #CBD5E1; "
            "border-radius: 6px; padding: 6px 14px; color: #1E2B4B; } "
            "QPushButton:hover { background-color: #F8FAFC; border-color: #94A3B8; }"
        )
        self.btn_test_audio.clicked.connect(self.toggle_audio_test)
        dev_row.addWidget(self.btn_test_audio)

        dev_row.addSpacing(12)

        # Language Selector Combobox
        lang_label = QLabel("Language:")
        lang_label.setStyleSheet("font-weight: 700; color: #1E2B4B; font-size: 12px;")
        dev_row.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.setMinimumWidth(160)
        self.lang_combo.addItem("Auto Detect", None)
        self.lang_combo.addItem("Marathi (मराठी)", "mr")
        self.lang_combo.addItem("Hindi (हिंदी)", "hi")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        dev_row.addWidget(self.lang_combo)

        dev_row.addStretch()

        # System Audio availability status tag
        self.sys_audio_tag = QLabel("Checking System Audio...")
        dev_row.addWidget(self.sys_audio_tag)

        hero_layout.addLayout(dev_row)

        # ---------------------------------------------------------------------
        # Pre-recording Live Audio Monitor Panel (Collapsible)
        # ---------------------------------------------------------------------
        self.test_panel = QFrame()
        self.test_panel.setObjectName("glassFrame")
        self.test_panel.setStyleSheet(
            "QFrame#glassFrame { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px; } "
            "QLabel { border: none; background: transparent; }"
        )
        t_layout = QVBoxLayout(self.test_panel)
        t_layout.setContentsMargins(14, 10, 14, 10)
        t_layout.setSpacing(8)

        t_title = QLabel("<b>Audio Monitor</b> — Real-time signal calibration (RMS + Peak dBFS)")
        t_title.setStyleSheet("font-size: 12px; color: #1E2B4B;")
        t_layout.addWidget(t_title)

        # Microphone Monitor Row
        self.mic_meter_row = QWidget()
        m_row = QHBoxLayout(self.mic_meter_row)
        m_row.setContentsMargins(0, 0, 0, 0)
        m_row.setSpacing(10)

        mic_icon_lbl = QLabel()
        mic_icon_lbl.setPixmap(get_svg_pixmap("mic", color="#1E2B4B", size=16))
        m_row.addWidget(mic_icon_lbl)

        mic_name_lbl = QLabel("Microphone:")
        mic_name_lbl.setFixedWidth(100)
        mic_name_lbl.setStyleSheet("font-weight: 600; color: #1E2B4B; font-size: 12px;")
        m_row.addWidget(mic_name_lbl)

        self.mic_meter = QProgressBar()
        self.mic_meter.setRange(0, 100)
        self.mic_meter.setValue(0)
        self.mic_meter.setTextVisible(False)
        self.mic_meter.setFixedHeight(12)
        self.mic_meter.setStyleSheet(
            "QProgressBar { background: #F1F5F9; border-radius: 6px; border: 1px solid #E2E8F0; } "
            "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:0.8 #F59E0B, stop:1 #EF4444); border-radius: 5px; }"
        )
        m_row.addWidget(self.mic_meter, stretch=1)

        self.mic_db_label = QLabel("-∞ dBFS")
        self.mic_db_label.setFixedWidth(75)
        self.mic_db_label.setStyleSheet("font-family: monospace; font-weight: 700; color: #5C6479; font-size: 11px;")
        m_row.addWidget(self.mic_db_label)

        self.mic_meter_status = QLabel("Waiting for audio")
        self.mic_meter_status.setFixedWidth(110)
        self.mic_meter_status.setStyleSheet("color: #94A3B8; font-size: 11px;")
        m_row.addWidget(self.mic_meter_status)

        t_layout.addWidget(self.mic_meter_row)

        # System Audio Monitor Row
        self.sys_meter_row = QWidget()
        s_row = QHBoxLayout(self.sys_meter_row)
        s_row.setContentsMargins(0, 0, 0, 0)
        s_row.setSpacing(10)

        sys_icon_lbl = QLabel()
        sys_icon_lbl.setPixmap(get_svg_pixmap("monitor-speaker", color="#1E2B4B", size=16))
        s_row.addWidget(sys_icon_lbl)

        sys_name_lbl = QLabel("System Audio:")
        sys_name_lbl.setFixedWidth(100)
        sys_name_lbl.setStyleSheet("font-weight: 600; color: #1E2B4B; font-size: 12px;")
        s_row.addWidget(sys_name_lbl)

        self.sys_meter = QProgressBar()
        self.sys_meter.setRange(0, 100)
        self.sys_meter.setValue(0)
        self.sys_meter.setTextVisible(False)
        self.sys_meter.setFixedHeight(12)
        self.sys_meter.setStyleSheet(
            "QProgressBar { background: #F1F5F9; border-radius: 6px; border: 1px solid #E2E8F0; } "
            "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6D59A7, stop:0.8 #8B5CF6, stop:1 #EC4899); border-radius: 5px; }"
        )
        s_row.addWidget(self.sys_meter, stretch=1)

        self.sys_db_label = QLabel("-∞ dBFS")
        self.sys_db_label.setFixedWidth(75)
        self.sys_db_label.setStyleSheet("font-family: monospace; font-weight: 700; color: #5C6479; font-size: 11px;")
        s_row.addWidget(self.sys_db_label)

        self.sys_meter_status = QLabel("Silent")
        self.sys_meter_status.setFixedWidth(110)
        self.sys_meter_status.setStyleSheet("color: #94A3B8; font-size: 11px;")
        s_row.addWidget(self.sys_meter_status)

        t_layout.addWidget(self.sys_meter_row)

        self.test_panel.hide()
        hero_layout.addWidget(self.test_panel)

        # Refresh initial devices & mode styling
        self.refresh_input_devices()
        self.set_source_mode(self.source_mode)

        # ---------------------------------------------------------------------
        # Waveform & Timer Section
        # ---------------------------------------------------------------------
        waveform_box = QFrame()
        waveform_box.setObjectName("glassFrame")
        wf_layout = QVBoxLayout(waveform_box)
        wf_layout.setContentsMargins(16, 16, 16, 16)

        timer_row = QHBoxLayout()
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 28px; font-weight: 800; font-family: monospace; color: #1E2B4B;")

        self.status_badge = QLabel("IDLE")
        self.status_badge.setObjectName("badgeActive")

        timer_row.addWidget(self.timer_label)
        timer_row.addWidget(self.status_badge)
        timer_row.addStretch()

        fmt_label = QLabel("PCM 16-bit | 16000 Hz Speech-Optimized")
        fmt_label.setStyleSheet("color: #5C6479; font-size: 12px; font-weight: 500;")
        timer_row.addWidget(fmt_label)

        wf_layout.addLayout(timer_row)

        # Live Audio Telemetry Strip (Pulsing state, live volume meter, dBFS, and active device)
        self.telemetry_strip = QFrame()
        self.telemetry_strip.setStyleSheet(
            "QFrame { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 4px 10px; } "
            "QLabel { border: none; background: transparent; }"
        )
        t_strip_layout = QHBoxLayout(self.telemetry_strip)
        t_strip_layout.setContentsMargins(8, 4, 8, 4)
        t_strip_layout.setSpacing(12)

        self.live_indicator = QLabel("○ READY")
        self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748B;")
        t_strip_layout.addWidget(self.live_indicator)

        self.live_level_bar = QProgressBar()
        self.live_level_bar.setRange(0, 100)
        self.live_level_bar.setValue(0)
        self.live_level_bar.setTextVisible(False)
        self.live_level_bar.setFixedSize(130, 8)
        self.live_level_bar.setStyleSheet(
            "QProgressBar { background: #E2E8F0; border-radius: 4px; border: none; } "
            "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:0.8 #F59E0B, stop:1 #EF4444); border-radius: 4px; }"
        )
        t_strip_layout.addWidget(self.live_level_bar)

        self.live_signal_label = QLabel("-∞ dBFS • Standby")
        self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #64748B;")
        t_strip_layout.addWidget(self.live_signal_label)

        t_strip_layout.addStretch()

        self.telemetry_dev_label = QLabel("Mic: Standby")
        self.telemetry_dev_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #1E2B4B;")
        t_strip_layout.addWidget(self.telemetry_dev_label)

        wf_layout.addWidget(self.telemetry_strip)

        # True Amplitude-Driven Waveform Canvas
        self.waveform = WaveformWidget()
        wf_layout.addWidget(self.waveform)

        hero_layout.addWidget(waveform_box)

        # ---------------------------------------------------------------------
        # Recording Control Buttons
        # ---------------------------------------------------------------------
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        self.btn_record = QPushButton("Start Recording")
        self.btn_record.setObjectName("recordBtn")
        self.btn_record.setIcon(get_svg_icon("mic", color="#FFFFFF", size=16))
        self.btn_record.clicked.connect(self.toggle_recording)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setObjectName("pauseBtn")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_restart = QPushButton("Restart")
        self.btn_restart.setObjectName("restartBtn")
        self.btn_restart.setIcon(get_svg_icon("refresh-cw", color="#1E2B4B", size=14))
        self.btn_restart.setToolTip("Discard current audio and restart recording from beginning")
        self.btn_restart.setEnabled(False)
        self.btn_restart.hide()
        self.btn_restart.clicked.connect(self.restart_recording)

        self.btn_stop = QPushButton("Stop Transcribe")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setIcon(get_svg_icon("square", color="#FFFFFF", size=14))
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_recording)

        self.btn_upload = QPushButton("Import Audio File")
        self.btn_upload.setObjectName("primaryBtn")
        self.btn_upload.setIcon(get_svg_icon("upload", color="#FFFFFF", size=16))
        self.btn_upload.clicked.connect(self.browse_audio_file)

        controls_row.addWidget(self.btn_record)
        controls_row.addWidget(self.btn_pause)
        controls_row.addWidget(self.btn_restart)
        controls_row.addWidget(self.btn_stop)
        controls_row.addSpacing(16)
        controls_row.addWidget(self.btn_upload)
        controls_row.addStretch()

        hero_layout.addLayout(controls_row)
        main_layout.addWidget(hero_card)

        # ---------------------------------------------------------------------
        # File Import Drop Zone
        # ---------------------------------------------------------------------
        drop_card = QFrame()
        drop_card.setObjectName("cardFrame")
        drop_layout = QVBoxLayout(drop_card)
        drop_layout.setContentsMargins(20, 20, 20, 20)

        drop_label = QLabel("Drag and drop meeting audio files here (WAV, MP3, MPEG, M4A, MP4, FLAC)")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_label.setStyleSheet("color: #5C6479; font-size: 14px; padding: 12px; border: 2px dashed #CBD5E1; border-radius: 4px; background: #FFFFFF;")
        drop_layout.addWidget(drop_label)

        self.progress_box = QWidget()
        p_layout = QVBoxLayout(self.progress_box)
        p_layout.setContentsMargins(0, 8, 0, 0)
        self.progress_label = QLabel("Running speech transcription & AI meeting intelligence...")
        self.progress_label.setStyleSheet("color: #6D59A7; font-weight: 600;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(65)
        p_layout.addWidget(self.progress_label)
        p_layout.addWidget(self.progress_bar)
        self.progress_box.hide()

        drop_layout.addWidget(self.progress_box)
        main_layout.addWidget(drop_card)

        # Second timer for elapsed recording time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def toggle_recording(self):
        if not self.waveform.is_recording and not self.is_paused:
            if self.is_testing_audio:
                self.toggle_audio_test()

            selected_idx = self.mic_combo.currentData()
            logger.info(f"Audio recording started: device={selected_idx}, mode={self.source_mode}")
            self.seconds_elapsed = 0
            self.timer_label.setText("00:00:00")

            # Start recording with selected source mode
            self.audio_engine.start_recording(device_index=selected_idx, source_mode=self.source_mode)

            self.waveform.set_recording(True)
            self.timer.start(1000)
            self.monitor_timer.start()  # Real-time amplitude updates for waveform

            self.btn_record.setText("Recording...")
            self.btn_record.setStyleSheet("background-color: #D04966; border: 1px solid #B93854; color: #FFFFFF;")
            self.btn_record.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_pause.setText("Pause")
            self.btn_restart.setEnabled(True)
            self.btn_restart.show()
            self.btn_stop.setEnabled(True)
            self.btn_test_audio.setEnabled(False)

            mode_text = "REC: MIC + SYS" if self.source_mode == "both" else ("REC: SYS" if self.source_mode == "system" else "RECORDING")
            self.status_badge.setText(mode_text)
            self.status_badge.setObjectName("badgeRose")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def toggle_pause(self):
        if self.is_paused:
            logger.info("Audio recording resumed from pause.")
            self.is_paused = False
            self.audio_engine.resume_recording()
            self.waveform.set_recording(True)
            self.timer.start(1000)
            self.btn_pause.setText("Pause")
            self.btn_restart.setEnabled(True)
            self.btn_restart.show()
            mode_text = "REC: MIC + SYS" if self.source_mode == "both" else ("REC: SYS" if self.source_mode == "system" else "RECORDING")
            self.status_badge.setText(mode_text)
            self.status_badge.setObjectName("badgeRose")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            if hasattr(self, "live_indicator"):
                self.live_indicator.setText("● LIVE CAPTURE ACTIVE")
                self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #E11D48;")
        elif self.waveform.is_recording:
            logger.info(f"Audio recording paused at {self.timer_label.text()}.")
            self.waveform.set_recording(False)
            self.audio_engine.pause_recording()
            self.timer.stop()
            self.is_paused = True
            self.btn_pause.setText("Resume")
            self.btn_restart.setEnabled(True)
            self.btn_restart.show()
            self.status_badge.setText("PAUSED")
            self.status_badge.setObjectName("badgeAmber")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            if hasattr(self, "live_indicator"):
                self.live_indicator.setText("❚❚ RECORDING PAUSED")
                self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #F59E0B;")

    def restart_recording(self):
        """Discard the current recording buffer, reset timer, and immediately restart fresh recording."""
        logger.info("Discarding current audio buffer and restarting fresh recording session...")
        self.audio_engine.cancel_recording()

        self.timer.stop()
        self.seconds_elapsed = 0
        self.timer_label.setText("00:00:00")
        self.is_paused = False
        self.waveform.reset()

        selected_idx = self.mic_combo.currentData()
        self.audio_engine.start_recording(device_index=selected_idx, source_mode=self.source_mode)
        self.waveform.set_recording(True)
        self.timer.start(1000)
        self.monitor_timer.start()

        self.btn_record.setText("Recording...")
        self.btn_record.setStyleSheet("background-color: #D04966; border: 1px solid #B93854; color: #FFFFFF;")
        self.btn_record.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_pause.setText("Pause")
        self.btn_restart.setEnabled(True)
        self.btn_restart.show()
        self.btn_stop.setEnabled(True)

        mode_text = "REC: MIC + SYS" if self.source_mode == "both" else ("REC: SYS" if self.source_mode == "system" else "RECORDING")
        self.status_badge.setText(mode_text)
        self.status_badge.setObjectName("badgeRose")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        if hasattr(self, "live_indicator"):
            self.live_indicator.setText("● LIVE CAPTURE ACTIVE")
            self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #E11D48;")

    def stop_recording(self):
        total_time = self.timer_label.text()
        logger.info(f"Audio recording stopped. Total duration: {total_time}.")

        try:
            saved_wav = self.audio_engine.stop_recording()
            self.active_audio_payload = saved_wav
            logger.info(f"Audio recording successfully stored at: {saved_wav}")
        except Exception as e:
            logger.error(f"Failed to save audio recording: {e}")
            self.active_audio_payload = f"Voice Recording ({total_time})"

        self.waveform.set_recording(False)
        self.timer.stop()
        if not self.is_testing_audio:
            self.monitor_timer.stop()
        self.is_paused = False
        self.seconds_elapsed = 0

        self.btn_record.setText("Start Recording")
        self.btn_record.setStyleSheet("")
        self.btn_record.setEnabled(True)
        self.btn_pause.setText("Pause")
        self.btn_pause.setEnabled(False)
        self.btn_restart.setEnabled(False)
        self.btn_restart.hide()
        self.btn_stop.setEnabled(False)
        self.btn_test_audio.setEnabled(True)

        self.timer_label.setText("00:00:00")
        self.status_badge.setText("IDLE")
        self.status_badge.setObjectName("badgeActive")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        if hasattr(self, "live_indicator"):
            self.live_indicator.setText("○ READY")
            self.live_indicator.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748B;")
        if hasattr(self, "live_level_bar"):
            self.live_level_bar.setValue(0)
        if hasattr(self, "live_signal_label"):
            self.live_signal_label.setText("-∞ dBFS • Standby")
            self.live_signal_label.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #64748B;")

        # Trigger transcription & AI pipeline with selected language
        self.transcription_requested.emit(self.active_audio_payload, self.selected_language or "")

    def finish_processing(self):
        self.transcription_requested.emit(self.active_audio_payload, self.selected_language or "")

    def update_timer(self):
        self.seconds_elapsed += 1
        mins, secs = divmod(self.seconds_elapsed, 60)
        hrs, mins = divmod(mins, 60)
        self.timer_label.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")

        # Check for device disconnection during recording
        if self.audio_engine.device_disconnected:
            self.status_badge.setText("DEV LOST - SAVING")
            self.status_badge.setObjectName("badgeAmber")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def browse_audio_file(self):
        """Open system file picker with support for MPEG, MP3, WAV, M4A, MP4, FLAC."""
        logger.info("Opening system audio file picker dialog...")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mpeg *.mp3 *.wav *.m4a *.mp4 *.aac *.flac *.ogg *.wma);;All Files (*.*)"
        )
        if file_path:
            src_path = Path(file_path)
            file_name = src_path.name
            file_ext = src_path.suffix.upper()
            try:
                file_size_kb = round(os.path.getsize(file_path) / 1024, 1)
            except Exception:
                file_size_kb = "N/A"

            RECORDING_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = RECORDING_DIR / f"imported_{timestamp}_{src_path.name}"
            try:
                shutil.copy2(src_path, dest_file)
                saved_audio_path = str(dest_file)
                logger.info(f"Imported audio file stored in recording directory: '{dest_file}'")
            except Exception as copy_err:
                logger.warning(f"Could not copy to data/recording folder ({copy_err}), using original path: {file_path}")
                saved_audio_path = file_path

            self.active_audio_payload = saved_audio_path
            logger.info(f"Audio payload ready: '{file_name}' ({file_ext}, {file_size_kb} KB). Sending to STT pipeline...")

            self.status_badge.setText("PROCESSING")
            self.status_badge.setObjectName("badgePurple")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)
            self.progress_box.show()
            QTimer.singleShot(1500, self.finish_processing)
        else:
            logger.info("Audio file import cancelled by user.")
