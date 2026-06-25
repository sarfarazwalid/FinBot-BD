"""Hybrid search orchestrator.

Combines BM25 keyword retrieval + Pinecone semantic retrieval via
Reciprocal Rank Fusion (RRF) to produce a fused, deduplicated ranking.

Supports bank-aware retrieval — when the query mentions a specific bank,
results from that bank's source are boosted, and results from other banks
are excluded.
"""

from __future__ import annotations

import concurrent.futures
import logging
import re
import time
from typing import Any, Dict, List, Optional

from app.retrieval.bm25 import bm25_search
from app.retrieval.query_rewriter import rewrite_query
from app.retrieval.rrf import fuse_results
from app.retrieval.vector_store import semantic_search

logger = logging.getLogger(__name__)

_BANK_PATTERNS: dict[str, re.Pattern] = {
    "bkash": re.compile(r"\bb?kash\b", re.IGNORECASE),
    "nagad": re.compile(r"\bnagad\b", re.IGNORECASE),
    "dbbl": re.compile(r"\bdbbl\b", re.IGNORECASE),
}

# Bank sources that should be excluded when a different bank is targeted
_NON_TARGET_BANK_SOURCES: set[str] = {"bkash_faq", "nagad_faq", "dbbl_faq"}


def _detect_target_bank(query: str) -> Optional[str]:
    """Return the bank source suffix if the query explicitly names a bank."""
    for bank, pattern in _BANK_PATTERNS.items():
        if pattern.search(query):
            logger.info("Detected target bank: %s", bank)
            return f"{bank}_faq"
    return None


def _exclude_other_banks(
    results: List[Dict[str, Any]],
    target_source: str,
) -> List[Dict[str, Any]]:
    """Remove chunks that belong to other known banks."""
    other_banks = _NON_TARGET_BANK_SOURCES - {target_source}
    filtered: List[Dict[str, Any]] = []
    dropped = 0
    for r in results:
        source = r.get("source", "")
        if source in other_banks:
            dropped += 1
            continue
        filtered.append(r)
    if dropped:
        logger.info("Excluded %d chunks from other banks", dropped)
    return filtered


def _text_fingerprint(text: str) -> int:
    """Compute a near-duplicate fingerprint for a text string."""
    words = text.split()
    if len(words) < 6:
        return hash(text[:100])
    trigrams = frozenset(
        tuple(words[i : i + 3]) for i in range(len(words) - 2)
    )
    return hash(trigrams)


def _filter_and_rerank(
    results: List[Dict[str, Any]],
    target_source: Optional[str],
    top_k: int,
    query: str = "",
) -> List[Dict[str, Any]]:
    """Filter results by bank preference, topic relevance, and remove duplicates."""
    if target_source:
        results = _exclude_other_banks(results, target_source)

    if target_source:
        target = [r for r in results if r.get("source") == target_source]
        other = [r for r in results if r.get("source") != target_source]
        results = target + other
        logger.info(
            "Bank filter: %d target (%s), %d other",
            len(target),
            target_source,
            len(other),
        )

    if query:
        query_words = set(query.lower().split())
        stop_words = {"how", "to", "reset", "my", "the", "a", "an", "is", "i", "?", "?"}
        query_keywords = query_words - stop_words
        if query_keywords:
            def topic_score(chunk: Dict[str, Any]) -> int:
                chunk_text = (chunk.get("text") or "").lower()
                return sum(1 for kw in query_keywords if kw in chunk_text)

            results = sorted(results, key=topic_score, reverse=True)
            logger.info("Topic boost applied: keywords=%s", sorted(query_keywords))

    deduped: List[Dict[str, Any]] = []
    seen_fingerprints: set[int] = set()

    for r in results:
        text = (r.get("text") or "").strip()
        fp = _text_fingerprint(text)
        if fp not in seen_fingerprints:
            seen_fingerprints.add(fp)
            deduped.append(r)

    logger.info("After dedup: %d results (from %d)", len(deduped), len(results))
    return deduped[:top_k]


def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Run the full hybrid search pipeline.

    Pipeline:
        1. Detect target bank from query.
        2. Rewrite the query (domain-specific expansions).
        3. Retrieve with BM25 (keyword).
        4. Retrieve with Pinecone (semantic).
        5. Fuse with RRF.
        6. Filter, rerank by bank preference, deduplicate.
        7. Return top-k results.

    Returns a list of dicts with keys ``id``, ``text``, ``source``,
    ``language``, ``score``.
    """
    timings: dict[str, float] = {}
    t0 = time.perf_counter()

    target_source = _detect_target_bank(query)

    # 1. Query rewriting
    t1 = time.perf_counter()
    expanded_query = rewrite_query(query)
    timings["rewrite"] = (time.perf_counter() - t1) * 1000
    logger.info("Timing rewrite: %.1f ms", timings["rewrite"])

    # 2. BM25 retrieval + 3. Semantic retrieval (parallelized)
    t1 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        bm25_future = executor.submit(bm25_search, expanded_query, top_k * 2)
        semantic_future = executor.submit(semantic_search, query, top_k * 2)
        bm25_results = bm25_future.result()
        semantic_results = semantic_future.result()
    parallel_ms = (time.perf_counter() - t1) * 1000
    logger.info("Timing parallel(bm25+semantic): %.1f ms", parallel_ms)

    # 4. RRF fusion
    t1 = time.perf_counter()
    fused = fuse_results(bm25_results, semantic_results, top_k=top_k * 3)
    timings["rrf"] = (time.perf_counter() - t1) * 1000
    logger.info("Timing rrf: %.1f ms", timings["rrf"])

    # 5. Bank-aware filter + topic boost + dedup
    t1 = time.perf_counter()
    filtered = _filter_and_rerank(
        fused, target_source, top_k=top_k, query=query
    )
    timings["filter"] = (time.perf_counter() - t1) * 1000
    logger.info("Timing filter: %.1f ms", timings["filter"])

    total_ms = (time.perf_counter() - t0) * 1000
    logger.info(
        "[PERF] rewrite=%.1f ms parallel_bm25+semantic=%.1f ms "
        "rrf=%.1f ms filter=%.1f ms total=%.1f ms",
        timings["rewrite"],
        parallel_ms,
        timings["rrf"],
        timings["filter"],
        total_ms,
    )

    return filtered