from voicenote.core.stt_engine import STTEngine


def main():
    print("Loading STT model...")

    stt = STTEngine(model_size="small")

    print("Transcribing audio...")

    result = stt.transcribe("test_audio/test_sample_01.m4a")
    # result = stt.transcribe("test_audio/does_not_exist.wav")

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