"""Tests for the hybrid retrieval system.

Verifies:
1. BM25 returns results with correct structure.
2. Semantic (Pinecone) returns results with correct structure.
3. RRF deduplicates and fuses results correctly.
4. Hybrid search returns top-k documents.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import pytest

from app.retrieval.bm25 import bm25_search
from app.retrieval.hybrid_search import search as hybrid_search
from app.retrieval.query_rewriter import rewrite_query
from app.retrieval.rrf import fuse_results
from app.retrieval.vector_store import semantic_search

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Query rewriting
# ---------------------------------------------------------------------------

class TestQueryRewriter:
    def test_empty_query(self: TestQueryRewriter) -> None:
        assert rewrite_query("") == ""

    def test_no_expansion_needed(self: TestQueryRewriter) -> None:
        result = rewrite_query("How do I reset my PIN?")
        # "How" and "PIN" trigger expansions.
        assert "reset" in result
        assert "forgot" in result

    def test_banglish_expansion(self: TestQueryRewriter) -> None:
        result = rewrite_query("amar bKash pin vule gechi")
        # "bKash" → "bkash", "pin" → ..., "vule" → ..., "gechi" in "vulegechi" match
        assert "bkash" in result
        assert "forgot" in result

    def test_dbbl_card_blocked(self: TestQueryRewriter) -> None:
        result = rewrite_query("DBBL card blocked korbo ki kore?")
        assert "dbbl" in result
        assert "dutch bangla bank" in result
        assert "block" in result
        assert "deactivate" in result


# ---------------------------------------------------------------------------
# BM25 retrieval
# ---------------------------------------------------------------------------

class TestBM25:
    def test_bm25_returns_results(self: TestBM25) -> None:
        """BM25 should return at least some results for a banking query."""
        results = bm25_search("how to create bkash account", top_k=5)
        assert isinstance(results, list)
        assert len(results) > 0
        # Verify structure.
        for r in results:
            assert "id" in r
            assert "text" in r
            assert "source" in r
            assert "language" in r
            assert "score" in r

    def test_bm25_top_k(self: TestBM25) -> None:
        results = bm25_search("bkash pin reset", top_k=3)
        assert len(results) <= 3

    def test_bm25_bengali_query(self: TestBM25) -> None:
        """Bengali queries should now produce BM25 results with the new tokenizer."""
        results = bm25_search("আমার নগদ PIN ভুলে গেছি", top_k=5)
        assert len(results) > 0, "Bengali query should return BM25 results"
        for r in results:
            assert "id" in r
            assert "text" in r
            assert "score" in r
            assert r["score"] > 0.0

    def test_bm25_empty_query(self: TestBM25) -> None:
        """An empty or punctuation-only query should produce no results."""
        results = bm25_search("???", top_k=5)
        assert results == []


# ---------------------------------------------------------------------------
# Semantic (Pinecone) retrieval
# ---------------------------------------------------------------------------

class TestSemantic:
    def test_semantic_returns_results(self: TestSemantic) -> None:
        """Semantic search should return results for a banking query."""
        results = semantic_search("amar bKash pin vule gechi", top_k=5)
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "id" in r
            assert "text" in r
            assert "source" in r
            assert "language" in r
            assert "score" in r
            assert isinstance(r["score"], float)

    def test_semantic_top_k(self: TestSemantic) -> None:
        results = semantic_search("How do I reset my PIN?", top_k=3)
        assert len(results) <= 3

    def test_semantic_source_set(self: TestSemantic) -> None:
        """Results should come from one of the three known sources."""
        results = semantic_search("bkash account", top_k=10)
        sources = {r["source"] for r in results}
        assert sources.issubset({"bkash_faq", "dbbl_faq", "nagad_faq"})


# ---------------------------------------------------------------------------
# RRF fusion
# ---------------------------------------------------------------------------

class TestRRF:
    def test_fuse_deduplicates(self: TestRRF) -> None:
        """If both lists contain the same doc, it should appear once."""
        list_a = [
            {"id": "doc1", "text": "A", "source": "s1", "language": "en", "score": 10.0},
            {"id": "doc2", "text": "B", "source": "s1", "language": "en", "score": 5.0},
        ]
        list_b = [
            {"id": "doc2", "text": "B", "source": "s1", "language": "en", "score": 8.0},
            {"id": "doc3", "text": "C", "source": "s1", "language": "en", "score": 3.0},
        ]
        fused = fuse_results(list_a, list_b, top_k=5)
        ids = [d["id"] for d in fused]
        assert ids == ["doc2", "doc1", "doc3"]  # doc2 has best RRF score

    def test_fuse_top_k(self: TestRRF) -> None:
        """Should respect top_k limit."""
        list_a = [{"id": f"doc{i}", "text": str(i), "source": "s", "language": "en", "score": 1.0} for i in range(10)]
        fused = fuse_results(list_a, top_k=3)
        assert len(fused) == 3

    def test_fuse_empty(self: TestRRF) -> None:
        assert fuse_results([], []) == []


# ---------------------------------------------------------------------------
# Hybrid search end-to-end
# ---------------------------------------------------------------------------

class TestHybridSearch:
    def test_hybrid_returns_results(self: TestHybridSearch) -> None:
        """Hybrid search should return fused results."""
        results = hybrid_search("amar bKash pin vule gechi", top_k=5)
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "id" in r
            assert "text" in r
            assert "source" in r
            assert "language" in r
            assert "score" in r

    def test_hybrid_no_duplicate_ids(self: TestHybridSearch) -> None:
        """Fused results should not have duplicate IDs."""
        results = hybrid_search("How do I reset my bKash PIN?", top_k=5)
        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids))

    def test_hybrid_top_k_respected(self: TestHybridSearch) -> None:
        results = hybrid_search("bkash account", top_k=3)
        assert len(results) <= 3

    def test_hybrid_varied_query(self: TestHybridSearch) -> None:
        """Different languages/scripts should all produce results."""
        for q in [
            "How do I reset my PIN?",
            "আমার একাউন্ট ব্লক হয়েছে",
            "amar pin vule gechi",
            "DBBL card blocked",
        ]:
            results = hybrid_search(q, top_k=5)
            assert len(results) > 0, f"Query {q!r} returned no results"