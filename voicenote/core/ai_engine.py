import json
import os
import logging
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

logger = logging.getLogger("AIEngine")
load_dotenv()


class Task(BaseModel):
    task: str
    owner: Optional[str] = None
    priority: Optional[str] = "Medium"  # Urgent, High, Medium, Low
    due_date: Optional[str] = None
    status: Optional[str] = "Not Started"  # Not Started, In Progress, Blocked, Completed
    notes: Optional[str] = None


class DeadlineItem(BaseModel):
    date: str
    commitment: str


class ImportantNumber(BaseModel):
    value: str
    context: str


class TranscriptAnalysis(BaseModel):
    language: str = "en"
    corrected_transcript: str = ""
    summary: str = ""
    key_points: List[str] = Field(default_factory=list)
    key_decisions: List[str] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    deadlines: List[DeadlineItem] = Field(default_factory=list)
    important_numbers: List[ImportantNumber] = Field(default_factory=list)
    risks_blockers: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    follow_ups: List[str] = Field(default_factory=list)


class AIEngine:
    """Interface between VoiceNote and AI Intelligence LLM backend."""

    def __init__(
        self,
        api_key=None,
        model="gemini-3.8-flash",
        temperature=0.3
    ):
        self.model = os.getenv("GEMINI_MODEL", model)
        self.temperature = temperature

        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str, max_retries: int = 3) -> str:
        """Send a prompt to Gemini and return the generated text with retry backoff."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        import time
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
                raise ValueError("AI returned an empty response.")
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                # If daily quota exhausted, skip retrying the same exhausted model and go to fallbacks
                if "quota exceeded" in err_str or "resource_exhausted" in err_str:
                    logger.info(f"Model {self.model} quota exhausted, switching to fallback models...")
                    break
                if attempt < max_retries - 1 and ("503" in err_str or "unavailable" in err_str or "429" in err_str or "timeout" in err_str):
                    sleep_time = (2 ** attempt) * 1.5
                    time.sleep(sleep_time)
                    continue

        # If primary model failed due to overload/503/quota, try fallback models gracefully
        fallback_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
        for fb_model in fallback_models:
            if fb_model != self.model:
                try:
                    logger.info(f"Retrying generation with fallback model {fb_model}...")
                    fb_response = self.client.models.generate_content(
                        model=fb_model,
                        contents=prompt,
                    )
                    if fb_response and fb_response.text:
                        return fb_response.text
                except Exception as fb_err:
                    logger.warning(f"Fallback model {fb_model} failed: {fb_err}")
                    continue

        if last_error:
            raise last_error
        raise RuntimeError("AI generation failed and no response was received.")

    def diarize_transcript(self, raw_transcript: str, language: Optional[str] = None) -> str:
        """
        Transform raw speech-to-text transcript into clean, 
        conversation-oriented dialogue format with consistent speaker labels
        (Speaker 1, Speaker 2, ...), merging consecutive speech blocks and
        removing all timestamps.
        
        For Marathi/Hindi content, includes language-specific correction rules
        to fix garbled Whisper output (wrong grammar endings, transliterated English, etc.).
        """
        if not raw_transcript or not raw_transcript.strip():
            return ""

        # Build language-specific correction instructions
        lang_code = (language or "").lower().strip()
        
        if lang_code == "mr" or (lang_code not in ("en", "hi") and self._has_devanagari(raw_transcript)):
            language_rules = """
MULTILINGUAL CORRECTION RULES (MARATHI + ENGLISH code-switching):
- The original audio is in MARATHI with English words mixed in (code-switching).
- RESTORE MISTRANSLATED SENTENCES: If the raw transcript translated spoken Marathi thoughts into English sentences (e.g. "Booking confirmed, here vendor will give Rs. 50,000 discount. Then I will prepare final quotation by tomorrow.", "Let's get final approval on Friday"), restore the sentence into natural spoken Marathi in Devanagari (e.g. "Booking confirm केली आहे, इथे vendor Rs. 50,000 discount देईल. मग मी उद्यापर्यंत final quotation तयार करेन.", "Perfect. आपण शुक्रवारी final approval घेऊया.").
- FIX Marathi grammar: "है" → "आहे", "हैं" → "आहेत", "साथी" → "साठी", "महंजे" → "म्हणजे", "जवल पास" → "जवळपास", "एकून" → "एकूण", "अपना" → "आपलं", "वाडला" → "वाढला", "तूलने" → "तुलनेत", "मागचा" → "मागच्या", "सद्ध्या" → "सध्या", "कराइचा" → "करायचा".
- KEEP isolated English business/technical loanwords in Latin script (e.g. Annual, Employee, Conference, planning, budget, vendor, discount, Management, approve, Booking, Venue, Catering, confirm, quotation, Friday, Perfect).
- Use "Rs." for Indian currency: Rs. 2,40,000 (NOT "रुपे" or "₹").
- Use "%" for percentages: 12% (NOT "टक्के").
- Write numbers in English digits: 180, 2,40,000, 1,200, 6,00,000.
"""
        elif lang_code == "hi":
            language_rules = """
