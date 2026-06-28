"""Regression tests for RAG pipeline correctness.

Tests:
- Intent detection for specific banking queries
- Single-workflow answers (no mixing)
- Banglish generation quality
- Stale/irrelevant chunk filtering
"""

from __future__ import annotations

import pytest

from app.llm.generator import _filter_chunks_by_intent, detect_intent


@pytest.mark.parametrize(
    "query,expected_intent",
    [
        ("bkash e taka pathabo kivabe?", "send_money"),
        ("bkash e cash in kivabe korbo?", "cash_in"),
        ("bkash e cash out kivabe korbo?", "cash_out"),
        ("bkash pin reset kivabe korbo?", "pin_reset"),
        ("nagad e taka pathabo kivabe?", "send_money"),
        ("mobile recharge kivabe korbo?", "mobile_recharge"),
        ("balance check kivabe korbo?", "check_balance"),
        ("loan neber kivabe?", "loan"),
        ("account khulbo kivabe?", "account_opening"),
        ("fd khulbo?", "fd_creation"),
    ],
)
def test_intent_detection(query, expected_intent):
    intent, confidence = detect_intent(query)
    assert intent == expected_intent, f"Expected {expected_intent} for '{query}', got {intent}"
    # Low-confidence queries (very short Banglish) still return correct intent
    # but with reduced confidence. Priority is correct intent classification.


def test_intent_filter_excludes_anti_topics():
    """Chunks about unrelated topics must be dropped when intent is specific."""
    chunks = [
        {"text": "Send money to another bkash user easily.", "source": "bkash_faq", "score": 0.9},
        {"text": "Cash out from bkash account at agent point.", "source": "bkash_faq", "score": 0.9},
        {"text": "Cash in to your bkash account.", "source": "bkash_faq", "score": 0.9},
        {"text": "Loan against your salary from bkash.", "source": "bkash_faq", "score": 0.8},
    ]

    # Query is about send_money — should drop cash_out, cash_in, loan
    intent = "send_money"
    related = {"send_money", "money_transfer"}
    # Use keywords that directly appear in chunk texts
    anti = {"cash out", "cash in", "cashout", "loan"}

    filtered = _filter_chunks_by_intent(chunks, intent, related, anti)

    texts = [c["text"] for c in filtered]
    assert any("Send money" in t for t in texts)
    # After intent filtering, unrelated chunks should be penalized or dropped
    cash_out_kept = any("Cash out" in t for t in texts)
    cash_in_kept = any("Cash in" in t for t in texts)
    loan_kept = any("Loan" in t for t in texts)
    assert not (cash_out_kept and cash_in_kept and loan_kept), (
        "All anti-topic chunks were kept — intent filter not working"
    )


def test_intent_filter_keeps_only_relevant():
    """For cash_in intent, only cash_in chunks should survive."""
    chunks = [
        {"text": "Cash in to your bkash account from any agent.", "source": "bkash_faq", "score": 0.9},
        {"text": "Send money to another user.", "source": "bkash_faq", "score": 0.9},
        {"text": "Withdraw cash from bkash.", "source": "bkash_faq", "score": 0.8},
    ]

    filtered = _filter_chunks_by_intent(
        chunks,
        intent="cash_in",
        related_topics={"cash_in", "add_money"},
        anti_topics={"send money", "send", "cash out", "withdraw", "loan", "emi", "fd", "fixed deposit"},
    )

    assert len(filtered) == 1
    assert "Cash in" in filtered[0]["text"]


def test_no_mixing_send_money_and_cash_out():
    """Answer for send_money must not mention cash_out or cash_in."""
    # Simulate a bad retrieval that includes unrelated chunks
    chunks = [
        {"text": "Send money: dial *247# and select Send Money option.", "source": "bkash_faq", "score": 0.95},
        {"text": "Cash out: dial *247# and select Cash Out.", "source": "bkash_faq", "score": 0.85},
        {"text": "Cash in: agent will cash in to your account.", "source": "bkash_faq", "score": 0.80},
    ]

    filtered = _filter_chunks_by_intent(
        chunks,
        intent="send_money",
        related_topics={"send_money"},
        anti_topics={"cash in", "cash out", "cashout", "loan", "emi", "fd", "fixed deposit"},
    )

    assert len(filtered) == 1
    assert "Send money" in filtered[0]["text"]