from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from .schemas import Chunk

logger = logging.getLogger(__name__)


def _load_chunks(path: Path) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array for chunks")
        return data
    except Exception as exc:
        logger.error("Failed to read chunks from %s: %s", path, exc)
        return []


def _validate_chunk(entry: Dict[str, Any], index: int) -> List[str]:
    problems: List[str] = []
    if not isinstance(entry, dict):
        return [f"Chunk {index} is not a dict"]

    required = ["id", "text", "source", "language", "chunk_index", "created_at"]
    for field in required:
        if field not in entry or entry[field] in (None, ""):
            problems.append(f"Chunk {index} missing or empty '{field}'")

    text = entry.get("text", "")
    if isinstance(text, str) and len(text.strip()) < 20:
        problems.append(f"Chunk {index} has very small text (< 20 chars)")

    return problems


def validate_chunks(chunks_path: str | Path) -> Dict[str, Any]:
    path = Path(chunks_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {path}"}

    entries = _load_chunks(path)
    if not entries:
        return {"status": "error", "message": "No chunks loaded or invalid format"}

    total = len(entries)
    by_source = Counter(str(e.get("source", "")) for e in entries)
    by_language = Counter(str(e.get("language", "")) for e in entries)

    problems: List[str] = []
    seen_ids = set()
    duplicates = 0

    for idx, entry in enumerate(entries):
        chunk_id = entry.get("id")
        if chunk_id:
            if chunk_id in seen_ids:
                duplicates += 1
                problems.append(f"Duplicate chunk id: {chunk_id}")
            seen_ids.add(chunk_id)
        problems.extend(_validate_chunk(entry, idx))

    report = {
        "status": "ok",
        "total_chunks": total,
        "chunks_by_source": dict(by_source),
        "chunks_by_language": dict(by_language),
        "duplicate_chunks": duplicates,
        "problems_found": problems,
    }
    return report