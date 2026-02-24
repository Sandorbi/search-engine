
from app.services.search_service import BM25Index, _normalize


def test_normalize_lowercases():
    assert _normalize("HELLO World") == ["hello", "world"]


def test_normalize_removes_punctuation():
    assert _normalize("phone-case!!!") == ["phone", "case"]


def test_normalize_handles_spaces():
    assert _normalize("  eco   cotton  ") == ["eco", "cotton"]


def test_search_respects_limit():
    products = [
        {"id": i, "name": f"Product {i}", "description": "test", "brand": "Brand"}
        for i in range(20)
    ]
    
    index = BM25Index(products)
    results = index.search("product", limit=5)
    
    assert len(results) <= 5


def test_search_field_boosting():
    products = [
        {"id": 1, "name": "Cotton Shirt", "description": "Nice shirt", "brand": "Brand"},
        {"id": 2, "name": "Silk Shirt", "description": "Made with cotton", "brand": "Brand"},
    ]
    
    index = BM25Index(products)
    results = index.search("cotton", limit=10)
    
    if len(results) >= 2:
        assert results[0][1]["id"] == 1
        assert results[0][0] > results[1][0]
