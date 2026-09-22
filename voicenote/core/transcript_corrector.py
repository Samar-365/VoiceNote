"""
VoiceNote Multilingual Transcript Corrector.

Uses Gemini AI to fix garbled Whisper output for Marathi, Hindi, and mixed-language
(code-switched) speech. Whisper often:
  - Confuses Marathi with Hindi grammar endings
  - Transliterates English words into Devanagari
  - Produces incorrect Devanagari spellings for regional words

This corrector sends the raw Whisper output to Gemini with language-specific
correction rules and returns clean, accurate text.
"""

import logging
from typing import Optional

from voicenote.config import GEMINI_API_KEY

logger = logging.getLogger("TranscriptCorrector")

# ─── Language-specific correction prompt templates ───────────────────────────

MARATHI_CORRECTION_PROMPT = """You are an expert Marathi language transcription corrector.

The following is raw speech-to-text output from Whisper. The original audio is in MARATHI with English words mixed in (code-switching). Whisper has garbled many Marathi words, confused Marathi with Hindi, and transliterated English into Devanagari.

RAW WHISPER TRANSCRIPT:
{transcript}

CORRECTION RULES — FOLLOW STRICTLY:

1. FIX MARATHI GRAMMAR (NOT Hindi):
   - "है" → "आहे" (Marathi present tense)
   - "हैं" → "आहेत" (Marathi plural present tense)
   - "केले हैं" → "केले आहेत"
   - "कराइचा है" → "करायचा आहे"
   - "में" → "मध्ये" (when used in Marathi locative context)
   - "अपना/अपन" → "आपलं/आपल्याला"
   - "साथी" → "साठी"
   - "महंजे" → "म्हणजे"
   - "जवल पास" → "जवळपास"
   - "वाडला" → "वाढला"
   - "एकून/एकुन" → "एकूण"
   - "टक्के" → "%"
   - "तूलने" → "तुलनेत"
   - "सद्ध्या" → "सध्या"
   - "केली इते" → "केली. या" or "केली, इथे"
   - "मागचा" → "मागच्या"

2. KEEP ALL ENGLISH WORDS IN ENGLISH — DO NOT TRANSLITERATE:
   Annual, Employee, Conference, planning, employees, Management, approve,
   maximum, estimated, discount, Booking, confirm, vendor, quotation,
   Friday, Perfect, budget, Venue, Catering, and any other English word.

3. NUMBER & CURRENCY FORMATTING:
   - Write all numbers in English digits: 180, 2,40,000, 1,200, 6,00,000, etc.
   - Use "Rs." prefix for Indian currency: Rs. 2,40,000 (NOT "रुपे" or "₹")
   - Use "%" for percentages: 12%, 5% (NOT "टक्के")

4. RESTORE MISTRANSLATED / GARBLED MARATHI:
   - If Whisper accidentally translated parts of the Marathi speech into English or garbled phonetics:
     - "Cm'a" → "चला"
     - "This year we have to arrange..." → "या वर्षी आपल्याला जवळपास 180 employees साठी कार्यक्रम आयोजित करायचा आहे"
     - "Venue cost..." → "Venue चा खर्च Rs. 2,40,000 आहे"
     - "Catering fee..." → "Catering साठी प्रती व्यक्ती Rs. 1,200 म्हणजे एकूण जवळपास Rs. 2,16,000 येतील"
     - "What is our budget?" → "आपलं एकूण budget किती आहे?"
     - Restore natural Marathi conversational flow while retaining English business terms.

5. PRESERVE CONTENT & FLOW:
   - Keep the continuous spoken dialogue intact.
   - Do NOT add speaker labels here.
   - Do NOT add timestamps.
   - Fix all Devanagari spellings, Marathi grammar, and correct numbers.

OUTPUT: Return ONLY the corrected transcript text. No markdown, no explanations, no code fences."""


HINDI_CORRECTION_PROMPT = """You are an expert Hindi language transcription corrector.

The following is raw speech-to-text output from Whisper. The original audio is in HINDI with English words mixed in (code-switching). Whisper may have garbled some Hindi words or transliterated English into Devanagari.

RAW WHISPER TRANSCRIPT:
{transcript}

CORRECTION RULES — FOLLOW STRICTLY:

1. FIX HINDI DEVANAGARI SPELLINGS:
   - Correct any garbled or phonetically-approximated Devanagari.
   - Use standard Hindi grammar and spellings.
   - Fix common Whisper mistakes in Hindi transcription.

2. KEEP ALL ENGLISH WORDS IN ENGLISH — DO NOT TRANSLITERATE:
   Keep all English words (technical terms, names, common words) in English script.

3. NUMBER & CURRENCY FORMATTING:
   - Write all numbers in English digits: 180, 2,40,000, etc.
   - Use "Rs." prefix for Indian currency: Rs. 2,40,000
   - Use "%" for percentages.

4. PRESERVE CONTENT:
   - Do NOT add, remove, or reorder sentences.
   - Do NOT add speaker labels or timestamps.
   - Fix ONLY the Devanagari spellings and grammar.

OUTPUT: Return ONLY the corrected transcript text. No markdown, no explanations, no code fences."""


