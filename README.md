# VoiceNote Documentation

This folder contains the formal project documentation for the VoiceNote Desktop application.

## Document Index

- [Architecture Overview](architecture.md)
- [Software Requirements Specification](srs.md)
- [Implementation Plan](implementation-plan.md)
- [Module Breakdown](module-breakdown.md)

## Product Summary

VoiceNote is a privacy-first, offline desktop application for recording audio, transcribing speech, extracting AI-generated insights, and creating searchable note artifacts. It runs locally on Windows and packages as a standalone .exe for end-user installation.

## Core Technology Stack

- Python 3.11+
- PySide6 (Qt for desktop UI)
- PostgreSQL for relational data
- ChromaDB for semantic search
- faster-whisper for speech-to-text
- Ollama with Llama/Gemma for AI summarization and task extraction
- PyInstaller for packaging
- Inno Setup for Windows installation
