"""Vector store and embedding module for semantic retrieval.

Provides:
- ``EmbeddingModel``: Singleton wrapper around ``SentenceTransformer`` that
  loads ``intfloat/multilingual-e5-large`` and validates output dimension.
- ``PineconeStore``: Interface to the Pinecone vector index for upserting
  and querying chunks.

Configuration is read from ``app.core.config.Settings`` and can be
overridden via environment variables (see ``.env.example``).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import Settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------

_EXPECTED_MODEL = "intfloat/multilingual-e5-large"
_EXPECTED_DIMENSION = 1024


class EmbeddingModel:
    """A singleton-style wrapper around a ``SentenceTransformer`` model.

    The model is loaded lazily on first call to ``embed()`` and cached for
    subsequent calls.  The output dimension is validated against the
    configured expected dimension (default: 1024).
    """

    _model: Optional[SentenceTransformer] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def embed(cls, texts: str | List[str]) -> np.ndarray:
        """Compute embeddings for one or more texts.

        Args:
            texts: A single string or a list of strings to embed.

        Returns:
            A 2-D NumPy array of shape ``(n_texts, embedding_dimension)``.

        Raises:
            RuntimeError: If the embedding dimension does not match the
                configured Pinecone index dimension (1024).
        """
        if cls._model is None:
            cls._load_model()

        if isinstance(texts, str):
            texts = [texts]

        vectors = cls._model.encode(texts, normalize_embeddings=True)  # type: ignore[union-attr]
        vectors = np.asarray(vectors, dtype=np.float32)

        if vectors.shape[1] != _EXPECTED_DIMENSION:
            raise RuntimeError(
                f"Embedding model returned dimension {vectors.shape[1]}, "
                f"but Pinecone index expects {_EXPECTED_DIMENSION}. "
                f"Check that EMBEDDING_MODEL is {_EXPECTED_MODEL!r} "
                f"and EMBEDDING_DIMENSION is {_EXPECTED_DIMENSION}."
            )

        return vectors

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _load_model(cls) -> None:
        settings = Settings()
        model_name = settings.embedding_model
        logger.info("Loading embedding model: %s", model_name)
        cls._model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded (dimension=%d)", _EXPECTED_DIMENSION)


# ---------------------------------------------------------------------------
# Pinecone integration
# ---------------------------------------------------------------------------

def _get_pinecone_index():
    """Return a Pinecone ``Index`` instance configured from settings.

    The environment must provide:
        PINECONE_API_KEY
        PINECONE_INDEX_NAME  (default: ``"finbot-bd"``)

    The index must have:
        dimension = 1024
        metric    = cosine

    Raises:
        ImportError: If the ``pinecone`` package is not installed.
    """
    try:
        from pinecone import Pinecone, ServerlessSpec
    except ImportError as exc:
        raise ImportError(
            "The 'pinecone' package is required. Install it with: "
            "pip install pinecone"
        ) from exc

    settings = Settings()

    pc = Pinecone(api_key=settings.pinecone_api_key)

    index_name = settings.pinecone_index_name

    # Create the index if it does not already exist.
    if index_name not in pc.list_indexes().names():
        logger.info(
            "Creating Pinecone index '%s' (dimension=%d, metric=cosine)",
            index_name,
            _EXPECTED_DIMENSION,
        )
        pc.create_index(
            name=index_name,
            dimension=_EXPECTED_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    # Validate dimension.
    stats = index.describe_index_stats()
    index_dimension = stats.get("dimension", 0)
    if index_dimension != _EXPECTED_DIMENSION:
        raise RuntimeError(
            f"Pinecone index '{index_name}' has dimension {index_dimension}, "
            f"but the embedding model produces {_EXPECTED_DIMENSION}-dim vectors. "
            f"Recreate the index with dimension={_EXPECTED_DIMENSION}."
        )

    return index


# ---------------------------------------------------------------------------
# Semantic search (Pinecone query)
# ---------------------------------------------------------------------------

def semantic_search(
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Embed *query* and search the Pinecone index for the top-k neighbours.

    Args:
        query: Free-text query string.
        top_k: Number of results to return.

    Returns:
        A list of dicts with keys ``id``, ``text``, ``source``,
        ``language``, ``score``.  ``score`` is the cosine similarity
        reported by Pinecone.

    Raises:
        RuntimeError: If the Pinecone API key is missing or the index
            dimension does not match the embedding dimension.
    """
    index = _get_pinecone_index()

    # Embed the query (1 x 1024).
    vectors = EmbeddingModel.embed(query)

    # Query Pinecone.
    response = index.query(
        vector=vectors[0].tolist(),
        top_k=top_k,
        include_metadata=True,
    )

    results: List[Dict[str, Any]] = []
    for match in response.get("matches", []):
        meta = match.get("metadata", {})
        results.append(
            {
                "id": match.get("id", ""),
                "text": meta.get("text", ""),
                "source": meta.get("source", ""),
                "language": meta.get("language", ""),
                "score": match.get("score", 0.0),
            }
        )

    logger.debug("Semantic search returned %d results for %r", len(results), query)
    return results
