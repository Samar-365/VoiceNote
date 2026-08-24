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
                self.progress.emit("Transcribing audio recording with Speech-to-Text...")
                
                # Calculate actual audio duration
                try:
                    import wave
                    with wave.open(str(self.audio_path), 'rb') as wf:
                        frames = wf.getnframes()
                        rate = wf.getframerate()
                        duration_sec = int(frames / float(rate))
                        mins, secs = divmod(duration_sec, 60)
                        duration_str = f"{mins:02d}m {secs:02d}s"
                except Exception:
                    duration_str = "00:30"

                # Use Groq if API key available, otherwise fallback to local Faster-Whisper
                segments = []
                if GROQ_API_KEY:
                    try:
                        stt = GroqSTTEngine()
                        res = stt.transcribe(self.audio_path)
                        full_transcript_text = res.get("text", "").strip()
                        detected_lang = res.get("language") or "en"
                        segments = res.get("segments", [])
                    except Exception as e:
                        self.progress.emit(f"Groq STT fallback to local Whisper: {str(e)}")
                        stt = STTEngine()
                        res = stt.transcribe(self.audio_path)
                        detected_lang = res.get("language") or "en"
                        segments = res.get("segments", [])
                        full_transcript_text = " ".join([s.get("text", "") for s in segments]).strip()
                else:
                    stt = STTEngine()
                    res = stt.transcribe(self.audio_path)
                    detected_lang = res.get("language") or "en"
                    segments = res.get("segments", [])
                    full_transcript_text = " ".join([s.get("text", "") for s in segments]).strip()

                # Build timestamped transcript if segments exist
                if segments:
                    formatted_lines = []
                    for s in segments:
                        txt = s.get("text", "").strip()
                        if txt:
                            start_sec = s.get("start", 0.0)
                            m, sec = divmod(int(start_sec), 60)
                            formatted_lines.append(f"[{m:02d}:{sec:02d}] {txt}")
                    if formatted_lines:
                        formatted_transcript = "\n".join(formatted_lines)
                    else:
                        formatted_transcript = full_transcript_text
                else:
                    formatted_transcript = full_transcript_text

            elif self.raw_transcript:
                full_transcript_text = self.raw_transcript.strip()
                formatted_transcript = full_transcript_text
                duration_str = "00:15"
            else:
                raise ValueError("Neither audio file nor transcript text was provided.")

            if not full_transcript_text.strip():
                raise ValueError("Transcription produced no speech text. Please verify microphone input.")

            # Save Initial Note & Raw Transcript
            note_obj = Note(
                title=self.title,
                duration=duration_str,
                audio_path=self.audio_path,
                category=detected_lang.upper() if detected_lang else "General"
            )
            note_id = db.add_note(note_obj)

            transcript_obj = Transcript(
                note_id=note_id,
                raw_text=full_transcript_text,
                cleaned_text=formatted_transcript,
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
                    
                    summary_text = analysis_res.summary
                    key_points = analysis_res.key_points
                    tasks_list = analysis_res.tasks
                    
                    summary_obj = AISummary(
                        note_id=note_id,
                        summary=summary_text,
                        key_points=key_points,
                        sentiment="Positive",
                        main_topics=[f"#{analysis_res.language.upper()}", "#VoiceNote"]
                    )
                    db.save_ai_summary(summary_obj)

                    for t in tasks_list:
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
                        "summary": summary_text,
                        "key_points": key_points,
                        "tasks": [t.model_dump() for t in tasks_list],
                        "tags": [f"#{analysis_res.language.upper()}", "#VoiceNote"]
                    }

                except Exception as ai_err:
                    self.progress.emit(f"AI Analysis Notice: {str(ai_err)}")
                    # Save basic summary fallback
                    summary_obj = AISummary(
                        note_id=note_id,
                        summary=full_transcript_text[:200] + ("..." if len(full_transcript_text) > 200 else ""),
                        key_points=["Audio captured & transcribed successfully"],
                        sentiment="Neutral",
                        main_topics=["#VoiceNote"]
                    )
                    db.save_ai_summary(summary_obj)
                    ai_data = {
                        "summary": summary_obj.summary,
                        "key_points": summary_obj.key_points,
                        "tasks": [],
                        "tags": ["#VoiceNote"]
                    }
            else:
                summary_obj = AISummary(
                    note_id=note_id,
                    summary=full_transcript_text[:200] + ("..." if len(full_transcript_text) > 200 else ""),
                    key_points=["Recorded note saved locally"],
                    sentiment="Neutral",
                    main_topics=["#OfflineNote"]
                )
                db.save_ai_summary(summary_obj)
                ai_data = {
                    "summary": summary_obj.summary,
                    "key_points": summary_obj.key_points,
                    "tasks": [],
                    "tags": ["#OfflineNote"]
                }

            self.finished.emit({
                "note_id": note_id,
                "title": self.title,
                "duration": duration_str,
                "transcript": formatted_transcript,
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
