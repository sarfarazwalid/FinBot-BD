"""Fine-grained intent detection for banking queries.

Detects specific user intents such as:
- send_money, cash_in, cash_out, add_money
- mobile_recharge, payment, bank_transfer
- pin_reset, check_balance, mini_statement
- loan, account_opening, fd_creation
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Intent definitions with keywords and anti-keywords
_INTENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "send_money": {
        "keywords": {
            "send", "pathano", "pathabo", "pathai", "transfer", "send money",
            "taka pathabo", "taka pathano", "parcel", "someone", "okhane",
            "otake", "onno", "arek", "arekjon", "arekta", "diger",
        },
        "anti_keywords": {
            "cash in", "cash in kore", "cashout", "cash out", "nijer",
            "ager", "previous", "history", "receipt", "statement",
        },
        "topics": {"send_money", "money_transfer", "payment"},
    },
    "cash_in": {
        "keywords": {
            "cash in", "cash in kore", "cash in korbo", "cash in kivabe",
            "add money", "joma", "joma korbo", "joma kore",
            "nijer account", "aje", "upor", "boshe",
        },
        "anti_keywords": {
            "send", "pathano", "pathabo", "cash out", "withdraw",
            "ber kore", "barikore", "loan", "emi",
        },
        "topics": {"cash_in", "add_money"},
    },
    "cash_out": {
        "keywords": {
            "cash out", "cashout", "cash out kore", "cash out korbo",
            "cash out kivabe", "withdraw", "taka ber", "taka barabe",
            "nika", "bera", "ber kore", "barikore", "agen",
        },
        "anti_keywords": {
            "cash in", "send", "pathabo", "pathano", "joma",
            "add money", "loan", "emi", "fd", "fixed deposit",
        },
        "topics": {"cash_out", "withdrawal"},
    },
    "mobile_recharge": {
        "keywords": {
            "recharge", "mobile recharge", "phone recharge", "topup",
            "top up", "balance recharge", "amar phone", "amar number",
            "sim", "sim recharge", "data pack", "internet pack",
            "minutes", "call package",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "payment", "bill",
        },
        "topics": {"mobile_recharge", "recharge"},
    },
    "payment": {
        "keywords": {
            "payment", "pay bill", "bill pay", "pay kore", "pay korbo",
            "dana", "khat", "katham", "vservice", "utility bill",
            "electric bill", "gas bill", "water bill", "internet bill",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "recharge", "mobile",
            "loan", "fd", "account opening",
        },
        "topics": {"payment", "bill_payment"},
    },
    "bank_transfer": {
        "keywords": {
            "bank transfer", "bank e transfer", "bank theke", "bank to bank",
            "account transfer", "NPSB", "BEFTN", "RTGS", "IFT",
            "another bank", "onno bank", "arek bank",
        },
        "anti_keywords": {
            "send money", "cash in", "cash out", "mobile", "recharge",
        },
        "topics": {"bank_transfer", "npsb", "beftn", "rtgs"},
    },
    "pin_reset": {
        "keywords": {
            "pin reset", "pin change", "change pin", "reset pin",
            "pin forgotten", "pin bhule", "pin change kore",
            "pin reset kore", "pin reset kivabe", "pin change kivabe",
            "forgot pin", "pin recovery", "new pin",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "recharge",
            "account opening", "loan", "balance",
        },
        "topics": {"pin_reset", "pin_change"},
    },
    "check_balance": {
        "keywords": {
            "balance", "check balance", "balance check", "amar balance",
            "koto taka", "koto ache", "bank balance", "account balance",
            "baki", "bakii", "taka ache", "amount",
        },
        "anti_keywords": {
            "send", "cash out", "cash in", "recharge", "payment",
            "loan", "emi", "fd", "statement",
        },
        "topics": {"check_balance", "balance_inquiry"},
    },
    "mini_statement": {
        "keywords": {
            "mini statement", "statement", "transaction history",
            "last transaction", "recent transaction", "kotojon",
            "kivabe kore", "history", "log", "activity",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "recharge",
            "loan", "emi", "balance", "pin",
        },
        "topics": {"mini_statement", "transaction_history"},
    },
    "loan": {
        "keywords": {
            "loan", "loan neber", "loan nei", "loan korbo", "loan kivabe",
            "borrow", "borrowing", "emi", "monthly payment",
            "loan interest", "loan rate", "personal loan",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "recharge",
            "pin", "balance", "fd", "account opening",
        },
        "topics": {"loan", "personal_loan", "emi"},
    },
    "account_opening": {
        "keywords": {
            "account open", "new account", "account khulbo", "account khule",
            "account khola", "open account", "account opening",
            "notun account", "new customer", "registration",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "recharge",
            "pin", "loan", "fd", "balance",
        },
        "topics": {"account_opening", "onboarding"},
    },
    "fd_creation": {
        "keywords": {
            "fd", "fixed deposit", "fd khulbo", "fd korbo",
            "deposit", "term deposit", "mutual fund",
            "investment", "save money", "saving",
        },
        "anti_keywords": {
            "send money", "cash out", "cash in", "recharge",
            "loan", "emi", "pin", "balance",
        },
        "topics": {"fd", "fixed_deposit", "investment"},
    },
}


def detect_intent(query: str) -> tuple[str, float]:
    """Detect the most likely intent from the query.

    Returns:
        Tuple of (intent_name, confidence_score)
    """
    if not query or not query.strip():
        return "general", 0.5

    query_lower = query.lower()
    query_words = set(re.findall(r"\b\w+\b", query_lower))

    best_intent = "general"
    best_score = 0.0

    # Also check for explicit intent declarations
    explicit_match = re.search(r"(?:ami|aami)\s+(\w+)\s+(?:korte|korbo|kori|chai)", query_lower)
    if explicit_match:
        action = explicit_match.group(1)
        intent_map = {
            "send": "send_money", "pathabo": "send_money", "pathano": "send_money",
            "cash": "cash_in", "joma": "cash_in",
            "withdraw": "cash_out", "nika": "cash_out",
            "recharge": "mobile_recharge",
            "pay": "payment", "payment": "payment",
            "transfer": "bank_transfer",
            "pin": "pin_reset", "change": "pin_reset",
            "balance": "check_balance", "check": "check_balance",
            "statement": "mini_statement",
            "loan": "loan", "emi": "loan",
            "open": "account_opening", "account": "account_opening",
            "fd": "fd_creation", "deposit": "fd_creation",
        }
        if action in intent_map:
            return intent_map[action], 0.9

    # Score each intent
    for intent_name, config in _INTENT_CONFIG.items():
        keywords = config["keywords"]
        anti_keywords = config["anti_keywords"]

        # Count keyword matches
        keyword_hits = sum(1 for kw in keywords if kw in query_lower or kw in query_words)
        anti_hits = sum(1 for akw in anti_keywords if akw in query_lower or akw in query_words)

        # Calculate raw score
        if keyword_hits == 0:
            continue

        # Base score from keyword hits
        raw_score = keyword_hits / max(1, len(keywords) * 0.3)

        # Penalize anti-keywords
        anti_penalty = anti_hits * 0.3

        # Final score
        score = max(0.0, raw_score - anti_penalty)

        if score > best_score:
            best_score = score
            best_intent = intent_name

    # Normalize score to 0-1 range
    if best_score > 0.5:
        confidence = min(1.0, best_score)
    elif best_score > 0.2:
        confidence = best_score * 0.8
    else:
        confidence = 0.3
        best_intent = "general"

    logger.info(
        "Intent detection: query=%r -> intent=%s (confidence=%.2f)",
        query[:50], best_intent, confidence,
    )

    return best_intent, confidence


def get_intent_related_topics(intent: str) -> Set[str]:
    """Get the set of topics related to a detected intent."""
    if intent not in _INTENT_CONFIG:
        return set()
    return _INTENT_CONFIG[intent]["topics"]


def get_intent_anti_topics(intent: str) -> Set[str]:
    """Get the set of topics that should be excluded for a detected intent."""
    if intent not in _INTENT_CONFIG:
        return set()
    anti_kw = _INTENT_CONFIG[intent]["anti_keywords"]
    # Map anti-keywords to topics
    anti_topics = set()
    for akw in anti_kw:
        if akw in {"cash in", "cash_in"}:
            anti_topics.add("cash_in")
        if akw in {"cash out", "cash_out"}:
            anti_topics.add("cash_out")
        if akw in {"send", "send money"}:
            anti_topics.add("send_money")
        if akw in {"recharge"}:
            anti_topics.add("mobile_recharge")
        if akw in {"payment", "bill"}:
            anti_topics.add("payment")
        if akw in {"loan", "emi"}:
            anti_topics.add("loan")
        if akw in {"pin"}:
            anti_topics.add("pin_reset")
        if akw in {"balance"}:
            anti_topics.add("check_balance")
        if akw in {"fd", "fixed deposit"}:
            anti_topics.add("fd")
        if akw in {"account opening"}:
            anti_topics.add("account_opening")
    return anti_topics
