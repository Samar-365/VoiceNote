# VoiceNote Desktop — Enterprise Voice Intelligence System

<div align="center">

![VoiceNote Logo](assets/voicenote_logo.png)

### *"LISTEN. UNDERSTAND. ORGANIZE. ACT."*

**A Privacy-First, Multilingual Desktop Intelligence Platform with Triple-Tier Hybrid Storage**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52.svg)](https://wiki.qt.io/Qt_for_Python)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2014%2B-336791.svg)](https://www.postgresql.org/)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-FF6F00.svg)](https://www.trychroma.com/)
[![Whisper](https://img.shields.io/badge/STT-Faster--Whisper-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![Gemini](https://img.shields.io/badge/AI%20Engine-Gemini%203.8%20Flash-4285F4.svg)](https://ai.google.dev/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011%20(64--bit)-0078D6.svg)](https://www.microsoft.com/windows)
[![Tests](https://img.shields.io/badge/Quality%20Gate-100%25%20Passing-success.svg)](run_all_tests.py)

[Features](#-core-features) •
[System Architecture](#-system-architecture) •
[Interaction Lifecycle](#-user-interaction-lifecycle) •
[Screen Tour](#-production-screen-tour) •
[Tech Stack](#-technical-specifications) •
[Quickstart](#-installation--quickstart-guide) •
[Team](#-engineering-team--module-ownership)

---

</div>

## 📌 Executive Summary & Project Vision

**VoiceNote Desktop** is an enterprise-grade, privacy-centric voice intelligence platform built specifically for Windows desktop environments. It bridges the gap between unstructured vocal communication (meetings, board conferences, technical standups, and voice notes) and actionable productivity.

VoiceNote captures dialogue from physical microphones and internal computer sound (via **Windows WASAPI System Loopback** for Zoom, Microsoft Teams, and Google Meet without requiring meeting bots), transcribes multi-speaker audio across English, Hindi, and Marathi, performs speaker diarization, generates executive summaries, extracts actionable deliverables with assigned owners and due dates, and indexes every utterance into a local vector database for sub-second semantic retrieval.

---

## 🏛️ System Architecture

VoiceNote implements a high-performance **8-Layer Architecture** designed to keep the desktop user interface completely fluid at 60 FPS while background workers execute computationally intensive speech recognition, vector indexing, and generative AI analysis:

<div align="center">

![System Architecture](assets/system_architecture.jpg)

</div>

### Architectural Layers:
1. **User Interface Layer**: Native PySide6 (Qt6) interface styled with a custom Bento Grid and Retro Warm Cream design system.
2. **Audio Acquisition Layer**: Captures physical microphones, USB headsets, and internal system audio (WASAPI Loopback) with real-time dBFS and RMS telemetry.
3. **Speech Processing Layer**: Dual-engine transcription using local **Faster-Whisper** (CTranslate2 int8) with cloud fallback to **Groq API** (`whisper-large-v3`).
4. **Speaker Diarization Layer**: Acoustic pause detection and turn segmentation attributing utterances to distinct speaker labels (`Speaker 1`, `Speaker 2`, etc.).
5. **AI Intelligence Layer**: Generative analysis via **Google GenAI (Gemini 3.8 Flash)** with a resilient fallback ladder (`3.8-flash` ➔ `2.5-flash` ➔ `2.0-flash` ➔ `1.5-flash`).
6. **Document Management Layer**: Structured intelligence extraction (Executive Summaries, Key Decisions, Action Items, Deadlines, and Numbers).
7. **Export & Access Layer**: Multi-format document compilation (ReportLab PDF with embedded Noto Sans Devanagari fonts, Microsoft Word `.docx`, and plaintext `.txt`).
8. **Triple-Tier Data Storage Layer**:
   - **PostgreSQL 14+**: ACID relational metadata, note records, transcripts, and cascading task boards.
   - **ChromaDB**: 384-dimensional dense text embeddings (`all-MiniLM-L6-v2`) with an HNSW index for natural language semantic search.
   - **Local File System**: Raw 16 kHz 16-bit Mono PCM `.wav` audio files in `data/recording/`.

---

## 🔄 User Interaction Lifecycle

The end-to-end lifecycle illustrates how audio transitions from raw acoustic signals into structured knowledge, action items, and searchable reports:

<div align="center">

![User Interaction Lifecycle](assets/user_interaction_lifecycle.png)

</div>

---

## 🚀 Core Features

* 🎙️ **Dual-Source Audio Capture & Loopback**: Seamlessly record physical microphone input, system audio (capturing internal sound from Teams/Zoom/Meet directly without external room echo), or both simultaneously.
* 📊 **Real-Time dBFS Calibration**: High-precision VU meter (calibrated from $-60\text{ dBFS}$ noise floor to $0\text{ dBFS}$ peak) with 60 FPS animated QPainter `WaveformWidget`.
* 🗣️ **Multilingual & Indic Devanagari Polish**: Specialized prompt engineering and Gemini `TranscriptCorrector` to resolve Whisper translation drift and preserve authentic Marathi and Hindi grammar and Indian currency (`₹`).
* 👥 **Acoustic Speaker Diarization**: Multi-speaker turn segmentation with color-coded dialogue bubbles and millisecond timestamps.
* 🧠 **Pydantic-Validated Meeting Intelligence**: Gemini 3.8 Flash extracts executive narrative summaries, key decisions, project risks, important numbers, and deliverables with urgency ratings (`HIGH`, `MEDIUM`, `LOW`).
* 🔍 **ChromaDB Sub-Second Semantic Search**: Conceptual search matching meaning and intent rather than literal keywords with ranked cosine relevance percentages (`96% Match`).
* 📄 **Multi-Format Export Engine**: One-click generation of professional PDF meeting minutes (with embedded Devanagari typography), Word `.docx` documents, and plaintext files.
* 📈 **Productivity Analytics Dashboard**: Visual graphs tracking weekly recording trends, task completion velocity, and estimated hours saved by AI automation.

---

## 🖥️ Production Screen Tour

### 1. Home Dashboard & Live Audio Calibration
*Dual-source recording selection, real-time dBFS level monitoring, waveform visualization, and live session counters.*
![Home Dashboard & Live Audio Calibration](assets/home_recorder.png)

---

### 2. Multi-Speaker Diarized Transcripts
*Color-coded speaker dialogue turns with millisecond timestamp seeking and Devanagari script support.*
![Transcripts & Notes](assets/transcripts_notes.png)

---

### 3. AI Executive Summary & Action Board
*Structured meeting synthesis, key decisions, and interactive task board with assignees and due dates.*
![AI Summary & Action Items](assets/ai_summary_tasks.png)

---

### 4. ChromaDB Sub-Second Semantic Search
*Natural language conceptual retrieval across all notes with ranked similarity match badges.*
![Semantic Search](assets/semantic_search.png)

---

### 5. Productivity Analytics & Insights Dashboard
*Weekly recording trends, task velocity metrics, and quantified time-saved calculations.*
![Analytics Dashboard](assets/analytics_dashboard.png)

---

## ⚙️ Technical Specifications

### Audio Pipeline Parameters
* **Capture Format**: Linear Uncompressed PCM (WAV)
* **Sampling Rate ($f_s$)**: $16,000\text{ Hz (16 kHz)}$
* **Bit Depth**: $16\text{-bit Signed Integer (int16)}$
* **Channel Configuration**: $1\text{ (Mono)}$
* **Bitrate**: $256\text{ kbps} = 32\text{ KB/second}$
* **Storage Consumption**: $1.875\text{ MB/minute} \approx 112.5\text{ MB/hour}$

### Empirical Processing Latency (Real-Time Factor Benchmarks)

$$\text{RTF} = \frac{\text{Processing Duration}}{\text{Audio Duration}}$$

| Audio Duration | WAV File Size | Local Mode (Faster-Whisper int8) | Cloud Mode (Groq whisper-large-v3) | Post-Processing (LLM + Vector) | Total Turnaround Time |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Minute** | $1.875\text{ MB}$ | $\approx 9 - 14\text{ s}$ | $\approx 1.5 - 2.5\text{ s}$ | $\approx 2.5\text{ s}$ | **$\approx 15\text{s}$ (Local) / $\approx 4.5\text{s}$ (Cloud)** |
| **2 Minutes**| $3.75\text{ MB}$ | $\approx 18 - 25\text{ s}$ | $\approx 2.8 - 4.0\text{ s}$ | $\approx 3.0\text{ s}$ | **$\approx 25\text{s}$ (Local) / $\approx 6.5\text{s}$ (Cloud)** |
| **5 Minutes**| $9.375\text{ MB}$ | $\approx 45 - 60\text{ s}$ | $\approx 6.0 - 8.5\text{ s}$ | $\approx 4.0\text{ s}$ | **$\approx 55\text{s}$ (Local) / $\approx 11.5\text{s}$ (Cloud)** |
| **10 Minutes**| $18.75\text{ MB}$ | $\approx 90 - 130\text{ s}$ | $\approx 12 - 18\text{ s}$ | $\approx 5.5\text{ s}$ | **$\approx 115\text{s}$ (Local) / $\approx 20.0\text{s}$ (Cloud)** |

---

## 🛠️ Installation & Quickstart Guide

### 1. Prerequisites
* **Operating System**: Windows 10 or Windows 11 (64-bit)
* **Python**: Version `3.11` or higher
* **PostgreSQL**: Version `14+` running locally or accessible via network

### 2. Clone & Environment Setup
```powershell
# Clone the repository
git clone https://github.com/Samar-365/VoiceNote.git
cd VoiceNote

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables (`.env`)
Create a `.env` file in the project root:
```env
# Application Settings
APP_NAME=VoiceNote
VERSION=0.1.0

# Database Configuration (PostgreSQL 14+)
=======
# VoiceNote: Intelligent Desktop Audio Intelligence & Semantic Retrieval System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20Qt6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-FF6F61)](https://www.trychroma.com/)
[![Gemini AI](https://img.shields.io/badge/LLM-Gemini%203.8%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Whisper STT](https://img.shields.io/badge/STT-Faster--Whisper%20%7C%20Groq-F55036)](https://github.com/SYSTRAN/faster-whisper)

**VoiceNote** is a privacy-first, offline-capable Windows desktop application designed to transform spoken meetings, lectures, and voice memos into structured, searchable intelligence. It features live audio waveform capture, multilingual transcription with specialized Marathi/Hindi code-switching correction, automated speaker diarization, AI-driven action item extraction, and natural language semantic retrieval powered by a hybrid dual-database architecture.

---

## Simple Workflow Diagram

How a recording turns into actionable knowledge:

```mermaid
flowchart LR
    A[Record / Upload Audio] --> B[Speech-to-Text]
    B --> C[Multilingual Grammar Fix]
    C --> D[Speaker Diarization]
    D --> E[Gemini Structured AI]
    E --> F[(Dual Storage:\nPostgres + ChromaDB)]
    F --> G[Semantic Search & Analytics]
```

### Step-by-Step User Journey:
1. **Capture**: Speak into the microphone with a real-time 60 FPS waveform display, or upload any `.wav`, `.mp3`, or `.m4a` recording.
2. **Transcribe**: Audio is processed locally via `faster-whisper` (offline) or accelerated via `Groq LPU` (cloud).
3. **Correct & Diarize**: Proprietary linguistic rules fix Indian multilingual code-switching (e.g. Marathi verbs confused with Hindi), strip distracting timestamps, and assign persistent speaker color tags.
4. **Extract Intelligence**: Google Gemini models map conversational transcripts into rigid Pydantic schemas: Executive Summaries, Action Items (Assignee, Priority, Due Date), Key Decisions, and Numbers.
5. **Store & Retrieve**: Relational data commits to **PostgreSQL**, while dense vector embeddings index into **ChromaDB** for instant natural language semantic retrieval.

---

## Key Features

- **Real-Time Waveform & Studio Audio Capture**: High-fidelity recording with live Decibel (dBFS) normalization using `sounddevice` and Windows WASAPI loopback support.
- **Dual-Engine Speech Recognition**: Offline-first via `faster-whisper` (CTranslate2 8-bit quantized) with zero cloud dependency, plus instant cloud inference via Groq `whisper-large-v3`.
- **Multilingual Code-Switching Corrector**: Solves Whisper's known degradation with regional languages (Marathi/Hindi mixed with English), restoring proper Devanagari grammar and undoing spontaneous mistranslations.
- **Speaker Diarization & Script Formatting**: Distinguishes multiple voices, merges contiguous dialogue into natural paragraphs, and strips noisy timestamp clutter.
- **Actionable Task & Decision Extraction**: Automatically extracts tasks with assignees, priorities, and deadlines, directly populated into an interactive task board.
- **Semantic Vector Search (RAG-Ready)**: Ask natural language questions like *"What did we decide about the budget?"* and retrieve matching notes based on conceptual meaning, not just exact keywords.
- **Real Data Analytics Dashboard**: 100% computed metrics: speaker talk-time distribution, sentiment analysis, task completion ratios, and recording trends over 7/30/90 days.
- **Multi-Format Document Export**: One-click generation of professional PDF reports (via ReportLab) and editable Microsoft Word documents (`.docx`).

---

## System Architecture

### 1. High-Level Layered Architecture

```mermaid
graph TB
    subgraph UI_Layer ["1. Presentation Layer (PySide6 / Qt6)"]
        MW["MainWindow & Router"]
        REC["AudioRecorderWidget (Waveform DSP)"]
        NOTE["NoteCard & Navigation Views"]
        SUM["Summary & Task Board View"]
        DASH["AnalyticsDashboardWidget"]
        SEARCH["SemanticSearchWidget"]
    end

    subgraph Service_Layer ["2. Asynchronous Concurrency Layer"]
        PW["PipelineWorker (QThread)"]
        Signals["Qt Signals / Slots (Progress, Finished, Error)"]
    end

    subgraph Engine_Layer ["3. Core Processing & Intelligence Layer"]
        AE["AudioEngine (sounddevice, pyaudiowpatch)"]
        STT["STT Engine (Faster-Whisper / Groq LPU)"]
        TC["Multilingual Transcript Corrector (Code-Switching)"]
        DIA["Speaker Diarization Engine"]
        LLM["AIEngine (Google Gemini + Pydantic Schema)"]
        EXP["ExportEngine (ReportLab PDF / python-docx)"]
    end

    subgraph Storage_Tier ["4. Hybrid Storage & Persistence Tier"]
        PG[("PostgreSQL Database\n(ACID, Relational Tables, Tasks)")]
        CHROMA[("ChromaDB Vector Store\n(384-dim all-MiniLM-L6-v2 Embeddings)")]
        FS[("Local File System\n(data/recordings/*.wav)")]
    end

    UI_Layer <-->|Asynchronous Invocation| Service_Layer
    Service_Layer --> Engine_Layer
    Engine_Layer --> Storage_Tier
    Storage_Tier -->|Hydrated Data| UI_Layer
```

---

### 2. End-to-End Processing Pipeline (Audio to Insight)

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant UI as PySide6 UI
    participant Worker as Background Worker (QThread)
    participant Audio as Audio Engine
    participant STT as Whisper / Groq STT
    participant Corrector as Transcript Corrector
    participant Gemini as Gemini AI (LLM)
    participant DB as Dual DB (Postgres + Chroma)

    User->>UI: Click Record / Upload Audio
    UI->>Audio: Capture Stream (44.1kHz WAV)
    Audio-->>UI: Real-Time Waveform Float Samples
    User->>UI: Stop Recording
    UI->>Worker: Trigger PipelineWorker(audio_path)
    
    rect rgb(240, 248, 255)
        Note over Worker,STT: Step 1: Speech-to-Text
        Worker->>STT: Transcribe Audio Chunks
        STT-->>Worker: Raw Transcript Text + Detected Lang
    end

    rect rgb(255, 250, 240)
        Note over Worker,Corrector: Step 2: Linguistic Correction & Diarization
        Worker->>Corrector: Apply Grammar & Code-Switching Heuristics
        Corrector-->>Worker: Cleaned Multilingual Conversation
    end

    rect rgb(245, 255, 245)
        Note over Worker,Gemini: Step 3: Structured AI Extraction
        Worker->>Gemini: Prompt with Pydantic Schema
        Gemini-->>Worker: JSON (Summary, Tasks, Owners, Priorities, Dates)
    end

    rect rgb(255, 245, 245)
        Note over Worker,DB: Step 4: Hybrid Persistence
        Worker->>DB: Save Relational Records to PostgreSQL
        Worker->>DB: Vectorize & Index Chunks into ChromaDB
    end

    Worker-->>UI: Emit finished(note_data) Signal
    UI->>User: Display Interactive Summary & Action Items
```

---

### 3. Hybrid Dual-Database & Semantic Search RAG Flow

```mermaid
flowchart TD
    Query["User enters Natural Language Query\n('What was decided about the budget?')"] --> Embed["Embedding Generator\n(sentence-transformers: all-MiniLM-L6-v2)"]
    Embed -->|384-dimensional Query Vector| Cosine["ChromaDB Collection: voicenote_embeddings"]
    
    subgraph ChromaSearch ["Vector Space Search"]
        Cosine -->|Cosine Distance Nearest Neighbors| Ranks["Ranked Document Chunks\nwith Relevance Scores"]
    end
    
    Ranks -->|Extract Primary Keys| NoteIDs["Target Note IDs\n(e.g., Note #4, Note #12)"]
    
    subgraph PostgresHydration ["Relational Fetch"]
        NoteIDs -->|SELECT * FROM notes JOIN transcripts JOIN tasks| PG[(PostgreSQL)]
        PG -->|Full Relational Entities| Hydrated["Hydrated Note Objects\n(Audio Path, Full Transcript, Action Items)"]
    end

    Hydrated --> Render["PySide6 Search View\n(Audio Player + Highlighted Excerpts)"]
```

---

### 4. PostgreSQL Relational Database Schema (ER Diagram)

```mermaid
erDiagram
    NOTES ||--o{ TRANSCRIPTS : "1 to 1"
    NOTES ||--o{ AI_SUMMARIES : "1 to 1"
    NOTES ||--o{ TASKS : "1 to Many"

    NOTES {
        int id PK "SERIAL PRIMARY KEY"
        varchar title "Note title"
        varchar created_at "Timestamp"
        varchar duration "e.g. 05m 24s"
        text audio_path "Local WAV path"
        varchar category "General, Meeting, etc."
    }

    TRANSCRIPTS {
        int id PK "SERIAL PRIMARY KEY"
        int note_id FK "REFERENCES notes(id) ON DELETE CASCADE"
        text raw_text "Whisper output"
        text cleaned_text "Post-processed script"
        varchar language "e.g. en, mr, hi"
    }

    AI_SUMMARIES {
        int id PK "SERIAL PRIMARY KEY"
        int note_id FK "REFERENCES notes(id) ON DELETE CASCADE"
        text summary "Executive paragraph"
        text key_points "JSON array of bullets"
        varchar sentiment "Positive / Neutral / Negative"
        text main_topics "JSON array of topics"
    }

    TASKS {
        int id PK "SERIAL PRIMARY KEY"
        int note_id FK "REFERENCES notes(id) ON DELETE CASCADE"
        varchar title "Action item summary"
        text description "Detailed context"
        varchar priority "Urgent, High, Medium, Low"
        varchar assignee "Person responsible"
        varchar due_date "Target completion date"
        varchar status "Pending, Completed, Blocked"
    }
```

---

## Technology Stack Breakdown

| Layer | Primary Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **PySide6 (Qt 6 for Python)** | Native desktop UI, 60 FPS waveform visualization, responsive layouts |
| **Concurrency** | **Qt QThread, Signal & Slot** | Non-blocking background worker pipeline |
| **Audio DSP** | **sounddevice, soundfile, pyaudiowpatch, numpy** | Audio capture, loopback recording, and real-time amplitude normalization |
| **Speech-to-Text (STT)** | **faster-whisper (CTranslate2) & Groq** | Local offline transcription & high-speed cloud STT |
| **AI & NLP** | **Google Gemini (google-genai) + Pydantic v2** | Structured summarization, task extraction, and linguistic error correction |
| **Relational Database** | **PostgreSQL (psycopg2-binary)** | ACID-compliant structured metadata, transcripts, and relational task tracking |
| **Vector Database** | **ChromaDB + sentence-transformers (all-MiniLM-L6-v2)** | 384-dimensional dense vector embeddings for cosine semantic retrieval |
| **Document Export** | **ReportLab & python-docx** | Formatted export to PDF, Word DOCX, and plain text |

---

## Repository Structure

```text
VoiceNote/
├── doc/                        # Architectural specifications and SRS documentation
│   ├── architecture.md         # Detailed dual-database and storage architecture
│   ├── database-setup.md       # PostgreSQL schema setup instructions
│   └── srs.md                  # Software Requirements Specification
├── voicenote/                  # Core application package
│   ├── config.py               # Central configuration, paths, and environment settings
│   ├── core/                   # Algorithmic and processing engines
│   │   ├── ai_engine.py            # Gemini integration and Pydantic schema validation
│   │   ├── analytics_engine.py     # Aggregation and metric computations
│   │   ├── audio_engine.py         # Audio capture, recording, and playback
│   │   ├── diarization_engine.py   # Speaker separation and conversation structuring
│   │   ├── export_engine.py        # PDF and Word DOCX document generation
│   │   ├── groq_stt_engine.py      # Cloud Whisper on Groq LPU
│   │   ├── stt_engine.py           # Local faster-whisper engine
│   │   ├── text_cleaner.py         # Text whitespace and symbol normalization
│   │   ├── transcript_corrector.py # Multilingual regional grammar & code-switch correction
│   │   └── vector_engine.py        # ChromaDB indexing and cosine search
│   ├── db/                     # Database access layer
│   │   ├── database.py             # PostgreSQL connection and CRUD operations
│   │   └── models.py               # Data models for notes, transcripts, summaries, and tasks
│   ├── services/               # Background task orchestration
│   │   └── worker.py               # Asynchronous QThread pipeline worker
│   └── ui/                     # PySide6 desktop user interface
│       ├── components/             # Reusable widgets (Waveform, Taskboard, Search, Analytics)
│       ├── dialogs/                # Modals (Login, Settings, Profile, Export)
│       ├── main_window.py          # Main application window & navigation controller
│       └── styles.py               # Custom retro-cream stylesheet tokens
├── data/                       # Local recordings and generated artifacts
├── main.py                     # Application entry point with session management
├── requirements.txt            # Python dependencies
└── run_all_tests.py            # Automated test runner suite
```

---

## Getting Started

### 1. Prerequisites
- **Python 3.11+** installed
- **PostgreSQL 14+** running locally or remotely

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/Samar-365/VoiceNote.git
cd VoiceNote

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file from the example template:

```bash
cp .env.example .env
```

Update your `.env` with your API keys and database credentials:
```env
# Application Settings
APP_NAME=VoiceNote
VERSION=0.1.0

# Database Configuration (PostgreSQL 14+)
DB_ENGINE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=voicenote
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here

# AI & Cloud STT API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash

GROQ_API_KEY=your_groq_api_key_here
GROQ_STT_MODEL=whisper-large-v3
LOCAL_STT_MODEL=small
```

### 4. Run Automated Quality Gate
Verify that all 9 subsystems pass before launching:
```powershell
python run_all_tests.py
```

### 5. Launch Application
```powershell
python main.py
```

*Default Demo Credentials*:
* **Username**: `admin`
* **Password**: `admin123`

---

## 🧪 Automated Testing & Verification Gate

VoiceNote enforces a **9-module automated verification gate** in `run_all_tests.py` ensuring zero regressions across all core engines:

```powershell
============================================================
           VOICENOTE TEST SUITE (9 MODULES)
============================================================
[1/9] Testing PostgreSQL Database Connection & Models...   [PASS]
[2/9] Testing Text Cleaner Utility...                      [PASS]
[3/9] Testing Audio Engine WAV Serialization...            [PASS]
[4/9] Testing Gemini AI Engine & JSON Schemas...           [PASS]
[5/9] Testing ReportLab & DOCX Export Engine...            [PASS]
[6/9] Testing Analytics Engine Metric Computations...      [PASS]
[7/9] Testing ChromaDB Vector Engine & Cosine Queries...   [PASS]
[8/9] Testing User Authentication & SHA-256 Hashing...     [PASS]
[9/9] Testing PySide6 UI Component Initialization...       [PASS]
------------------------------------------------------------
Overall Result: 9/9 PASSED (100% Quality Verification)
============================================================
```

---

## 👥 Engineering Team & Module Ownership

| Team Member | Engineering Role | Core Subsystems & Architectural Contributions |
| :--- | :--- | :--- |
| **Tejas Rawool** (`@admin`) | **System Architect & Backend Lead** | PostgreSQL persistence layer, ChromaDB vector engine, multi-tier fallback Gemini LLM integration, live audio RMS/dBFS telemetry calibration, Marathi Devanagari `TranscriptCorrector`, cascading deletions, and unified 9-module test suite. |
| **Samar Shetye** | **UI/UX Lead & Presentation Architect** | PySide6 Bento Grid & Retro Warm Cream design system, `WaveformWidget`, `AudioRecorderWidget`, `TranscriptViewWidget`, `SummaryTaskWidget`, ReportLab PDF (with embedded Indic fonts), DOCX `ExportEngine`, and user authentication dialog. |
| **Atharv Pavar** | **AI & Machine Learning Lead** | Initial Faster-Whisper and Groq Cloud STT integration, prompt engineering for meeting intelligence, structured JSON schemas, Pydantic validation models, and Speaker Diarization turn segmentation engine. |

* **Project Guide**: **Prof. Omkar Dike**
* **Institution**: B.E. Information Technology • Open Source Project Lab (Semester VII)

---

## 📄 License & Intellectual Property

This project is licensed under the **MIT License**. All rights reserved. Built with open-source technologies for privacy-centric enterprise intelligence.
