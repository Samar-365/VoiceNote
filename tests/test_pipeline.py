from voicenote.core.vector_engine import VectorEngine
from voicenote.core.groq_stt_engine import GroqSTTEngine
from voicenote.core.text_cleaner import TextCleaner
from voicenote.core.ai_engine import AIEngine
from voicenote.core.vector_engine import VectorEngine


def main():
    audio_path = "test_audio/test_sample_01.m4a"

    print("=" * 60)
    print("        VOICENOTE FULL AI PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # STEP 1: Groq STT
    # --------------------------------------------------

    print("\n[1/5] Loading Groq STT...")

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

    print("\n[2/5] Cleaning transcript...")

    cleaner = TextCleaner()

    clean_result = cleaner.clean(stt_result)

    print("\n--- CLEANED TRANSCRIPT ---")
    print(clean_result["text"])

    # --------------------------------------------------
    # STEP 3: Gemini AI
    # --------------------------------------------------

    print("\n[3/5] Sending transcript to Gemini...")

    ai = AIEngine()

    analysis = ai.analyze_transcript(
        clean_result["text"],
        language=clean_result["language"]
    )

    print("\n--- AI ANALYSIS ---")

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

    # --------------------------------------------------
    # STEP 4: Vector Indexing
    # --------------------------------------------------

    print("\n[4/5] Indexing timestamped transcript...")

    vector = VectorEngine(
        persist_directory="./test_pipeline_chroma_db"
    )

    vector_ids = vector.add_timestamped_segments(
    note_id="pipeline_test",
    segments=clean_result["segments"],
    metadata={
        "language": clean_result["language"]
    },
    corrected_transcript=analysis.corrected_transcript,
    )

    print("\nIndexed chunks:")

    for vector_id in vector_ids:
        print("-", vector_id)

    print("\nTotal indexed chunks:")
    print(vector.count())

    # --------------------------------------------------
    # STEP 5: Semantic Search
    # --------------------------------------------------

    print("\n[5/5] Testing semantic search...")

    search_query = "whats his role"

    results = vector.search(
        search_query,
        top_k=3
    )

    print("\n--- SEARCH RESULTS ---")

    for result in results:

        print("\nID:")
        print(result["id"])

        print("\nText:")
        print(result["text"])

        print("\nStart time:")
        print(result["metadata"].get("start_time"))

        print("\nEnd time:")
        print(result["metadata"].get("end_time"))

        print("\nDistance:")
        print(result["distance"])

    print("\n" + "=" * 60)
    print("        FULL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()