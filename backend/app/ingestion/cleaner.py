from __future__ import annotations

import html
import logging
import re

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean raw FAQ text while preserving structure and Bengali characters.

    Steps:
    - Normalize Unicode whitespace.
    - Remove excessive spaces.
    - Remove repeated newlines.
    - Strip unwanted symbols while preserving Bengali and common punctuation.
    - Unescape HTML entities.
    - Preserve FAQ separator and labels.

    Args:
        text: Raw input text.

    Returns:
        Cleaned text string.
    """
    if not isinstance(text, str):
        text = str(text)

    text = html.unescape(text)

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)

    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    allowed_symbols = (
        r"!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~"
    )
    text = re.sub(
        rf"[^\w\s\n{re.escape(allowed_symbols)}\u0980-\u09FF]",
        "",
        text,
        flags=re.UNICODE,
    )

    text = re.sub(r"<[^>]+>", "", text)

    text = text.strip()

    return text