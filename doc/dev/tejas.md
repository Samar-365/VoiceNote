# Tejas — Dev Activity Log (Branch: `tejas`)

- **2026-08-18** | **Task:** Updated application configuration constants (`APP_NAME`, `APP_SUBTITLE`, `VERSION`, storage directories `DATA_DIR`, `RECORDINGS_DIR`, `DB_PATH`) in `voicenote/config.py`.
- **2026-08-18** | **Task:** Built thread-safe SQLite database persistence layer (`voicenote/db/models.py`, `voicenote/db/database.py`, `voicenote/db/__init__.py`) supporting `Note`, `Transcript`, `AISummary`, and `Task` relational models and initial sample seeding.
- **2026-08-18** | **Task:** Implemented PySide6 background worker thread service (`voicenote/services/worker.py`) using `QThread` and Qt signals (`progress`, `finished`, `error`) for non-blocking speech-to-text (Whisper/Groq) and Gemini LLM analysis.
- **2026-08-18** | **Task:** Integrated `MainWindow` (`voicenote/ui/main_window.py`) with SQLite database manager for dynamic note rendering, live audio recording pipeline callbacks, and status bar updates.
- **2026-08-18** | **Task:** Created application bootstrap entry point (`main.py`) to initialize PySide6 `QApplication`, database connections, and launch `MainWindow`.
