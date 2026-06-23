"""RAG evaluation pipeline.

Usage:
    python -m app.evaluation.ragas_eval

Loads questions from ``data/evaluation/questions.json``, runs the hybrid
search + generation pipeline, computes metrics, and writes
``evaluation_results.json``.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import Settings
from app.evaluation.metrics import compute_metrics
from app.llm.generator import generate_answer
from app.retrieval.hybrid_search import search as hybrid_search

logger = logging.getLogger(__name__)

QUESTIONS_PATH = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "questions.json"
OUTPUT_PATH = Path(__file__).resolve().parents[2] / "evaluation_results.json"


def load_questions(path: Path = QUESTIONS_PATH) -> List[Dict[str, Any]]:
    """Load the evaluation question dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Questions file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_question(question: str, top_k: int = 5) -> Dict[str, Any]:
    """Run a single question through the pipeline and compute metrics."""
    retrieved = hybrid_search(question, top_k=top_k)
    gen_result = generate_answer(question, retrieved)
    metrics = compute_metrics(question, gen_result["answer"], retrieved)
    return {
        "question": question,
        "answer": gen_result["answer"],
        "sources": gen_result["sources"],
        "confidence": gen_result["confidence"],
        "metrics": metrics,
        "retrieved_count": len(retrieved),
    }


def run_evaluation() -> None:
    """Run the full evaluation suite and write results."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    settings = Settings()
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY is not set. Evaluation requires Claude.")
        sys.exit(1)

    questions = load_questions()
    logger.info("Starting FinBot BD RAG Evaluation")
    logger.info("Questions: %d", len(questions))

    results: List[Dict[str, Any]] = []
    for entry in questions:
        q = entry.get("question", "")
        if not q:
            continue
        result = evaluate_question(q, top_k=settings.top_k)
        result["ground_truth"] = entry.get("ground_truth", "")
        result["category"] = entry.get("category", "unknown")
        results.append(result)

    # Aggregate metrics across all questions.
    n = len(results)
    if n > 0:
        agg = {
            "faithfulness": round(sum(r["metrics"]["faithfulness"] for r in results) / n, 4),
            "answer_relevancy": round(sum(r["metrics"]["answer_relevancy"] for r in results) / n, 4),
            "context_precision": round(sum(r["metrics"]["context_precision"] for r in results) / n, 4),
        }
    else:
        agg = {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0}

    report = {
        "questions_evaluated": n,
        "aggregated_metrics": agg,
        "results": results,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info("Evaluation completed. Results saved to %s", OUTPUT_PATH)
    logger.info("=" * 50)
    logger.info("FinBot BD RAG Evaluation")
    logger.info("=" * 50)
    logger.info("Questions: %d", n)
    logger.info("Faithfulness: %s", agg["faithfulness"])
    logger.info("Answer Relevancy: %s", agg["answer_relevancy"])
    logger.info("Context Precision: %s", agg["context_precision"])
    logger.info("=" * 50)


if __name__ == "__main__":
    run_evaluation()