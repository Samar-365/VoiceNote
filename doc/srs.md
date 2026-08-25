# VoiceNote Desktop Software Requirements Specification

## 1. Introduction

VoiceNote is an AI-powered Windows desktop application that records audio, transcribes speech, generates structured summaries, extracts tasks, and enables semantic search across recorded notes.

The system is designed for users who want a local, secure, and intelligent note-taking workflow without relying on cloud processing.

## 2. Objectives

The core objectives of the system are to:

- record voice notes from a microphone or local audio file
- convert spoken content into accurate text using speech recognition
- generate AI summaries from transcript content
- identify and structure actionable tasks from notes
- enable search across historical note content using semantic retrieval
- export final notes into usable document formats

## 3. Functional Requirements

### FR1: User Profile and Preferences
The system shall support a user profile configuration, including preferred AI model settings and application preferences.

### FR2: Audio Recording and Upload
The system shall allow users to:

- record audio from the microphone
- pause and resume a recording session
- stop and finalize a recording
- upload local audio files in common formats such as WAV, MP3, M4A, and MP4

### FR3: Whisper Transcription
The system shall transcribe audio into text using a local speech-to-text engine and provide timestamped transcript output.

### FR4: AI Summarization
The system shall generate a concise summary of each note, including key themes, decisions, and notable points.

### FR5: Task Extraction
The system shall parse transcript content and extract task items, including descriptions, ownership, status, and priority where reasonable.

### FR6: Tagging
The system shall allow users to create and assign tags to notes and transcript content for categorization and organization.

### FR7: Semantic Search
The system shall index notes and transcripts for semantic retrieval and allow end users to search by natural language queries.

### FR8: Export PDF/DOCX/TXT
The system shall allow users to export notes in the following formats:

- PDF
- DOCX
- TXT

### FR9: Analytics Dashboard
The system shall provide metrics such as recording duration, word count trends, task completion rates, and usage summaries.

## 4. Non-Functional Requirements

### NFR1: Responsive Desktop UI
The user interface shall remain responsive even during processing-heavy operations such as transcription, AI summarization, and semantic indexing.

### NFR2: Offline Operation
The system shall primarily function without internet access, using local AI and local storage solutions.

### NFR3: Secure Local Storage
User data shall be stored locally in a secured application data directory with structured persistence and controlled access.

### NFR4: Fast Transcription
The system shall support efficient speech-to-text processing using local models and hardware acceleration when available.

### NFR5: Scalable Modular Architecture
The system shall be structured into modular services to support future enhancements without major design rework.

## 5. System Architecture Summary

The system architecture includes:

- PySide6 for the desktop UI
- Python as the application language
- PostgreSQL for relational data management
- ChromaDB for vector search and embedding storage
- Gemini AI API for cloud AI inference and summarization
- faster-whisper and Groq for transcription
- PyInstaller and Inno Setup for distribution packaging

## 6. Technology Stack

- PySide6
- Python
- PostgreSQL
- SQLAlchemy and psycopg
- ChromaDB
- faster-whisper / Groq STT
- Gemini AI API
- PyInstaller
- Inno Setup
- Git/GitHub

## 7. Assumptions and Constraints

- The application targets Windows desktop deployment.
- The user environment may include local dependencies such as PostgreSQL.
- Some features depend on machine capabilities such as CPU or GPU acceleration.
- The system is optimized for local, privacy-preserving operation rather than cloud-based services.

## 8. Future Scope

The product roadmap may include:

- cloud synchronization
- mobile applications
- plugin ecosystems
- collaborative features
- multilingual transcription support

## 9. Acceptance Criteria

The product will be considered successful when the user can:

1. record or import audio,
2. produce transcripts,
3. review AI-generated summaries,
4. manage extracted tasks,
5. search note content semantically,
6. export final notes in preferred formats,
7. use the application as a standalone local desktop workflow.

## 10. Summary

VoiceNote addresses the need for a secure, local, AI-assisted note-taking system that combines voice capture, transcribed text, intelligent summaries, actionable tasks, and semantic retrieval in a professional desktop environment.
