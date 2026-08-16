from voicenote.core.ai_engine import AIEngine


def test_generate():
    """Test basic communication with Ollama."""

    ai = AIEngine()

    response = ai.generate(
        "Say 'VoiceNote test successful' and nothing else."
    )

    assert response
    print("✓ test_generate passed")


def test_analyze_transcript():
    """Test transcript analysis."""

    ai = AIEngine()

    transcript = """
    Today we discussed the VoiceNote project.
    Rahul will prepare the project presentation by Friday.
    Atharva will implement the AI engine.
    We decided to use ChromaDB for semantic search.
    The team will test the complete STT to LLM pipeline next week.
    """

    result = ai.analyze_transcript(transcript)

    assert result.summary
    assert len(result.key_points) > 0
    assert len(result.tasks) > 0

    print("✓ test_analyze_transcript passed")

    print("\nSUMMARY:")
    print(result.summary)

    print("\nKEY POINTS:")
    for point in result.key_points:
        print("-", point)

    print("\nTASKS:")
    for task in result.tasks:
        print("-", task.task)
        print("  Owner:", task.owner)
        print("  Priority:", task.priority)
        print("  Due Date:", task.due_date)


def test_empty_prompt():
    """Test that empty prompts are rejected."""

    ai = AIEngine()

    try:
        ai.generate("")
        assert False, "Empty prompt should raise ValueError"

    except ValueError:
        print("✓ test_empty_prompt passed")


def test_empty_transcript():
    """Test that empty transcripts are rejected."""

    ai = AIEngine()

    try:
        ai.analyze_transcript("")
        assert False, "Empty transcript should raise ValueError"

    except ValueError:
        print("✓ test_empty_transcript passed")


if __name__ == "__main__":
    test_generate()
    test_analyze_transcript()
    test_empty_prompt()
    test_empty_transcript()

    print("\nAll AI Engine tests passed.")