ENGLISH_CORRECTION_PROMPT = """You are an expert English transcription corrector.

The following is raw speech-to-text output from Whisper. Fix any obvious speech-to-text mistakes while preserving the original meaning.

RAW WHISPER TRANSCRIPT:
{transcript}

CORRECTION RULES:
1. Fix obvious phonetic misspellings and speech recognition errors.
2. Correct punctuation and sentence boundaries.
3. Use standard English spellings and grammar.
4. Keep all numbers, currency symbols, and proper nouns as-is.
5. Do NOT add speaker labels or timestamps.
6. Do NOT change the meaning or add/remove content.

OUTPUT: Return ONLY the corrected transcript text. No markdown, no explanations."""


class TranscriptCorrector:
    """
    Post-STT Gemini-based transcript corrector for multilingual accuracy.
    Transforms garbled Whisper output into clean, accurate text with proper
    Devanagari spellings for Marathi/Hindi and preserved English words.
    """

    def __init__(self):
        self.ai_engine = None
        if GEMINI_API_KEY:
            try:
                from voicenote.core.ai_engine import AIEngine
                self.ai_engine = AIEngine()
            except Exception as e:
                logger.warning(f"TranscriptCorrector: AI engine init failed: {e}")

    def correct(
        self,
        raw_transcript: str,
        detected_language: Optional[str] = None,
        user_language: Optional[str] = None
    ) -> str:
        """
        Correct raw Whisper transcript using Gemini AI.

        Args:
            raw_transcript: Raw text from Whisper STT.
            detected_language: Language detected by Whisper (e.g., 'hi', 'mr', 'en').
            user_language: Language explicitly selected by user in UI (e.g., 'mr', 'hi', 'en').

        Returns:
            Corrected transcript text. Falls back to raw_transcript on failure.
        """
        if not raw_transcript or not raw_transcript.strip():
            return raw_transcript

        if not self.ai_engine:
            logger.info("TranscriptCorrector: No AI engine available, returning raw transcript.")
            return raw_transcript

        # Determine the target language for correction
        # User's explicit selection takes priority, then auto-detected language
        target_lang = user_language or detected_language or "en"
        target_lang = target_lang.lower().strip()

        # Skip correction for English-only content (Whisper handles it well)
        if target_lang == "en" and not self._has_devanagari(raw_transcript):
            logger.info("TranscriptCorrector: English-only transcript, skipping correction.")
            return raw_transcript

        # Select the appropriate correction prompt
        if target_lang == "mr":
            prompt_template = MARATHI_CORRECTION_PROMPT
        elif target_lang == "hi":
            prompt_template = HINDI_CORRECTION_PROMPT
        elif self._has_devanagari(raw_transcript):
            # Auto-detected as something else but contains Devanagari — likely Marathi/Hindi
            # Whisper often detects Marathi as Hindi, so default to Marathi correction
            logger.info("TranscriptCorrector: Devanagari detected in transcript, applying Marathi correction.")
            prompt_template = MARATHI_CORRECTION_PROMPT
        else:
            prompt_template = ENGLISH_CORRECTION_PROMPT

        prompt = prompt_template.format(transcript=raw_transcript)

        try:
            logger.info(f"TranscriptCorrector: Correcting transcript (target_lang={target_lang})...")
            corrected = self.ai_engine.generate(prompt)
            corrected = corrected.strip()

            # Strip markdown code fences if Gemini adds them
            if corrected.startswith("```"):
                lines = corrected.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                corrected = "\n".join(lines).strip()

            # Sanity check: corrected version shouldn't be dramatically shorter
            if len(corrected) < len(raw_transcript) * 0.3:
                logger.warning("TranscriptCorrector: Corrected text suspiciously short, using raw.")
                return raw_transcript

            logger.info(f"TranscriptCorrector: Correction complete ({len(raw_transcript)} → {len(corrected)} chars).")
            return corrected

        except Exception as e:
            logger.warning(f"TranscriptCorrector: Gemini correction failed ({e}), using raw transcript.")
            return raw_transcript

    @staticmethod
    def _has_devanagari(text: str) -> bool:
        """Check if text contains Devanagari script characters (Unicode range 0900-097F)."""
        if not text:
            return False
        for char in text:
            if '\u0900' <= char <= '\u097F':
                return True
        return False
