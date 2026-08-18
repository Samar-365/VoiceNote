from voicenote.core.stt_engine import STTEngine


def main():
    print("Loading STT model...")

    stt = STTEngine(model_size="medium")

    print("Transcribing audio...")

    result = stt.transcribe("test_audio/marathi.wma")

    print("\n--- TRANSCRIPT ---")

    print(f"Detected language: {result['language']}")
    print(
        f"Language confidence: "
        f"{result['language_probability']:.2f}"
    )

    for segment in result["segments"]:
        print(
            f"[{segment['start']:.2f}s - "
            f"{segment['end']:.2f}s] "
            f"{segment['text']}"
        )


if __name__ == "__main__":
    main()