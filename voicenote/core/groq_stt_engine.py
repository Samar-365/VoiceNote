"""
VoiceNote Groq Cloud STT Engine.

Uses Groq's hosted Whisper API for fast cloud-based speech-to-text.
Supports language-specific Devanagari initial prompts to improve
Marathi and Hindi transcription quality.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    from groq import Groq
    GROQ_PKG_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_PKG_AVAILABLE = False

from voicenote.config import GROQ_API_KEY, GROQ_STT_MODEL

logger = logging.getLogger("GroqSTTEngine")

# ─── Language-specific initial prompts ───────────────────────────────────────
# These Devanagari prompts guide Whisper to output the correct script.
# Without them, Whisper often outputs Latin transliterations for Indian languages.

GROQ_PROMPTS = {
    "mr": (
        "हा एक मराठी संवाद आहे. सर्व वाक्ये मराठी देवनागरी लिपीत लिहा, इंग्रजीत भाषांतर करू नका. "
        "चला, आजच्या बैठकीत आपण वार्षिक कर्मचारी परिषदेचे नियोजन करूया. "
        "बजेट Rs. 2,40,000 आहे. Venue, Catering, vendor, planning, budget, "
        "employees, Management, discount, approval, booking, quotation, Friday, Perfect. "
        "म्हणजे, जवळपास, आहे, आहेत, साठी, करायचा, एकूण, वाढला, देईल, करेन, घेऊया."
    ),
    "hi": (
        "नमस्ते, आज की बैठक में हम कार्य योजना, बजट और चर्चा करेंगे। "
        "Budget Rs. 2,40,000 है। Venue, Catering, vendor, planning, employees, "
        "Management, discount, approval।"
    ),
    "en": (
        "Meeting discussion with multiple speakers. Complete sentences, numbers, "
        "currency notation like Rs. and lakhs, and short acknowledgments like "
        "Got it, Done, Okay, Perfect."
    ),
}

DEFAULT_PROMPT = GROQ_PROMPTS["en"]


class GroqSTTEngine:
    """
    Cloud-based STT engine using Groq's Whisper API.
    Sends language-appropriate Devanagari prompts for Marathi/Hindi.
    """

    def __init__(self, model: str = GROQ_STT_MODEL):
        if not GROQ_PKG_AVAILABLE or Groq is None:
            raise ImportError(
                "The 'groq' package is not installed. Use local Faster-Whisper instead."
            )
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured. "
                "Add it to the .env file."
            )

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file using Groq Whisper API.

        Args:
            audio_path: Path to the audio file.
            language: Target language code ('mr', 'hi', 'en') or None for auto-detect.
            prompt: Custom initial prompt. If None, uses language-specific default.

        Returns:
            Dict with 'language', 'segments', and 'text' keys.
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if not audio_path.is_file():
            raise ValueError(f"Audio path is not a file: {audio_path}")

        # Select language-appropriate prompt
        if prompt:
            meeting_prompt = prompt
        elif language and language.lower() in GROQ_PROMPTS:
            meeting_prompt = GROQ_PROMPTS[language.lower()]
            logger.info(f"Using {language.upper()} Devanagari prompt for Groq Whisper.")
        else:
            meeting_prompt = DEFAULT_PROMPT

        # For Marathi/Hindi, do NOT pass language parameter to let Whisper auto-detect.
        # Passing language='mr' often produces truncated output. Auto-detect + prompt is better.
        whisper_language = None
        if language and language.lower() == "en":
            whisper_language = "en"
        # For 'mr'/'hi', we rely on the Devanagari prompt instead of the language parameter
        # because Whisper's Marathi support is weak and often truncates output.

        logger.info(
            f"Groq Whisper transcribing: {audio_path.name} "
            f"(language_param={whisper_language}, prompt_lang={language or 'auto'})"
        )

        with open(audio_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                language=whisper_language,
                prompt=meeting_prompt,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
                temperature=0.0
            )

        segments = []
        for segment in transcription.segments:
            if isinstance(segment, dict):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
            else:
                start = segment.start
                end = segment.end
                text = segment.text

            segments.append({
                "start": start,
                "end": end,
                "text": text.strip()
            })

        detected_lang = getattr(transcription, "language", None) or language
        logger.info(f"Groq Whisper detected language: {detected_lang}")

        return {
            "language": detected_lang,
            "segments": segments,
            "text": transcription.text
        }