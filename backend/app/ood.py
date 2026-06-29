"""Out-of-domain (OOD) detection for FinBot BD."""

from __future__ import annotations
import logging
import re
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

_BANKING_PATTERN_RE = re.compile(
    r"\b(?:pin|account|balance|transfer|deposit|loan|card|bank|recharge|payment|"
    r"taka|bdt|bkash|nagad|dbbl|brac|agent|otp|ussd|statement|"
    r"limit|fee|charge|interest|emi|cheque|atm|pos|qr|visa|mastercard)\b",
    re.IGNORECASE,
)

_BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_BANGLISH_INDICATORS: list[str] = [
    "korbo", "korar", "kore", "korun", "kivabe", "paben",
    "de", "lagen", "hobe", "asche", "gelo", "vabe",
    "ache", "ki", "er", "jante", "bolar", "bolun",
    "khulte", "khulbo", "dakte", "dakbo", "pathanor",
    "pathate", "pathalam", "dile", "dhorun", "korte",
    "korben", "korlam", "parsi", "parbo", "parben",
]

_BANKING_PHRASES: list[str] = [
    "account open", "open account", "account create", "create account",
    "account block", "block account", "unblock account", "account unblock",
    "account close", "close account", "account type", "savings account",
    "current account", "student account", "mobile account",
    "pin reset", "reset pin", "forgot pin", "pin change", "change pin",
    "forgot password", "password reset", "reset password",
    "pin number", "new pin", "old pin", "wrong pin", "pin wrong",
    "pin invalid", "invalid pin", "pin expired", "set pin",
    "send money", "receive money", "money transfer", "transfer money",
    "add money", "cash in", "cash out", "cashin", "cashout",
    "remittance", "inward remittance", "outward remittance",
    "balance check", "check balance", "balance enquiry", "balance inquiry",
    "mini statement", "account statement", "transaction history",
    "debit card", "credit card", "atm card", "card block", "block card",
    "unblock card", "card unblock", "card apply", "apply card",
    "card activate", "activate card", "card limit", "card pin",
    "card renewal", "replace card", "lost card", "stolen card",
    "loan apply", "apply loan", "personal loan", "home loan",
    "education loan", "car loan", "loan emi", "loan interest",
    "loan repayment", "loan eligibility", "loan amount",
    "fixed deposit", "recurring deposit", "deposit rate", "interest rate",
    "fdr", "dps",
    "cash out fee", "cash out charge", "transaction fee", "service charge",
    "annual fee", "maintenance charge",
    "transaction limit", "daily limit", "monthly limit",
    "withdrawal limit", "send limit", "receive limit",
    "mobile banking", "mobile financial", "mobile recharge",
    "bill pay", "pay bill", "utility bill", "merchant payment",
    "qr payment", "qr scan", "top up", "topup",
    "one time password", "verification code", "verify number",
    "registered number", "mobile number change",
    "agent banking", "agent point", "agent location",
    "internet banking", "online banking", "net banking",
    "financial service", "mobile financial service",
]

_BANKING_PHRASES_LOWER: list[str] = [p.lower() for p in _BANKING_PHRASES]

_BN_FINANCE_TERMS: list[str] = [
    "\u099f\u09be\u0995\u09be",
    "\u09ac\u09cd\u09af\u09be\u0982\u0995",
    "\u09aa\u09bf\u09a8",
    "\u0985\u09cd\u09af\u09be\u0995\u09be\u0989\u09a8\u09cd\u099f",
    "\u099f\u09cd\u09b0\u09be\u09a8\u09cd\u099c\u09be\u09b0",
    "\u09b2\u09cb\u09a8",
    "\u099c\u09ae\u09be",
    "\u0995\u09be\u09b0\u09cd\u09a1",
    "\u09ae\u09cb\u09ac\u09be\u0987\u09b2",
    "\u09aa\u09c7\u09ae\u09a8\u09cd\u099f",
    "\u09aa\u09be\u09a0\u09be\u09a8\u09cb",
]

_OOD_RESPONSES: Dict[str, str] = {
    "en": "I'm FinBot, and I can only assist with banking and mobile financial services.",
    "bn": (
        "\u0986\u09ae\u09bf FinBot\u0964 \u0986\u09ae\u09bf "
        "\u09b6\u09c1\u09a7\u09c1\u09ae\u09be\u09a4\u09cd\u09b0 "
        "\u09ac\u09cd\u09af\u09be\u0982\u0995\u09bf\u0982 \u0993 "
        "\u09ae\u09cb\u09ac\u09be\u0987\u09b2 \u0986\u09b0\u09cd\u09a5\u09bf\u0995 "
        "\u09aa\u09b0\u09bf\u09b7\u09c7\u09ac\u09be "
        "\u09b8\u09ae\u09cd\u09aa\u09b0\u09cd\u0995\u09bf\u09a4 "
        "\u09a4\u09a5\u09cd\u09af \u09a6\u09bf\u09a4\u09c7 "
        "\u09aa\u09be\u09b0\u09bf\u0964"
    ),
    "banglish": (
        "Ami FinBot. Ami shudhumatro banking ebong mobile financial "
        "service somporkito prosner uttor dite pari."
    ),
}


def _detect_language(query: str) -> str:
    has_bengali = bool(_BENGALI_RE.search(query))
    has_latin = bool(_LATIN_RE.search(query))
    has_banglish = any(w in query.lower() for w in _BANGLISH_INDICATORS)
    if has_bengali and has_latin:
        return "banglish"
    if has_bengali:
        return "bn"
    if has_banglish:
        return "banglish"
    return "en"


def is_in_domain(query: str) -> bool:
    q_lower = query.lower().strip()
    if _BANKING_PATTERN_RE.search(q_lower):
        return True
    for phrase in _BANKING_PHRASES_LOWER:
        if phrase in q_lower:
            return True
    if _BENGALI_RE.search(query):
        if any(term in q_lower for term in _BN_FINANCE_TERMS):
            return True
    return False


def get_ood_response(query: str) -> Tuple[str, str]:
    language = _detect_language(query)
    response = _OOD_RESPONSES.get(language, _OOD_RESPONSES["en"])
    return response, language
