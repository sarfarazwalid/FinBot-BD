"""Tests for the indexing pipeline.

Verifies:
1. ``load_chunks`` loads correctly or raises on missing/empty file.
2. ``build_pinecone_vectors`` produces correctly formatted payloads.
3. ``batch_upsert`` splits vectors into expected batch sizes.
4. Metadata is preserved.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

from app.embeddings.index_pipeline import (
    BATCH_SIZE,
    load_chunks,
    build_pinecone_vectors,
    batch_upsert,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_chunks() -> List[Dict[str, Any]]:
    """Return a small list of realistic chunk dicts for testing."""
    return [
        {
            "id": "bkash_faq_000_0",
            "text": "How can I create a bKash account?",
            "source": "bkash_faq",
            "language": "en",
            "chunk_index": 0,
            "created_at": "2026-06-23T22:59:17Z",
        },
        {
            "id": "bkash_faq_001_1",
            "text": "আমার bKash অ্যাকাউন্ট খুলতে চাই, কেমন করা যাবে?",
            "source": "bkash_faq",
            "language": "bn",
            "chunk_index": 1,
            "created_at": "2026-06-23T22:59:17Z",
        },
        {
            "id": "dbbl_faq_000_0",
            "text": "amar account block hoye geche, kivabe unblock korbo?",
            "source": "dbbl_faq",
            "language": "mixed",
            "chunk_index": 0,
            "created_at": "2026-06-23T22:59:17Z",
        },
    ]


@pytest.fixture
def sample_embeddings() -> np.ndarray:
    """Return a dummy (3, 1024) embedding array."""
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(3, 1024)).astype(np.float32)
    # Normalise to unit length (like the real model does).
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms


# ---------------------------------------------------------------------------
# load_chunks
# ---------------------------------------------------------------------------

class TestLoadChunks:
    def test_loads_valid_file(self: TestLoadChunks, sample_chunks: List[Dict[str, Any]]) -> None:
        """Should load and return all records from a valid chunks.json."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(sample_chunks, f)
            tmp_path = f.name

        try:
            result = load_chunks(tmp_path)
            assert len(result) == 3
            assert result[0]["id"] == "bkash_faq_000_0"
            assert result[2]["language"] == "mixed"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_missing_file_raises(self: TestLoadChunks) -> None:
        """Should raise FileNotFoundError when the file does not exist."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_chunks("/nonexistent/path/chunks.json")

    def test_empty_file_raises(self: TestLoadChunks) -> None:
        """Should raise ValueError when the file contains an empty list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump([], f)
            tmp_path = f.name

        try:
            with pytest.raises(ValueError, match="empty"):
                load_chunks(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# build_pinecone_vectors
# ---------------------------------------------------------------------------

class TestBuildPineconeVectors:
    def test_correct_structure(
        self: TestBuildPineconeVectors,
        sample_chunks: List[Dict[str, Any]],
        sample_embeddings: np.ndarray,
    ) -> None:
        """Each vector must have id, values (list of floats), and metadata."""
        vectors = build_pinecone_vectors(sample_chunks, sample_embeddings)

        assert len(vectors) == 3

        for i, v in enumerate(vectors):
            assert "id" in v, f"vector[{i}] missing id"
            assert v["id"] == sample_chunks[i]["id"]

            assert "values" in v, f"vector[{i}] missing values"
            assert isinstance(v["values"], list)
            assert len(v["values"]) == 1024
            assert all(isinstance(x, float) for x in v["values"])

            assert "metadata" in v, f"vector[{i}] missing metadata"
            meta = v["metadata"]
            assert meta["text"] == sample_chunks[i]["text"]
            assert meta["source"] == sample_chunks[i]["source"]
            assert meta["language"] == sample_chunks[i]["language"]
            assert meta["chunk_index"] == sample_chunks[i]["chunk_index"]

    def test_values_are_copy_not_view(
        self: TestBuildPineconeVectors,
        sample_chunks: List[Dict[str, Any]],
        sample_embeddings: np.ndarray,
    ) -> None:
        """The values list should be a standalone copy, not a view into the array."""
        vectors = build_pinecone_vectors(sample_chunks, sample_embeddings)
        # Modifying the original array should not affect the payload.
        sample_embeddings[0, :] = 0.0
        assert not np.allclose(vectors[0]["values"], 0.0)


# ---------------------------------------------------------------------------
# batch_upsert (mock index)
# ---------------------------------------------------------------------------

class MockIndex:
    """A minimal mock that records upsert calls."""

    def __init__(self: MockIndex) -> None:
        self.upsert_calls: List[List[Dict[str, Any]]] = []

    def upsert(self, vectors: List[Dict[str, Any]], **kwargs: Any) -> Any:
        self.upsert_calls.append(vectors)
        return {"upserted_count": len(vectors)}


class TestBatchUpsert:
    def test_batch_split_4_vectors_bs_3(
        self: TestBatchUpsert,
        sample_chunks: List[Dict[str, Any]],
        sample_embeddings: np.ndarray,
    ) -> None:
        """4 vectors with batch_size=3 → batches of 3 and 1."""
        embeddings_4 = np.vstack([sample_embeddings, sample_embeddings[0:1]])
        chunks_4 = sample_chunks + [sample_chunks[0]]
        vectors = build_pinecone_vectors(chunks_4, embeddings_4)

        index = MockIndex()
        batch_upsert(vectors, index, batch_size=3)

        assert len(index.upsert_calls) == 2
        assert len(index.upsert_calls[0]) == 3
        assert len(index.upsert_calls[1]) == 1

    def test_batch_split_183_vectors_bs_50(self) -> None:
        """Simulate real workload: 183 vectors → 4 batches (50, 50, 50, 33)."""
        # Create 183 dummy chunk-like dicts.
        chunks: List[Dict[str, Any]] = [
            {"id": f"chunk_{i:03d}", "text": f"text {i}", "source": "test", "language": "en", "chunk_index": i}
            for i in range(183)
        ]
        rng = np.random.default_rng(0)
        embeddings = rng.normal(size=(183, 1024)).astype(np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms

        vectors = build_pinecone_vectors(chunks, embeddings)

        index = MockIndex()
        batch_upsert(vectors, index, batch_size=50)

        assert len(index.upsert_calls) == 4
        assert len(index.upsert_calls[0]) == 50
        assert len(index.upsert_calls[1]) == 50
        assert len(index.upsert_calls[2]) == 50
        assert len(index.upsert_calls[3]) == 33

    def test_upsert_all_vectors(
        self: TestBatchUpsert,
        sample_chunks: List[Dict[str, Any]],
        sample_embeddings: np.ndarray,
    ) -> None:
        """All vectors should be upserted exactly once."""
        vectors = build_pinecone_vectors(sample_chunks, sample_embeddings)
        index = MockIndex()
        batch_upsert(vectors, index, batch_size=2)

        total_upserted = sum(len(call) for call in index.upsert_calls)
        assert total_upserted == len(sample_chunks)

        all_ids = [v["id"] for call in index.upsert_calls for v in call]
        assert set(all_ids) == {c["id"] for c in sample_chunks}