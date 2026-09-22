import math
import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen


class WaveformWidget(QWidget):
    """
    Real-time Audio Waveform Visualizer responding directly to actual audio amplitude:
    - Unmistakable active pulse when recording (never looks frozen or dead, even in quiet pauses).
    - Surges dramatically with dynamic Coral-Violet-Amber gradients upon detecting real speech energy.
    - Testing mode support with Emerald Green telemetry wave.
    - Soft, subtle resting baseline when idle.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(76)
        self.is_recording = False
        self.is_testing = False
        self.phase = 0.0
        self.live_amplitude = 0.0
        self._smoothed_amp = 0.0

        self.lines_count = 90
        # Initialize flat resting amplitudes
        self.amplitudes = [0.05 for _ in range(self.lines_count)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(33)  # ~30 fps refresh

    def set_recording(self, recording: bool):
        self.is_recording = recording
        if not recording and not self.is_testing:
            self.live_amplitude = 0.0
            self._smoothed_amp = 0.0
        self.update()

    def set_testing(self, testing: bool):
        self.is_testing = testing
        if not testing and not self.is_recording:
            self.live_amplitude = 0.0
            self._smoothed_amp = 0.0
        self.update()

    def reset(self):
        """Reset waveform visualization to clean idle baseline."""
        self.is_recording = False
        self.is_testing = False
        self.live_amplitude = 0.0
        self._smoothed_amp = 0.0
        self.amplitudes = [0.05 for _ in range(self.lines_count)]
        self.update()

    def set_live_amplitude(self, amp: float):
        """Set normalized live audio amplitude (0.0 to 1.0) from AudioEngine."""
        self.live_amplitude = max(0.0, min(1.0, float(amp)))

    def update_waveform(self):
        self.phase += 0.16

        # Fast attack (0.75) for responsive syllable peaks; smooth release (0.20)
        if self.live_amplitude > self._smoothed_amp:
            self._smoothed_amp = 0.75 * self.live_amplitude + 0.25 * self._smoothed_amp
        else:
            self._smoothed_amp = 0.20 * self.live_amplitude + 0.80 * self._smoothed_amp

        if self.is_recording:
            self.amplitudes.pop(0)

            # Check if real incoming audio energy is present (> 0.015)
            if self._smoothed_amp > 0.015:
                # Dynamic surge responding directly to voice
                dynamic_boost = self._smoothed_amp * 2.2
                harmonic = 0.06 * math.sin(self.phase * 2.0)
                jitter = random.uniform(-0.04, 0.04) * self._smoothed_amp
                bar_amp = min(0.96, max(0.12, dynamic_boost + harmonic + jitter))
            else:
                # Active living recording wave (ambient rhythm) so user KNOWS mic is listening
                bar_amp = 0.16 + 0.07 * math.sin(self.phase * 1.4) + 0.03 * math.cos(self.phase * 0.9)

            self.amplitudes.append(bar_amp)

        elif self.is_testing:
            self.amplitudes.pop(0)
            if self._smoothed_amp > 0.015:
                bar_amp = min(0.95, max(0.12, self._smoothed_amp * 2.2))
            else:
                bar_amp = 0.12 + 0.05 * math.sin(self.phase * 1.2)
            self.amplitudes.append(bar_amp)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height / 2.0

        count = min(len(self.amplitudes), self.lines_count)
        spacing = (width - 24) / max(1, count)
        line_width = max(2.2, min(3.5, spacing - 1.2))

        # Faint center guide line
        guide_color = QColor("#E2E8F0") if not self.is_recording else QColor("#F1F5F9")
        guide_pen = QPen(guide_color, 1.0)
        painter.setPen(guide_pen)
        painter.drawLine(10, int(center_y), width - 10, int(center_y))

        for i in range(count):
            x = 12 + i * spacing
            amp = self.amplitudes[i]

            if self.is_recording:
                line_h = max(5.0, amp * (height * 0.85))
            elif self.is_testing:
                line_h = max(4.0, amp * (height * 0.80))
            else:
                idle_amp = 0.04 + 0.02 * math.sin(self.phase + i * 0.09)
                line_h = max(3.0, idle_amp * (height * 0.45))

            y1 = center_y - (line_h / 2.0)
            y2 = center_y + (line_h / 2.0)

            gradient = QLinearGradient(x, y1, x, y2)
            if self.is_recording and self._smoothed_amp > 0.015:
                # Active vocal surge: Vivid Coral Rose -> Royal Violet -> Radiant Amber
                gradient.setColorAt(0.0, QColor("#F43F5E"))
                gradient.setColorAt(0.5, QColor("#6D59A7"))
                gradient.setColorAt(1.0, QColor("#F59E0B"))
            elif self.is_recording:
                # Active ambient recording pulse: Bright Violet -> Deep Lavender
                gradient.setColorAt(0.0, QColor("#C084FC"))
                gradient.setColorAt(0.5, QColor("#8B5CF6"))
                gradient.setColorAt(1.0, QColor("#6D59A7"))
            elif self.is_testing:
                # Testing audio mode: Mint to Emerald Green
                gradient.setColorAt(0.0, QColor("#34D399"))
                gradient.setColorAt(1.0, QColor("#059669"))
            else:
                # Idle baseline: Soft slate
                gradient.setColorAt(0.0, QColor("#CBD5E1"))
                gradient.setColorAt(1.0, QColor("#94A3B8"))

            pen = QPen(gradient, line_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(x), int(y1), int(x), int(y2))
