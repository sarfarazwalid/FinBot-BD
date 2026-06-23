from app.ingestion.chunker import _detect_language


def test_bengali_detection():
    assert _detect_language("আমার একাউন্ট ব্লক হয়েছে") == "bn"


def test_mixed_detection():
    assert _detect_language("amar account block hoyeche") == "mixed"


def test_english_detection():
    assert _detect_language("How to reset PIN?") == "en"