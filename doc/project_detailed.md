# VoiceNote Desktop — Complete Project Documentation

> **Version**: 0.1.0  
> **Tagline**: *"LISTEN. UNDERSTAND. ORGANIZE. ACT."*  
> **Architecture**: Privacy-First Hybrid Dual-Database & File Storage System  
> **Target OS**: Windows 10/11 Desktop  
> **Core Stack**: Python 3.11+, PySide6 (Qt6), PostgreSQL, ChromaDB, Faster-Whisper, Gemini 3.8 Flash  

---

## 1. Executive Summary & Project Vision

**VoiceNote Desktop** is an enterprise-grade, privacy-centric desktop application designed to bridge the gap between unstructured vocal communication and structured, actionable productivity. Built specifically for local desktop environments, VoiceNote captures spoken dialogue from live microphones and internal computer audio (e.g., Zoom, Microsoft Teams, Google Meet), transcribes conversations with high precision across multiple languages (including English, Hindi, and Marathi), performs speaker diarization, generates executive summaries, extracts actionable tasks with assigned owners and deadlines, and indexes every word into a local vector database for semantic search.

### Core Problems Addressed
1. **Meeting Information Loss**: Vital decisions, commitments, budget figures, and ownership details discussed in meetings often get forgotten or lost in scratchpads.
2. **Cloud Privacy & Security Concerns**: Sending raw audio streams of confidential board meetings, financial projections, or internal discussions to multi-tenant cloud SaaS tools presents enterprise data governance and privacy risks.
3. **Multilingual & Indic Dialect Challenges**: Generic cloud transcription engines frequently misinterpret mixed-language conversations (e.g., Marathi/Hinglish), corrupt currency figures, and botch regional grammar endings.
4. **Search Inability**: Traditional audio recorders create opaque `.wav` or `.mp3` files that cannot be searched conceptually (e.g., searching for *"What was the approved vendor discount?"* without knowing the exact recording name or timestamp).

---

## 2. Core Team & Engineering Roles

| Team Member | Engineering Role | Key Modules & Contributions |
| :--- | :--- | :--- |
| **Tejas Rawool** (`@admin`) | **System Architect & Backend Lead** | PostgreSQL persistence layer, ChromaDB vector engine, multi-tier fallback Gemini LLM integration, live audio RMS/dBFS telemetry calibration, Marathi Devanagari `TranscriptCorrector`, cross-module cascading deletions, and test suite. |
| **Samar** | **UI/UX Lead & Presentation Architect** | PySide6 Bento Grid & Retro Warm Cream design system, `WaveformWidget`, `AudioRecorderWidget`, `TranscriptViewWidget`, `SummaryTaskWidget`, multi-format `ExportEngine` (PDF, DOCX, TXT), Lucide vector icon integration, and user authentication portal. |
| **Atharv** | **AI & Machine Learning Lead** | Initial Faster-Whisper and Groq STT integration, prompt engineering for meeting intelligence, JSON parsing, Pydantic data schemas, initial pipeline test harness, and Speaker Diarization engine. |

---

## 3. High-Level System Architecture

VoiceNote implements a **Triple-Tier Hybrid Storage Architecture** paired with an asynchronous background worker pipeline that keeps the PySide6 user interface completely responsive at 60 FPS.

