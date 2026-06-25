"""Pending intent state management for clarification flow."""

import time
import threading
from typing import Dict, Optional

# In-memory store for pending intents
_pending_intents: Dict[str, dict] = {}
_lock = threading.Lock()

# Time-to-live for pending intents (in seconds)
_PENDING_INTENT_TTL = 5 * 60  # 5 minutes

# Bank keywords that disambiguate
_BANK_KEYWORDS = ["bkash", "nagad", "dbbl", "rocket", "upay"]

# Template for reconstructing queries from intent and bank
_QUERY_TEMPLATES = {
    "pin reset": "How to reset {bank} PIN?",
    "forgot pin": "How to reset {bank} PIN?",
    "change pin": "How to change {bank} PIN?",
    "cash out": "What is the cash out fee for {bank}?",
    "cash out fee": "What is the cash out fee for {bank}?",
    "cash out charge": "What is the cash out charge for {bank}?",
    "send money": "How to send money using {bank}?",
    "money transfer": "How to transfer money using {bank}?",
    "add money": "How to add money to {bank}?",
    "cash in": "How to cash in using {bank}?",
    "account open": "How to open an account with {bank}?",
    "open account": "How to open an account with {bank}?",
    "registration": "How to register with {bank}?",
    "transaction limit": "What is the transaction limit for {bank}?",
    "daily limit": "What is the daily transaction limit for {bank}?",
    "withdraw limit": "What is the withdrawal limit for {bank}?",
    "statement": "How to get a statement from {bank}?",
    "mini statement": "How to get a mini statement from {bank}?",
    "balance check": "How to check balance in {bank}?",
    "check balance": "How to check balance in {bank}?",
    "merchant payment": "How to make a merchant payment using {bank}?",
    "payment": "How to make a payment using {bank}?",
    "mobile recharge": "How to recharge mobile using {bank}?",
    "recharge": "How to recharge mobile using {bank}?",
}


def get_pending_intent(client_host: str) -> Optional[dict]:
    """Retrieve and remove the pending intent for the given client host."""
    with _lock:
        data = _pending_intents.get(client_host)
        if data is None:
            return None
        # Check if expired
        if time.time() - data["timestamp"] > _PENDING_INTENT_TTL:
            del _pending_intents[client_host]
            return None
        # Remove the intent from the store
        del _pending_intents[client_host]
        return data


def store_pending_intent(client_host: str, intent: str, language: str, original_query: str) -> None:
    """Store a pending intent for the given client host."""
    with _lock:
        _pending_intents[client_host] = {
            "intent": intent,
            "language": language,
            "original_query": original_query,
            "timestamp": time.time(),
        }


def reconstruct_query(intent: str, bank: str, language: str) -> str:
    """Reconstruct a query from the intent and bank."""
    template = _QUERY_TEMPLATES.get(intent)
    if template is None:
        return f"How to {intent.replace('_', ' ')} {bank}?"
    return template.format(bank=bank)


def is_bank_name(text: str) -> bool:
    """Check if the given text is a bank name (case-insensitive)."""
    text_lower = text.strip().lower()
    return text_lower in [bank.lower() for bank in _BANK_KEYWORDS]