"""Regression tests for out-of-domain (OOD) detection.

Verifies that queries outside FinBot's banking domain are rejected
early without invoking retrieval or the LLM.
"""
from app.ood import is_in_domain, get_ood_response


class TestOODDetection:
    """Verify that OOD queries are correctly identified."""

    def test_ronaldo_is_ood(self):
        assert not is_in_domain("Who is Cristiano Ronaldo?")

    def test_python_program_is_ood(self):
        assert not is_in_domain("Write me a Python program.")

    def test_weather_is_ood(self):
        assert not is_in_domain("What's the weather today?")

    def test_joke_is_ood(self):
        assert not is_in_domain("Tell me a joke.")


class TestOODResponse:
    """Verify language-matched OOD responses."""

    def test_english_response(self):
        resp, lang = get_ood_response("Who is Cristiano Ronaldo?")
        assert lang == "en"
        assert "FinBot" in resp
        assert "banking" in resp.lower()

    def test_bengali_response(self):
        resp, lang = get_ood_response("রোনালদো কে?")
        assert lang == "bn"
        assert "FinBot" in resp

    def test_banglish_response(self):
        resp, lang = get_ood_response("Ronaldo ke bolar?")
        assert lang == "banglish"
        assert "FinBot" in resp


class TestInDomainStillPasses:
    """Ensure legitimate banking questions pass through."""

    def test_bkash_pin_reset(self):
        assert is_in_domain("How do I reset my bKash PIN?")

    def test_balance_check(self):
        assert is_in_domain("How to check balance in Nagad?")

    def test_send_money(self):
        assert is_in_domain("How to send money using Rocket?")

    def test_loan_inquiry(self):
        assert is_in_domain("What is the interest rate for personal loan?")

    def test_transaction_limit(self):
        assert is_in_domain("What is the daily transaction limit for bKash?")

    def test_debit_card(self):
        assert is_in_domain("How to apply for a debit card?")

    def test_mobile_recharge(self):
        assert is_in_domain("How to recharge mobile using DBBL?")

    def test_agent_banking(self):
        assert is_in_domain("Where is the nearest agent location?")
