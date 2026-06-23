from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from .schemas import Document

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".json"}

# Files to exclude regardless of extension (matched by stem).
# Prevents README.md, README.txt, README.rst, etc. from being ingested.
EXCLUDED_FILES = frozenset({
    "README",
    "README_TEMPLATE",
})

# Directories to skip entirely (parent directory name check).
EXCLUDED_DIRS = frozenset({
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    "__MACOSX",
})


def _is_excluded(file_path: Path, exclude_patterns: List[str]) -> bool:
    name = file_path.name
    stem = file_path.stem
    suffix = file_path.suffix.lower()

    # Exclude hidden files (starting with ".")
    if name.startswith("."):
        return True

    # Exclude temporary editor files (starting with "~")
    if name.startswith("~"):
        return True

    # Exclude files inside excluded directories
    for part in file_path.parts:
        if part in EXCLUDED_DIRS:
            return True

    # Exclude by stem (e.g. "README" matches README.md, README.txt, etc.)
    if stem in EXCLUDED_FILES:
        return True

    # Exclude by explicit user-provided patterns (from config)
    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if suffix == pattern[1:].lower():
                return True
        else:
            if name == pattern or stem == pattern:
                return True

    return False


def load_documents(
    directory_path: str | Path,
    exclude_patterns: List[str] | None = None,
    supported_extensions: set[str] | None = None,
) -> List[Document]:
    """Load all supported documents from a directory recursively.

    Args:
        directory_path: Path to the directory containing raw documents.
        exclude_patterns: Filename or extension patterns to skip.
        supported_extensions: Allowed file extensions.

    Returns:
        List of Document objects with text, source, and file_type.

    Raises:
        No exceptions are raised; corrupted files are skipped with a warning.
    """
    docs: List[Document] = []
    root = Path(directory_path)
    if exclude_patterns is None:
        exclude_patterns = []
    if supported_extensions is None:
        supported_extensions = SUPPORTED_EXTENSIONS

    if not root.exists() or not root.is_dir():
        logger.warning("Directory not found or not a directory: %s", directory_path)
        return docs

    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, exclude_patterns):
            logger.debug("Excluding file: %s", file_path)
            continue
        if file_path.suffix.lower() not in supported_extensions:
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
            if not text.strip():
                logger.warning("Skipping empty file: %s", file_path)
                continue
            docs.append(
                Document(
                    text=text,
                    source=file_path.name,
                    file_type=file_path.suffix.lower(),
                )
            )
        except Exception as exc:
            logger.error("Failed to read file %s: %s", file_path, exc)

    return docs