from pathlib import Path

from faster_whisper import WhisperModel


class STTEngine:
    def __init__(self, model_size="small"):
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path, language=None, initial_prompt=None):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if not audio_path.is_file():
            raise ValueError(
                f"Audio path is not a file: {audio_path}"
            )

        # Default prompt hint to prime Whisper's tokenizer for meeting dialogues and short responses
        prompt = initial_prompt or (
            "Meeting discussion with multiple speakers. Complete sentences, numbers, "
            "currency notation like ₹ and lakhs, and short acknowledgments like Got it, Done, Okay."
        )

        # Fine-tuned Silero VAD parameters to ensure short utterances ("Done", "Got it")
        # and soft sentence starts are never skipped or clipped as background noise
        vad_params = dict(
            threshold=0.35,              # Sensitive threshold to capture soft and quick speech
            min_speech_duration_ms=80,   # Keep short responses ("Done", "Got it", "Okay")
            max_speech_duration_s=float("inf"),
            min_silence_duration_ms=400, # Natural pause between speaker turns
            speech_pad_ms=300            # Preserve word start and end phonemes
        )

        # If language is None, Whisper automatically detects the spoken language.
        segments, info = self.model.transcribe(
            str(audio_path),
            language=language,
            vad_filter=True,
            vad_parameters=vad_params,
            initial_prompt=prompt,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=False
        )

        transcript = []

        for segment in segments:
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

