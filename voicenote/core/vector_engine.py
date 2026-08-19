from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


class VectorEngine:
    """Local semantic indexing and search engine for VoiceNote."""

    def __init__(
        self,
        persist_directory="./chroma_db",
        collection_name="transcripts",
        embedding_model="all-MiniLM-L6-v2",
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
        )

    # ==========================================================
    # TEXT CHUNKING
    # ==========================================================

    def chunk_transcript(
        self,
        text,
        chunk_size=400,
        overlap=50,
    ):
        """Split plain transcript text into overlapping word chunks."""

        if not text or not text.strip():
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be >= 0 and smaller than chunk_size."
            )

        words = text.split()
        chunks = []

        step = chunk_size - overlap

        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]

            if not chunk_words:
                break

            chunks.append(" ".join(chunk_words))

            if start + chunk_size >= len(words):
                break

        return chunks

    # ==========================================================
    # TIMESTAMP-AWARE CHUNKING
    # ==========================================================

    def chunk_timestamped_segments(
        self,
        segments,
        chunk_size=400,
        overlap=50,
    ):
        """
        Group timestamped STT segments into searchable chunks.

        Each chunk keeps the original start and end timestamps
        from the STT segments.
        """

        if not segments:
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be >= 0 and smaller than chunk_size."
            )

        normalized = []

        for segment in segments:
            text = str(segment.get("text", "")).strip()

            if not text:
                continue

            if "start" not in segment or "end" not in segment:
                raise ValueError(
                    "Each segment must contain start, end and text."
                )

            normalized.append(
                {
                    "start": float(segment["start"]),
                    "end": float(segment["end"]),
                    "text": text,
                }
            )

        chunks = []
        start_index = 0

        while start_index < len(normalized):

            word_count = 0
            end_index = start_index

            while end_index < len(normalized):

                segment_words = len(
                    normalized[end_index]["text"].split()
                )

                if (
                    end_index > start_index
                    and word_count + segment_words > chunk_size
                ):
                    break

                word_count += segment_words
                end_index += 1

                if word_count >= chunk_size:
                    break

            selected = normalized[start_index:end_index]

            if not selected:
                break

            chunks.append(
                {
                    "text": " ".join(
                        item["text"]
                        for item in selected
                    ),
                    "start": selected[0]["start"],
                    "end": selected[-1]["end"],
                }
            )

            if end_index >= len(normalized):
                break

            # Preserve approximately `overlap` words
            # for the next chunk.
            retained_words = 0
            next_start = end_index - 1

            while next_start > start_index:

                retained_words += len(
                    normalized[next_start]["text"].split()
                )

                if retained_words >= overlap:
                    break

                next_start -= 1

            start_index = max(
                next_start,
                start_index + 1
            )

        return chunks

    # ==========================================================
    # NORMAL TRANSCRIPT INDEXING
    # ==========================================================

    def add_transcript(
        self,
        note_id,
        transcript,
        metadata=None,
        chunk_size=400,
        overlap=50,
    ):
        """Chunk and index a plain transcript."""

        if note_id is None:
            raise ValueError("note_id cannot be None.")

        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty.")

        chunks = self.chunk_transcript(
            transcript,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not chunks:
            return []

        base_metadata = metadata.copy() if metadata else {}

        ids = []
        documents = []
        metadatas = []

        for index, chunk in enumerate(chunks):

            chunk_id = f"{note_id}_chunk_{index}"

            chunk_metadata = {
                **base_metadata,
                "note_id": str(note_id),
                "chunk_index": index,
            }

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(chunk_metadata)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return ids

    # ==========================================================
    # TIMESTAMP-AWARE INDEXING
    # ==========================================================

    def add_timestamped_segments(
        self,
        note_id,
        segments,
        metadata=None,
        corrected_transcript=None,
        chunk_size=400,
        overlap=50,
    ):
        """
        Index timestamped STT transcript segments.

        Original STT text is stored as the searchable document.
        Original timestamps are preserved as metadata.
        The Gemini corrected transcript is also stored as metadata
        so search results can expose both versions.

        Note:
            The corrected transcript is currently stored at note/chunk
            level because Gemini returns it as a complete corrected
            transcript rather than timestamp-aligned segments.
        """

        if note_id is None:
            raise ValueError("note_id cannot be None.")

        if not segments:
            raise ValueError(
                "Transcript segments cannot be empty."
            )

        chunks = self.chunk_timestamped_segments(
            segments,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not chunks:
            return []

        base_metadata = metadata.copy() if metadata else {}

        ids = []
        documents = []
        metadatas = []

        for index, chunk in enumerate(chunks):

            chunk_id = f"{note_id}_chunk_{index}"

            chunk_metadata = {
                **base_metadata,
                "note_id": str(note_id),
                "chunk_index": index,
                "start_time": chunk["start"],
                "end_time": chunk["end"],
            }

            if corrected_transcript:
                chunk_metadata["corrected_transcript"] = (
                    corrected_transcript
                )

            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(chunk_metadata)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return ids

    # ==========================================================
    # SEMANTIC SEARCH
    # ==========================================================

    def search(
        self,
        query,
        top_k=5,
    ):
        """Return the most semantically relevant transcript chunks."""

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        matches = []

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        ids = results.get(
            "ids",
            [[]]
        )[0]

        for index, document in enumerate(documents):

            matches.append(
                {
                    "id": (
                        ids[index]
                        if index < len(ids)
                        else None
                    ),
                    "text": document,
                    "metadata": (
                        metadatas[index]
                        if index < len(metadatas)
                        else {}
                    ),
                    "distance": (
                        distances[index]
                        if index < len(distances)
                        else None
                    ),
                }
            )

        return matches

    # ==========================================================
    # DELETE NOTE
    # ==========================================================

    def delete_note(self, note_id):
        """Delete all indexed chunks belonging to a note."""

        if note_id is None:
            raise ValueError(
                "note_id cannot be None."
            )

        result = self.collection.get(
            where={
                "note_id": str(note_id)
            }
        )

        ids = result.get(
            "ids",
            []
        )

        if ids:
            self.collection.delete(
                ids=ids
            )

        return len(ids)

    # ==========================================================
    # COUNT
    # ==========================================================

    def count(self):
        """Return the number of indexed transcript chunks."""

        return self.collection.count()