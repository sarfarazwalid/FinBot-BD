from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List

from .schemas import Document, Chunk

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def _detect_language(text: str) -> str:
    """Heuristic language detection for Bengali/English/Banglish text.

    Rules:
    - If Bengali characters > 40% of total characters -> bn
    - If Bengali characters > 10% and English characters exist -> mixed
    - Otherwise -> en

    Args:
        text: Input text.

    Returns:
        One of: 'bn', 'en', 'mixed'.
    """
    if not text:
        return "en"

    bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))
    english_chars = len(re.findall(r"[A-Za-z]", text))
    total_chars = len(text)

    if total_chars == 0:
        return "en"

    bengali_ratio = bengali_chars / total_chars
    english_ratio = english_chars / total_chars

    if bengali_ratio > 0.40:
        return "bn"
    if bengali_ratio > 0.10 and english_ratio > 0:
        return "mixed"
    return "en"


def _build_chunk_id(source_name: str, chunk_index: int) -> str:
    """Build a deterministic chunk identifier.

    Example: bkash_faq.txt -> bkash_faq_001_0
    """
    base = Path(source_name).stem
    base = re.sub(r"[^a-zA-Z0-9_-]", "_", base)
    return f"{base}_{chunk_index:03d}_{chunk_index}"


def create_chunks(document: Document) -> List[Chunk]:
    """Split a document into overlapping chunks.

    Args:
        document: Loaded document.

    Returns:
        List of Chunk instances.
    """
    text = document.text
    if not text:
        return []

    chunks: List[Chunk] = []
    start = 0
    index = 0
    length = len(text)

    while start < length:
        end = min(start + CHUNK_SIZE, length)
        chunk_text = text[start:end]

        language = _detect_language(chunk_text)
        source = Path(document.source).stem
        chunk_id = f"{source}_{index:03d}_{index}"
        created_at = datetime.utcnow().isoformat() + "Z"

        chunks.append(
            Chunk(
                id=chunk_id,
                text=chunk_text,
                source=source,
                language=language,
                chunk_index=index,
                created_at=created_at,
            )
        )
        index += 1
        start = end - CHUNK_OVERLAP if end < length else length

    return chunks