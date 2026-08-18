import re


class TextCleaner:
    def clean_segment(self, text):
        if not text:
            return ""

        text = text.strip()

        # Normalize repeated whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove spaces before punctuation
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)

        # Remove repeated punctuation
        text = re.sub(r"([,.!?;:])\1+", r"\1", text)

        return text.strip()

    def clean(self, transcript):
        cleaned_segments = []

        for segment in transcript.get("segments", []):
            cleaned_text = self.clean_segment(segment.get("text", ""))

            if not cleaned_text:
                continue

            cleaned_segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": cleaned_text
            })

        return {
            "language": transcript.get("language"),
            "segments": cleaned_segments,
            "text": " ".join(
                segment["text"]
                for segment in cleaned_segments
            )
        }