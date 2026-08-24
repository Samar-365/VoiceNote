from pathlib import Path

from groq import Groq

from voicenote.config import GROQ_API_KEY, GROQ_STT_MODEL


class GroqSTTEngine:
    def __init__(self, model=GROQ_STT_MODEL):
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured. "
                "Add it to the .env file."
            )

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model

    def transcribe(self, audio_path, language=None):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if not audio_path.is_file():
            raise ValueError(
                f"Audio path is not a file: {audio_path}"
            )

        with open(audio_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                language=language,
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
        return {
            "language": detected_lang,
            "segments": segments,
            "text": transcription.text
        }