MULTILINGUAL CORRECTION RULES (HINDI + ENGLISH code-switching):
- The original audio is HINDI with English words mixed in.
- Fix any garbled Hindi Devanagari spellings using standard Hindi grammar.
- KEEP all English words in ENGLISH script.
- Use "Rs." for Indian currency amounts.
- Use "%" for percentages.
- Write numbers in English digits.
"""
        else:
            language_rules = """
LANGUAGE NOTE: The transcript is primarily in English.
- Fix any phonetic misspellings from speech recognition.
- Correct punctuation and sentence structure.
"""

        prompt = f"""You are an expert audio dialogue and speaker diarization specialist for the VoiceNote desktop application.
Your task is to transform the following raw speech-to-text transcript into a clean, professional, conversation-oriented transcript with speaker labels.

INPUT TRANSCRIPT:
{raw_transcript}

{language_rules}

STRICT REQUIREMENTS:
1. SPEAKER SEPARATION & LABELS:
   - Identify distinct voices/speakers and assign them labels strictly in the format: "Speaker 1:", "Speaker 2:", "Speaker 3:", etc.
   - Do NOT use real names as the speaker label (e.g. use "Speaker 2:", never "Rahul:").
   - Maintain consistent identities throughout: if Speaker 1 speaks again later, keep labeling them as "Speaker 1:".
   - When a new speaker speaks, assign the next speaker number.

2. SEGMENT MERGING:
   - Merge all consecutive sentences spoken by the same speaker into one single paragraph/block.
   - Only start a new paragraph when the active speaker changes.
   - Do NOT split a single speaker's continuous thought into multiple small chunks.

3. ZERO TIMESTAMPS:
   - Absolutely DO NOT include timestamps (such as [00:00], [00:12], etc.) in the final transcript.

4. PRESERVE SHORT UTTERANCES:
   - Preserve short responses and acknowledgments ("Got it.", "Done.", "Okay.", "Perfect.").

5. ACCURACY:
   - Correct obvious speech-to-text phonetic slips using conversation context.

