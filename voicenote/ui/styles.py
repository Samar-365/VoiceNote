"""QSS Stylesheet with sharp edges and 100% uniform warm cream background canvas (matching assets/ screenshots)."""

MAIN_STYLE = """
/* Global Window & Background Canvas - Uniform Soft Warm Cream #ECE7DF */
QMainWindow, QDialog, QStackedWidget, QScrollArea, QAbstractScrollArea, QWidget#centralWidget {
    background-color: #ECE7DF;
    color: #4A3980;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

/* Ensure ScrollArea Viewport and container widgets inherit warm cream canvas */
QScrollArea {
    background-color: #ECE7DF;
    border: none;
}

QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: #ECE7DF;
}

QAbstractScrollArea::viewport {
    background-color: #ECE7DF;
    border: none;
}

QWidget {
    color: #4A3980;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #ECE7DF;
    width: 8px;
    margin: 0px;
    border-radius: 0px;
}
QScrollBar::handle:vertical {
    background: #D8D2C5;
    min-height: 20px;
    border-radius: 0px;
}
QScrollBar::handle:vertical:hover {
    background: #B8B2A4;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #ECE7DF;
    height: 8px;
    margin: 0px;
    border-radius: 0px;
}
QScrollBar::handle:horizontal {
    background: #D8D2C5;
    min-width: 20px;
    border-radius: 0px;
}

/* Base Buttons */
QPushButton {
    background-color: #F8F6F0;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #4A3980;
    padding: 8px 16px;
    font-weight: 700;
}
QPushButton:hover {
    background-color: #ECE7DF;
    border-color: #D8D2C5;
}
QPushButton:pressed {
    background-color: #E2DDD3;
}
QPushButton:disabled {
    background-color: #ECE7DF;
    border-color: #E2DDD3;
    color: #A39C90;
}

/* Primary Action Button (Retro Purple #6D59A7) */
QPushButton#primaryBtn {
    background-color: #6D59A7;
    border: 1px solid #5B4896;
    color: #FFFFFF;
    border-radius: 0px;
    font-weight: 700;
}
QPushButton#primaryBtn:hover {
    background-color: #5B4896;
}
QPushButton#primaryBtn:pressed {
    background-color: #4A3980;
}

/* Record Button (Retro Coral #E05A77) */
QPushButton#recordBtn {
    background-color: #E05A77;
    border: 1px solid #D04966;
    color: #FFFFFF;
    border-radius: 0px;
    padding: 10px 24px;
    font-weight: 700;
}
QPushButton#recordBtn:hover {
    background-color: #C8425F;
}

/* Pause Button (Retro Golden Amber #F4B447) */
QPushButton#pauseBtn {
    background-color: #F4B447;
    border: 1px solid #E0A235;
    color: #4A3980;
    border-radius: 0px;
    font-weight: 700;
}
QPushButton#pauseBtn:hover {
    background-color: #E0A235;
}

/* Stop Button (Muted Slate #64748B) */
QPushButton#stopBtn {
    background-color: #64748B;
    border: 1px solid #475569;
    color: #FFFFFF;
    border-radius: 0px;
    font-weight: 700;
}
QPushButton#stopBtn:hover {
    background-color: #475569;
}

/* Sidebar Navigation Buttons */
QPushButton#navBtn {
    background-color: transparent;
    border: none;
    border-radius: 0px;
    color: #5C6479;
    text-align: left;
    padding: 11px 16px;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#navBtn:hover {
    background-color: #F8F6F0;
    color: #4A3980;
}
QPushButton#navBtn[active="true"] {
    background-color: #6D59A7;
    color: #FFFFFF;
}

/* Cards & Frames */
QFrame#cardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
}

QFrame#heroCard {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
}

QFrame#glassFrame {
    background-color: #F8F6F0;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
}

/* Titles & Text */
QLabel#titleLabel {
    font-size: 18px;
    font-weight: 800;
    color: #1E2B4B;
}

QLabel#subtitleLabel {
    color: #5C6479;
    font-size: 13px;
}

/* Badges & Status Chips */
QLabel#badgeActive {
    background-color: #EBF3EC;
    color: #2E7D32;
    border: 1px solid #A6D7AC;
    border-radius: 0px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgePurple {
    background-color: #F2EFF9;
    color: #6D59A7;
    border: 1px solid #D8D0EB;
    border-radius: 0px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeCyan {
    background-color: #EEF2F6;
    color: #3B82F6;
    border: 1px solid #CBD5E1;
    border-radius: 0px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeAmber {
    background-color: #FEF6E6;
    color: #D97706;
    border: 1px solid #FCD34D;
    border-radius: 0px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 11px;
}

QLabel#badgeRose {
    background-color: #FCE8EC;
    color: #E05A77;
    border: 1px solid #F5B0C0;
    border-radius: 0px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 11px;
}

/* Form Inputs */
QLineEdit, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #1E2B4B;
    padding: 8px 12px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #6D59A7;
}

QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #1E2B4B;
    padding: 6px 12px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    selection-background-color: #6D59A7;
    selection-color: #FFFFFF;
}

/* Progress Bars */
QProgressBar {
    background-color: #ECE7DF;
    border: 1px solid #E2DDD3;
    border-radius: 0px;
    height: 14px;
    text-align: right;
}
QProgressBar::chunk {
    background-color: #6D59A7;
    border-radius: 0px;
}

/* CheckBoxes & RadioButtons */
QCheckBox, QRadioButton {
    color: #1E2B4B;
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 0px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #6D59A7;
    border-color: #5B4896;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #E5E0D6;
    background-color: #FFFFFF;
    border-radius: 0px;
}
QTabBar::tab {
    background-color: #ECE7DF;
    border: 1px solid #E5E0D6;
    color: #5C6479;
    padding: 8px 16px;
    margin-right: 2px;
    border-radius: 0px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background-color: #FFFFFF;
    border-bottom: 2px solid #6D59A7;
    color: #4A3980;
}

/* Status Bar */
QStatusBar {
    background-color: #ECE7DF;
    color: #5C6479;
    font-size: 11px;
    border-top: 1px solid #E5E0D6;
    padding: 4px 12px;
}
"""
