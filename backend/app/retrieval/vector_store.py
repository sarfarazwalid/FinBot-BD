"""Vector store and embedding module for semantic retrieval.

Provides:
- ``EmbeddingModel``: Singleton wrapper around an ``EmbeddingProvider`` that
  lazily initialises the configured provider and validates output dimension.
- ``PineconeStore``: Interface to the Pinecone vector index for upserting
  and querying chunks.

Configuration is read from ``app.core.config.Settings`` and can be
overridden via environment variables (see ``.env.example``).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.config import Settings
from app.embeddings.provider import get_embedding_provider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hugging Face authentication (called once at startup)
# ---------------------------------------------------------------------------

_HF_AUTHENTICATED = False
_HF_USERNAME: Optional[str] = None


def configure_huggingface_auth() -> dict:
    """Authenticate with Hugging Face using the token from Settings.

    Uses ``huggingface_hub.login()`` with ``skip_if_logged_in=True`` so
    repeated calls are a no-op.  Returns a dict with auth status info.
    """
    global _HF_AUTHENTICATED, _HF_USERNAME

    result = {
        "authenticated": False,
        "user": None,
        "token_present": False,
    }

    try:
        settings = Settings()
        token = settings.hf_token
        result["token_present"] = bool(token)

        if not token:
            logger.info("[CACHE] HuggingFace authenticated: NO (no token)")
            _HF_AUTHENTICATED = False
            _HF_USERNAME = None
            return result

        # Use the official login flow
        from huggingface_hub import login, whoami

        login(token=token, add_to_git_credential=False, skip_if_logged_in=True)

        # Verify authentication
        identity = whoami()
        _HF_USERNAME = identity.get("name", "unknown")
        _HF_AUTHENTICATED = True

        # Also set environment variables for underlying libs
        os.environ["HF_TOKEN"] = token
        os.environ["HUGGINGFACE_HUB_TOKEN"] = token

        logger.info("[CACHE] HuggingFace authenticated: YES (user=%s)", _HF_USERNAME)
        result["authenticated"] = True
        result["user"] = _HF_USERNAME

    except Exception as exc:
        logger.warning("[HF] Authentication failed: %s", exc)
        _HF_AUTHENTICATED = False
        _HF_USERNAME = None

    return result


def get_hf_auth_status() -> dict:
    """Return the current HF authentication status."""
    from huggingface_hub import whoami
    try:
        identity = whoami()
        username = identity.get("name", "unknown")
        return {
            "authenticated": True,
            "user": username,
        }
    except Exception:
        return {
            "authenticated": False,
            "user": None,
        }


# ---------------------------------------------------------------------------
# Embedding model (remote provider wrapper)
# ---------------------------------------------------------------------------

_EXPECTED_MODEL = "text-embedding-3-small"
_EXPECTED_DIMENSION = 1536


class EmbeddingModel:
    """A singleton-style wrapper around a remote ``EmbeddingProvider``.

    The provider is initialised lazily on first call to ``embed()`` and
    cached for subsequent calls.  The output dimension is validated against
    the configured expected dimension (default: 1536).
    """

    _provider: Any = None
    _cache_found: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def embed(cls, texts: str | List[str]) -> np.ndarray:
        """Compute embeddings for one or more texts via remote API."""
        if cls._provider is None:
            cls._load_provider()
        else:
            logger.info("[CACHE] Embedding provider reused")

        if isinstance(texts, str):
            texts = [texts]

        vectors = cls._provider.embed(texts)
        return vectors

    @classmethod
    def get_info(cls) -> dict:
        """Return metadata about the embedding model."""
        return {
            "model": _EXPECTED_MODEL,
            "dimension": _EXPECTED_DIMENSION,
            "cache_found": cls._cache_found,
            "model_loaded": cls._provider is not None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _load_provider(cls) -> None:
        settings = Settings()
        model_name = settings.embedding_model
        dim = settings.embedding_dimension
        logger.info("Initialising embedding provider (model=%s, dim=%d)", model_name, dim)

        # Instantiate the configured remote provider (lazy — no network yet)
        from app.embeddings.provider import get_embedding_provider
        cls._provider = get_embedding_provider()

        logger.info(
            "Embedding provider ready: %s (model=%s, dimension=%d)",
            settings.embedding_provider, model_name, _EXPECTED_DIMENSION,
        )

        # Verify dimension with a test embedding
        try:
            test_vec = cls._provider.embed(["hello"])
            actual_dim = test_vec.shape[1]
            if actual_dim != _EXPECTED_DIMENSION:
                raise RuntimeError(
                    f"Embedding provider returned dimension {actual_dim}, "
                    f"but expected {_EXPECTED_DIMENSION}. "
                    f"Check that EMBEDDING_MODEL is '{_EXPECTED_MODEL}' "
                    f"and EMBEDDING_DIMENSION is {_EXPECTED_DIMENSION}. "
                    f"If you changed the embedding model, you must recreate "
                    f"the Pinecone index to match the new dimension."
                )
            logger.info("Embedding dimension verified: %d", actual_dim)
        except RuntimeError:
            raise
        except Exception as exc:
            logger.warning("Could not verify embedding dimension: %s", exc)


# ---------------------------------------------------------------------------
# Pinecone integration (cached client)
# ---------------------------------------------------------------------------

_pinecone_index = None


def _get_pinecone_index() -> Any:
    """Return a cached Pinecone ``Index`` instance configured from settings.

    The Pinecone client and index handle are created once and reused for
    all subsequent queries.  This avoids the multi-second penalty of
    reconnecting on every request.
    """
    global _pinecone_index
    if _pinecone_index is not None:
        logger.info("[CACHE] Pinecone client reused")
        return _pinecone_index

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

    _pinecone_index = pc.Index(index_name)

    # Validate dimension once at connection time.
    try:
        stats = _pinecone_index.describe_index_stats()
        index_dimension = stats.get("dimension", 0)
        if index_dimension != _EXPECTED_DIMENSION:
            raise RuntimeError(
                f"Pinecone index '{index_name}' has dimension {index_dimension}, "
                f"but the current embedding model '{_EXPECTED_MODEL}' produces "
                f"{_EXPECTED_DIMENSION}-dim vectors. "
                f"This index was created with a different embedding model. "
                f"Recreate the index with dimension={_EXPECTED_DIMENSION} "
                f"or set EMBEDDING_MODEL to match the existing index."
            )
    except Exception:
        logger.warning("Could not validate Pinecone index dimension")

    logger.info("Pinecone index ready: %s", index_name)
    return _pinecone_index


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
    """
    index = _get_pinecone_index()  # cached after first call

    # Embed the query (1 x 1536).
    vectors = EmbeddingModel.embed(query)  # cached provider after first call

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