```mermaid
graph TD
    subgraph UI_Layer ["Presentation Layer (PySide6 / Qt6)"]
        UI[MainWindow Desktop Interface]
        RecUI[AudioRecorderWidget & WaveformWidget]
        TransUI[TranscriptViewWidget & Speaker Blocks]
        SummUI[SummaryTaskWidget & Action Items]
        SearchUI[SemanticSearchWidget]
        DashUI[AnalyticsDashboardWidget]
    end

    subgraph Audio_Capture ["Audio Subsystem"]
        Mic[Microphone Hardware]
        SysAudio[WASAPI System Loopback (Teams/Zoom)]
        AudioEng[AudioEngine (SoundDevice / PyAudio / NumPy)]
    end

    subgraph Worker_Pipeline ["Asynchronous Background Worker (PipelineWorker / QThread)"]
        STT[Speech-to-Text: Faster-Whisper / Groq API]
        Corrector[TranscriptCorrector: Devanagari & Grammar Polish]
        Diarize[DiarizationEngine: Multi-Speaker Turn Segmentation]
        AI[AIEngine: Gemini 3.8 Flash (Multi-Tier Fallback)]
        Chunker[Embedding Generator: all-MiniLM-L6-v2]
    end

    subgraph Storage_Tiers ["Triple-Tier Storage Architecture"]
        FS[(Local File System: data/recording/*.wav)]
        PG[(PostgreSQL Database: Relational Metadata & Tasks)]
        Chroma[(ChromaDB: Vector Embeddings & Similarity Index)]
    end

    Mic --> AudioEng
    SysAudio --> AudioEng
    AudioEng --> FS
    AudioEng --> RecUI

    RecUI -->|Audio File Reference| Worker_Pipeline
    Worker_Pipeline --> STT
    STT --> Corrector
    Corrector --> Diarize
    Diarize --> AI
    Diarize --> Chunker
    AI --> Chunker

    FS -.->|WAV Path| PG
    Diarize -.->|Diarized Text| PG
    AI -.->|Summary & Extracted Tasks| PG
    Chunker -.->|Document Vectors & Metadata| Chroma

    PG --> UI
    Chroma -->|Cosine Distance Scores| SearchUI
    PG -->|Enriched Note Objects| SearchUI
    PG --> DashUI
```

---

## 4. Triple-Tier Storage Architecture Specification

| Storage Tier | Technology | Items Stored | Capabilities & Rationale |
| :--- | :--- | :--- | :--- |
| **Tier 1: Relational Database** | **PostgreSQL 14+** (`psycopg2`) | • User profiles & password hashes<br>• Note metadata (`title`, `duration`, `audio_path`, `category`)<br>• Raw & cleaned transcripts<br>• Structured summaries, topics, sentiment<br>• Actionable tasks (`assignee`, `due_date`, `priority`, `status`) | • ACID transactional integrity<br>• Foreign key cascading constraints (`ON DELETE CASCADE`)<br>• Fast relational queries by date, tag, and status |
| **Tier 2: Vector Database** | **ChromaDB** (`chromadb`) | • 384-dimensional dense text embeddings<br>• Transcript chunks with timestamps<br>• Summary concept embeddings<br>• Filterable document metadata | • Sub-second cosine similarity searches<br>• Natural language semantic search (concept matching over keyword matching)<br>• Timestamp jumping from search results |
| **Tier 3: Local Disk Storage** | **File System** (`data/recording/`) | • Uncompressed 16-bit 16kHz PCM `.wav` audio files | • Zero-latency native audio playback<br>• Keeps PostgreSQL database lightweight and fast |

---

## 5. Relational Database Schema (PostgreSQL)

```sql
-- 1. Users & Authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Voice Notes Metadata
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at VARCHAR(100) NOT NULL,
    duration VARCHAR(50) DEFAULT '00:00',
    audio_path TEXT,
    category VARCHAR(100) DEFAULT 'General'
);

-- 3. Transcripts (Diarized & Segmented)
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT,
    language VARCHAR(20) DEFAULT 'en'
);

-- 4. AI Structured Summaries
CREATE TABLE ai_summaries (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    key_points TEXT,     -- Serialized JSON array of strings
    sentiment VARCHAR(50) DEFAULT 'Neutral',
    main_topics TEXT     -- Serialized JSON array of strings
);

-- 5. Actionable Tasks Board
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(50) DEFAULT 'Medium',      -- 'Urgent', 'High', 'Medium', 'Low'
    assignee VARCHAR(100) DEFAULT 'Unassigned',  -- Identified speaker or role
    due_date VARCHAR(100) DEFAULT 'TBD',         -- Extracted date or deadline
    status VARCHAR(50) DEFAULT 'Pending'        -- 'Not Started', 'In Progress', 'Completed'
);
```

---

## 6. ChromaDB Vector Store Schema

* **Collection Name**: `voicenote_embeddings`
* **Embedding Model**: Default sentence-transformers (`all-MiniLM-L6-v2`) or Chroma internal embedding function.
* **Document Chunk ID Pattern**: `note_{note_id}_chunk_{chunk_index}`
* **Document Content**: Individual timestamped dialogue blocks or summary paragraphs.
* **Metadata Schema**:
  ```json
  {
    "note_id": 14,
    "title": "NovaFlow Sprint Standup",
    "category": "Sprint Planning",
    "speaker": "Speaker 2",
    "start_time": "00:12",
    "end_time": "00:35",
    "created_at": "2026-09-22 19:20"
  }
  ```
