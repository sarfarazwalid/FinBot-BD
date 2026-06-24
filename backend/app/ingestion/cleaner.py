"""Context sanitization for retrieved chunks.

Strips metadata labels (Question:, Answer:, Category:, Language:, ==== separators)
from chunk text so that only the clean answer content is sent to the LLM.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

_METADATA_LINE = re.compile(
    r"^(Question:|Answer:|Category:|Language:|={2,})",
    re.MULTILINE,
)

_SEPARATOR_LINE = re.compile(r"^-{3,}|={3,}", re.MULTILINE)

_ANSWER_LINE = re.compile(r"^Answer:\s*", re.MULTILINE)

_LABEL_AND_VALUE = re.compile(
    r"(?:Question|Category|Language):[^\n]*\n?", re.MULTILINE
)


def sanitize_chunk_text(text: str) -> str:
    """Extract only the answer content from a FAQ chunk.

    If the chunk contains an ``Answer:`` line, returns everything after
    ``Answer:`` up to the next label or separator.  Otherwise falls back
    to stripping all metadata lines (``Question:``, ``Category:``,
    ``Language:``, ``====``) and returning what remains.
    """
    # Strategy 1: extract text after Answer: line
    answer_match = _ANSWER_LINE.split(text, maxsplit=1)
    if len(answer_match) == 2:
        after_answer = answer_match[1]
        # Cut off at the next label or separator
        cut = re.split(r"\n(?:Question|Category|Language):|=+", after_answer, maxsplit=1)[0]
        cleaned = cut.strip()
        if cleaned:
            return cleaned

    # Strategy 2: strip all metadata labels
    cleaned = _LABEL_AND_VALUE.sub("", text)
    cleaned = _SEPARATOR_LINE.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def sanitize_context(
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a new list of chunks with sanitized ``text`` fields.

    Each chunk dict is copied and its ``text`` key is replaced with the
    cleaned version.  Other fields (``source``, ``score``, …) are left
    untouched.
    """
    sanitized: List[Dict[str, Any]] = []
    for chunk in chunks:
        c = dict(chunk)
        c["text"] = sanitize_chunk_text(c.get("text", ""))
        sanitized.append(c)
    return sanitized