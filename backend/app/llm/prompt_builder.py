"""Prompt builder for FinBot BD LLM responses.

Constructs system messages and user prompts that instruct the
configured language model to answer banking queries using only
the retrieved context chunks.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")

# Banglish indicators (common Banglish words that suggest mixed intent)
_BANGLISH_INDICATORS = [
    "korbo", "korar", "kore", "korun", "ki", "vabe", "er", "ache",
    "kivabe", "paben", "de", "lagen", "hobe", "asche", "gelo",
]


def _contains_banglish_indicators(text: str) -> bool:
    """Check if the text contains Banglish indicators."""
    lower = text.lower()
    return any(indicator in lower for indicator in _BANGLISH_INDICATORS)


def detect_query_language(query: str) -> str:
    has_bengali = bool(_BENGALI_RE.search(query))
    has_english = bool(_LATIN_RE.search(query))
    has_banglish = _contains_banglish_indicators(query)

    if has_bengali and has_english:
        return "banglish"
    if has_bengali:
        return "bn"
    if has_banglish:
        return "banglish"
    return "en"


_BASE_SYSTEM_INSTRUCTION = """You are FinBot BD, a banking support assistant for Bangladesh.

## Core Rules
1. Answer ONLY using the provided context below. Do NOT use outside knowledge.
2. If the context does not contain enough information, say "I don't have enough information to answer that. Please contact your bank directly."
3. NEVER ask for or request OTP, PIN, password, or any sensitive credentials.
4. Be concise. Provide direct, actionable answers.

## Formatting
- **SYNTHESIZE** information: combine all relevant context entries into one coherent answer. Do NOT repeat the same instruction multiple times just because it appeared in multiple chunks.
- Do NOT copy chunks verbatim. Rewrite everything in natural, fluent language.
- Never output raw context, metadata labels, separators, or document structure.
- Do not prefix your answer with "Answer:", "Response:", or any label.
- If multiple banks are discussed in the context, group by bank with clear headings. If only one bank is relevant, answer only about that bank.
- Remove any redundant or duplicate information before answering.

## Language
{language_rule}
"""

_LANGUAGE_RULES = {
    "en": "Respond ONLY in English.",
    "bn": "Respond ONLY in Bengali (বাংলা). Use Bengali script only.",
    "banglish": "Respond ONLY in natural Banglish (বাংলা + English mixed, as the user wrote). Use a natural mix of Bengali and English. Do NOT use pure English or pure Bengali."
}


def build_prompt(query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a provider-agnostic prompt payload."""
    language = detect_query_language(query)
    context_parts: List[str] = []
    seen_content: set[int] = set()

    for chunk in chunks:
        text = chunk.get("text", "")
        source = chunk.get("source", "unknown")
        fp = hash(text[:120].strip())
        if fp in seen_content:
            continue
        seen_content.add(fp)
        bank_label = source.replace("_faq", "").replace("_", " ").title()
        context_parts.append(f"[{bank_label}]: {text}")

    context_block = "\n\n".join(context_parts) if context_parts else "No relevant context found."

    lang_instructions = {
        "bn": "Answer in Bengali (বাংলা). Use Bengali script only.",
        "en": "Answer in English only.",
        "banglish": "Answer in Banglish (বাংলা + English mixed, as the user wrote). Use a natural mix of Bengali and English. Do NOT use pure English or pure Bengali.",
    }
    lang_hint = lang_instructions.get(language, "Answer in English only.")

    # Compose the system instruction with the language rule
    system_instruction = _BASE_SYSTEM_INSTRUCTION.format(language_rule=_LANGUAGE_RULES[language])

    user_message = f"{context_block}\n\nQuestion:\n{query}\n\n{lang_hint}\n\nAnswer:"

    logger.debug("Built prompt for query %r (language=%s)", query, language)

    return {
        "system": system_instruction,
        "user": user_message,
        "language": language,
    }