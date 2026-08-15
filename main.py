import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from voicenote.ui.main_window import MainWindow

def main():
    # Enable High DPI scaling for crisp Windows desktop rendering
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceNote Desktop")
    app.setOrganizationName("VoiceNote")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
