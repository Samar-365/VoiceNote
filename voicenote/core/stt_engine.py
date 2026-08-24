from pathlib import Path

from faster_whisper import WhisperModel


class STTEngine:
    def __init__(self, model_size="small"):
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

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

        # If language is None, Whisper automatically detects the spoken language.
        segments, info = self.model.transcribe(
            str(audio_path),
            language=language,
            vad_filter=True
        )

        transcript = []

        for segment in segments:
            transcript.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })

        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": transcript
        }
