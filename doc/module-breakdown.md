# VoiceNote Module Breakdown Specification

## 1. Executive Summary

This document defines the functional structure of the VoiceNote Desktop system and aligns the implementation with the software requirements and architecture design. The application is organized around a layered architecture that isolates UI concerns, service logic, storage, and deployment responsibilities.

## 2. Project Directory Structure

```text
voicenote/
├── pyproject.toml
├── main.py
├── voicenote/
│   ├── __init__.py
│   ├── config.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── audio_recorder_widget.py
│   │   │   ├── transcript_view_widget.py
│   │   │   ├── summary_task_widget.py
│   │   │   ├── semantic_search_widget.py
│   │   │   └── analytics_dashboard_widget.py
│   │   └── dialogs/
│   │       ├── __init__.py
│   │       ├── profile_dialog.py
│   │       ├── export_dialog.py
│   │       └── settings_dialog.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── audio_engine.py
│   │   ├── stt_engine.py
│   │   ├── ai_engine.py
│   │   ├── vector_engine.py
│   │   ├── analytics_engine.py
│   │   └── export_engine.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── postgres_manager.py
│   │   ├── models.py
│   │   └── chroma_manager.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── threading_utils.py
│       └── file_utils.py
├── installer/
│   ├── voicenote.spec
│   └── setup.iss
└── tests/
```

## 3. Module-by-Module Specification

### Module 1: Bootstrap and Configuration

#### main.py
Responsible for:

- creating the Qt application instance
- validating environment prerequisites
- launching the main window
- managing application lifecycle events and logging

#### config.py
Responsible for:

- resolving local app data folders
- storing database and AI configuration values
- centralizing application constants and default settings

### Module 2: Presentation Layer

#### main_window.py
Responsible for:

- hosting the primary desktop layout
- managing view switching and UI navigation
- coordinating signals across subcomponents

#### audio_recorder_widget.py
Responsible for:

- microphone controls
- waveform visualization
- local file upload and recording session management

#### transcript_view_widget.py
Responsible for:

- transcript display and editing
- timestamp references
- tag assignment and label UI

#### summary_task_widget.py
Responsible for:

- summary visualization
- task board display and editing
- AI outcome presentation

#### semantic_search_widget.py
Responsible for:

- natural-language query input
- ranked semantic search results
- evidence snippet display and navigation

#### analytics_dashboard_widget.py
Responsible for:

- usage metrics
- task completion summaries
- productivity dashboards

### Module 3: Core Services

#### audio_engine.py
Responsible for:

- capture and storage of microphone audio
- file conversion and waveform metrics
- raw audio processing for transcription pipeline

#### stt_engine.py
Responsible for:

- handling faster-whisper transcription
- processor optimization and fallback strategy
- timestamp extraction and confidence tracking

#### ai_engine.py
Responsible for:

- Gemini AI interaction
- structured prompt orchestration
- summary and task output parsing

#### vector_engine.py
Responsible for:

- text chunking
- vector embedding generation
- semantic similarity queries

#### analytics_engine.py
Responsible for:

- summary statistics
- tag trends
- productivity and task performance calculations

#### export_engine.py
Responsible for:

- PDF generation
- DOCX generation
- plain text exports

### Module 4: Data Storage Layer

#### postgres_manager.py
Responsible for:

- PostgreSQL connection setup
- migration management
- CRUD and application service access

#### models.py
Responsible for:

- ORM entity definitions for User, Note, Transcript, Task, Tag, and Analytics records

#### chroma_manager.py
Responsible for:

- vector collection creation
- embedding insertion and updates
- semantic search index management

### Module 5: Utility Infrastructure

#### logger.py
Responsible for:

- application logging with local file output

#### threading_utils.py
Responsible for:

- worker thread coordination for long-running tasks
- UI-safe signaling and progress updates

#### file_utils.py
Responsible for:

- path handling
- directory creation
- binary and environment checks

### Module 6: Packaging and Distribution

#### voicenote.spec
Responsible for:

- bundling the Python app into a Windows executable

#### setup.iss
Responsible for:

- creating the Windows installer wrapper and user-facing deployment artifact

## 4. Requirement-to-Module Mapping

| Requirement ID | Requirement Description | Primary Module(s) |
| --- | --- | --- |
| FR1 | User profile and preferences | config.py, profile_dialog.py |
| FR2 | Audio recording and upload | audio_engine.py, audio_recorder_widget.py |
| FR3 | Whisper transcription | stt_engine.py, transcript_view_widget.py |
| FR4 | AI summarization | ai_engine.py, summary_task_widget.py |
| FR5 | Task extraction | ai_engine.py, summary_task_widget.py |
| FR6 | Tagging | analytics_engine.py, transcript_view_widget.py |
| FR7 | Semantic search | vector_engine.py, semantic_search_widget.py |
| FR8 | Export PDF/DOCX/TXT | export_engine.py, export_dialog.py |
| FR9 | Analytics | analytics_engine.py, analytics_dashboard_widget.py |

## 5. Implementation Phase Mapping

### Phase 1: Foundation and Database

- main.py
- config.py
- postgres_manager.py
- models.py
- main_window.py
- profile_dialog.py
- logger.py
- threading_utils.py

### Phase 2: Audio and Notes UI

- audio_engine.py
- audio_recorder_widget.py
- transcript_view_widget.py

### Phase 3: AI Core and Search

- stt_engine.py
- ai_engine.py
- vector_engine.py
- chroma_manager.py
- summary_task_widget.py
- semantic_search_widget.py

### Phase 4: Export and Analytics

- export_engine.py
- analytics_engine.py
- export_dialog.py
- analytics_dashboard_widget.py
- tests/

### Phase 5: Packaging and Deployment

- voicenote.spec
- setup.iss

## 6. Summary

The system is designed around a strong separation of concerns, ensuring each module owns a specific responsibility. This decomposition provides maintainability, robust development sequencing, and a clear path to packaging and deployment for a Windows desktop AI productivity tool.
