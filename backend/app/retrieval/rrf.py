"""Reciprocal Rank Fusion (RRF) for merging BM25 and semantic results.

Combines two ranked result lists by summing the reciprocal ranks of
each document, producing a single fused ranking.

Reference:
    https://plg.uwaterloo.ca/~gvcormack/cormack04.pdf
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Default constant used to smooth the reciprocal rank.
_K = 60


def fuse_results(
    *ranked_lists: List[Dict[str, Any]],
    k: int = _K,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Fuse two or more ranked result lists with RRF.

    Each result dict must contain at least an ``"id"`` key that uniquely
    identifies the document across lists.  Documents are deduplicated
    by their ``"id"`` — the first occurrence's ``text`` / ``source`` /
    ``language`` metadata is kept.

    The final ``score`` field in each result is the RRF score (not the
    original BM25 or cosine score).

    Args:
        *ranked_lists: One or more lists of result dicts, each sorted
            by descending relevance.  Each dict must have an ``"id"``
            field and may also have ``"text"``, ``"source"``,
            ``"language"``.
        k: RRF smoothing constant (default 60).
        top_k: Number of documents to keep in the fused list.

    Returns:
        A list of up to ``top_k`` deduplicated result dicts, fused and
        sorted by descending RRF score.

    Example:
        >>> fuse_results(bm25_results, semantic_results, top_k=5)
    """
    if not ranked_lists:
        return []

    # Accumulate RRF scores by document id.
    scores: Dict[str, float] = {}
    meta: Dict[str, Dict[str, Any]] = {}  # id -> metadata snapshot

    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked, start=1):
            doc_id = doc.get("id")
            if doc_id is None:
                continue

            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)

            # Keep metadata from the first occurrence only.
            if doc_id not in meta:
                meta[doc_id] = {
                    "text": doc.get("text", ""),
                    "source": doc.get("source", ""),
                    "language": doc.get("language", ""),
                }

    # Sort by descending RRF score.
    ranked_ids = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)

    fused: List[Dict[str, Any]] = []
    for doc_id in ranked_ids[:top_k]:
        fused.append(
            {
                "id": doc_id,
                "text": meta[doc_id]["text"],
                "source": meta[doc_id]["source"],
                "language": meta[doc_id]["language"],
                "score": scores[doc_id],
            }
        )

    logger.debug(
        "RRF fused %d lists into %d results", len(ranked_lists), len(fused),
    )
    return fused