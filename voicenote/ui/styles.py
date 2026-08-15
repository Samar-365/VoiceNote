"""QSS Stylesheet with sharp edges and 100% uniform warm cream background canvas (zero black gaps)."""

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

/* Buttons */
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

/* Primary Action Button (Retro Purple) */
QPushButton#primaryBtn {
    background-color: #6D59A7;
    border: 1px solid #5B4896;
    color: #FFFFFF;
    border-radius: 0px;
}
QPushButton#primaryBtn:hover {
    background-color: #5B4896;
}
QPushButton#primaryBtn:pressed {
    background-color: #4A3980;
}

/* Record Button (Retro Coral) */
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

/* Pause Button (Retro Golden Amber) */
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

/* Stop Button (Muted Slate) */
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

/* Sidebar Nav Buttons */
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
    font-weight: 800;
}

/* Line Edit / Inputs */
QLineEdit {
    background-color: #F8F6F0;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #4A3980;
    padding: 9px 14px;
    selection-background-color: #6D59A7;
}
QLineEdit:focus {
    border: 2px solid #6D59A7;
    background-color: #FFFFFF;
}

/* Text Edit */
QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #4A3980;
    padding: 14px;
    line-height: 1.5;
}

/* Combo Box */
QComboBox {
    background-color: #F8F6F0;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #4A3980;
    padding: 6px 12px;
    font-weight: 600;
}
QComboBox:hover {
    border-color: #D8D2C5;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
    color: #4A3980;
    selection-background-color: #6D59A7;
    selection-color: #FFFFFF;
}

/* Sharp Edges Cards & Frames */
QFrame#cardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
}

QFrame#glassFrame {
    background-color: #F8F6F0;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
}

QFrame#heroCard {
    background-color: #F8F6F0;
    border: 1px solid #E5E0D6;
    border-radius: 0px;
}

/* Typography & Headings */
QLabel#titleLabel {
    font-size: 20px;
    font-weight: 900;
    color: #1E2B4B;
    letter-spacing: -0.5px;
}
QLabel#subtitleLabel {
    font-size: 13px;
    color: #5C6479;
    font-weight: 500;
}

/* Badges with Sharp Edges */
QLabel#badgeActive {
    background-color: #EBF3EC;
    color: #2E7D32;
    border: 1px solid #A6D7AC;
    border-radius: 0px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 800;
}
QLabel#badgePurple {
    background-color: #F0ECF9;
    color: #6D59A7;
    border: 1px solid #C4B9E3;
    border-radius: 0px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 800;
}
QLabel#badgeCyan {
    background-color: #F0ECF9;
    color: #6D59A7;
    border: 1px solid #C4B9E3;
    border-radius: 0px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 800;
}
QLabel#badgeAmber {
    background-color: #FEF6E6;
    color: #D97706;
    border: 1px solid #FCD34D;
    border-radius: 0px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 800;
}

/* Checkbox */
QCheckBox {
    color: #4A3980;
    spacing: 8px;
    font-weight: 600;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 0px;
    border: 1px solid #D8D2C5;
    background-color: #F8F6F0;
}
QCheckBox::indicator:checked {
    background-color: #6D59A7;
    border-color: #5B4896;
}

/* Progress Bar */
QProgressBar {
    border: none;
    background-color: #E5E0D6;
    border-radius: 0px;
    height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #6D59A7;
    border-radius: 0px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #E5E0D6;
    background-color: #FFFFFF;
    border-radius: 0px;
}
QTabBar::tab {
    background-color: #ECE7DF;
    color: #5C6479;
    padding: 10px 20px;
    border-radius: 0px;
    margin-right: 4px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background-color: #6D59A7;
    color: #FFFFFF;
}
QTabBar::tab:hover:!selected {
    background-color: #F8F6F0;
    color: #4A3980;
}

/* Status Bar */
QStatusBar {
    background: #ECE7DF;
    color: #5C6479;
    border-top: 1px solid #E5E0D6;
    font-weight: 600;
}
"""
