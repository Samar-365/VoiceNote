# VoiceNote Architecture & Integration Implementation Plan (Tejas)

## Goal
Implement the main application entry point (`main.py`), local SQLite database persistence layer (`voicenote/db/`), PySide6 background worker thread orchestration (`voicenote/services/`), configuration updates, and full UI-to-AI pipeline integration.

## Tasks

- [x] **Task 1: Update Application Configuration (`voicenote/config.py`)**
  - Add missing application constants: `APP_NAME`, `APP_SUBTITLE`, `VERSION`.
  - Add database path, audio storage directory path, and Gemini API key variables.
  - Test config imports to ensure `main_window.py` imports succeed.

- [x] **Task 2: Implement Local Database Persistence (`voicenote/db/`)**
  - Create `voicenote/db/__init__.py`, `voicenote/db/models.py`, `voicenote/db/database.py`.
  - Build SQLite storage schema for:
    - `Note` (id, title, audio_path, duration, created_at, category)
    - `Transcript` (id, note_id, raw_text, cleaned_text, language)
    - `AISummary` (id, note_id, summary, key_points, sentiment, main_topics)
    - `Task` (id, note_id, title, description, priority, assignee, due_date, status)
  - Implement thread-safe CRUD methods for saving and fetching notes, transcripts, summaries, and tasks.

- [x] **Task 3: Implement Background Worker Thread Service (`voicenote/services/worker.py`)**
  - Create `PySide6.QtCore.QThread` worker classes (`AudioProcessingWorker`, `PipelineWorker`).
  - Emit Qt signals (`started`, `finished`, `error`, `progress`) to update the status bar and UI components without blocking the PySide6 main UI loop.
  - Connect worker to Atharv's `stt_engine.py` and `ai_engine.py`.

- [x] **Task 4: Wire UI to Service Layer & Database in `MainWindow`**
  - Update `main_window.py` and UI widgets to load actual notes from the database.
  - Wire live transcription & AI analysis callbacks from `AudioRecorderWidget` through `PipelineWorker`.
  - Display AI summary and extracted tasks in `SummaryTaskWidget` dynamically when a note is selected or transcribed.

- [x] **Task 5: Create Application Bootstrap (`main.py`)**
  - Initialize PySide6 `QApplication`, set app metadata, run database migrations/init.
  - Launch `MainWindow` and handle clean application shutdown.
  - Add quick manual execution test.

- [x] **Task 6: Update Developer Log (`doc/dev/tejas.md`)**
  - Record Tejas's architectural setup, database implementation, thread worker layer, and UI-AI pipeline integration.
