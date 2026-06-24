"""LLM answer generation using Anthropic Claude."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from app.core.config import Settings
from app.ingestion.cleaner import sanitize_context
from app.llm.prompt_builder import build_prompt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Claude client (lazy singleton)
# ---------------------------------------------------------------------------

_client = None


def _get_client() -> Any:
    """Return a cached Anthropic client, creating it on first call."""
    global _client
    if _client is not None:
        return _client

    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise ImportError(
            "The 'anthropic' package is required. Install it with: "
            "pip install anthropic"
        ) from exc

    settings = Settings()
    api_key = settings.anthropic_api_key

    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file."
        )

    _client = Anthropic(api_key=api_key)
    logger.info("Anthropic client initialised")
    return _client


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_answer(
    query: str,
    context: List[Dict[str, Any]],
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
) -> Dict[str, Any]:
    """Generate an answer using Claude Sonnet.

    Args:
        query: The user's question.
        context: Retrieved chunks from the hybrid search.
        model: Claude model identifier (default: claude-sonnet-4-20250514).
        max_tokens: Maximum tokens in the response.

    Returns:
        A dict with:
            - ``"answer"``: Claude's generated answer string,
            - ``"sources"``: list of unique source identifiers used,
            - ``"confidence"``: estimated confidence float (0.0–1.0).

    Raises:
        RuntimeError: If the Anthropic API key is missing or the API
            call fails.
    """
    if not context:
        return {
            "answer": "I don't have enough information to answer that.",
            "sources": [],
            "confidence": 0.0,
        }

    # Sanitize context before passing to the LLM.
    sanitized_chunks = sanitize_context(context)

    # Build the prompt payload.
    prompt_payload = build_prompt(query, sanitized_chunks)

    # Extract unique sources.
    sources = list(
        {chunk.get("source", "unknown") for chunk in sanitized_chunks}
    )

    try:
        client = _get_client()

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=prompt_payload["system"],
            messages=[
                {
                    "role": "user",
                    "content": prompt_payload["user"],
                }
            ],
        )

        answer_text = ""
        if response.content and len(response.content) > 0:
            block = response.content[0]
            if hasattr(block, "text"):
                answer_text = block.text.strip()

        if not answer_text:
            answer_text = "I don't have enough information to answer that."
            confidence = 0.0
        else:
            # Heuristic confidence: length of answer relative to context.
            # Longer, more detailed answers from rich context → higher.
            confidence = min(1.0, len(answer_text) / 500.0)

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": round(confidence, 3),
        }

    except Exception as exc:
        logger.error("Claude API call failed: %s", exc)
        # Fallback: use sanitized chunks and group by bank.
        sanitized = sanitize_context(context)
        source_texts: dict[str, list[str]] = {}
        seen = set()
        for chunk in sanitized:
            source = chunk.get("source", "unknown")
            text = (chunk.get("text") or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            first_sentence = text.split(".")[0].strip()
            if not first_sentence:
                continue
            source_texts.setdefault(source, []).append(first_sentence)
            if sum(len(v) for v in source_texts.values()) >= 6:
                break

        if source_texts:
            parts: list[str] = []
            for src, sentences in source_texts.items():
                bank_label = src.replace("_", " ").title()
                parts.append(f"{bank_label}:")
                parts.extend(sentences)
            fallback_answer = "\n".join(parts)
        else:
            fallback_answer = "I don't have enough information to answer that."

        return {
            "answer": fallback_answer,
            "sources": sources,
            "confidence": 0.0,
        }
