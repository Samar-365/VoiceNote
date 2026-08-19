import random
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen

class WaveformWidget(QWidget):
    """Custom Audio Waveform Visualizer rendering dynamic glowing lines in Neon Indigo/Cyan palette."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(90)
        self.is_recording = False
        self.phase = 0.0
        
        self.lines_count = 120
        self.amplitudes = [random.uniform(0.05, 0.25) for _ in range(self.lines_count)]
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(35)

    def set_recording(self, recording: bool):
        self.is_recording = recording
        self.update()

    def update_waveform(self):
        self.phase += 0.18
        if self.is_recording:
            self.amplitudes.pop(0)
            wave_val = (math.sin(self.phase) * 0.35 + math.sin(self.phase * 2.3) * 0.25 + 0.5)
            noise = random.uniform(0.08, 0.5)
            new_amp = max(0.06, min(0.96, wave_val * 0.65 + noise * 0.35))
            self.amplitudes.append(new_amp)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height / 2.0

        line_width = 2.5
        spacing = (width - 24) / max(1, self.lines_count)

        for i in range(min(len(self.amplitudes), self.lines_count)):
            x = 12 + i * spacing
            amp = self.amplitudes[i]
            
            if self.is_recording:
                line_h = max(6.0, amp * (height * 0.82))
            else:
                idle_amp = 0.08 + 0.04 * math.sin(self.phase + i * 0.12)
                line_h = max(3.5, idle_amp * (height * 0.45))

            y1 = center_y - (line_h / 2.0)
            y2 = center_y + (line_h / 2.0)

            gradient = QLinearGradient(x, y1, x, y2)
            if self.is_recording:
                gradient.setColorAt(0.0, QColor("#F43F5E")) # Neon Rose
                gradient.setColorAt(0.4, QColor("#818CF8")) # Indigo
                gradient.setColorAt(1.0, QColor("#06B6D4")) # Cyan
            else:
                gradient.setColorAt(0.0, QColor("#334155")) # Slate 700
                gradient.setColorAt(1.0, QColor("#1E293B")) # Slate 800

            pen = QPen(gradient, line_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(x), int(y1), int(x), int(y2))