* **Similarity Score Formula**: Normalized confidence percentage calculated via cosine distance $d$:
  $$\text{Relevance Score} = \max(0, \min(100, (1.0 - d) \times 100))$$

---

## 7. Complete Technology Stack

| Layer / Subsystem | Technology | Purpose |
| :--- | :--- | :--- |
| **Runtime & Language** | Python 3.11+ | Primary application language |
| **GUI Framework** | PySide6 (Qt6) | High-performance, cross-platform native desktop UI |
| **Relational Database** | PostgreSQL 14+ | ACID metadata, user authentication, and relational data |
| **Database Driver** | `psycopg2` | High-performance PostgreSQL connector |
| **Vector Database** | ChromaDB (`chromadb`) | Local embedding store and vector search engine |
| **Audio Processing** | `sounddevice`, `numpy`, `soundfile`, `PyAudio` | Hardware audio capture, WASAPI loopback, RMS/dBFS calculation |
| **Speech-to-Text (Local)** | `faster-whisper` (CTranslate2) | GPU/CPU accelerated local transcription |
| **Speech-to-Text (Cloud)** | Groq API (`whisper-large-v3`) | Low-latency cloud transcription fallback |
| **Generative AI / LLM** | Google GenAI (`gemini-3.8-flash`) | Executive summaries, meeting plans, task extraction |
| **Devanagari Correction** | Custom Gemini AI Engine | Specialized prompt chain correcting Marathi grammar and currency |
| **PDF Generation** | ReportLab (`reportlab`) | Enterprise PDF generator with custom palettes and table layout |
| **Word Generation** | `python-docx` | Native Microsoft Word document compilation |
| **Icons & Typography** | Lucide SVG + Noto Sans Devanagari | High-DPI scalable vector icons and native Indic typography |
| **Testing** | `unittest`, `pytest` | 9-module automated testing pipeline |

---

## 8. End-to-End Processing Pipeline Walkthrough

```text
[Input Source] (Mic / System Loopback / WAV Upload)
       │
       ▼
[AudioEngine Calibration] (Computes Peak dBFS & RMS Signal)
       │
       ▼
[WAV Serialization] (16-bit 16kHz Mono to data/recording/recording_YYYYMMDD_HHMMSS.wav)
       │
       ▼
[STT Engine] (faster-whisper auto-detects language or Groq whisper-large-v3)
       │
       ▼
[TranscriptCorrector] (Gemini post-processor cleans Marathi endings, fixes numbers & Rs.)
       │
       ▼
[DiarizationEngine] (Segments turns into Speaker 1, Speaker 2, etc. with timestamps)
       │
       ▼
[AIEngine Analysis] (Gemini 3.8 Flash extracts Executive Summary, Key Takeaways, Tasks)
       │
       ▼
[VectorEngine Indexing] (Chunks text, generates embeddings, stores into ChromaDB)
       │
       ▼
[PostgreSQL Persistence] (Transacts Note, Transcript, AISummary, and Tasks atomically)
       │
       ▼
[PySide6 UI Signals] (Refreshes Notes sidebar, populates TranscriptView and SummaryTask)
```

### Detailed Pipeline Steps:
1. **Audio Capture & Hardware Calibration**:
   - The user selects either `Microphone`, `System Audio`, or `Both`.
   - `AudioEngine` establishes a callback stream calculating real-time Root Mean Square (RMS) amplitude and peak dBFS levels.
   - Attack/release smoothing prevents jittery visual meters.
   - Upon pressing **Record**, raw audio is buffered and written to `data/recording/recording_YYYYMMDD_HHMMSS.wav`.
2. **Speech Recognition (STT)**:
   - If cloud processing is enabled and `GROQ_API_KEY` is present, audio is routed to Groq's `whisper-large-v3` for sub-3-second transcription.
   - If offline or on failure, `faster-whisper` (`small` or `base` model) runs locally via CTranslate2.
