from voicenote.core.vector_engine import VectorEngine


def test_vector_engine_initialization(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    assert engine.count() == 0


def test_chunk_transcript(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    transcript = " ".join(
        f"word{i}" for i in range(100)
    )

    chunks = engine.chunk_transcript(
        transcript,
        chunk_size=40,
        overlap=10,
    )

    assert len(chunks) > 1
    assert chunks[0]
    assert chunks[1]


def test_add_transcript(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    transcript = (
        "The team discussed the VoiceNote project deadline. "
        "Atharv will finish the AI pipeline and semantic search "
        "implementation before Friday."
    )

    ids = engine.add_transcript(
        note_id="test_note",
        transcript=transcript,
    )

    assert ids == ["test_note_chunk_0"]
    assert engine.count() == 1


def test_semantic_search(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    transcript = (
        "The team discussed the VoiceNote project deadline. "
        "Atharv will finish the AI pipeline and semantic search "
        "implementation before Friday."
    )

    engine.add_transcript(
        note_id="test_note",
        transcript=transcript,
    )

    results = engine.search(
        "Who is working on the AI pipeline?",
        top_k=1,
    )

    assert len(results) == 1
    assert "AI pipeline" in results[0]["text"]


def test_delete_note(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    engine.add_transcript(
        note_id="test_note",
        transcript="This is a test transcript.",
    )

    assert engine.count() == 1

    deleted = engine.delete_note("test_note")

    assert deleted == 1
    assert engine.count() == 0


def test_chunk_timestamped_segments(tmp_path):
    engine = VectorEngine(
    persist_directory=str(tmp_path / "chroma_db")
    )

    segments = [
        {
            "start": 0.0,
            "end": 2.0,
            "text": "The project meeting started today."
        },
        {
            "start": 2.0,
            "end": 5.0,
            "text": "We discussed the VoiceNote AI pipeline."
        },
        {
            "start": 5.0,
            "end": 8.0,
            "text": "Atharv will implement semantic search."
        },
    ]

    chunks = engine.chunk_timestamped_segments(
        segments,
        chunk_size=20,
        overlap=0,
    )

    assert len(chunks) == 1
    assert chunks[0]["start"] == 0.0
    assert chunks[0]["end"] == 8.0
    assert "VoiceNote AI pipeline" in chunks[0]["text"]


def test_add_timestamped_segments(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    segments = [
        {
            "start": 0.0,
            "end": 2.0,
            "text": "The project meeting started today."
        },
        {
            "start": 2.0,
            "end": 5.0,
            "text": "We discussed the VoiceNote AI pipeline."
        },
    ]

    ids = engine.add_timestamped_segments(
        note_id="timestamp_test",
        segments=segments,
        metadata={
            "language": "en"
        },
        chunk_size=20,
        overlap=0,
    )

    assert ids == ["timestamp_test_chunk_0"]
    assert engine.count() == 1

    results = engine.search(
        "What did we discuss?",
        top_k=1,
    )

    assert len(results) == 1

    metadata = results[0]["metadata"]

    assert metadata["note_id"] == "timestamp_test"
    assert metadata["start_time"] == 0.0
    assert metadata["end_time"] == 5.0
    assert metadata["language"] == "en"

def test_add_timestamped_segments_with_corrected_text(tmp_path):
    engine = VectorEngine(
        persist_directory=str(tmp_path / "chroma_db")
    )

    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "माझे नाव अथरवा आहे."
        }
    ]

    corrected_text = "माझे नाव अथर्व आहे."

    ids = engine.add_timestamped_segments(
        note_id="corrected_test",
        segments=segments,
        corrected_transcript=corrected_text,
    )

    assert ids == ["corrected_test_chunk_0"]

    results = engine.search(
        "अथर्व",
        top_k=1,
    )

    assert len(results) == 1

    metadata = results[0]["metadata"]

    assert metadata["corrected_transcript"] == corrected_text
    assert metadata["start_time"] == 0.0
    assert metadata["end_time"] == 5.0