"""Tests for the evaluation pipeline.

Mocks LLM and retrieval so no real API calls are made.
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from app.evaluation.metrics import (
    answer_relevancy,
    compute_metrics,
    context_precision,
    faithfulness,
)
from app.evaluation.ragas_eval import evaluate_question, load_questions


# ---------------------------------------------------------------------------
# Metrics unit tests
# ---------------------------------------------------------------------------

class TestMetrics:
    def test_faithfulness_perfect(self: TestMetrics) -> None:
        ctx = ["bKash PIN reset dial *247#"]
        ans = "Dial *247# to reset PIN."
        assert faithfulness(ans, ctx) > 0.0

    def test_faithfulness_empty(self: TestMetrics) -> None:
        assert faithfulness("answer", []) == 0.0
        assert faithfulness("", ["ctx"]) == 0.0

    def test_answer_relevancy_perfect(self: TestMetrics) -> None:
        assert answer_relevancy("PIN reset procedure", "How to reset PIN?") >= 0.5

    def test_answer_relevancy_empty(self: TestMetrics) -> None:
        assert answer_relevancy("", "question") == 0.0

    def test_context_precision(self: TestMetrics) -> None:
        ctx = ["PIN reset", "cash out", "balance check"]
        q = "How to reset PIN?"
        score = context_precision(ctx, q)
        assert 0.0 <= score <= 1.0

    def test_compute_metrics_structure(self: TestMetrics) -> None:
        contexts = [{"text": "PIN reset dial *247#"}]
        result = compute_metrics("reset pin", "Dial *247#", contexts)
        assert set(result.keys()) == {"faithfulness", "answer_relevancy", "context_precision"}
        for v in result.values():
            assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

class TestDataset:
    def test_load_questions(self: TestDataset) -> None:
        questions = load_questions()
        assert len(questions) >= 20
        for q in questions:
            assert "id" in q
            assert "question" in q
            assert "ground_truth" in q
            assert "category" in q

    def test_categories(self: TestDataset) -> None:
        questions = load_questions()
        cats = {q["category"] for q in questions}
        assert "bKash" in cats
        assert "Nagad" in cats
        assert "DBBL" in cats


# ---------------------------------------------------------------------------
# evaluate_question (mocked)
# ---------------------------------------------------------------------------

class TestEvaluateQuestion:
    @pytest.fixture(autouse=True)
    def _mock_pipeline(self: TestEvaluateQuestion) -> Any:
        self.mock_hybrid = MagicMock(return_value=[
            {"id": "c1", "text": "PIN reset dial *247#", "source": "bkash_faq", "score": 0.9}
        ])
        self.mock_gen = MagicMock(return_value={
            "answer": "Dial *247#.",
            "sources": ["bkash_faq"],
            "confidence": 0.8,
        })

        with patch("app.evaluation.ragas_eval.hybrid_search", self.mock_hybrid), \
             patch("app.evaluation.ragas_eval.generate_answer", self.mock_gen):
            yield

    def test_evaluate_question_returns_metrics(self: TestEvaluateQuestion) -> None:
        result = evaluate_question("How to reset PIN?")
        assert "metrics" in result
        assert "answer" in result
        assert "sources" in result
        assert result["answer"] == "Dial *247#."
        assert result["sources"] == ["bkash_faq"]

    def test_evaluate_question_calls_hybrid_search(self: TestEvaluateQuestion) -> None:
        evaluate_question("test query", top_k=3)
        self.mock_hybrid.assert_called_once_with("test query", top_k=3)

    def test_evaluate_question_calls_generate_answer(self: TestEvaluateQuestion) -> None:
        evaluate_question("test query")
        args = self.mock_gen.call_args
        assert args[0][0] == "test query"