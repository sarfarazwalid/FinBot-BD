from app.ingestion.chunker import _detect_language


def test_bengali_detection():
    assert _detect_language("আমার একাউন্ট ব্লক হয়েছে") == "bn"


def test_bengali_with_english_loanword_pin():
    """Bengali text with an English loanword 'PIN': bengali_chars (11) > english_chars (3) * 2? 11 > 6 → bn"""
    assert _detect_language("আমার PIN ভুলে গেছি") == "bn"


def test_bengali_with_english_loanword_bkash():
    """Bengali text with 'bKash' and 'account' → both scripts present → mixed"""
    assert _detect_language("আমার bKash account block হয়েছে") == "mixed"


def test_english_detection():
    assert _detect_language("How do I reset my PIN?") == "en"


def test_mixed_detection_banglish():
    assert _detect_language("amar pin vule gechi") == "mixed"


def test_empty_text():
    assert _detect_language("") == "en"


def test_only_spaces():
    assert _detect_language("   ") == "en"


def test_bengali_with_english_loanwords():
    """Bengali text containing English words like 'bKash', 'PIN' should
    still be detected as Bengali if Bengali Unicode dominates heavily."""
    text = "আমার bKash অ্যাকাউন্ট ব্লক হয়ে গেছে, কিভাবে আনব্লক করব?"
    assert _detect_language(text) == "bn"


def test_mostly_bengali_mixed():
    """Mix where Bengali Unicode > 10% and English chars exist → mixed."""
    text = "amar account block hoye geche, kivabe unblock korbo?"
    assert _detect_language(text) == "mixed"


def test_pure_bengali():
    assert _detect_language("আপনার নাম কী?") == "bn"


def test_banglish_with_common_verbs():
    assert _detect_language("apnar account block hoye geche") == "mixed"


def test_english_with_banglish_loanword_single():
    """A single matching Banglish word in an English sentence should not trigger mixed."""
    text = "I need to go to the bank for money transfer"
    assert _detect_language(text) == "en"