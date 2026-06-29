"""BM25 keyword retriever using ``rank-bm25``.

Loads chunk corpus from ``chunks.json``, builds a BM25Okapi index, and
provides ``bm25_search()`` for keyword-based retrieval.

Handles missing or invalid corpus gracefully: logs a warning and returns
empty results instead of crashing.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

CHUNKS_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "chunks.json"

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

# Matches English/Latin tokens (letters + digits) AND Bengali Unicode
# characters (U+0980–U+09FF).  English tokens are lowercased; Bengali
# tokens are kept as-is since they have no case.
_WORD_RE = re.compile(r"[A-Za-z0-9\u0980-\u09FF]+")


def _tokenize(text: str) -> List[str]:
    """Tokenize *text* into terms for BM25.

    English / Latin tokens are lowercased.  Bengali Unicode characters
    are matched directly and kept in their original form.

    Example:
        >>> _tokenize("আমার bKash PIN ভুলে গেছি")
        ['আমার', 'bkash', 'pin', 'ভুলে', 'গেছি']
    """
    tokens: List[str] = []
    for match in _WORD_RE.finditer(text):
        token = match.group()
        # Lowercase only if the token is entirely Latin
        if token.isascii():
            token = token.lower()
        tokens.append(token)
    return tokens


# ---------------------------------------------------------------------------
# Corpus loader
# ---------------------------------------------------------------------------

def _load_corpus(path: Path = CHUNKS_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Processed corpus missing at: {path}. "
            "Run preprocessing first: cd backend && python -m app.ingestion.pipeline"
        )
    with open(path, "r", encoding="utf-8") as f:
        chunks: List[Dict[str, Any]] = json.load(f)
    if not chunks:
        raise ValueError(
            f"Chunks file is empty: {path}. "
            "Run preprocessing first: cd backend && python -m app.ingestion.pipeline"
        )
    return chunks


# ---------------------------------------------------------------------------
# BM25 index (lazy singleton)
# ---------------------------------------------------------------------------

_corpus: Optional[List[Dict[str, Any]]] = None
_tokenized_corpus: Optional[List[List[str]]] = None
_bm25: Optional[BM25Okapi] = None
_CORPUS_MISSING: bool = False


def _ensure_index() -> None:
    """Load corpus and build BM25 index on first call.

    If the corpus file is missing or empty, logs a warning and marks the
    index as unavailable.  Subsequent search calls will return empty lists
    instead of crashing.
    """
    global _corpus, _tokenized_corpus, _bm25, _CORPUS_MISSING

    if _bm25 is not None:
        logger.info("[CACHE] BM25 index reused")
        return

    if _CORPUS_MISSING:
        return

    logger.info("Loading BM25 corpus from %s", CHUNKS_PATH)
    try:
        _corpus = _load_corpus()
    except FileNotFoundError:
        _CORPUS_MISSING = True
        logger.warning(
            "BM25 corpus not found at %s. "
            "BM25 will return empty results. "
            "To fix: cd backend && python -m app.ingestion.pipeline",
            CHUNKS_PATH,
        )
        return
    except ValueError as exc:
        _CORPUS_MISSING = True
        logger.warning("BM25 corpus invalid: %s", exc)
        return

    _tokenized_corpus = [_tokenize(doc["text"]) for doc in _corpus]
    _bm25 = BM25Okapi(_tokenized_corpus)
    logger.info("BM25 index built with %d documents", len(_corpus))


def is_bm25_ready() -> bool:
    """Return True if the BM25 index has been successfully built."""
    return _bm25 is not None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def bm25_search(
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Search the corpus with BM25 and return the top-k results.

    Args:
        query: Raw query string.
        top_k: Number of results to return.

    Returns:
        A list of dicts, each with keys: ``text``, ``source``,
        ``language``, ``score``.  Returns an empty list if the BM25
        index is unavailable (corpus missing).
    """
    _ensure_index()

    if _bm25 is None or _corpus is None:
        logger.warning("BM25 index not available, returning empty results")
        return []

    tokenized_query = _tokenize(query)

    if not tokenized_query:
        logger.warning("Query produced no tokens after tokenisation: %r", query)
        return []

    scores = _bm25.get_scores(tokenized_query)
    top_n = sorted(
        enumerate(scores),
        key=lambda item: item[1],
        reverse=True,
    )[:top_k]

    results: List[Dict[str, Any]] = []
    for idx, score in top_n:
        doc = _corpus[idx]
        # BM25 score is a raw float; skip zero-score results.
        if score <= 0.0:
            continue
        results.append(
            {
                "id": doc["id"],
                "text": doc["text"],
                "source": doc["source"],
                "language": doc["language"],
                "score": score,
            }
        )

    logger.debug("BM25 returned %d results for query %r", len(results), query)
    return results