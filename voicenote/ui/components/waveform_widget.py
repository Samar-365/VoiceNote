import random
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen

class WaveformWidget(QWidget):
    """Custom Audio Waveform Visualizer rendering thin moving vertical lines in Retro Cream palette."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.is_recording = False
        self.phase = 0.0
        
        self.lines_count = 120
        self.amplitudes = [random.uniform(0.05, 0.25) for _ in range(self.lines_count)]
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(40)

    def set_recording(self, recording: bool):
        self.is_recording = recording
        self.update()

    def update_waveform(self):
        self.phase += 0.15
        if self.is_recording:
            self.amplitudes.pop(0)
            wave_val = (math.sin(self.phase) * 0.3 + math.sin(self.phase * 2.3) * 0.2 + 0.5)
            noise = random.uniform(0.05, 0.45)
            new_amp = max(0.05, min(0.95, wave_val * 0.6 + noise * 0.4))
            self.amplitudes.append(new_amp)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height / 2.0

        line_width = 2.0
        spacing = (width - 20) / max(1, self.lines_count)

        for i in range(min(len(self.amplitudes), self.lines_count)):
            x = 10 + i * spacing
            amp = self.amplitudes[i]
            
            if self.is_recording:
                line_h = max(4.0, amp * (height * 0.75))
            else:
                idle_amp = 0.08 + 0.04 * math.sin(self.phase + i * 0.1)
                line_h = max(3.0, idle_amp * (height * 0.5))

            y1 = center_y - (line_h / 2.0)
            y2 = center_y + (line_h / 2.0)

            gradient = QLinearGradient(x, y1, x, y2)
            if self.is_recording:
                gradient.setColorAt(0.0, QColor("#E05A77")) # Retro Coral
                gradient.setColorAt(0.5, QColor("#6D59A7")) # Retro Purple
                gradient.setColorAt(1.0, QColor("#F4B447")) # Retro Amber
            else:
                gradient.setColorAt(0.0, QColor("#B8B2A6"))
                gradient.setColorAt(1.0, QColor("#A39C90"))

            pen = QPen(gradient, line_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(x), int(y1), int(x), int(y2))
