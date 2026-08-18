from voicenote.core.groq_stt_engine import GroqSTTEngine
from voicenote.core.text_cleaner import TextCleaner
from voicenote.core.ai_engine import AIEngine


def main():
    audio_path = "test_audio/marathi_test.m4a"

    print("=" * 60)
    print("        VOICENOTE STT → GEMINI PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # STEP 1: Groq STT
    # --------------------------------------------------

    print("\n[1/3] Loading Groq STT...")

    stt = GroqSTTEngine()

    print("Transcribing audio...")

    stt_result = stt.transcribe(
        audio_path,
        language="mr"
    )

    print("\n--- RAW TRANSCRIPT ---")
    print(stt_result["text"])

    print("\nDetected language:")
    print(stt_result["language"])

    # --------------------------------------------------
    # STEP 2: Text Cleaning
    # --------------------------------------------------

    print("\n[2/3] Cleaning transcript...")

    cleaner = TextCleaner()

    clean_result = cleaner.clean(stt_result)

    print("\n--- CLEANED TRANSCRIPT ---")
    print(clean_result["text"])

    # --------------------------------------------------
    # STEP 3: Gemini
    # --------------------------------------------------

    print("\n[3/3] Sending transcript to Gemini...")

    ai = AIEngine()

    analysis = ai.analyze_transcript(
        clean_result["text"],
        language=clean_result["language"]
    )

    print("\n--- FINAL RESULT ---")

    print("\nLanguage:")
    print(analysis.language)

    print("\nCorrected Transcript:")
    print(analysis.corrected_transcript)

    print("\nSummary:")
    print(analysis.summary)

    print("\nKey Points:")
    for point in analysis.key_points:
        print("-", point)

    print("\nTasks:")

    if analysis.tasks:
        for task in analysis.tasks:
            print("-", task.task)
            print("  Owner:", task.owner)
            print("  Priority:", task.priority)
            print("  Due Date:", task.due_date)
    else:
        print("No tasks detected.")

    print("\n" + "=" * 60)
    print("        PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()