3. **Multilingual Transcript Correction**:
   - For Indic languages (especially Marathi and Hindi), Whisper often confuses verb endings (e.g., using Hindi *'है'* instead of Marathi *'आहे'*, or phonetic *'महंजे'* instead of *'म्हणजे'*).
   - `TranscriptCorrector` invokes Gemini to restore standard Devanagari grammar without translating English business jargon (e.g., keeping *"Annual Employee Conference"*, *"Quotation"*, *"Budget"*).
   - Standardizes Indian currency expressions (e.g., `Rs. 5,45,000` / `₹5,45,000`) and percentages (`%`).
4. **Speaker Diarization**:
   - `DiarizationEngine` analyzes acoustic changes and speech pauses to group utterances into distinct speaker identities (`Speaker 1`, `Speaker 2`, `Speaker 3`).
5. **AI Synthesis & Intelligence Extraction**:
   - `AIEngine` prompts `gemini-3.8-flash` with a strict JSON contract.
   - Extracts:
     - **Executive Summary**: High-level executive synthesis.
     - **Key Takeaways**: Bulleted findings and metrics.
     - **Action Items**: Explicit deliverables with owners, due dates, and priority tags.
     - **Important Numbers & Risks**: Budget variations, technical bottlenecks, and timeline dependencies.
   - If `gemini-3.8-flash` encounters transient 503 load spikes, the system automatically falls back to `gemini-2.5-flash`, `gemini-2.0-flash`, or `gemini-1.5-flash`.
6. **Vector Indexing**:
   - `VectorEngine` chunks the transcript by speaker turn and indexes chunks along with note metadata into ChromaDB.
7. **Relational Database Synchronization**:
   - `DatabaseManager` commits all models into PostgreSQL in a thread-safe transaction.
8. **UI Presentation**:
   - The background `PipelineWorker` emits Qt signals (`progress(int, str)` and `finished(dict)`), unlocking the UI and navigating directly to the formatted note.

---

## 9. Comprehensive Codebase & Directory Structure

```text
VoiceNote/
├── .agents/                        # Agentic workflow rules and skills
├── assets/                         # Static design assets
│   ├── fonts/                      # Embedded TrueType fonts (NotoSansDevanagari, Nirmala UI)
│   ├── icons/                      # Scalable Lucide vector SVGs
│   └── mockups/                    # Design system references
├── chroma_db/                      # Local persistent ChromaDB vector store
├── data/                           # Application runtime data
│   └── recording/                  # Centralized PCM WAV audio files
├── doc/                            # Technical architecture documentation
│   ├── architecture.md             # Storage & database specification
│   ├── database-setup.md           # PostgreSQL configuration guide
│   ├── dev/                        # Developer activity journals
│   │   ├── atharv.md               # AI & STT progress log
│   │   ├── samar.md                # UI/UX & design progress log
│   │   └── tejas.md                # Architecture, database & pipeline log
│   ├── implementation-plan.md      # Milestone implementation roadmap
│   ├── module-breakdown.md         # Detailed module responsibilities
│   └── srs.md                      # Formal Software Requirements Specification
├── tests/                          # Automated unit and integration tests
│   ├── test_ai_engine.py           # Gemini API & prompt validation tests
│   ├── test_analytics_engine.py    # Metric aggregation & calculation tests
│   ├── test_audio_recording.py     # WAV serialization & file storage tests
│   ├── test_auth.py                # Password hashing & user auth tests
│   ├── test_db.py                  # PostgreSQL CRUD & cascading deletion tests
│   ├── test_diarization.py         # Multi-speaker segmentation tests
│   ├── test_export_engine.py       # PDF, DOCX, TXT document generation tests
│   ├── test_pipeline.py            # End-to-end processing pipeline tests
│   └── test_vector_engine.py       # ChromaDB semantic query & deletion tests
├── Voicenote_ss/                   # Production UI screenshots & walkthroughs
├── voicenote/                      # Core application package
│   ├── __init__.py
│   ├── config.py                   # Centralized application constants & paths
│   ├── core/                       # Core service engines
│   │   ├── ai_engine.py            # Gemini LLM orchestration & JSON parser
│   │   ├── analytics_engine.py     # Productivity & duration analytics
│   │   ├── audio_engine.py         # Hardware audio capture & dBFS telemetry
│   │   ├── diarization_engine.py   # Speaker separation & turn assignment
│   │   ├── export_engine.py        # ReportLab PDF, DOCX, & TXT compiler
│   │   ├── groq_stt_engine.py      # Cloud Groq Whisper STT driver
│   │   ├── stt_engine.py           # Local Faster-Whisper STT driver
│   │   ├── text_cleaner.py         # Whitespace & punctuation normalization
│   │   ├── transcript_corrector.py # Multilingual Indic/Devanagari correction
│   │   └── vector_engine.py        # ChromaDB indexer & semantic search queries
│   ├── db/                         # Data storage layer
│   │   ├── database.py             # PostgreSQL DatabaseManager & connection pool
│   │   └── models.py               # Data dataclasses (Note, Transcript, Task, User)
│   ├── services/                   # Background execution services
│   │   └── worker.py               # Non-blocking PySide6 QThread PipelineWorker
│   └── ui/                         # Presentation layer (PySide6)
│       ├── icon_helper.py          # Lucide SVG tinting & QIcon factory
│       ├── main_window.py          # Master window, navigation & state manager
│       ├── styles.py               # Bento Grid & Retro Warm Cream QSS design system
│       ├── components/             # Reusable UI widgets
│       │   ├── analytics_dashboard_widget.py # Charts & usage metrics
│       │   ├── audio_recorder_widget.py      # Recording controls & calibration
│       │   ├── header.py                     # Global search & profile header
│       │   ├── login_showcase_widgets.py     # Bento Grid feature cards for login
│       │   ├── note_card.py                  # Note list card item
│       │   ├── semantic_search_widget.py     # Vector search query & score cards
│       │   ├── sidebar.py                    # Left navigation sidebar
│       │   ├── summary_task_widget.py        # AI executive summary & task board
│       │   ├── transcript_view_widget.py     # Color-coded speaker transcript viewer
│       │   └── waveform_widget.py            # QPainter live audio wave visualizer
│       └── dialogs/                # Modal dialogs
│           ├── export_dialog.py              # PDF/DOCX/TXT custom export dialog
│           ├── login_dialog.py               # Full-screen Bento Grid auth modal
│           ├── processing_dialog.py          # Progress dialog for AI pipeline
│           ├── profile_dialog.py             # User profile & sign-out dialog
│           └── settings_dialog.py            # Audio device & engine preferences
├── .env.example                    # Template environment configuration
├── main.py                         # Application bootstrap entry point
├── pyproject.toml                  # Project packaging metadata
├── README.md                       # High-level documentation index
├── requirements.txt                # Python runtime dependencies
├── run_all_tests.py                # Unified 9-module quality gate test runner
└── task_plan.md                    # Developer milestone tracker
```

