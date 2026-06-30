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
import re
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
# Pinecone integration (cached client, robust error handling)
# ---------------------------------------------------------------------------

_pinecone_index = None
_pinecone_connection_error: Optional[str] = None


def _validate_pinecone_config() -> tuple[bool, Optional[str]]:
    """Validate Pinecone configuration from Settings.

    Returns (is_valid, error_message).
    Never exposes the API key in logs/errors.
    """
    settings = Settings()
    api_key = settings.pinecone_api_key
    index_name = settings.pinecone_index_name

    logger.info("Pinecone API Key: %s", "PRESENT" if api_key else "MISSING")
    logger.info("Pinecone Index: %s", index_name)

    if not api_key:
        return False, "PINECONE_API_KEY is missing. Set it in environment variables."
    if not index_name:
        return False, "PINECONE_INDEX_NAME is missing. Set it in environment variables."
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', index_name):
        return False, (
            f"Pinecone index name '{index_name}' is invalid. "
            "Index names must contain only lowercase letters, digits, and hyphens, "
            "and must start and end with a letter or digit."
        )
    return True, None


def _get_pinecone_index() -> Any:
    """Return a cached Pinecone ``Index`` instance configured from settings.

    The Pinecone client and index handle are created once and reused for
    all subsequent queries.  This avoids the multi-second penalty of
    reconnecting on every request.

    Raises RuntimeError with descriptive messages on auth/config failures.
    """
    global _pinecone_index, _pinecone_connection_error
    if _pinecone_index is not None:
        logger.info("[CACHE] Pinecone client reused")
        return _pinecone_index

    if _pinecone_connection_error:
        raise RuntimeError(_pinecone_connection_error)

    try:
        from pinecone import Pinecone, ServerlessSpec
    except ImportError as exc:
        raise ImportError(
            "The 'pinecone' package is required. Install it with: "
            "pip install pinecone"
        ) from exc

    # Validate config before connecting
    valid, error = _validate_pinecone_config()
    if not valid:
        _pinecone_connection_error = error
        raise RuntimeError(error)

    settings = Settings()
    api_key = settings.pinecone_api_key
    index_name = settings.pinecone_index_name

    try:
        logger.info("Connecting to Pinecone (index=%s)...", index_name)
        pc = Pinecone(api_key=api_key)

        existing_indexes = pc.list_indexes().names()
        if index_name not in existing_indexes:
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
            vector_count = stats.get("total_vector_count", 0)
            metric = stats.get("metric", "cosine")
            if index_dimension != _EXPECTED_DIMENSION:
                raise RuntimeError(
                    f"Pinecone index '{index_name}' has dimension {index_dimension}, "
                    f"but the current embedding model '{_EXPECTED_MODEL}' produces "
                    f"{_EXPECTED_DIMENSION}-dim vectors. "
                    f"This index was created with a different embedding model. "
                    f"Recreate the index with dimension={_EXPECTED_DIMENSION} "
                    f"or set EMBEDDING_MODEL to match the existing index."
                )
            logger.info(
                "Pinecone index ready: %s (dimension=%d, metric=%s, vectors=%d)",
                index_name, index_dimension, metric, vector_count,
            )
        except RuntimeError:
            raise
        except Exception as exc:
            logger.warning("Could not validate Pinecone index dimension: %s", exc)

        return _pinecone_index

    except RuntimeError:
        raise
    except Exception as exc:
        error_type = type(exc).__name__
        user_message = str(exc).lower()

        # Classify error and provide actionable message
        if "unauthorized" in user_message or "401" in user_message or "invalid api key" in user_message:
            error_msg = (
                "Pinecone authentication failed. "
                f"Verify PINECONE_API_KEY belongs to the project containing index '{index_name}'. "
                "Check that the API key is correct and not expired."
            )
        elif "forbidden" in user_message or "403" in user_message:
            error_msg = (
                "Pinecone access denied. "
                f"Verify PINECONE_API_KEY has permissions for index '{index_name}'."
            )
        elif "not found" in user_message or "404" in user_message:
            error_msg = (
                f"Pinecone index '{index_name}' not found. "
                "Create it in the Pinecone console or enable auto-creation."
            )
        elif "timeout" in user_message or "timed out" in user_message:
            error_msg = (
                "Pinecone connection timed out. "
                "Check network connectivity and try again."
            )
        elif "connection" in user_message or "network" in user_message:
            error_msg = (
                "Pinecone connection failed. "
                "Check network connectivity and Pinecone service status."
            )
        else:
            # Generic fallback — don't expose raw exception internals
            error_msg = (
                f"Pinecone connection failed for index '{index_name}'. "
                f"Verify configuration and try again. ({error_type})"
            )

        logger.error("Pinecone error: %s", error_msg)
        _pinecone_connection_error = error_msg
        raise RuntimeError(error_msg) from exc


def reset_pinecone_connection() -> None:
    """Reset the Pinecone connection (useful for testing or recovery)."""
    global _pinecone_index, _pinecone_connection_error
    _pinecone_index = None
    _pinecone_connection_error = None


def get_pinecone_status() -> dict:
    """Return Pinecone connection status without raising exceptions."""
    settings = Settings()
    api_key_present = bool(settings.pinecone_api_key)
    index_name = settings.pinecone_index_name

    valid, error = _validate_pinecone_config()
    if not valid:
        return {
            "authenticated": False,
            "api_key_present": api_key_present,
            "index_name": index_name,
            "index_exists": False,
            "error": error,
        }

    try:
        index = _get_pinecone_index()
        stats = index.describe_index_stats()
        return {
            "authenticated": True,
            "api_key_present": api_key_present,
            "index_name": index_name,
            "index_exists": True,
            "dimension": stats.get("dimension", 0),
            "metric": stats.get("metric", "cosine"),
            "vector_count": stats.get("total_vector_count", 0),
            "status": "ok",
        }
    except Exception as exc:
        return {
            "authenticated": False,
            "api_key_present": api_key_present,
            "index_name": index_name,
            "index_exists": False,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Semantic search (Pinecone query) — production-safe error handling
# ---------------------------------------------------------------------------

def semantic_search(
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Embed *query* and search the Pinecone index for the top-k neighbours.

    Returns empty list with a warning log if Pinecone is unavailable.
    Never raises uncaught exceptions.
    """
    try:
        index = _get_pinecone_index()  # cached after first call
    except RuntimeError as exc:
        logger.error("Semantic search unavailable: %s", exc)
        return []

    # Embed the query (1 x 1536).
    try:
        vectors = EmbeddingModel.embed(query)  # cached provider after first call
    except Exception as exc:
        logger.error("Embedding failed for semantic search: %s", exc)
        return []

    # Query Pinecone.
    try:
        response = index.query(
            vector=vectors[0].tolist(),
            top_k=top_k,
            include_metadata=True,
        )
    except Exception as exc:
        logger.error("Pinecone query failed: %s", exc)
        return []

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