Return ONLY the formatted speaker dialogue. Do not include markdown code fences or conversational intros.
"""
        result = self.generate(prompt)
        clean_res = result.strip()
        if clean_res.startswith("```"):
            lines = clean_res.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_res = "\n".join(lines).strip()
        return clean_res

    @staticmethod
    def _has_devanagari(text: str) -> bool:
        """Check if text contains Devanagari script characters."""
        if not text:
            return False
        for char in text:
            if '\u0900' <= char <= '\u097F':
                return True
        return False

    @classmethod
    def _detect_script_and_language(cls, transcript: str, explicit_language: Optional[str] = None) -> str:
        """
        Detect whether the primary language is Marathi ('mr'), Hindi ('hi'), or English ('en').
        Checks explicit parameter, Devanagari presence, and Marathi vs Hindi vocabulary markers.
        """
        lang = (explicit_language or "").lower().strip()
        if lang in ("mr", "hi", "en"):
            return lang

        if not transcript or not cls._has_devanagari(transcript):
            return "en"

        # Unique Marathi linguistic cues
        marathi_markers = [
            "आहे", "आहेत", "करूया", "करा", "झाला", "झाली", "झाले", "साठी", "म्हणजे",
            "जवळपास", "वाढला", "खर्च", "एकूण", "कडून", "देईल", "करेन", "घेऊया", "आपलं",
            "आपल्याला", "करायचा", "सध्या", "तुलनेत", "मागच्या", "बैठक", "चर्चा"
        ]
        # Hindi linguistic cues
        hindi_markers = ["है", "हैं", "किया", "करेंगे", "होगा", "होगी", "होंगे", "के लिए", "मतलब", "लगभग", "बढ़ाया", "चाहिए"]

        mr_score = sum(1 for kw in marathi_markers if kw in transcript)
        hi_score = sum(1 for kw in hindi_markers if kw in transcript)

        if mr_score >= hi_score and mr_score > 0:
            return "mr"
        elif hi_score > mr_score:
            return "hi"

        return "mr"

    def _parse_json_response(self, raw_response: str) -> Dict[str, Any]:
        """Extract and parse a JSON object from an LLM response."""
        if not raw_response or not raw_response.strip():
            raise ValueError("AI returned an empty response.")

        start = raw_response.find("{")
        end = raw_response.rfind("}")

        if start == -1 or end == -1 or start >= end:
            raise ValueError("AI did not return a valid JSON object.")

        json_text = raw_response[start:end + 1]
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as error:
            raise ValueError("AI returned malformed JSON.") from error

    def analyze_transcript(self, transcript: str, language: Optional[str] = None) -> TranscriptAnalysis:
        """
        Analyze transcript into comprehensive AI Meeting Intelligence:
        Executive Summary, Key Decisions, Action Items, Deadlines & Commitments,
        Important Numbers, Risks & Blockers, Open Questions, and Follow-Ups.
        Ensures all output fields are strictly in the same language as the conversation.
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        target_lang = self._detect_script_and_language(transcript, language)

        if target_lang == "mr":
            lang_instruction = """
LANGUAGE REQUIREMENT — STRICT MARATHI (मराठी):
The conversation is in MARATHI (मराठी).
You MUST generate ALL output fields (summary, key_points, key_decisions, tasks descriptions, deadlines commitments, important_numbers contexts, risks_blockers, open_questions, follow_ups) STRICTLY IN MARATHI (मराठी) using Devanagari script.
DO NOT WRITE IN HINDI! Use proper Marathi grammar, verbs, and phrasing:
- 'आहे', 'आहेत', 'केले', 'ठरवले', 'चर्चा करण्यात आली', 'नियोजन करण्यात आले', 'निर्णय घेण्यात आला'.
- Keep standard technical/business loanwords in Latin script (e.g. Annual, Employee, Conference, budget, vendor, discount, quotation, Friday, Perfect).
"""
            detected_code = "mr"
        elif target_lang == "hi":
            lang_instruction = """
LANGUAGE REQUIREMENT — STRICT HINDI (हिंदी):
The conversation is in HINDI (हिंदी).
You MUST generate ALL output fields (summary, key_points, key_decisions, tasks, deadlines, numbers, risks, questions, follow-ups) STRICTLY IN HINDI (हिंदी) using Devanagari script.
- Keep standard technical/business loanwords in Latin script.
"""
            detected_code = "hi"
        else:
            lang_instruction = """
LANGUAGE REQUIREMENT — ENGLISH:
The conversation is in ENGLISH.
Generate all narrative output fields in clean, professional ENGLISH.
"""
            detected_code = "en"

        prompt = f"""
You are an expert AI Meeting Intelligence & Productivity Architect for the VoiceNote desktop application.
Analyze the following meeting/conversation transcript and extract structured, high-signal intelligence.

{lang_instruction}

TRANSCRIPT:
{transcript}

Return ONLY a valid JSON object with EXACTLY this structure:
{{
    "language": "{detected_code}",
    "corrected_transcript": "Transcript with obvious speech-to-text slips corrected in original language.",
    "summary": "Short concise executive summary in the requested language.",
    "key_points": [
        "Concise key takeaway point 1 in the requested language",
        "Concise key takeaway point 2 in the requested language"
    ],
    "key_decisions": [
        "Explicit decision 1 agreed upon during the meeting in the requested language",
        "Explicit decision 2"
    ],
    "tasks": [
        {{
            "task": "Actionable task description in the requested language",
            "owner": "Person name or null if unmentioned",
            "priority": "Urgent, High, Medium, or Low",
            "due_date": "Target date/day or null",
            "status": "Not Started",
            "notes": "Optional brief context note"
        }}
    ],
    "deadlines": [
        {{
            "date": "Extracted date or milestone (e.g. September 29, शुक्रवार)",
            "commitment": "What is due or committed on that date in the requested language"
        }}
    ],
    "important_numbers": [
        {{
            "value": "Formatted figure (e.g. Rs. 2,40,000, 12%, Rs. 6,00,000)",
            "context": "Brief context for what this number represents in the requested language"
        }}
    ],
    "risks_blockers": [
        "Statements indicating delays, cost overruns, dependencies, or blockers in the requested language"
    ],
    "open_questions": [
        "Questions asked during the conversation that remained unanswered in the requested language"
    ],
    "follow_ups": [
        "Suggested next steps strictly grounded in the conversation in the requested language"
    ]
}}

STRICT RULES:
1. OUTPUT LANGUAGE: Every text field (summary, key_points, key_decisions, tasks, deadlines, important_numbers contexts, risks, questions, follow_ups) MUST be in the requested language ({target_lang}). Never substitute Marathi with Hindi.
2. Ground everything strictly in the transcript. Do NOT invent facts, numbers, or deadlines.
3. If no decisions were made, key_decisions should be an empty list [].
4. For important_numbers, detect monetary figures (Rs., ₹, $, etc.), percentages, participant counts, budgets, and metrics.
5. For risks_blockers, extract statements showing dependencies, approaching deadlines, or cost increases.
6. For open_questions, extract genuine unanswered questions.
7. Return JSON ONLY with no outer markdown fences.
"""
        raw_response = self.generate(prompt)
        data = self._parse_json_response(raw_response)
        return TranscriptAnalysis.model_validate(data)

    def regenerate_summary(self, transcript: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Regenerate only Executive Summary and Key Points in the same language as the transcript."""
        target_lang = self._detect_script_and_language(transcript, language)
        lang_note = "Generate strictly in MARATHI (मराठी) - DO NOT use Hindi." if target_lang == "mr" else (
            "Generate strictly in HINDI (हिंदी)." if target_lang == "hi" else "Generate in ENGLISH."
        )

        prompt = f"""
Provide a fresh, high-impact Executive Summary and Key Takeaways for this transcript:
{transcript}

LANGUAGE REQUIREMENT: {lang_note}

Return valid JSON ONLY:
{{
    "summary": "Concise executive summary in the requested language.",
    "key_points": ["Point 1 in requested language", "Point 2", "Point 3"]
}}
"""
        raw = self.generate(prompt)
        return self._parse_json_response(raw)

    def regenerate_tasks(self, transcript: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Regenerate only Action Items and Tasks in the same language as the transcript."""
        target_lang = self._detect_script_and_language(transcript, language)
        lang_note = "Generate descriptions strictly in MARATHI (मराठी) - DO NOT use Hindi." if target_lang == "mr" else (
            "Generate descriptions strictly in HINDI (हिंदी)." if target_lang == "hi" else "Generate descriptions in ENGLISH."
        )

        prompt = f"""
Extract all genuine actionable tasks from this transcript:
{transcript}

LANGUAGE REQUIREMENT: {lang_note}

Return valid JSON ONLY:
{{
    "tasks": [
        {{
            "task": "Clear action description in requested language",
            "owner": "Person name or null",
            "priority": "Urgent, High, Medium, or Low",
            "due_date": "Date/day or null",
            "status": "Not Started"
        }}
    ]
}}
"""
        raw = self.generate(prompt)
        data = self._parse_json_response(raw)
        return data.get("tasks", [])

    def regenerate_insights(self, transcript: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Regenerate Decisions, Deadlines, Numbers, Risks, Questions, and Follow-Ups in the same language as the transcript."""
        target_lang = self._detect_script_and_language(transcript, language)
        lang_note = "Generate all text fields strictly in MARATHI (मराठी) - DO NOT use Hindi." if target_lang == "mr" else (
            "Generate all text fields strictly in HINDI (हिंदी)." if target_lang == "hi" else "Generate in ENGLISH."
        )

        prompt = f"""
Extract meeting insights (decisions, deadlines, numbers, risks, open questions, follow-ups) from this transcript:
{transcript}

LANGUAGE REQUIREMENT: {lang_note}

Return valid JSON ONLY:
{{
    "key_decisions": ["Decision 1 in requested language"],
    "deadlines": [{{"date": "Sep 29 / शुक्रवार", "commitment": "Release freeze / वचनबद्धता"}}],
    "important_numbers": [{{"value": "Rs. 2,40,000", "context": "खर्च / Cloud cost"}}],
    "risks_blockers": ["Approaching deadline / संभाव्य अडचण"],
    "open_questions": ["What is the infrastructure plan? / अनुत्तरित प्रश्न?"],
    "follow_ups": ["Validate model results / पुढील पायरी"]
}}
"""
        raw = self.generate(prompt)
        return self._parse_json_response(raw)