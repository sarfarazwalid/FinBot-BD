"""Hybrid search orchestrator.

Combines BM25 keyword retrieval + Pinecone semantic retrieval via
Reciprocal Rank Fusion (RRF) to produce a fused, deduplicated ranking.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.retrieval.bm25 import bm25_search
from app.retrieval.query_rewriter import rewrite_query
from app.retrieval.rrf import fuse_results
from app.retrieval.vector_store import semantic_search

logger = logging.getLogger(__name__)


def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Run the full hybrid search pipeline.

    Pipeline:
        1. Rewrite the query (domain-specific expansions).
        2. Retrieve with BM25 (keyword).
        3. Retrieve with Pinecone (semantic).
        4. Fuse with RRF.
        5. Return top-k deduplicated results.

    Args:
        query: Raw user query.
        top_k: Number of final results to return.

    Returns:
        A list of dicts with keys ``id``, ``text``, ``source``,
        ``language``, ``score``.  ``score`` is the RRF score.
    """
    # 1. Query rewriting
    logger.info("Original query: %r", query)
    expanded_query = rewrite_query(query)
    logger.info("Rewritten: %r", expanded_query)

    # 2. BM25 retrieval
    bm25_results = bm25_search(expanded_query, top_k=top_k * 2)
    logger.info("BM25 results: %d", len(bm25_results))

    # 3. Semantic retrieval
    semantic_results = semantic_search(query, top_k=top_k * 2)
    logger.info("Semantic results: %d", len(semantic_results))

    # 4. RRF fusion
    fused = fuse_results(bm25_results, semantic_results, top_k=top_k)
    logger.info("Final fused: %d", len(fused))

    return fused