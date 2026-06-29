"""Index pipeline: load chunks, generate embeddings, upsert to Pinecone.

Usage::

    python -m app.embeddings.index_pipeline

Requires ``PINECONE_API_KEY`` and ``PINECONE_INDEX_NAME`` to be set
in the environment (or in ``.env``).
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from app.core.config import Settings
from app.retrieval.vector_store import EmbeddingModel, _get_pinecone_index

logger = logging.getLogger(__name__)

BATCH_SIZE = 50

CHUNKS_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "chunks.json"


# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------

def load_chunks(path: str | Path = CHUNKS_PATH) -> List[Dict[str, Any]]:
    """Load chunk records from ``chunks.json``.

    Returns:
        A list of dicts with keys ``id``, ``text``, ``source``,
        ``language``, ``chunk_index``, etc.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains no records.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Chunks file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        chunks: List[Dict[str, Any]] = json.load(f)

    if not chunks:
        raise ValueError(f"Chunks file is empty: {path}")

    logger.info("Loaded %d chunks", len(chunks))
    return chunks


# ---------------------------------------------------------------------------
# 2. Generate embeddings
# ---------------------------------------------------------------------------

def generate_embeddings(chunks: List[Dict[str, Any]]) -> np.ndarray:
    """Generate normalized embeddings for all chunk texts.

    Args:
        chunks: List of chunk dicts (must contain ``"text"``).

    Returns:
        A 2-D float32 NumPy array of shape ``(n_chunks, 1536)``.
    """
    texts = [c["text"] for c in chunks]
    logger.info("Generating embeddings for %d texts...", len(texts))
    vectors = EmbeddingModel.embed(texts)
    logger.info("Generated embeddings: %s", list(vectors.shape))
    return vectors


# ---------------------------------------------------------------------------
# 3. Build Pinecone vectors
# ---------------------------------------------------------------------------

def build_pinecone_vectors(
    chunks: List[Dict[str, Any]],
    embeddings: np.ndarray,
) -> List[Dict[str, Any]]:
    """Build a list of Pinecone upsert payloads.

    Each payload has the structure::

        {
            "id": chunk["id"],
            "values": embedding (list of floats),
            "metadata": {
                "text": chunk["text"],
                "source": chunk["source"],
                "language": chunk["language"],
                "chunk_index": chunk["chunk_index"]
            }
        }

    Args:
        chunks: Original chunk dicts.
        embeddings: 2-D array of shape ``(n_chunks, 1536)``.

    Returns:
        List of dicts ready for ``index.upsert()``.
    """
    payloads: List[Dict[str, Any]] = []
    for i, chunk in enumerate(chunks):
        payloads.append(
            {
                "id": chunk["id"],
                "values": embeddings[i].tolist(),
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "language": chunk["language"],
                    "chunk_index": chunk["chunk_index"],
                },
            }
        )
    return payloads


# ---------------------------------------------------------------------------
# 4. Batch upsert
# ---------------------------------------------------------------------------

def batch_upsert(
    vectors: List[Dict[str, Any]],
    index,
    batch_size: int = BATCH_SIZE,
) -> None:
    """Upsert vectors to Pinecone in batches.

    Args:
        vectors: Full list of Pinecone vector payloads.
        index: A Pinecone ``Index`` instance.
        batch_size: Number of vectors per upsert call.
    """
    total = len(vectors)
    n_batches = (total + batch_size - 1) // batch_size  # ceil division

    for batch_idx in range(n_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, total)
        batch = vectors[start:end]

        logger.info("Uploading batch %d/%d  (%d vectors)", batch_idx + 1, n_batches, len(batch))
        index.upsert(vectors=batch)
        logger.info("Batch %d/%d upload complete", batch_idx + 1, n_batches)


# ---------------------------------------------------------------------------
# 5. Main pipeline
# ---------------------------------------------------------------------------

def run_index_pipeline() -> None:
    """Run the full indexing pipeline end-to-end."""
    logger.info("Starting FinBot BD indexing")

    # 1. Load chunks
    chunks = load_chunks()

    # 2. Generate embeddings
    embeddings = generate_embeddings(chunks)

    # 3. Validate embedding dimension matches Pinecone
    index = _get_pinecone_index()

    # 4. Build Pinecone vector payloads
    vectors = build_pinecone_vectors(chunks, embeddings)

    # 5. Batch upsert (idempotent — same IDs overwrite existing vectors)
    batch_upsert(vectors, index)

    # 6. Final summary
    stats = index.describe_index_stats()
    vector_count = stats.get("total_vector_count", 0)
    logger.info("Indexing completed")
    logger.info("Chunks: %d", len(chunks))
    logger.info("Vectors: %d", vector_count)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        run_index_pipeline()
    except (FileNotFoundError, ValueError, RuntimeError, ImportError) as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()