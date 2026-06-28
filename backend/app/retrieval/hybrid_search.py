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
from app.retrieval.intent_detector import detect_intent, get_intent_anti_topics, get_intent_related_topics
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
    """Filter results by bank preference, intent relevance, and remove duplicates."""
    # 1. Detect intent
    intent, intent_confidence = detect_intent(query)
    related_topics = get_intent_related_topics(intent)
    anti_topics = get_intent_anti_topics(intent)

    logger.info(
        "Intent: %s (confidence=%.2f) | related_topics=%s | anti_topics=%s",
        intent, intent_confidence, related_topics, anti_topics,
    )

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

    # 2. Intent-based topic scoring
    if query and related_topics:
        def intent_score(chunk: Dict[str, Any]) -> float:
            chunk_text = (chunk.get("text") or "").lower()
            chunk_source = (chunk.get("source") or "").lower()

            # Check if chunk topic matches related topics
            topic_match = any(topic in chunk_text or topic in chunk_source for topic in related_topics)

            # Check if chunk contains anti-topics
            anti_match = any(anti in chunk_text for anti in anti_topics)

            # Base score from chunk score field
            base_score = float(chunk.get("score", 0.0) or 0.0)

            if topic_match and not anti_match:
                return base_score + 2.0  # Strong boost
            elif topic_match:
                return base_score + 1.0  # Moderate boost
            elif anti_match:
                return base_score - 1.0  # Penalty
            else:
                return base_score

        results = sorted(results, key=intent_score, reverse=True)
        logger.info("Intent-based rerank applied (intent=%s)", intent)

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

    # 5. Intent-aware filter + rerank + dedup
    t1 = time.perf_counter()
    filtered = _filter_and_rerank(
        fused, target_source, top_k=top_k, query=query
    )
    timings["filter"] = (time.perf_counter() - t1) * 1000
    logger.info("Timing filter: %.1f ms", timings["filter"])

    # 6. Log final intent and chunk topics for audit
    intent, intent_confidence = detect_intent(query)
    logger.info(
        "[AUDIT] query=%r | intent=%s (conf=%.2f) | final_chunks=%d",
        query[:80], intent, intent_confidence, len(filtered),
    )
    for i, chunk in enumerate(filtered, 1):
        logger.info(
            "[AUDIT] chunk[%d] source=%s | topic_keywords=%s",
            i,
            chunk.get("source"),
            _get_chunk_topics(chunk),
        )

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


def _get_chunk_topics(chunk: Dict[str, Any]) -> List[str]:
    """Extract topic indicators from a chunk for audit logging."""
    text = (chunk.get("text") or "").lower()
    topics = []
    topic_indicators = {
        "send money": "send_money",
        "cash in": "cash_in",
        "cash out": "cash_out",
        "recharge": "mobile_recharge",
        "payment": "payment",
        "bank transfer": "bank_transfer",
        "pin": "pin_reset",
        "balance": "check_balance",
        "statement": "mini_statement",
        "loan": "loan",
        "account": "account_opening",
        "fd": "fd_creation",
    }
    for indicator, topic in topic_indicators.items():
        if indicator in text:
            topics.append(topic)
    return topics
