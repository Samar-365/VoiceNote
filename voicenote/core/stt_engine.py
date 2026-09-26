"""
VoiceNote Speech-to-Text Engine powered by Faster-Whisper.
Supports Multilingual Speech Recognition with high-accuracy Marathi, Hindi, and English transcription.
Ensures Marathi audio produces correct Unicode Devanagari text instead of Latin transliteration.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from faster_whisper import WhisperModel

logger = logging.getLogger("STTEngine")

MARATHI_PROMPT = (
    "हा एक मराठी संवाद आहे. सर्व वाक्ये मराठी देवनागरी लिपीत लिहा, इंग्रजीत भाषांतर करू नका. "
    "चला, आजच्या बैठकीत आपण नियोजन, कर्मचारी, बजेट, vendor, discount, booking, quotation, approval यावर चर्चा करूया."
)
HINDI_PROMPT = "नमस्ते, आज की बैठक में हम कार्य योजना, बजट और चर्चा करेंगे।"
ENGLISH_PROMPT = (
    "Meeting discussion with multiple speakers. Complete sentences, numbers, "
    "currency notation like ₹ and lakhs, and short acknowledgments like Got it, Done, Okay."
)


class STTEngine:
    def __init__(self, model_size: str = "small"):
        # Ensure we always use multilingual models, stripping any legacy .en suffixes
        clean_model = model_size.lower().replace(".en", "").strip()
        if clean_model not in ("tiny", "base", "small", "medium", "large-v2", "large-v3"):
            clean_model = "small"

        logger.info(f"Initializing multilingual Faster-Whisper engine with model '{clean_model}' on CPU (int8)...")
        self.model = WhisperModel(
            clean_model,
            device="cpu",
            compute_type="int8"
        )
        self.model_size = clean_model

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text with language detection and Devanagari prompting.
        Parameters:
        - audio_path: Path to audio file.
        - language: 'auto', 'mr' (Marathi), 'hi' (Hindi), 'en' (English), or None.
        - initial_prompt: Optional custom prompt.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if not audio_path.is_file():
            raise ValueError(f"Audio path is not a file: {audio_path}")

        # Normalize language parameter
        lang_code = None
        if language and language.lower() not in ("auto", "none", ""):
            lang_code = language.lower().strip()

        # Determine prompt based on target language
        if initial_prompt:
            prompt = initial_prompt
        elif lang_code == "mr":
            prompt = MARATHI_PROMPT
        elif lang_code == "hi":
            prompt = HINDI_PROMPT
        elif lang_code == "en":
            prompt = ENGLISH_PROMPT
        else:
            prompt = None  # Neutral start for auto-detection

        vad_params = dict(
            threshold=0.35,
            min_speech_duration_ms=80,
            max_speech_duration_s=float("inf"),
            min_silence_duration_ms=400,
            speech_pad_ms=300
        )

        # Initial transcription call
        segments_gen, info = self.model.transcribe(
            str(audio_path),
            language=lang_code,
            vad_filter=True,
            vad_parameters=vad_params,
            initial_prompt=prompt,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            repetition_penalty=1.2,
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6,
            condition_on_previous_text=False
        )

        detected_lang = info.language
        prob = info.language_probability
        logger.info(f"STT language detected: '{detected_lang}' (probability: {prob:.2f})")

        # If language was auto-detected as Marathi or Hindi and no specific prompt was given,
        # re-transcribe with the native Devanagari prompt to guarantee correct Devanagari script
        if lang_code is None:
            if detected_lang == "mr":
                logger.info("Auto-detected Marathi: applying native Devanagari prompt...")
                segments_gen, info = self.model.transcribe(
                    str(audio_path),
                    language="mr",
                    vad_filter=True,
                    vad_parameters=vad_params,
                    initial_prompt=MARATHI_PROMPT,
                    beam_size=5,
                    best_of=5,
                    temperature=0.0,
                    repetition_penalty=1.2,
                    compression_ratio_threshold=2.4,
                    no_speech_threshold=0.6,
                    condition_on_previous_text=False
                )
            elif detected_lang == "hi":
                logger.info("Auto-detected Hindi: applying native Devanagari prompt...")
                segments_gen, info = self.model.transcribe(
                    str(audio_path),
                    language="hi",
                    vad_filter=True,
                    vad_parameters=vad_params,
                    initial_prompt=HINDI_PROMPT,
                    beam_size=5,
                    best_of=5,
                    temperature=0.0,
                    repetition_penalty=1.2,
                    compression_ratio_threshold=2.4,
                    no_speech_threshold=0.6,
                    condition_on_previous_text=False
                )

        transcript: List[Dict[str, Any]] = []
        for segment in segments_gen:
            text = segment.text.strip()
            if text:
                transcript.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": text
                })

        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": transcript
        }