---

## 10. Key Modules & Subsystem Details

### 10.1 `voicenote/core/audio_engine.py`
* **Purpose**: Hardware-level sound recording and real-time audio analysis.
* **Capabilities**:
  * Scans and enumerates all input devices (microphones, USB interfaces, virtual loopbacks).
  * Computes real-time Root Mean Square (RMS) amplitude and Peak decibels relative to full scale (dBFS):
    $$\text{dBFS} = 20 \times \log_{10}(\text{Peak Amplitude})$$
  * Manages continuous recording buffer using `sounddevice` and converts raw numpy arrays into standard 16-bit 16000 Hz mono PCM WAV files.
  * Supports test mode to allow audio level calibration without writing files to disk.

### 10.2 `voicenote/core/transcript_corrector.py`
* **Purpose**: Devanagari and multilingual grammar polish engine.
* **Capabilities**:
  * Corrects Whisper transcription artifacts for Marathi and Hindi dialects.
  * Enforces proper Marathi verb auxiliary forms (*'आहे'*, *'नाही'*, *'झाले'*).
  * Preserves English corporate loan words in Latin or clean Devanagari script without garbled transliteration.
  * Standardizes currency numbers into Indian numbering format (e.g., `₹2,40,000`, `₹6,00,000`).

### 10.3 `voicenote/core/ai_engine.py`
* **Purpose**: LLM orchestration using Google GenAI SDK.
* **Capabilities**:
  * Default model: `gemini-3.8-flash`.
  * Fallback ladder: If `gemini-3.8-flash` triggers an HTTP 503/429, the engine automatically tries `gemini-2.5-flash` ➔ `gemini-2.0-flash` ➔ `gemini-1.5-flash`.
  * Enforces JSON output adhering to the Pydantic schema:
    - `summary`: High-level narrative summary.
    - `key_points`: List of atomic takeaway bullet points.
    - `tasks`: Array of objects (`title`, `assignee`, `due_date`, `priority`).
    - `sentiment`: Sentiment classification (`Positive`, `Neutral`, `Constructive`).
    - `main_topics`: Extracted category tags.

