"""RAG evaluation metrics.

Computes Faithfulness, Answer Relevancy, and Context Precision
using lightweight heuristics (no heavy ragas dependency required).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9\u0980-\u09FF]+", text.lower()))


def faithfulness(answer: str, contexts: List[str]) -> float:
    """Calculate faithfulness using a context–answer token overlap heuristic.

    RAG-inspired heuristic metric that measures whether the generated
    answer is supported by the retrieved context.
    """
    if not answer or not contexts:
        return 0.0
    answer_tokens = _tokenize(answer)
    context_tokens = set()
    for c in contexts:
        context_tokens |= _tokenize(c)
    if not answer_tokens:
        return 1.0
    return len(answer_tokens & context_tokens) / len(answer_tokens)


def answer_relevancy(answer: str, question: str) -> float:
    """Calculate answer relevancy using a question–answer token overlap heuristic.

    RAG-inspired heuristic metric that measures whether the generated
    answer addresses the user's original question.
    """
    if not answer or not question:
        return 0.0
    q_tokens = _tokenize(question)
    a_tokens = _tokenize(answer)
    if not q_tokens:
        return 1.0
    return len(q_tokens & a_tokens) / len(q_tokens)


def context_precision(contexts: List[str], question: str) -> float:
    """Calculate context precision using token overlap with the question.

    RAG-inspired heuristic metric that measures whether the retrieved
    chunks are useful for producing the final answer.
    """
    if not contexts or not question:
        return 0.0
    q_tokens = _tokenize(question)
    scores = []
    for ctx in contexts:
        ctx_tokens = _tokenize(ctx)
        if q_tokens:
            scores.append(len(q_tokens & ctx_tokens) / len(q_tokens))
    return sum(scores) / len(scores) if scores else 0.0


def compute_metrics(
    question: str,
    answer: str,
    contexts: List[Dict[str, Any]],
) -> Dict[str, float]:
    context_texts = [c.get("text", "") for c in contexts if isinstance(c, dict)]
    return {
        "faithfulness": round(faithfulness(answer, context_texts), 4),
        "answer_relevancy": round(answer_relevancy(answer, question), 4),
        "context_precision": round(context_precision(context_texts, question), 4),
    }