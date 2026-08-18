from PySide6.QtCore import QThread, Signal
from pathlib import Path
from typing import Optional, Dict, Any

from voicenote.core.ai_engine import AIEngine
from voicenote.core.stt_engine import STTEngine
from voicenote.core.groq_stt_engine import GroqSTTEngine
from voicenote.config import GROQ_API_KEY, GEMINI_API_KEY
from voicenote.db.database import get_db
from voicenote.db.models import Note, Transcript, AISummary, Task


class PipelineWorker(QThread):
    """
    Background worker thread to run Speech-to-Text and Gemini AI analysis 
    without blocking the PySide6 UI.
    """
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, audio_path: Optional[str] = None, raw_transcript: Optional[str] = None, title: str = "Voice Note"):
        super().__init__()
        self.audio_path = audio_path
        self.raw_transcript = raw_transcript
        self.title = title

    def run(self):
        try:
            db = get_db()
            detected_lang = "en"
            full_transcript_text = ""

            # Step 1: STT Transcription
            if self.audio_path and Path(self.audio_path).exists():
                self.progress.emit("Transcribing audio recording...")
                
                # Use Groq if API key available, otherwise fallback to local Faster-Whisper
                if GROQ_API_KEY:
                    try:
                        stt = GroqSTTEngine()
                        res = stt.transcribe(self.audio_path)
                        full_transcript_text = res.get("text", "")
                    except Exception as e:
                        self.progress.emit(f"Groq STT fallback to local Whisper: {str(e)}")
                        stt = STTEngine()
                        res = stt.transcribe(self.audio_path)
                        detected_lang = res.get("language", "en")
                        segments = res.get("segments", [])
                        full_transcript_text = " ".join([s.get("text", "") for s in segments])
                else:
                    stt = STTEngine()
                    res = stt.transcribe(self.audio_path)
                    detected_lang = res.get("language", "en")
                    segments = res.get("segments", [])
                    full_transcript_text = " ".join([s.get("text", "") for s in segments])

            elif self.raw_transcript:
                full_transcript_text = self.raw_transcript
            else:
                raise ValueError("Neither audio file nor transcript text was provided.")

            if not full_transcript_text.strip():
                raise ValueError("Transcription produced no speech text.")

            # Save Initial Note & Raw Transcript
            note_obj = Note(
                title=self.title,
                duration="02m 15s",
                audio_path=self.audio_path,
                category="General"
            )
            note_id = db.add_note(note_obj)

            transcript_obj = Transcript(
                note_id=note_id,
                raw_text=full_transcript_text,
                cleaned_text=full_transcript_text,
                language=detected_lang
            )
            db.save_transcript(transcript_obj)

            # Step 2: Gemini AI Analysis
            self.progress.emit("Analyzing transcript with Gemini AI...")
            ai_data = None
            if GEMINI_API_KEY:
                try:
                    ai_engine = AIEngine()
                    analysis_res = ai_engine.analyze_transcript(full_transcript_text, language=detected_lang)
                    
                    summary_obj = AISummary(
                        note_id=note_id,
                        summary=analysis_res.summary,
                        key_points=analysis_res.key_points,
                        sentiment="Positive",
                        main_topics=[analysis_res.language.upper()]
                    )
                    db.save_ai_summary(summary_obj)

                    for t in analysis_res.tasks:
                        task_obj = Task(
                            note_id=note_id,
                            title=t.task,
                            assignee=t.owner or "Unassigned",
                            priority=t.priority or "Medium",
                            due_date=t.due_date or "TBD",
                            status="Pending"
                        )
                        db.save_task(task_obj)

                    ai_data = {
                        "summary": analysis_res.summary,
                        "key_points": analysis_res.key_points,
                        "tasks": [t.model_dump() for t in analysis_res.tasks]
                    }

                except Exception as ai_err:
                    self.progress.emit(f"AI Analysis Notice: {str(ai_err)}")
                    # Save basic summary fallback
                    summary_obj = AISummary(
                        note_id=note_id,
                        summary=full_transcript_text[:200] + "...",
                        key_points=["Audio captured successfully", "Pending detailed LLM analysis"],
                        sentiment="Neutral",
                        main_topics=["Speech Capture"]
                    )
                    db.save_ai_summary(summary_obj)
            else:
                summary_obj = AISummary(
                    note_id=note_id,
                    summary=full_transcript_text[:200] + "...",
                    key_points=["Recorded note saved"],
                    sentiment="Neutral",
                    main_topics=["Offline Note"]
                )
                db.save_ai_summary(summary_obj)

            self.finished.emit({
                "note_id": note_id,
                "title": self.title,
                "transcript": full_transcript_text,
                "ai_data": ai_data
            })

        except Exception as e:
            self.error.emit(str(e))


class AIEngineWorker(QThread):
    """Worker to perform direct LLM prompts in background."""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            engine = AIEngine()
            res = engine.generate(self.prompt)
            self.finished.emit(res)
        except Exception as e:
            self.error.emit(str(e))
