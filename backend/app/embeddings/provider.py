"""Embedding provider abstraction with factory support.

Provides:
- ``EmbeddingProvider``: Abstract base class for all embedding providers.
- ``OpenAIEmbeddingProvider``: Uses OpenAI's embeddings API directly.
- ``OpenRouterEmbeddingProvider``: Uses OpenRouter's embedding endpoint.
- ``get_embedding_provider``: Factory function that returns the configured provider.

Configuration is read from ``app.core.config.Settings``.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional

import numpy as np

from app.core.config import Settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------


class EmbeddingProvider(ABC):
    """Abstract interface for embedding generation.

    Subclasses must implement ``embed()`` which accepts a list of texts
    and returns a float32 NumPy array of shape ``(n_texts, dimension)``.
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        ...


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_MAX_RETRIES = 3
_BASE_DELAY_MS = 500


def _embed_with_retry(client: Any, model: str, texts: List[str]) -> np.ndarray:
    """Call ``client.embeddings.create()`` with retry logic.

    Handles transient errors (timeouts, rate limits, server errors).
    Returns a float32 array of shape ``(len(texts), dimension)``.
    """
    last_exc: Optional[Exception] = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = client.embeddings.create(
                model=model,
                input=texts,
            )
            # Sort by index to preserve original ordering
            sorted_data = sorted(response.data, key=lambda d: d.index)
            vectors = np.array([d.embedding for d in sorted_data], dtype=np.float32)
            logger.info(
                "Embedding API success: %d texts, dim=%d (attempt %d/%d)",
                len(texts),
                vectors.shape[1],
                attempt,
                _MAX_RETRIES,
            )
            return vectors

        except Exception as exc:
            last_exc = exc
            error_str = str(exc).lower()

            # Classify error for logging
            if "401" in error_str or "unauthorized" in error_str or "invalid_api_key" in error_str:
                logger.error("Embedding API auth error (attempt %d/%d): %s", attempt, _MAX_RETRIES, exc)
                raise  # Non-retryable

            if "429" in error_str or "rate" in error_str or "limit" in error_str:
                delay = _BASE_DELAY_MS * (2 ** (attempt - 1)) / 1000.0
                logger.warning(
                    "Embedding API rate limited (attempt %d/%d), retrying in %.1fs: %s",
                    attempt, _MAX_RETRIES, delay, exc,
                )
                time.sleep(delay)
                continue

            if attempt < _MAX_RETRIES:
                delay = _BASE_DELAY_MS * (2 ** (attempt - 1)) / 1000.0
                logger.warning(
                    "Embedding API error (attempt %d/%d), retrying in %.1fs: %s",
                    attempt, _MAX_RETRIES, delay, exc,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "Embedding API failed after %d attempts: %s",
                    _MAX_RETRIES, exc,
                )
                raise

    # Should not reach here, but satisfy the type checker
    raise RuntimeError(
        f"Embedding API failed after {_MAX_RETRIES} attempts: {last_exc}"
    ) from last_exc


# ---------------------------------------------------------------------------
# OpenAI provider
# ---------------------------------------------------------------------------


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Uses OpenAI's Embeddings API (text-embedding-3-small etc.)."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url if base_url else "https://api.openai.com/v1"
        self._client: Optional[Any] = None

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        from openai import OpenAI
        self._client = OpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )
        logger.info(
            "OpenAI embedding client initialized (base_url=%s, model=%s)",
            self._base_url, self._model,
        )
        return self._client

    def embed(self, texts: List[str]) -> np.ndarray:
        client = self._ensure_client()
        return _embed_with_retry(client, self._model, texts)


# ---------------------------------------------------------------------------
# OpenRouter provider
# ---------------------------------------------------------------------------


class OpenRouterEmbeddingProvider(EmbeddingProvider):
    """Uses OpenRouter's embedding endpoint.

    Reuses the same API key and base URL configured for LLM generation.
    You must use an embedding-capable model (e.g. ``text-embedding-3-small``).
    """

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = (
            base_url if base_url else "https://openrouter.ai/api/v1"
        )
        self._client: Optional[Any] = None

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        from openai import OpenAI
        self._client = OpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )
        logger.info(
            "OpenRouter embedding client initialized (base_url=%s, model=%s)",
            self._base_url, self._model,
        )
        return self._client

    def embed(self, texts: List[str]) -> np.ndarray:
        client = self._ensure_client()
        return _embed_with_retry(client, self._model, texts)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_PROVIDER_CACHE: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured embedding provider (cached singleton).

    Reads ``Settings().embedding_provider`` to decide which implementation
    to instantiate.  The provider is created once and cached for all
    subsequent calls.

    Providers:
        - ``"openai"``: Direct OpenAI API.
        - ``"openrouter"`` (default): OpenRouter embedding endpoint (reuses
          ``OPENROUTER_API_KEY``).

    Raises:
        ValueError: If ``embedding_provider`` is unknown.
        RuntimeError: If required API keys are missing.
    """
    global _PROVIDER_CACHE

    if _PROVIDER_CACHE is not None:
        return _PROVIDER_CACHE

    settings = Settings()
    provider_name = settings.embedding_provider
    model = settings.embedding_model

    if provider_name == "openai":
        api_key = settings.embedding_api_key or settings.openrouter_api_key
        base_url = settings.embedding_base_url or "https://api.openai.com/v1"
        if not api_key:
            raise RuntimeError(
                "EMBEDDING_API_KEY or OPENROUTER_API_KEY must be set for provider='openai'"
            )
        logger.info(
            "Factory: creating OpenAIEmbeddingProvider (model=%s)", model,
        )
        _PROVIDER_CACHE = OpenAIEmbeddingProvider(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

    elif provider_name == "openrouter":
        api_key = settings.openrouter_api_key
        base_url = settings.openrouter_base_url
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY must be set for provider='openrouter'"
            )
        logger.info(
            "Factory: creating OpenRouterEmbeddingProvider (model=%s, base_url=%s)",
            model, base_url,
        )
        _PROVIDER_CACHE = OpenRouterEmbeddingProvider(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

    else:
        raise ValueError(
            f"Unknown embedding provider '{provider_name}'. "
            f"Supported: 'openai', 'openrouter'."
        )

    return _PROVIDER_CACHE


def clear_provider_cache() -> None:
    """Reset the provider singleton (useful for testing)."""
    global _PROVIDER_CACHE
    _PROVIDER_CACHE = None