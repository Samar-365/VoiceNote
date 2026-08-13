# VoiceNote Desktop Architecture

## 1. Overview

VoiceNote Desktop is a privacy-first, local AI-powered Windows application designed to record audio, transcribe speech, generate summaries, identify tasks, perform semantic search, and export notes in standard document formats.

The application is built on a modular Python architecture using PySide6 for the desktop interface and a layered service model to separate UI concerns from processing, storage, and deployment responsibilities.

## 2. Architecture Goals

- Keep all processing local to the user machine
- Ensure offline operation without cloud dependency
- Maintain a responsive desktop experience during transcription and AI processing
- Support modular extension for future features and integrations
- Provide secure local persistence for notes, tasks, metadata, and embeddings
- Package as a standalone Windows executable for client distribution

## 3. High-Level System View

```text
┌───────────────────────────────────────────────────────────────┐
│                     Presentation Layer                         │
│                PySide6 Desktop UI / Qt Widgets                │
│  Main Window  │  Recorder  │  Transcript  │  Summary  │ Search │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                  Application / Controller Layer                │
│           Qt Signals, Slots, Worker Threads, Task Orchestration │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                       Core Services Layer                     │
│ Audio │ STT │ AI Summary │ Tasks │ Search │ Export │ Analytics │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                        Data & Storage Layer                    │
│   PostgreSQL   │   ChromaDB   │   Local Filesystem / Audio    │
└───────────────────────────────────────────────────────────────┘
```

## 4. Layered Architecture

### 4.1 Presentation Layer

The presentation layer is implemented with PySide6 and contains the desktop UI components required for user interaction.

Key UI areas include:

- Profile view and configuration
- Audio recording panel with waveform and controls
- Transcript editor and tag manager
- AI summary and task board
- Semantic search interface
- Export dialog
- Analytics dashboard

This layer is responsible for capturing user actions and rendering results while delegating all heavy processing to background services.

### 4.2 Application Logic Layer

The application controller layer coordinates background operations using Qt signals, slots, and worker threads.

Responsibilities include:

- Triggering STT after recording
- Prompting the AI summarization pipeline
- Updating the UI with progress states
- Managing async processing without freezing the desktop interface
- Routing export and search activities through the appropriate service layer

### 4.3 Core Services Layer

This layer encapsulates domain functionality and system-specific integrations.

#### Audio Engine
- Captures microphone input
- Saves recordings to local audio files
- Imports user audio files such as WAV, MP3, M4A, and MP4
- Provides input-level metrics for waveform rendering

#### Speech-to-Text Engine
- Uses faster-whisper with CTranslate2 backend
- Supports GPU acceleration when available
- Falls back to CPU execution when necessary
- Produces timestamped transcript segments

#### AI Summary and Task Engine
- Integrates with Ollama running local LLM models such as Llama and Gemma
- Extracts structured summaries and task items from transcript content
- Uses structured outputs to ensure consistent JSON-based results

#### Semantic Search Engine
- Splits transcripts into natural chunks
- Builds vector embeddings from note content
- Queries indexed content with semantic similarity
- Returns ranked evidence snippets with matching transcript references

#### Export Engine
- Generates PDF, DOCX, and TXT files from completed notes
- Preserves note summaries, tasks, and transcript content in user-selected formats

#### Analytics Engine
- Tracks durations, notes created, productivity patterns, and task completion metrics
- Provides dashboard-level insights to the user

### 4.4 Data and Storage Layer

The data layer separates relational and vector storage responsibilities.

#### PostgreSQL
Stores structured and transactional application data, including:

- users
- notes
- transcripts
- tasks
- tags
- note-tag associations
- analytics summaries

#### ChromaDB
Stores vector embeddings and semantic search indexes for transcript content. This supports fast semantic retrieval of relevant note segments.

#### Local File System
Holds user-created recordings, exported documents, logs, and configuration files in dedicated local application directories.

## 5. Module Structure

```text
voicenote/
├── pyproject.toml
├── main.py
├── voicenote/
│   ├── __init__.py
│   ├── config.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── components/
│   │   │   ├── audio_recorder_widget.py
│   │   │   ├── transcript_view_widget.py
│   │   │   ├── summary_task_widget.py
│   │   │   ├── semantic_search_widget.py
│   │   │   └── analytics_dashboard_widget.py
│   │   └── dialogs/
│   │       ├── profile_dialog.py
│   │       ├── export_dialog.py
│   │       └── settings_dialog.py
│   ├── core/
│   │   ├── audio_engine.py
│   │   ├── stt_engine.py
│   │   ├── ai_engine.py
│   │   ├── vector_engine.py
│   │   ├── analytics_engine.py
│   │   └── export_engine.py
│   ├── db/
│   │   ├── postgres_manager.py
│   │   ├── models.py
│   │   └── chroma_manager.py
│   └── utils/
│       ├── logger.py
│       ├── threading_utils.py
│       └── file_utils.py
├── installer/
│   ├── voicenote.spec
│   └── setup.iss
└── tests/
```

## 6. Data Flow Pipelines

### 6.1 Record and Transcribe Flow

```text
Mic Input -> Audio Engine -> Save Local Audio File -> faster-whisper -> Transcript Data -> PostgreSQL
                                         |
                                         └-> UI Live Transcript View
```

### 6.2 AI Summary and Task Flow

```text
Transcript Text -> AI Engine (Ollama) -> Summary + Tasks -> PostgreSQL
                    |
                    └-> ChromaDB Vector Indexing
```

### 6.3 Semantic Search Flow

```text
User Query -> Vector Search -> Relevant Chunks -> Ranked Results -> UI Evidence View
```

### 6.4 Export Flow

```text
Selected Note -> Export Engine -> PDF/DOCX/TXT -> User File Destination
```

## 7. Deployment and Packaging Architecture

VoiceNote is designed to be a Windows desktop application packaged as a standalone executable using PyInstaller.

### Packaging Stack

- PyInstaller: creates the distributable executable bundle
- Inno Setup: creates an installer for end-user deployment
- Desktop and Start Menu shortcuts are added during installation
- Local config and data directories are created under the user profile app data folder

### Runtime Considerations

- Local dependency services such as Ollama and PostgreSQL must be available for full functionality
- The application behaves offline for most user flows after its local dependencies are configured
- Audio, transcript, export, and log paths are stored in user-local application directories

## 8. Design Principles

1. Modularity: each subsystem is isolated by responsibility.
2. Privacy-first: user data remains local and secure by default.
3. Responsiveness: background processing is decoupled from the UI thread.
4. Extensibility: new services such as plugins, sync or collaboration can be added later.
5. Reliability: structured data validation and service-layer boundaries reduce failure risk.

## 9. Non-Functional Requirements Supported by Architecture

- Responsive desktop UI
- Offline operation
- Secure local data persistence
- Fast transcription processing
- Scalable modular extension path
- Installation-ready desktop deployment using Windows packaging tools

## 10. Summary

The architecture of VoiceNote follows a layered, modular desktop application design that is well suited for local AI-driven voice note capture. It combines a modern Qt UI with offline AI, semantic indexing, and structured persistence to deliver a practical and privacy-focused desktop experience.
