
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

# Distinctive Banglish words — Bengali words commonly written in Roman script,
# used to detect Romanized Bengali (Banglish) text that contains 0 Unicode
# Bengali characters but is not pure English.
_BANGLISH_WORDS = frozenset({
    # Pronouns
    'amar', 'amake',
    'tumi', 'ami', 'amra', 'tomra', 'tui', 'apni', 'apnar', 'apnake', 'apner',
    'tara', 'ora', 'tader', 'oder',
    'she', 'tah', 'tate', 'tai',
    'ki', 'kicchu', 'kichu',
    # Common verbs (present/continuous/perfect stems)
    'korte', 'kore', 'koren', 'koreche', 'korechen', 'korbe', 'korben',
    'hobe', 'hoye', 'hoyeche', 'hote', 'hole', 'holo', 'hocche', 'hoini', 'hoy',
    'ache', 'ache', 'chai', 'chaite', 'chole', 'cholche', 'cholbe', 'chilo',
    'geche', 'gechi', 'gechen', 'gelen', 'gelo', 'gelam', 'giye',
    'eshe', 'ese', 'esechen', 'eseche',
    'niyeche', 'niyechen', 'niyechi', 'niye',
    'theke', 'diye', 'niye', 'dhore',
    'bujhi', 'bujhte', 'bollo', 'bolche', 'bolbe', 'bolte', 'bole', 'bollen', 'bolte',
    'dite', 'dibe', 'diben', 'dewa', 'debe',
    'jani', 'jante', 'janen', 'jan', 'janben', 'janbe',
    'pari', 'paro', 'parbe', 'parben', 'pabe', 'paben', 'pawa', 'pai',
    'gele', 'giye', 'jai', 'jabe', 'jaben', 'jete',
    'ashbe', 'ashche', 'ashe', 'ashte', 'asben', 'ash', 'ashen',
    'dekh', 'dekhbe', 'dekhben', 'dekhte', 'dekhche', 'dekhabe', 'dekhbo',
    'rakh', 'rakhte', 'rakhbe', 'rakhben', 'rakhe', 'rakhi', 'rakhbo',
    'chara', 'char', 'chare',
    'nibo', 'nibe', 'niben', 'ni', 'nichi', 'nilo', 'nilam', 'nil',
    # Common modifiers / particles
    'taka', 'tk', 'jonno', 'karon', 'kono', 'onek', 'khub', 'beshi', 'kom',
    'kintu', 'tobe', 'jodi', 'tahole', 'tai', 'shei', 'ei', 'oi',
    'egulo', 'ogulo', 'jegulo', 'jeta', 'jate', 'jokhon', 'tokhon',
    'kivabe', 'koto', 'keno', 'kobe', 'kokhon', 'kotha',
    'niche', 'upor', 'majhe', 'pashe', 'samne', 'pichone',
    'vitor', 'bahire', 'bhitore', 'baire',
    'shomoy', 'somoy', 'dorkar', 'lomba', 'choto', 'boro',
    # Additional common Banglish words found in FAQ data
    'jodi', 'ta', 'kokeo', 'keu', 'kar', 'kake', 'tobe',
    'bhalo', 'kharap', 'thik', 'thake', 'thakbe', 'thakben',
    'paben', 'pabe', 'paro', 'parbo',
    'bol', 'bolben', 'bolbe',
    'bujhi', 'bujhe', 'bujhiye',
    'diben', 'dibe', 'dite', 'diyechi',
    'niye', 'niyechi', 'niyechi', 'niyechen',
    'theke', 'thekeo', 'thekei',
    'rekhe', 'rekhechi', 'rekhechen',
    'mone', 'mone', 'monei',
    'dhar', 'dhara', 'dhare', 'dhare',
    'sadharon', 'sadharonoto', 'proyojon',
    'bartaman', 'bartamane', 'notun', 'purono',
})

_BANGLISH_REGEX = re.compile(
    r'\b(?:' + '|'.join(re.escape(w) for w in _BANGLISH_WORDS) + r')\b',
    re.IGNORECASE,
)


def _count_banglish_words(text: str) -> int:
    """Return the number of distinct Banglish word occurrences in *text*."""
    return len(_BANGLISH_REGEX.findall(text))


def _detect_language(text: str) -> str:
    """Script-aware language detection for Bengali/English/Banglish text.

    Detection counts only meaningful letters (Bengali Unicode + English Latin)
    and applies the following rules:

    1. If **no** Bengali characters **and no** English characters → ``"en"``
    2. If Bengali characters > English characters × 2 → ``"bn"``
    3. If **both** Bengali and English characters exist → ``"mixed"``
    4. If Bengali characters > 0 (but no English) → ``"bn"``
    5. If **no** Bengali characters **but** English characters exist →
       consult Banglish word list. ≥ 2 matches → ``"mixed"``, else ``"en"``

    Args:
        text: Input text.

    Returns:
        One of ``'bn'``, ``'en'``, ``'mixed'``.
    """
    if not text:
        return "en"

    bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))
    english_chars = len(re.findall(r"[A-Za-z]", text))

    # Rule 1 — no Bengali or English letters at all (numbers, punctuation, spaces only)
    if bengali_chars == 0 and english_chars == 0:
        return "en"

    # Rule 2 — Bengali heavily dominates English → Bengali
    if bengali_chars > english_chars * 2:
        return "bn"

    # Rule 3 — both scripts present and not dominated by Bengali → mixed
    if bengali_chars > 0 and english_chars > 0:
        return "mixed"

    # Rule 4 — Bengali only (no English letters) → Bengali
    if bengali_chars > 0:
        return "bn"

    # Rule 5 — English letters only → check for Banglish
    if bengali_chars == 0 and english_chars > 0:
        banglish_count = _count_banglish_words(text)
        if banglish_count >= 2:
            return "mixed"
        return "en"

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