"""Test the stateful clarification flow end-to-end."""

import app.intent_state
import time


def test_is_bank_name():
    assert app.intent_state.is_bank_name("bKash") == True
    assert app.intent_state.is_bank_name("nagad") == True
    assert app.intent_state.is_bank_name("DBBL") == True
    assert app.intent_state.is_bank_name("Rocket") == True
    assert app.intent_state.is_bank_name("upay") == True
    assert app.intent_state.is_bank_name("how to reset pin") == False
    assert app.intent_state.is_bank_name("what is BKash") == False
    print("[PASS] test_is_bank_name")


def test_store_and_retrieve_pending_intent():
    app.intent_state.store_pending_intent("client1", "pin reset", "en", "How to reset PIN?")
    pending = app.intent_state.get_pending_intent("client1")
    assert pending is not None
    assert pending["intent"] == "pin reset"
    assert pending["language"] == "en"
    assert pending["original_query"] == "How to reset PIN?"
    # Second call should return None (consumed)
    assert app.intent_state.get_pending_intent("client1") is None
    print("[PASS] test_store_and_retrieve_pending_intent")


def test_pending_intent_expiration():
    # Force a short TTL
    old_ttl = app.intent_state._PENDING_INTENT_TTL
    try:
        app.intent_state._PENDING_INTENT_TTL = 0.001  # 1ms
        app.intent_state.store_pending_intent("client2", "cash out", "en", "Cash out charge?")
        time.sleep(0.01)
        pending = app.intent_state.get_pending_intent("client2")
        assert pending is None  # Should be expired
        print("[PASS] test_pending_intent_expiration")
    finally:
        app.intent_state._PENDING_INTENT_TTL = old_ttl


def test_reconstruct_query():
    query = app.intent_state.reconstruct_query("pin reset", "bKash", "en")
    assert "bKash" in query
    assert "reset" in query
    assert "PIN" in query
    print(f"  Reconstructed: {query}")
    print("[PASS] test_reconstruct_query")


def test_reconstruct_query_without_template():
    query = app.intent_state.reconstruct_query("unknown_intent", "Nagad", "en")
    assert "Nagad" in query
    assert "unknown intent" in query or "unknown_intent" in query
    print(f"  Reconstructed (fallback): {query}")
    print("[PASS] test_reconstruct_query_without_template")


def test_separate_client_intents():
    app.intent_state.store_pending_intent("client_a", "pin reset", "en", "Reset PIN?")
    app.intent_state.store_pending_intent("client_b", "cash out", "bn", "Cash out fee?")
    pending_a = app.intent_state.get_pending_intent("client_a")
    pending_b = app.intent_state.get_pending_intent("client_b")
    assert pending_a is not None
    assert pending_b is not None
    assert pending_a["intent"] == "pin reset"
    assert pending_b["intent"] == "cash out"
    print("[PASS] test_separate_client_intents")


if __name__ == "__main__":
    print("=== Clarification Flow Tests ===\n")
    test_is_bank_name()
    test_store_and_retrieve_pending_intent()
    test_pending_intent_expiration()
    test_reconstruct_query()
    test_reconstruct_query_without_template()
    test_separate_client_intents()
    print("\n=== All tests passed ===")