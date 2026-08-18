from voicenote.core.groq_stt_engine import GroqSTTEngine


def main():
    print("Loading Groq STT...")

    stt = GroqSTTEngine()

    print("Transcribing audio...")

    result = stt.transcribe(
        "test_audio/marathi_test.m4a",
        language="mr"
    )

    print("\n--- GROQ TRANSCRIPT ---")

    print(f"Language: {result['language']}")

    print(f"\nFull text:\n{result['text']}")

    print("\n--- SEGMENTS ---")

    for segment in result["segments"]:
        print(
            f"[{segment['start']:.2f}s - "
            f"{segment['end']:.2f}s] "
            f"{segment['text']}"
        )


if __name__ == "__main__":
    main()