### 10.4 `voicenote/core/vector_engine.py`
* **Purpose**: Semantic vector search engine powered by ChromaDB.
* **Capabilities**:
  * Splits transcripts into semantic chunks with speaker metadata and timestamps.
  * Computes dense vector embeddings.
  * Executes query vector distance lookups using cosine similarity.
  * Supports atomic `delete_note(note_id)` and bulk `delete_all()` to keep ChromaDB synchronized with PostgreSQL deletions.

### 10.5 `voicenote/core/export_engine.py`
* **Purpose**: Professional document generation.
* **Capabilities**:
  * **PDF Export**: Built with ReportLab using a custom color palette, embedded Noto Sans Devanagari fonts for accurate Indic script shaping, styled metadata cards, callout boxes for executive summaries, structured task tables, and speaker-attributed transcripts.
  * **DOCX Export**: Generates fully formatted Microsoft Word `.docx` documents with native Heading 1/2 styles, bullet lists, checkboxes, and formatted dialogue blocks.
  * **TXT Export**: Clean ASCII/UTF-8 formatted plaintext layout.

---

## 11. UI/UX Design System & Aesthetics

VoiceNote employs a **Retro Warm Cream Bento Grid** visual identity designed in PySide6 QSS (`voicenote/ui/styles.py`):

* **Color Palette**:
  * Canvas Background: Warm Cream (`#ECE7DF`, `#FBF9F5`)
  * Primary Accent: Deep Slate Indigo (`#4A3E72`, `#5B4E8C`)
  * Success / Active Accent: Emerald Sage (`#2E7D32`, `#E8F5E9`)
  * Warning / Urgent Accent: Warm Amber & Rose (`#D32F2F`, `#F57C00`)
  * Text Colors: High-contrast Charcoal (`#1E1E24`, `#2D2A26`) and Muted Grey (`#6E6B65`)
* **Typography & Layout**:
  * Crisp typography with embedded support for **Noto Sans Devanagari** and **Nirmala UI**.
  * Bento Grid card hierarchy with clean 12px rounded borders and subtle drop shadows.
  * **Elimination of Wireframe Artifacts**: All `QLabel` and container components use reset border rules to prevent harsh rectangular lines, replaced with soft-tinted pill badges.
* **Vector Icons**:
  * Integrated **Lucide SVG** vector icon library in `assets/icons/` loaded dynamically via `IconHelper` with resolution-independent vector rendering.

---

## 12. Application Screen Tour (Production Walkthrough)

