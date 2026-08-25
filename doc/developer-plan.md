# VoiceNote Developer Plan

## 1. Project Objective

Build a professional Python desktop application for VoiceNote using PySide6, with a modern UI, modular architecture, and local AI-powered note capture, transcription, summarization, semantic search, and export workflows.

The project will be developed by three developers:

- Tejas
- Samar
- Atharv

## 2. Team Role Strategy

The team will work in parallel with clear ownership boundaries. Tejas will serve as the technical lead and integration owner, while Samar and Atharv will own major feature delivery streams.

### Workload Distribution

| Developer | Primary Role | Approx. Ownership |
| --- | --- | --- |
| Tejas | Architecture, core app orchestration, integrations, release readiness | 30-35% |
| Samar | UI/UX, audio engine & recording workflow, transcript experience, settings, export, analytics | 35-40% |
| Atharv | STT, AI summarization, task extraction, vector engine/search, data models | 30-35% |

This keeps Tejas focused on the critical backbone without taking all implementation work himself.

---

## 3. Developer Responsibilities

### Tejas — Core Architecture & Integration Lead

Tejas will own the foundation and integration layer of the product.

#### Responsibilities
- Define the overall application architecture and package structure
- Build the main application bootstrap and window shell
- Implement configuration, settings, and path management
- Own the application lifecycle and central event orchestration
- Handle authentication/login flow and user profile foundation
- Coordinate integration between UI, database, AI services, and storage layers
- Manage dependency setup, code structure consistency, and architecture reviews
- Lead release packaging, testing coordination, and stability fixes
- Resolve cross-module integration issues and code review feedback

#### Priority modules
- main.py
- config.py
- app bootstrap and session management
- login/profile foundation
- database service integration
- service orchestration layer
- packaging and installer readiness

### Samar — Front-End, UX, Audio Engine, Export & Analytics Lead

Samar will own the UI experience, audio capture engine, user-facing workflows, export generation, and analytics engine.

#### Responsibilities
- Implement hardware microphone audio capture engine (`core/audio_engine.py`) and recording file storage
- Design and implement the modern PySide6 desktop UI
- Build the main window, sidebar, top bar, and dashboard layout
- Design the recorder screen, waveform, and recording controls
- Build transcript editor, note layout, tag UI, and editing interactions
- Build analytics dashboard panels and settings dialogs
- Deliver polished UI styling using custom QSS and modern visual design
- Improve usability, motion, spacing, input states, and consistency
- Ensure screens support responsive desktop experience
- Build export engine for PDF/DOCX/TXT generation
- Implement analytics calculations and note metadata aggregation

#### Priority modules
- core/audio_engine.py
- ui/main_window.py
- ui/components/audio_recorder_widget.py
- ui/components/transcript_view_widget.py
- ui/components/analytics_dashboard_widget.py
- ui/dialogs/profile_dialog.py
- ui/dialogs/settings_dialog.py
- core/export_engine.py
- core/analytics_engine.py
- modern theme and QSS styling

### Atharv — AI, Vector Search, and STT Pipeline Lead

Atharv will own the STT pipeline, AI summarization, vector engine, semantic search backend, and data persistence workflows.

#### Responsibilities
- Build STT pipeline with faster-whisper and Groq STT integration
- Implement LLM summarization and task extraction workflows
- Build semantic search indexing, embeddings, and vector retrieval
- Manage ChromaDB and transcript chunk storage
- Support database models and persistence operations for AI-generated content

#### Priority modules
- core/stt_engine.py
- core/groq_stt_engine.py
- core/ai_engine.py
- core/vector_engine.py
- core/text_cleaner.py
- db/postgres_manager.py
- db/models.py
- db/chroma_manager.py

---

## 4. Delivery Phases

### Phase 1: Setup and Foundation

#### Tejas  
- project structure and dependency setup
- base config and logging
- app bootstrap and main window shell
- common architecture and conventions
- login/profile base implementation

#### Samar
- initial UI layout and theme design
- sidebar, header, and empty workspace shell
- basic styling and base components

#### Atharv
- database setup skeleton
- models and data layer scaffolding
- AI service connection testing

### Phase 2: Recording and Notes Workflow

#### Tejas
- core service orchestration for recording pipeline
- app event wiring between UI and services
- app status and service state handling

#### Samar
- microphone audio capture engine (`audio_engine.py`) and recording file storage
- recorder widget implementation
- transcript view and editing UI
- tag UI and note cards
- note dashboard screens

#### Atharv
- transcription pipeline and transcript storage
- note metadata handling and data persistence

### Phase 3: AI Intelligence and Search

#### Tejas
- service integration contracts between UI and AI modules
- data validation and processing flow management
- app-level error handling and state management

#### Samar
- AI summary panel UI
- task board layout
- semantic search results screen
- analytics dashboard components

#### Atharv
- summary generation and prompt engineering
- task extraction logic
- LLM response parsing and structured outputs
- vector indexing and search pipeline
- embeddings and retrieval integration

### Phase 4: Export, Analytics, and Quality

#### Tejas
- release configuration and architecture checks
- review quality gates and integration fixes
- testing coordination and troubleshooting

#### Samar
- export generation and validation (PDF/DOCX/TXT)
- analytics calculation and dashboard integration
- final polishing of UI details
- settings dialog improvements
- visual consistency review

#### Atharv
- database, vector search, and AI pipeline validation
- STT & AI engine output quality checks
- end-to-end testing of speech, summarization, and retrieval features

### Phase 5: Packaging and Release

#### Tejas
- final app packaging
- installer setup
- release configuration and deployment checks
- final integration verification

#### Samar
- final UI QA and polish pass
- export and analytics validation
- icon, spacing, and theme finalization

#### Atharv
- final backend QA and pipeline stress checks
- STT, vector search, and AI processing validation

---

## 5. Work Coordination Rules

1. Tejas is the final technical owner for architecture and integration.
2. Samar owns UI implementation quality, audio recording engine, workflow usability, export, and analytics.
3. Atharv owns AI pipeline quality, transcription/summarization functionality, and vector search/retrieval engine.
4. Tejas should review all cross-layer integration before merge.
5. Samar and Atharv should create feature branches and raise integration issues early.
6. Tejas does not need to do all development work; he should focus on architecture, core app logic, and module coordination.
7. All developers must maintain code modularity and clean interfaces.

---

## 6. Merge and Review Process

- Daily standup: 15-20 minutes
- Tejas reviews architecture and dependency contracts daily
- Samar reviews UI consistency, audio capture, export flows, and feature integration
- Atharv reviews STT, AI pipeline correctness, vector search retrieval, and output quality
- End-of-sprint review for functionality, bugs, and release readiness

---

## 7. Final Delivery Model

By the end of the project:

- Tejas will own the application backbone and core technical health
- Samar will deliver the modern user experience, audio recording engine, export engine, and analytics
- Atharv will deliver the STT, vector search engine, and AI intelligence pipeline

This distribution ensures a balanced and productive team model while keeping Tejas as the primary technical leader rather than the only implementer.

---

## 8. Recommended Execution Summary

- Tejas: architecture + login + integration + release leadership
- Samar: modern UI + audio engine & recorder + transcript + settings + export + analytics
- Atharv: STT + AI summarization + task extraction + vector engine

This is the best balance for a professional desktop product with parallel execution and strong technical ownership.

