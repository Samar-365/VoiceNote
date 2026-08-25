import time

from voicenote.core.audio_engine import AudioEngine
from voicenote.core.groq_stt_engine import GroqSTTEngine


def main():
    print("=" * 60)
    print("Audio Engine → Groq STT Integration Test")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Initialize Audio Engine
    # --------------------------------------------------

    print("\n[1] Initializing Audio Engine...")

    audio = AudioEngine(
        sample_rate=16000,
        channels=1,
        output_dir="test_audio",
    )

    if not audio.check_microphone():
        print("ERROR: No microphone detected.")
        return

    print("Microphone detected.")

    # --------------------------------------------------
    # 2. Record audio
    # --------------------------------------------------

    print("\n[2] Recording...")
    print("Speak something for 5 seconds.")

    audio.start_recording()

    for remaining in range(5, 0, -1):
        print(f"Recording... {remaining}")
        time.sleep(1)

    audio_path = audio.stop_recording()

    print(f"\nAudio saved to:")
    print(audio_path)

    # --------------------------------------------------
    # 3. Initialize Groq STT
    # --------------------------------------------------

    print("\n[3] Loading Groq STT...")

    stt = GroqSTTEngine()

    # --------------------------------------------------
    # 4. Transcribe recorded audio
    # --------------------------------------------------

    print("\n[4] Sending audio to Groq...")

    result = stt.transcribe(audio_path)

    # --------------------------------------------------
    # 5. Display result
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("GROQ TRANSCRIPTION RESULT")
    print("=" * 60)

    print(f"\nLanguage: {result['language']}")

    print("\nFull Text:")
    print(result["text"])

    print("\nSegments:")

    for segment in result["segments"]:
        print(
            f"[{segment['start']:.2f}s - "
            f"{segment['end']:.2f}s] "
            f"{segment['text']}"
        )

    print("\n" + "=" * 60)
    print("INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()