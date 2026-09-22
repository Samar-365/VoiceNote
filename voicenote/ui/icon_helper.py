"""
VoiceNote Icon Helper: Clean Lucide-style vector icon loader and renderer for PySide6.
Renders resolution-independent SVG vector icons with customized colors and sizes,
replacing raw Unicode emoji glyphs.
"""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QByteArray, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

from voicenote.config import BASE_DIR

ICONS_DIR = BASE_DIR / "assets" / "icons"


def get_svg_icon(name: str, color: Optional[str] = None, size: int = 20) -> QIcon:
    """
    Load an SVG icon from assets/icons/{name}.svg and return a crisp QIcon.
    If color is provided, overrides the stroke/fill with the specified HEX color.
    """
    pixmap = get_svg_pixmap(name, color=color, size=size)
    return QIcon(pixmap)


def get_svg_pixmap(name: str, color: Optional[str] = None, size: int = 20) -> QPixmap:
    """
    Load an SVG icon from assets/icons/{name}.svg and render to a crisp QPixmap.
    """
    svg_path = ICONS_DIR / f"{name}.svg"
    if not svg_path.exists():
        # Fallback empty transparent pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap

    svg_content = svg_path.read_text(encoding="utf-8")
    if color:
        # Replace stroke="#..." or fill="#..."
        import re
        svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', svg_content)

    renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()

    return pixmap
