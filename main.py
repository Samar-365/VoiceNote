import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from voicenote.ui.main_window import MainWindow

# Configure immediate, unbuffered standard output logging
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger("VoiceNote")

def main():
    logger.info("Initializing VoiceNote Desktop Application...")
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceNote Desktop")
    app.setOrganizationName("VoiceNote")

    window = MainWindow()
    window.show()
    logger.info("VoiceNote Main Window opened and ready for user interactions.")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
