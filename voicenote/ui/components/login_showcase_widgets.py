"""
Login Showcase Widgets & Visual Animation Suite for VoiceNote Desktop Studio.
Contains native PySide6 vector-rendered components, animated waveform,
pulsing microphone, traveling-dot AI pipeline, interactive feature cards,
capability chips, and trust badges.
"""

import math
import random
from typing import Optional, List, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect,
    QPushButton
)
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QByteArray, Property
from PySide6.QtGui import (
    QPainter, QColor, QLinearGradient, QPen, QBrush, QPixmap, QPainterPath,
    QFont, QEnterEvent, QIcon
)
from PySide6.QtSvg import QSvgRenderer

# =============================================================================
# LUCIDE VECTOR ICONS (Raw SVG Definitions - Clean 24x24 Stroke SVGs)
# =============================================================================
LUCIDE_SVGS = {
    "microphone": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>""",
    "waveform": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10v3"/><path d="M6 6v11"/><path d="M10 3v18"/><path d="M14 8v7"/><path d="M18 5v13"/><path d="M22 10v3"/></svg>""",
    "users": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
    "sparkles": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>""",
    "brain": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-5.04Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-5.04Z"/></svg>""",
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>""",
    "check_circle": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "shield_check": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>""",
    "database": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "cpu": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>""",
    "arrow_right": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>""",
    "activity": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>""",
    "lock": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>""",
    "zap": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "win_minimize": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round"><line x1="4" y1="12" x2="20" y2="12"/></svg>""",
    "win_maximize": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="5" y="5" rx="1.5"/></svg>""",
    "win_restore": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="11" height="11" x="4" y="9" rx="1"/><path d="M8 9V6a1.5 1.5 0 0 1 1.5-1.5H18A1.5 1.5 0 0 1 19.5 6v8.5A1.5 1.5 0 0 1 18 16h-3"/></svg>""",
    "win_close": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>"""
}


def render_svg_pixmap(icon_name: str, color: str = "#6D59A7", size: int = 24) -> QPixmap:
    """Render a Lucide vector icon to a crisp QPixmap at target dimensions."""
    svg_template = LUCIDE_SVGS.get(icon_name, LUCIDE_SVGS["sparkles"])
    svg_data = svg_template.format(color=color).encode("utf-8")
    
    renderer = QSvgRenderer(QByteArray(svg_data))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    
    return pixmap


# =============================================================================
# 1. ANIMATED AUDIO WAVEFORM WIDGET
# =============================================================================
class AnimatedWaveformWidget(QWidget):
    """
    Continuous, smooth harmonic audio waveform visualizer.
    Renders moving frequency bars with a gradient in the brand's purple/blue/cyan palette.
    Simulates real-time listening with very low CPU impact.
    """

    def __init__(self, parent=None, bar_count: int = 42, height: int = 44):
        super().__init__(parent)
        self.bar_count = bar_count
        self.setFixedHeight(height)
        self.setMinimumWidth(260)
        
        self.phase = 0.0
        self.amplitudes = [0.1] * self.bar_count
        
        # 30 FPS update timer
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def _on_tick(self):
        self.phase += 0.08
        # Harmonic formula generating continuous organic voice-like wave movement
        for i in range(self.bar_count):
            norm_x = i / float(self.bar_count)
            # Center envelope (edges taper softly, center is higher)
            envelope = math.sin(norm_x * math.pi) ** 1.3
            
            w1 = math.sin(self.phase * 1.8 + i * 0.32) * 0.45
            w2 = math.cos(self.phase * 2.7 - i * 0.22) * 0.30
            w3 = math.sin(self.phase * 0.9 + i * 0.15) * 0.25
            val = (w1 + w2 + w3 + 1.0) / 2.0
            
            target = 0.12 + val * 0.82 * envelope
            # Smooth lerp
            self.amplitudes[i] += (target - self.amplitudes[i]) * 0.25
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        center_y = h / 2.0
        
        # Calculate bar width & spacing
        padding_x = 8.0
        available_w = max(10.0, w - (padding_x * 2.0))
        bar_w = max(2.5, min(5.0, (available_w / self.bar_count) * 0.60))
        stride = available_w / max(1, self.bar_count - 1)

        # Gradient along width: Purple (#6D59A7) -> Soft Blue (#3B82F6) -> Cyan (#0D9488)
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, QColor("#6D59A7"))
        grad.setColorAt(0.5, QColor("#3B82F6"))
        grad.setColorAt(1.0, QColor("#0D9488"))

        pen = QPen(QBrush(grad), bar_w)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for i, amp in enumerate(self.amplitudes):
            x = padding_x + (i * stride)
            bar_h = max(4.0, amp * (h * 0.85))
            y1 = center_y - (bar_h / 2.0)
            y2 = center_y + (bar_h / 2.0)
            painter.drawLine(QPointF(x, y1), QPointF(x, y2))
            
        painter.end()

    def stop_animation(self):
        if self.timer.isActive():
            self.timer.stop()

    def start_animation(self):
        if not self.timer.isActive():
            self.timer.start()


# =============================================================================
# 2. ANIMATED VOICE / MICROPHONE PULSE WIDGET
# =============================================================================
class PulseMicWidget(QWidget):
    """
    Pulsing microphone indicator.
    Features a stable Lucide microphone icon in a circular purple badge,
    surrounded by continuous concentric expanding radial pulse waves that softly fade out.
    """

    def __init__(self, parent=None, size: int = 68):
        super().__init__(parent)
        self.widget_size = size
        self.setFixedSize(size, size)
        
        self.pulse_phase = 0.0
        self.mic_pixmap = render_svg_pixmap("microphone", color="#FFFFFF", size=24)
        
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def _on_tick(self):
        self.pulse_phase += 0.04
        if self.pulse_phase >= 1.0:
            self.pulse_phase -= 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        base_radius = 20.0
        max_expand = (self.width() / 2.0) - base_radius - 2.0

        # 1. Draw 2 expanding pulse rings (staggered by 0.5)
        for offset in (0.0, 0.5):
            progress = (self.pulse_phase + offset) % 1.0
            r = base_radius + progress * max_expand
            alpha = int((1.0 - progress) * 110)
            
            pulse_pen = QPen(QColor(109, 89, 167, alpha), 1.8)
            painter.setPen(pulse_pen)
            painter.setBrush(QColor(109, 89, 167, int(alpha * 0.15)))
            painter.drawEllipse(QPointF(cx, cy), r, r)

        # 2. Draw stable center badge (Purple Circle)
        painter.setPen(QPen(QColor("#8E74D5"), 1.5))
        painter.setBrush(QColor("#6D59A7"))
        painter.drawEllipse(QPointF(cx, cy), base_radius, base_radius)

        # 3. Draw white mic icon centered
        ix = int(cx - (self.mic_pixmap.width() / 2.0))
        iy = int(cy - (self.mic_pixmap.height() / 2.0))
        painter.drawPixmap(ix, iy, self.mic_pixmap)
        
        painter.end()

    def stop_animation(self):
        if self.timer.isActive():
            self.timer.stop()

    def start_animation(self):
        if not self.timer.isActive():
            self.timer.start()


# =============================================================================
# 3. ANIMATED AI PROCESSING PIPELINE WIDGET
# =============================================================================
class AnimatedPipelineWidget(QFrame):
    """
    Displays the VoiceNote intelligence pipeline:
    Record -> Transcribe -> Diarize -> AI Insights -> Action
    A glowing dot smoothly travels along the connecting pipeline track.
    """

    STEPS = [
        ("microphone", "Record"),
        ("waveform", "Transcribe"),
        ("users", "Diarize"),
        ("sparkles", "Insights"),
        ("check_circle", "Action")
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet("""
            AnimatedPipelineWidget {
                background: #FFFFFF;
                border: 1px solid #E5E0D6;
                border-radius: 8px;
            }
        """)
        
        self.progress = 0.0  # 0.0 to len(STEPS)-1
        self.cached_icons = {
            icon_name: render_svg_pixmap(icon_name, color="#5C6479", size=16)
            for icon_name, _ in self.STEPS
        }
        self.cached_icons_active = {
            icon_name: render_svg_pixmap(icon_name, color="#6D59A7", size=16)
            for icon_name, _ in self.STEPS
        }

        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def _on_tick(self):
        total_steps = len(self.STEPS) - 1
        self.progress += 0.015
        if self.progress > total_steps:
            self.progress = 0.0
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = self.width()
        h = self.height()
        n = len(self.STEPS)
        
        margin_x = 36.0
        track_y = 24.0
        step_spacing = (w - (margin_x * 2.0)) / max(1, n - 1)
        
        node_positions: List[Tuple[float, float]] = []
        for i in range(n):
            nx = margin_x + (i * step_spacing)
            node_positions.append((nx, track_y))

        # 1. Draw base connection track
        track_pen = QPen(QColor("#E2DDD3"), 2.0, Qt.PenStyle.SolidLine)
        painter.setPen(track_pen)
        painter.drawLine(QPointF(node_positions[0][0], track_y), QPointF(node_positions[-1][0], track_y))

        # 2. Draw active progress line behind the glowing dot
        active_track_x = margin_x + (self.progress * step_spacing)
        active_grad = QLinearGradient(margin_x, track_y, active_track_x, track_y)
        active_grad.setColorAt(0.0, QColor("#6D59A7"))
        active_grad.setColorAt(1.0, QColor("#0D9488"))
        
        active_pen = QPen(QBrush(active_grad), 2.5)
        painter.setPen(active_pen)
        painter.drawLine(QPointF(margin_x, track_y), QPointF(active_track_x, track_y))

        # 3. Draw nodes
        font = QFont("Segoe UI", 8)
        font.setBold(True)
        painter.setFont(font)

        for i, (icon_name, label_text) in enumerate(self.STEPS):
            nx, ny = node_positions[i]
            is_active = (i <= self.progress)
            
            # Node circle
            painter.setPen(QPen(QColor("#6D59A7" if is_active else "#D8D2C5"), 1.5))
            painter.setBrush(QColor("#FFFFFF" if not is_active else "#F2EFF9"))
            painter.drawEllipse(QPointF(nx, ny), 13, 13)

            # Node icon
            icon_pix = self.cached_icons_active[icon_name] if is_active else self.cached_icons[icon_name]
            painter.drawPixmap(int(nx - 8), int(ny - 8), icon_pix)

            # Node label text below
            painter.setPen(QColor("#1E2B4B" if is_active else "#7A8299"))
            rect = QRectF(nx - 36, ny + 14, 72, 16)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label_text)

        # 4. Draw traveling glowing dot with soft outer halo
        dot_x = active_track_x
        # Outer soft glow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(13, 148, 136, 50))
        painter.drawEllipse(QPointF(dot_x, track_y), 9.0, 9.0)
        # Inner glow
        painter.setBrush(QColor(13, 148, 136, 120))
        painter.drawEllipse(QPointF(dot_x, track_y), 5.5, 5.5)
        # Core dot
        painter.setBrush(QColor("#0D9488"))
        painter.drawEllipse(QPointF(dot_x, track_y), 3.2, 3.2)

        painter.end()

    def stop_animation(self):
        if self.timer.isActive():
            self.timer.stop()

    def start_animation(self):
        if not self.timer.isActive():
            self.timer.start()


# =============================================================================
# 4. FLOATING PARTICLES & SPARKLES BACKGROUND
# =============================================================================
class FloatingParticlesOverlay(QWidget):
    """
    Extremely subtle floating micro-particles and occasional AI sparkles.
    Rendered at low opacity (8-16%) so it remains professional, calm, and never distracts.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.particles: List[dict] = []
        self._init_particles()
        
        self.sparkle_phase = 0.0
        self.sparkle_pos = (0.2, 0.4)
        
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def _init_particles(self):
        # 14 subtle micro particles
        colors = ["#6D59A7", "#3B82F6", "#0D9488", "#C4B5FD"]
        for _ in range(14):
            self.particles.append({
                "x": random.uniform(0.0, 1.0),
                "y": random.uniform(0.0, 1.0),
                "r": random.uniform(1.6, 3.2),
                "vx": random.uniform(-0.0004, 0.0004),
                "vy": random.uniform(-0.0008, -0.0002),  # gentle upward drift
                "color": random.choice(colors),
                "alpha": random.uniform(0.08, 0.20)
            })

    def _on_tick(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -0.05:
                p["y"] = 1.05
                p["x"] = random.uniform(0.0, 1.0)
            if p["x"] < -0.05:
                p["x"] = 1.05
            elif p["x"] > 1.05:
                p["x"] = -0.05

        self.sparkle_phase += 0.02
        if self.sparkle_phase > 1.0:
            self.sparkle_phase = 0.0
            self.sparkle_pos = (random.uniform(0.1, 0.9), random.uniform(0.1, 0.8))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Draw subtle drifting particles
        for p in self.particles:
            px = p["x"] * w
            py = p["y"] * h
            c = QColor(p["color"])
            c.setAlphaF(p["alpha"])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(QPointF(px, py), p["r"], p["r"])

        # Draw occasional subtle AI sparkle (star ✦)
        # Fade in then fade out smoothly
        if 0.1 <= self.sparkle_phase <= 0.9:
            norm_s = math.sin((self.sparkle_phase - 0.1) / 0.8 * math.pi)
            sx = self.sparkle_pos[0] * w
            sy = self.sparkle_pos[1] * h
            
            sc = QColor("#8E74D5")
            sc.setAlphaF(norm_s * 0.35)
            painter.setPen(sc)
            
            s_len = 5.0 * norm_s
            painter.drawLine(QPointF(sx - s_len, sy), QPointF(sx + s_len, sy))
            painter.drawLine(QPointF(sx, sy - s_len), QPointF(sx, sy + s_len))

        painter.end()

    def stop_animation(self):
        if self.timer.isActive():
            self.timer.stop()

    def start_animation(self):
        if not self.timer.isActive():
            self.timer.start()


# =============================================================================
# 5. COMPACT INTERACTIVE FEATURE CARD (WITH HOVER ANIMATION)
# =============================================================================
class InteractiveFeatureCard(QFrame):
    """
    Modern compact Bento card for left showcase.
    Displays Lucide vector icon badge, title, and crisp 1-sentence description.
    Provides smooth hover animation (subtle elevation lift and border glow).
    """

    def __init__(
        self,
        icon_name: str,
        title: str,
        description: str,
        tag_text: str = "",
        tag_color: str = "#6D59A7",
        tag_bg: str = "",
        tag_border: str = "",
        parent=None
    ):
        super().__init__(parent)
        self.icon_name = icon_name
        self.title_str = title
        self.desc_str = description
        self.tag_text = tag_text
        self.tag_color = tag_color
        self.tag_bg = tag_bg or f"{tag_color}18"
        self.tag_border = tag_border or f"{tag_color}40"
        
        self.is_hovered = False
        self.lift_offset = 0.0  # 0.0 to 3.0 px
        
        self.setObjectName("featureCard")
        self.setFixedHeight(105)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._setup_ui()
        self._apply_style(hover=False)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(5)

        # Header row: Vector Icon Badge + Tag
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        # Icon Label
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(28, 28)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {self.tag_bg};
                border: 1px solid {self.tag_border};
                border-radius: 6px;
            }}
        """)
        pix = render_svg_pixmap(self.icon_name, color=self.tag_color, size=18)
        self.icon_lbl.setPixmap(pix)
        header_row.addWidget(self.icon_lbl)

        # Title
        self.title_lbl = QLabel(self.title_str)
        self.title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E2B4B;")
        header_row.addWidget(self.title_lbl)
        header_row.addStretch()

        # Tag Badge
        if self.tag_text:
            tag_lbl = QLabel(self.tag_text)
            tag_lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.tag_bg};
                    color: {self.tag_color};
                    border: 1px solid {self.tag_border};
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 0.5px;
                }}
            """)
            header_row.addWidget(tag_lbl)

        layout.addLayout(header_row)

        # Description
        self.desc_lbl = QLabel(self.desc_str)
        self.desc_lbl.setStyleSheet("color: #5C6479; font-size: 12px; line-height: 1.3;")
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)

    def _apply_style(self, hover: bool):
        if hover:
            self.setStyleSheet("""
                QFrame#featureCard {
                    background-color: #FFFFFF;
                    border: 1.5px solid #6D59A7;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#featureCard {
                    background-color: #FFFFFF;
                    border: 1px solid #E5E0D6;
                    border-radius: 8px;
                }
            """)

    def enterEvent(self, event: QEnterEvent):
        super().enterEvent(event)
        self.is_hovered = True
        self._apply_style(hover=True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.is_hovered = False
        self._apply_style(hover=False)


# =============================================================================
# 6. CAPABILITY CHIP WIDGET
# =============================================================================
class CapabilityChip(QFrame):
    """
    Lightweight, modern pill tag representing a VoiceNote capability.
    Equipped with a crisp 13px Lucide vector icon and clean typography.
    """

    def __init__(self, icon_name: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("capabilityChip")
        self.setStyleSheet("""
            QFrame#capabilityChip {
                background-color: #F8F6F0;
                border: 1px solid #E2DDD3;
                border-radius: 13px;
            }
            QFrame#capabilityChip:hover {
                background-color: #F2EFF9;
                border-color: #D8D0EB;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 10, 4)
        layout.setSpacing(6)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(14, 14)
        icon_lbl.setPixmap(render_svg_pixmap(icon_name, color="#6D59A7", size=13))
        layout.addWidget(icon_lbl)

        txt_lbl = QLabel(label)
        txt_lbl.setStyleSheet("color: #3A435A; font-size: 11px; font-weight: 600;")
        layout.addWidget(txt_lbl)


# =============================================================================
# 7. PRIVACY & SECURITY TRUST BADGE
# =============================================================================
class PrivacyTrustBadge(QFrame):
    """
    Bottom reassurance banner on the left showcase panel.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("trustBadge")
        self.setStyleSheet("""
            QFrame#trustBadge {
                background-color: #F8F6F0;
                border: 1px solid #E5E0D6;
                border-radius: 6px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Shield-Check Vector Icon
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(18, 18)
        icon_lbl.setPixmap(render_svg_pixmap("shield_check", color="#2E7D32", size=18))
        layout.addWidget(icon_lbl)

        # Trust Statement
        trust_lbl = QLabel("Privacy-first • Local AI • Secure Storage")
        trust_lbl.setStyleSheet("color: #2E7D32; font-size: 12px; font-weight: 700;")
        layout.addWidget(trust_lbl)

        layout.addStretch()

        note_lbl = QLabel("Zero external audio telemetry")
        note_lbl.setStyleSheet("color: #7A8299; font-size: 11px; font-style: italic;")
        layout.addWidget(note_lbl)


# =============================================================================
# 8. TITLE BAR WINDOW CONTROL BUTTON
# =============================================================================
class TitleBarButton(QPushButton):
    """
    Crisp vector-rendered title bar button for Minimize, Maximize/Restore, and Close.
    Provides standard desktop hover behaviors (red for close, light gray for min/max).
    """

    def __init__(self, icon_name: str, is_close: bool = False, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.is_close = is_close
        self.setFixedSize(36, 30)
        self._apply_base_style()
        self.set_icon_color(hover=False)

    def _apply_base_style(self):
        if self.is_close:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F8F6F0;
                    border: 1px solid #E2DDD3;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #E81123;
                    border-color: #E81123;
                }
                QPushButton:pressed {
                    background-color: #C4101E;
                    border-color: #C4101E;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F8F6F0;
                    border: 1px solid #E2DDD3;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #ECE7DF;
                    border-color: #D8D2C5;
                }
                QPushButton:pressed {
                    background-color: #E2DDD3;
                }
            """)

    def set_icon_color(self, hover: bool):
        if self.is_close:
            c = "#FFFFFF" if hover else "#3A435A"
        else:
            c = "#1E2B4B" if hover else "#3A435A"
        self.setIcon(QIcon(render_svg_pixmap(self.icon_name, color=c, size=14)))

    def enterEvent(self, event: QEnterEvent):
        super().enterEvent(event)
        self.set_icon_color(hover=True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.set_icon_color(hover=False)

    def update_icon(self, icon_name: str):
        self.icon_name = icon_name
        self.set_icon_color(hover=self.underMouse())
