"""Ambiguity detection for banking queries."""

import re
from typing import Tuple, Optional, List, Dict

# Ambiguous intent phrases (case-insensitive)
_AMBIGUOUS_INTENTS = [
    "pin reset",
    "forgot pin",
    "change pin",
    "cash out",
    "cash out fee",
    "cash out charge",
    "send money",
    "money transfer",
    "add money",
    "cash in",
    "account open",
    "open account",
    "registration",
    "transaction limit",
    "daily limit",
    "withdraw limit",
    "statement",
    "mini statement",
    "balance check",
    "check balance",
    "merchant payment",
    "payment",
    "mobile recharge",
    "recharge",
]

# Bank keywords that disambiguate
_BANK_KEYWORDS = [
    "bkash",
    "nagad",
    "dbbl",
    "rocket",
    "upay",
]

# Clarification messages for specific intents and languages
_CLARIFICATION_MESSAGES: Dict[str, Dict[str, str]] = {
    "pin reset": {
        "en": "Which banking service are you referring to for PIN reset? (bKash, Nagad, DBBL, Rocket, Upay)",
        "bn": "PIN reset korte chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
        "banglish": "PIN reset korte chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
    },
    "forgot pin": {
        "en": "Which banking service are you referring to for forgot PIN? (bKash, Nagad, DBBL, Rocket, Upay)",
        "bn": "Forgot PIN korte chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
        "banglish": "Forgot PIN korte chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
    },
    "cash out": {
        "en": "Which banking service are you referring to for cash out? (bKash, Nagad, DBBL, Rocket, Upay)",
        "bn": "Cash out charge jante chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
        "banglish": "Cash out charge jante chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
    },
    "send money": {
        "en": "Which banking service are you referring to for sending money? (bKash, Nagad, DBBL, Rocket, Upay)",
        "bn": "Paisa pathate chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
        "banglish": "Paisa pathate chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
    },
    "account open": {
        "en": "Which banking service are you referring to for opening an account? (bKash, Nagad, DBBL, Rocket, Upay)",
        "bn": "Account khulte chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
        "banglish": "Account khulte chan kon service-er jonno? (bKash, Nagad, DBBL, Rocket, Upay)",
    },
}

# Default clarification message for intents not in the above map
_DEFAULT_CLARIFICATION_MESSAGE = {
    "en": "Which banking service are you referring to? (bKash, Nagad, DBBL, Rocket, Upay)",
    "bn": "আপনি কোন সেবার কথা বলছেন? (bKash, Nagad, DBBL, Rocket, Upay)",
    "banglish": "Apni kon service-er kotha bolchen? (bKash, Nagad, DBBL, Rocket, Upay)",
}

# Clarification options (always the same list of bank names)
_CLARIFICATION_OPTIONS = ["bKash", "Nagad", "DBBL", "Rocket", "Upay"]


def is_ambiguous_banking_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Check if the query is an ambiguous banking query.

    Returns:
        (is_ambiguous, detected_intent)
        If ambiguous, returns the intent that triggered the ambiguity.
    """
    query_lower = query.lower()
    
    # Check for any ambiguous intent
    for intent in _AMBIGUOUS_INTENTS:
        # Split the intent into words and check if all words are in the query
        words = intent.split()
        if all(word in query_lower for word in words):
            # Check if any bank keyword is present
            if not any(bank in query_lower for bank in _BANK_KEYWORDS):
                return True, intent
    
    return False, None


def get_clarification_message(intent: str, language: str) -> str:
    """
    Get the clarification message for the given intent and language.
    """
    intent_messages = _CLARIFICATION_MESSAGES.get(intent)
    if intent_messages is not None:
        message = intent_messages.get(language)
        if message is not None:
            return message
    # Fallback to default message
    return _DEFAULT_CLARIFICATION_MESSAGE.get(language, _DEFAULT_CLARIFICATION_MESSAGE["en"])


def get_clarification_options() -> List[str]:
    """
    Get the list of clarification options (bank names).
    """
    return _CLARIFICATION_OPTIONS.copy()