import json
import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()


class Task(BaseModel):
    task: str
    owner: str | None = None
    priority: str | None = None
    due_date: str | None = None


class TranscriptAnalysis(BaseModel):
    summary: str
    key_points: list[str]
    tasks: list[Task]


class AIEngine:
    """Interface between VoiceNote and the Gemini LLM."""

    def __init__(self, model="gemini-3.6-flash"):
        self.model = model

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set."
            )

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt):
        """Send a prompt to Gemini and return the generated text."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        return response.text

    def _parse_json_response(self, raw_response):
        """Extract and parse a JSON object from an LLM response."""

        if not raw_response or not raw_response.strip():
            raise ValueError(
                "Gemini returned an empty response."
            )

        start = raw_response.find("{")
        end = raw_response.rfind("}")

        if start == -1 or end == -1 or start >= end:
            raise ValueError(
                "Gemini did not return a valid JSON object."
            )

        json_text = raw_response[start:end + 1]

        try:
            return json.loads(json_text)

        except json.JSONDecodeError as error:
            raise ValueError(
                "Gemini returned malformed JSON."
            ) from error

    def analyze_transcript(self, transcript):
        """
        Analyze a transcript and return structured
        summary, key points and tasks.
        """

        if not transcript or not transcript.strip():
            raise ValueError(
                "Transcript cannot be empty."
            )

        prompt = f"""
You are an AI assistant for the VoiceNote application.

Analyze the following transcript.

TRANSCRIPT:
{transcript}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "A concise summary of the transcript.",
    "key_points": [
        "Important point 1",
        "Important point 2"
    ],
    "tasks": [
        {{
            "task": "Task description",
            "owner": null,
            "priority": null,
            "due_date": null
        }}
    ]
}}

Rules:

1. Only use information explicitly present in the transcript.
2. Never invent a task, person, priority or date.
3. If a person is explicitly associated with a task,
   use that person's name as the owner.
4. If the owner is not mentioned, use null.
5. If the priority is not mentioned, use null.
6. If the due date is not mentioned, use null.
7. Include only genuine tasks or action items.
8. Do not assign a priority unless the transcript explicitly
   states one.
9. Do not create information that is implied but not explicitly
   stated.
10. Return JSON only.
"""

        raw_response = self.generate(prompt)

        data = self._parse_json_response(raw_response)

        return TranscriptAnalysis.model_validate(data)