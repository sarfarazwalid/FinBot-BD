"""Query rewriting module for improved recall.

Expands queries with domain-specific synonyms and normalisations
for Bengali banking terminology before they are sent to the
BM25 / semantic retrievers.
"""

from __future__ import annotations

import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain-specific expansion dictionary
# ---------------------------------------------------------------------------
# Maps a trigger word (lowercase) to a list of expansion tokens that
# will be appended to the query.
#
# The expansions are chosen to bridge the gap between Banglish, Bengali,
# and English variants that banking FAQ questions use.

_EXPANSIONS: dict[str, List[str]] = {
    # bKash
    "bkash": ["bkash", "bKash"],
    "bKash": ["bkash", "bKash"],
    # DBBL (Dutch-Bangla Bank)
    "dbbl": ["dbbl", "dutch bangla bank"],
    "dutch": ["dbbl", "dutch bangla bank"],
    # Nagad
    "nagad": ["nagad"],
    # PIN
    "pin": ["pin", "password", "reset pin", "forgot pin"],
    # OTP
    "otp": ["otp", "one time password", "verification code"],
    # card
    "card": ["card", "debit card", "credit card", "atm card"],
    # transaction
    "transaction": ["transaction", "transfer", "payment", "send money"],
    "transfer": ["transaction", "transfer", "send money"],
    # account
    "account": ["account", "account"],
    "acc": ["account", "acc"],
    # block
    "block": ["block", "blocked", "deactivate", "freeze"],
    "blocked": ["block", "blocked", "deactivate"],
    # unblock / activate
    "unblock": ["unblock", "activate", "reactivate"],
    # forgot
    "forgot": ["forgot", "reset", "recover", "lost"],
    "vule": ["vule", "forgot", "lost"],
    "vulegechi": ["vule", "forgot", "lost", "gechi"],
    # how to / kivabe
    "kivabe": ["kivabe", "how to", "how do i"],
    # help
    "help": ["help", "how", "support", "guide"],
    "how": ["how", "how to", "how do i"],
    # money / taka
    "taka": ["taka", "money", "cash"],
    "money": ["money", "taka", "cash"],
    "cash": ["cash", "taka", "money"],
    # balance
    "balance": ["balance", "balance check"],
    "check": ["check", "balance check", "how much"],
    # limit
    "limit": ["limit", "maximum", "daily limit"],
    # register
    "register": ["register", "open", "create", "sign up"],
    "open": ["register", "open", "create", "sign up account"],
    "create": ["register", "open", "create", "sign up"],
    # recharge
    "recharge": ["recharge", "top up", "add money"],
    "top": ["top up", "recharge", "add money"],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rewrite_query(query: str) -> str:
    """Expand a user query with domain-specific synonyms.

    Steps:
        1. Lowercase the query.
        2. For each word present as a key in ``_EXPANSIONS``, append the
           expansion terms.
        3. Return the original query concatenated with all expansion
           tokens.

    Args:
        query: Raw user query.

    Returns:
        Expanded query string.

    Example:
        >>> rewrite_query("DBBL card blocked korbo ki kore?")
        'DBBL card blocked korbo ki kore? dbbl dutch bangla bank card debit card credit card atm card block blocked deactivate freeze'
    """
    if not query.strip():
        return query

    expansions: List[str] = []
    lower = query.lower()
    words = lower.split()

    for word in words:
        # Remove trailing punctuation for matching.
        clean_word = word.strip(".,!?;:")
        if clean_word in _EXPANSIONS:
            expansions.extend(_EXPANSIONS[clean_word])

    # Deduplicate while preserving order.
    seen = set()
    unique_expansions: List[str] = []
    for tok in expansions:
        if tok not in seen:
            seen.add(tok)
            unique_expansions.append(tok)

    if unique_expansions:
        expanded = f"{query} {' '.join(unique_expansions)}"
        logger.debug(
            "Query expanded: %r -> %r", query, expanded,
        )
        return expanded

    return query