Based on the production screenshots in [Voicenote_ss](file:///d:/D/VoiceNote/Voicenote_ss):

1. **Authentication Portal (`login_dialog.py`)**:
   * Dual-panel showcase featuring the VoiceNote value proposition on the left and a streamlined PostgreSQL authentication card on the right.
   * Includes one-click quick demo login for administrative review.
2. **Home Recorder & Calibration (`audio_recorder_widget.py`)**:
   * Live statistics banner showing total notes, recorded audio time, active tasks, and privacy status.
   * Audio source toggle (`Microphone`, `System Audio`, `Both`) with real-time VU meter calibration (-60 dBFS to 0 dBFS) and live animated `WaveformWidget`.
3. **Transcripts & Notes (`transcript_view_widget.py`)**:
   * Multi-speaker dialogue bubbles color-coded by speaker (e.g., Speaker 1 in Purple, Speaker 2 in Teal, Speaker 3 in Amber).
   * Supports seamless multilingual dialogue, from English corporate standups to Indic Marathi budget negotiations.
   * Full-text search and timestamp jumping.
4. **AI Summary & Action Items (`summary_task_widget.py`)**:
   * Multi-tab intelligence dashboard: `Overview`, `Action Items`, `Your Meeting Plan`, `Important Numbers`, and `Risks`.
   * Interactive task list with checkable completion status, assignee pill badges, urgency tags, and manual task creation.
5. **Semantic Search (`semantic_search_widget.py`)**:
   * Natural language query interface returning ranked result cards with relevance percentage badges (e.g., `92% Match`) and snippet previews.
6. **Analytics Dashboard (`analytics_dashboard_widget.py`)**:
   * High-level productivity metrics: weekly recording activity, word count accumulation, task completion velocity, and AI time saved estimation.

---

## 13. Installation, Setup & Developer Guide

### 13.1 Prerequisites
* **Operating System**: Windows 10 or Windows 11 (64-bit).
* **Python**: Version 3.11 or higher.
* **PostgreSQL**: Version 14 or higher running locally or accessible via network.
* **C++ Build Tools**: Required for compiling CTranslate2 / faster-whisper if prebuilt wheels are not cached.
* **Audio Drivers**: Functioning microphone or stereo mix / virtual loopback device.

### 13.2 Environment Configuration (`.env`)
Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME=VoiceNote
VERSION=0.1.0

# Database Configuration (Strictly PostgreSQL Engine)
DB_ENGINE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=voicenote
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# AI & Speech Recognition API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash

GROQ_API_KEY=your_groq_api_key_here
GROQ_STT_MODEL=whisper-large-v3
LOCAL_STT_MODEL=small
```

### 13.3 Installation Steps
```powershell
# 1. Clone repository and navigate to root
cd d:\D\VoiceNote

# 2. Activate Python Virtual Environment
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify PostgreSQL Database Initialization
# The application automatically runs CREATE DATABASE voicenote and table schemas if not present.
python run_all_tests.py

# 5. Launch Application
python main.py
```

### 13.4 Running the Test Suite
VoiceNote includes an automated 9-module quality gate in `run_all_tests.py`:

```powershell
python run_all_tests.py
```

The test runner verifies:
1. PostgreSQL Database Connectivity & Seeding
2. Text Cleaner Normalization
3. Audio Recording Storage (`data/recording/`)
4. Gemini AI Engine & Structured Prompt Schemas
5. ReportLab & python-docx Export Engine (PDF, DOCX, TXT)
6. Analytics Engine Metric Calculations
7. ChromaDB Vector Store & Cosine Similarity Lookups
8. User Authentication & Password Hashing
9. PySide6 GUI Component Initialization

---

## 14. Project Milestones & Development History

### Milestone 1: Foundations & Dual-Database Layer
* Initialized PySide6 desktop architecture and established application configuration constants.
* Transitioned from embedded SQLite to robust PostgreSQL persistence with foreign key cascading deletion.
* Implemented ChromaDB vector database integration with segment chunking and metadata attribution.

### Milestone 2: Presentation & Design System Overhaul
* Rebuilt entire desktop UI using Bento Grid layout and Retro Warm Cream visual design.
* Developed full-featured authentication system with SHA-256 password hashing.
* Built ReportLab multilingual PDF export engine and python-docx Word exporter.
* Implemented `AnalyticsEngine` for productivity insights and tag usage trends.

### Milestone 3: Real-Time Audio & Indic Language Intelligence
* Built real-time audio telemetry in `AudioEngine` (RMS amplitude, peak dBFS, input switching, WASAPI system audio loopback).
* Upgraded to Google GenAI `gemini-3.8-flash` with resilient multi-tier fallback against API throttling.
* Built `TranscriptCorrector` to resolve Devanagari grammar discrepancies for Marathi and Hindi dialogues.
* Replaced raster images with Lucide SVG vector icon system and embedded Noto Sans Devanagari TrueType fonts.

### Milestone 4: Quality Assurance & Cross-Module Synchronization
* Implemented synchronized three-way note deletion (PostgreSQL row purge, local WAV file removal, and ChromaDB vector deletion).
* Added automated database reseeding in test runner.
* Verified 100% test pass rate across all 9 core subsystems.

---

## 15. Future Roadmap & Packaging (Phase 5)

* **PyInstaller Standalone Executable**: Bundling Python runtime, PySide6 binaries, CTranslate2 DLLs, and embedded fonts into a single `VoiceNote.exe`.
* **Inno Setup Windows Installer**: Windows installer wizard with desktop shortcuts, Start Menu entries, and uninstaller logic.
* **Hardware Accelerated Diarization**: Integrating local PyAnnote neural audio speaker diarization when GPU acceleration (NVIDIA CUDA) is present.
* **Encrypted Vault Storage**: Optional AES-256 encryption on rest for local audio recordings in `data/recording/`.
