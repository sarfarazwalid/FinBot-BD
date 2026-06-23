"""Prompt builder for FinBot BD LLM responses.

Constructs system messages and user prompts that instruct Claude to
answer banking queries using only the retrieved context chunks.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

_BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def _detect_query_language(query: str) -> str:
    """Detect whether a query is Bengali, Banglish, or English.

    Returns:
        ``"bn"`` — if the query contains Bengali Unicode characters,
        ``"en"`` — if it contains only English/Latin characters,
        ``"banglish"`` — if it contains both Bengali and English scripts
             (or neither but has length > 0, treated as English-default).
    """
    has_bengali = bool(_BENGALI_RE.search(query))
    has_english = bool(_LATIN_RE.search(query))

    if has_bengali and has_english:
        return "banglish"
    if has_bengali:
        return "bn"
    return "en"


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = """You are FinBot BD, a banking support assistant for Bangladesh.

Rules:
1. Answer ONLY using the provided context below. Do NOT use outside knowledge.
2. If the context does not contain enough information, say "I don't have enough information to answer that." Do NOT invent banking details.
3. NEVER ask for or request OTP, PIN, password, or any sensitive credentials.
4. Be concise. Provide direct, actionable answers.
5. Match the user's language (Bengali, Banglish, or English) in your response."""


def build_prompt(query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a complete Anthropic-style message payload.

    Args:
        query: The user's original query.
        chunks: Retrieved context chunks. Each chunk must have at least
            ``"text"``, ``"source"``, and ``"score"`` keys.

    Returns:
        A dict with:
            - ``"system"``: system instruction string,
            - ``"user"``: formatted user message string,
            - ``"language"``: detected query language (``"bn"``,
              ``"en"``, or ``"banglish"``).
    """
    language = _detect_query_language(query)

    # Build context block.
    context_parts: List[str] = []
    for i, chunk in enumerate(chunks, start=1):
        text = chunk.get("text", "")
        source = chunk.get("source", "unknown")
        context_parts.append(f"Source: {source}\nContext {i}:\n{text}")

    context_block = "\n\n".join(context_parts) if context_parts else "No relevant context found."

    # Language-specific instruction for the user prompt.
    lang_instructions = {
        "bn": "Answer in Bengali (বাংলা). Use Bengali script.",
        "en": "Answer in English.",
        "banglish": "Answer in Bengali (বাংলা). Use Bengali script.",
    }
    lang_hint = lang_instructions.get(language, "Answer in English.")

    user_message = f"""{context_block}

Question:
{query}

{lang_hint}

Answer:"""

    logger.debug("Built prompt for query %r (language=%s)", query, language)

    return {
        "system": _SYSTEM_INSTRUCTION,
        "user": user_message,
        "language": language,
    }