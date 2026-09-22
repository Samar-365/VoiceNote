# VoiceNote Developer Task Plan (Tejas)

## Milestone 1: ChromaDB & Semantic Search Integration
- [x] **Task 1: Integrate ChromaDB Indexing into `PipelineWorker` (`voicenote/services/worker.py`)**
  - Import `VectorEngine` in `voicenote/services/worker.py`.
  - Index STT transcript segments with timestamps and metadata into ChromaDB upon note completion.
  - Emit progress updates during vector indexing.

- [x] **Task 2: Wire Semantic Search into `MainWindow` (`voicenote/ui/main_window.py`)**
  - Initialize `VectorEngine` instance and bind `SemanticSearchWidget`.
  - Connect search queries to live ChromaDB cosine distance queries.
  - Render formatted match cards with percentage relevance badges.

- [x] **Task 3: Update Test Runner for Vector Engine (`run_all_tests.py`)**
  - Integrated `test_vector_engine.py` into unified test runner.

---

## Milestone 2 (Phase 4): Quality Gates, Integration Fixes & Testing Coordination
- [x] **Task 4: Vector Store Deletion Synchronization (`voicenote/core/vector_engine.py`)**
  - Implemented `delete_all()` method to safely purge all collections/embeddings in ChromaDB.
  - Verified `delete_note(note_id)` and `delete_all()` with dedicated pytest unit tests.

- [x] **Task 5: Cross-Module Deletion Synchronization (`voicenote/ui/main_window.py`, `voicenote/db/database.py`)**
  - Added `get_note_by_title(title)` to `DatabaseManager`.
  - Connected `on_delete_note` and `on_delete_all_notes` in `MainWindow` to synchronize deletions across PostgreSQL, disk storage, and ChromaDB vector embeddings.
  - Added auto-reset to `SemanticSearchWidget` to purge stale search results upon note deletion.

- [x] **Task 6: Pipeline Worker Resilience & Processing Dialog Safety**
  - Added safe cleanup handling for `ProcessingDialog` in `on_pipeline_error`.
  - Verified non-blocking background execution with status bar and dialog tracking.

- [x] **Task 7: Comprehensive 9-Module Quality Gate Verification (`run_all_tests.py`)**
  - Automated sample data re-seeding when the database is empty.
  - Verified 100% test pass across Database, Auth, Text Cleaner, Audio Storage, Export Engine, Analytics Engine, AI Engine, Vector Engine, and GUI Services.

- [x] **Task 8: Document Activity in Developer Log (`doc/dev/tejas.md`)**
  - Logged all Phase 4 activities and synchronization fixes.

---

## Milestone 3: Audio Capture, Real-Time Monitoring & Multilingual Transcription Correction
- [x] **Task 9: Real-time Audio Level & Monitoring Pipeline (`voicenote/core/audio_engine.py`, `voicenote/ui/components/audio_recorder_widget.py`)**
  - Producer/consumer callback architecture with calibrated dBFS levels and attack/release smoothing.
  - Live amplitude monitoring in `get_latest_amplitude` dynamically reflecting microphone and system audio.
  - Active visual wave pulses and responsive gradients in `WaveformWidget`.

- [x] **Task 10: Multilingual Transcript Corrector (`voicenote/core/transcript_corrector.py`)**
  - Post-STT Gemini-powered Devanagari correction module fixing Marathi grammar endings (e.g. 'है' -> 'आहे', 'महंजे' -> 'म्हणजे').
  - Preserves English business and technical terms without transliteration.
  - Corrects numbers and standardizes Indian currency (`Rs.`) and percentages (`%`).
  - Integrated into `PipelineWorker` (`voicenote/services/worker.py`) prior to diarization and intelligence analysis.

- [x] **Task 11: Gemini API Resilience & Model Upgrades (`voicenote/core/ai_engine.py`)**
  - Configured default model to `gemini-3.8-flash`.
  - Added multi-tier fallback mechanism (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`) to gracefully withstand temporary 503 high-demand spikes.

---

*(Phase 5: PyInstaller packaging and Inno Setup installer are explicitly on hold until mentor feedback and real-life field testing).*
