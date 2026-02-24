from app.services.search_service import _normalize


def test_normalize_lowercases():
    assert _normalize("HELLO World") == ["hello", "world"]


def test_normalize_removes_punctuation():
    assert _normalize("phone-case!!!") == ["phone", "case"]


def test_normalize_handles_spaces():
    assert _normalize("  eco   cotton  ") == ["eco", "cotton"]
