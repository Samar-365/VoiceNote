import json

import requests
from pydantic import BaseModel


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
    """Interface between VoiceNote and the local Ollama LLM."""

    def __init__(
        self,
        ollama_url="http://localhost:11434",
        model="llama3",
    ):
        self.ollama_url = ollama_url
        self.model = model

    def generate(self, prompt):
        """Send a prompt to Ollama and return the generated text."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )

            response.raise_for_status()

        except requests.exceptions.ConnectionError as error:
            raise ConnectionError(
                "Could not connect to Ollama. "
                "Make sure Ollama is running."
            ) from error

        except requests.exceptions.Timeout as error:
            raise TimeoutError(
                "Ollama request timed out."
            ) from error

        except requests.exceptions.HTTPError as error:
            raise RuntimeError(
                f"Ollama returned HTTP error: {response.status_code}"
            ) from error

        data = response.json()

        if "response" not in data:
            raise ValueError(
                "Ollama response does not contain generated text."
            )

        return data["response"]

    def _parse_json_response(self, raw_response):
        """Extract and parse a JSON object from an LLM response."""

        if not raw_response or not raw_response.strip():
            raise ValueError(
                "Ollama returned an empty response."
            )

        start = raw_response.find("{")
        end = raw_response.rfind("}")

        if start == -1 or end == -1 or start >= end:
            raise ValueError(
                "Ollama did not return a valid JSON object."
            )

        json_text = raw_response[start:end + 1]

        try:
            return json.loads(json_text)

        except json.JSONDecodeError as error:
            raise ValueError(
                "Ollama returned malformed JSON."
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

IMPORTANT:
Your entire response must be valid JSON.
Do not write anything before the JSON.
Do not write anything after the JSON.
Do not use markdown code blocks.
Do not explain your answer.
The first character of your response must be {{
and the last character must be }}.

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