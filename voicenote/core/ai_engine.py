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
- The original audio is MARATHI with English words mixed in.
- FIX Marathi grammar: "है" → "आहे", "हैं" → "आहेत", "साथी" → "साठी", "महंजे" → "म्हणजे", "जवल पास" → "जवळपास", "एकून" → "एकूण", "अपना" → "आपलं", "वाडला" → "वाढला", "तूलने" → "तुलनेत", "मागचा" → "मागच्या", "सद्ध्या" → "सध्या", "कराइचा" → "करायचा".
- KEEP all English words in ENGLISH script: Annual, Employee, Conference, planning, budget, vendor, discount, Management, approve, Booking, Venue, Catering, confirm, quotation, Friday, Perfect, etc.
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
        """
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        language_hint = language if language else "unknown"

        prompt = f"""
You are an expert AI Meeting Intelligence & Productivity Architect for the VoiceNote desktop application.
Analyze the following meeting/conversation transcript and extract structured, high-signal intelligence.

EXPECTED LANGUAGE:
{language_hint}

TRANSCRIPT:
{transcript}

Return ONLY a valid JSON object with EXACTLY this structure:
{{
    "language": "Detected language code (e.g. en)",
    "corrected_transcript": "Transcript with obvious speech-to-text slips corrected in original language.",
    "summary": "Short concise executive summary of the entire conversation.",
    "key_points": [
        "Concise key takeaway point 1",
        "Concise key takeaway point 2"
    ],
    "key_decisions": [
        "Explicit decision 1 agreed upon during the meeting",
        "Explicit decision 2"
    ],
    "tasks": [
        {{
            "task": "Actionable task description",
            "owner": "Person name or null if unmentioned",
            "priority": "Urgent, High, Medium, or Low",
            "due_date": "Target date/day or null",
            "status": "Not Started",
            "notes": "Optional brief context note"
        }}
    ],
    "deadlines": [
        {{
            "date": "Extracted date or milestone (e.g. September 29)",
            "commitment": "What is due or committed on that date"
        }}
    ],
    "important_numbers": [
        {{
            "value": "Formatted figure (e.g. ₹68,000/mo, 37%, ₹18,50,000)",
            "context": "Brief context for what this number represents"
        }}
    ],
    "risks_blockers": [
        "Statements indicating delays, cost overruns, dependencies, or blockers"
    ],
    "open_questions": [
        "Questions asked during the conversation that remained unanswered or unresolved"
    ],
    "follow_ups": [
        "Suggested next steps strictly grounded in the conversation"
    ]
}}

STRICT RULES:
1. Ground everything strictly in the transcript. Do NOT invent facts, numbers, or deadlines.
2. If no decisions were made, key_decisions should be an empty list [].
3. For important_numbers, detect monetary figures (₹, $, etc.), percentages, server counts, budgets, and metrics.
4. For risks_blockers, extract statements showing dependencies, approaching deadlines, or hurdles.
5. For open_questions, extract genuine unanswered questions.
6. Return JSON ONLY with no outer markdown fences.
"""
        raw_response = self.generate(prompt)
        data = self._parse_json_response(raw_response)
        return TranscriptAnalysis.model_validate(data)

    def regenerate_summary(self, transcript: str) -> Dict[str, Any]:
        """Regenerate only Executive Summary and Key Points."""
        prompt = f"""
Provide a fresh, high-impact Executive Summary and Key Takeaways for this transcript:
{transcript}

Return valid JSON ONLY:
{{
    "summary": "Concise executive summary.",
    "key_points": ["Point 1", "Point 2", "Point 3"]
}}
"""
        raw = self.generate(prompt)
        return self._parse_json_response(raw)

    def regenerate_tasks(self, transcript: str) -> List[Dict[str, Any]]:
        """Regenerate only Action Items and Tasks."""
        prompt = f"""
Extract all genuine actionable tasks from this transcript:
{transcript}

Return valid JSON ONLY:
{{
    "tasks": [
        {{
            "task": "Clear action description",
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

    def regenerate_insights(self, transcript: str) -> Dict[str, Any]:
        """Regenerate Decisions, Deadlines, Numbers, Risks, Questions, and Follow-Ups."""
        prompt = f"""
Extract meeting insights (decisions, deadlines, numbers, risks, open questions, follow-ups) from this transcript:
{transcript}

Return valid JSON ONLY:
{{
    "key_decisions": ["Decision 1"],
    "deadlines": [{{"date": "Sep 29", "commitment": "Release freeze"}}],
    "important_numbers": [{{"value": "₹68,000", "context": "Cloud cost"}}],
    "risks_blockers": ["Approaching deadline"],
    "open_questions": ["What is the infrastructure plan?"],
    "follow_ups": ["Validate model results"]
}}
"""
        raw = self.generate(prompt)
        return self._parse_json_response(raw)