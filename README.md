# VoiceNote: Intelligent Desktop Audio Intelligence & Semantic Retrieval System

VoiceNote is a privacy-first, offline-capable desktop application for recording audio, transcribing speech, repairing multilingual code-switched transcripts (e.g., Marathi/Hindi with English), extracting structured AI-generated insights, and enabling high-performance semantic search.

Developed by:
- **Tejas** — Architecture & Integration Lead
- **Samar** — UI/UX & System Integration Lead
- **Atharv** — AI Lead

---

## Document Index

- [Architecture Overview](doc/architecture.md)
- [Software Requirements Specification](doc/srs.md)
- [Implementation Plan](doc/implementation-plan.md)
- [Module Breakdown](doc/module-breakdown.md)
- [Database Setup Guide](doc/database-setup.md)

---

## Core Technology Stack

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

## System Architecture Diagrams

### 1. High-Level Layered System Architecture

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
        Cosine -->|K-Nearest Neighbor / Cosine Distance| Ranks["Ranked Document Chunks\nwith Distance Scores"]
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

