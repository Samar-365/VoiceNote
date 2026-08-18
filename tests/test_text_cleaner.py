from voicenote.core.text_cleaner import TextCleaner


def main():
    cleaner = TextCleaner()

    transcript = {
        "language": "mr",
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "text": "  माजे   नाओ अत्रवा हैं,  "
            },
            {
                "start": 5.0,
                "end": 10.0,
                "text": "माजे शालेच नाओ गुरुकोल असे हैं!!!"
            }
        ]
    }

    result = cleaner.clean(transcript)

    print("\n--- CLEANED TRANSCRIPT ---")
    print(result["text"])

    print("\n--- SEGMENTS ---")

    for segment in result["segments"]:
        print(
            f"[{segment['start']:.2f}s - "
            f"{segment['end']:.2f}s] "
            f"{segment['text']}"
        )


if __name__ == "__main__":
    main()