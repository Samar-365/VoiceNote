"""Modern Dark Slate & Indigo QSS Stylesheet for VoiceNote AI Desktop Studio.
Featuring refined Bento Grid aesthetic, glowing accents, and high-readability typography.
"""

MAIN_STYLE = """
/* Global Window & Background Canvas - Deep Slate */
QMainWindow, QDialog, QStackedWidget, QScrollArea, QAbstractScrollArea, QWidget#centralWidget {
    background-color: #0B0F19;
    color: #F8FAFC;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

/* Ensure ScrollArea Viewport and container widgets inherit dark canvas */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QAbstractScrollArea::viewport {
    background-color: transparent;
    border: none;
}

QWidget {
    color: #F8FAFC;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #6366F1;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #0F172A;
    height: 6px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 24px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #6366F1;
}

/* Base Buttons */
QPushButton {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}
QPushButton:pressed {
    background-color: #0F172A;
}
QPushButton:disabled {
    background-color: #0F172A;
    border-color: #1E293B;
    color: #64748B;
}

/* Primary Action Button (Indigo to Violet Gradient) */
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #7C3AED);
    border: 1px solid #6366F1;
    color: #FFFFFF;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 700;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #6D28D9);
    border-color: #818CF8;
}
QPushButton#primaryBtn:pressed {
    background: #3730A3;
}

/* Record Button (Vibrant Crimson/Rose) */
QPushButton#recordBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E11D48, stop:1 #F43F5E);
    border: 1px solid #FB7185;
    color: #FFFFFF;
    border-radius: 6px;
    padding: 10px 24px;
    font-weight: 700;
}
QPushButton#recordBtn:hover {
    background: #BE123C;
}

/* Pause Button (Vibrant Amber) */
QPushButton#pauseBtn {
    background-color: #D97706;
    border: 1px solid #F59E0B;
    color: #FFFFFF;
    border-radius: 6px;
    font-weight: 700;
}
QPushButton#pauseBtn:hover {
    background-color: #B45309;
}

/* Stop Button (Muted Slate) */
QPushButton#stopBtn {
    background-color: #334155;
    border: 1px solid #475569;
    color: #F8FAFC;
    border-radius: 6px;
    font-weight: 700;
}
QPushButton#stopBtn:hover {
    background-color: #475569;
}

/* Sidebar Navigation Buttons */
QPushButton#navBtn {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    color: #94A3B8;
    text-align: left;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#navBtn:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}
QPushButton#navBtn[active="true"] {
    background-color: #1E293B;
    border: 1px solid #4F46E5;
    color: #818CF8;
    font-weight: 700;
}

/* Bento Cards & Containers */
QFrame#cardFrame {
    background-color: #131B2E;
    border: 1px solid #1E293B;
    border-radius: 10px;
}

QFrame#cardFrame:hover {
    border-color: #334155;
}

QFrame#heroCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #131B2E);
    border: 1px solid #334155;
    border-radius: 12px;
}

QFrame#glassFrame {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 8px;
}

/* Typography & Titles */
QLabel#titleLabel {
    font-size: 17px;
    font-weight: 800;
    color: #F8FAFC;
}

QLabel#subtitleLabel {
    color: #94A3B8;
    font-size: 12px;
}

/* Badges & Status Chips */
QLabel#badgeActive {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#badgePurple {
    background-color: rgba(99, 102, 241, 0.15);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#badgeCyan {
    background-color: rgba(6, 182, 212, 0.15);
    color: #67E8F9;
    border: 1px solid rgba(6, 182, 212, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#badgeAmber {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#badgeRose {
    background-color: rgba(244, 63, 94, 0.15);
    color: #FDA4AF;
    border: 1px solid rgba(244, 63, 94, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

/* Inputs & Form Controls */
QLineEdit, QTextEdit {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 8px 12px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #6366F1;
    background-color: #131B2E;
}

QComboBox {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 6px 12px;
}
QComboBox:hover {
    border-color: #475569;
}
QComboBox QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #334155;
    color: #F8FAFC;
    selection-background-color: #4F46E5;
}

/* Progress Bars */
QProgressBar {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 4px;
    height: 8px;
    text-align: right;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #06B6D4);
    border-radius: 4px;
}

/* CheckBoxes & RadioButtons */
QCheckBox, QRadioButton {
    color: #E2E8F0;
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    background-color: #0F172A;
    border: 1px solid #475569;
    border-radius: 4px;
}
QRadioButton::indicator {
    border-radius: 8px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #4F46E5;
    border-color: #6366F1;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1E293B;
    background-color: #131B2E;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    color: #94A3B8;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #131B2E;
    border-bottom: 2px solid #6366F1;
    color: #F8FAFC;
    font-weight: 700;
}

/* Status Bar */
QStatusBar {
    background-color: #0B0F19;
    color: #94A3B8;
    font-size: 11px;
    border-top: 1px solid #1E293B;
    padding: 4px 12px;
}
"""
