from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import List

from app.core.config import Settings
from .loader import load_documents
from .cleaner import clean_text
from .chunker import create_chunks
from .validator import validate_chunks

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
PROCESSED_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "chunks.json"


def run_pipeline(raw_dir: str | Path = RAW_DIR, output_path: str | Path = PROCESSED_PATH) -> None:
    """Run the full ingestion pipeline.

    Steps:
    1. Load documents
    2. Clean text
    3. Detect language (heuristic)
    4. Create chunks
    5. Validate chunks
    6. Save output

    Args:
        raw_dir: Directory containing raw documents.
        output_path: Path to write chunks.json.
    """
    raw_dir = Path(raw_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    settings = Settings()
    logger.info("Loading documents from %s", raw_dir)
    documents = load_documents(
        raw_dir,
        exclude_patterns=settings.ingestion_exclude_patterns,
    )
    if not documents:
        logger.warning("No documents loaded. Exiting pipeline.")
        return

    logger.info("Loaded %d documents", len(documents))

    cleaned_docs: List = []
    for doc in documents:
        cleaned = clean_text(doc.text)
        cleaned_docs.append(
            type(doc)(text=cleaned, source=doc.source, file_type=doc.file_type)
        )

    logger.info("Cleaned %d documents", len(cleaned_docs))

    all_chunks = []
    for doc in cleaned_docs:
        chunks = create_chunks(doc)
        all_chunks.extend(chunks)

    logger.info("Created %d chunks", len(all_chunks))

    serialized = [chunk.model_dump() if hasattr(chunk, "model_dump") else chunk.dict() for chunk in all_chunks]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)

    logger.info("Saved chunks to %s", output_path)

    report = validate_chunks(output_path)
    logger.info("Validation report: %s", report)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_pipeline()