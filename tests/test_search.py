
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.search_service import BM25Index

@pytest.fixture
def client():
    test_products = [
        {"id": 1, "name": "Phone Case Pro", "description": "Protective case", "brand": "Vibe", "price": 29.99, "country": "USA", "inStock": True},
        {"id": 2, "name": "Cotton T-Shirt", "description": "Eco-friendly cotton", "brand": "Terra", "price": 19.99, "country": "UK", "inStock": True},
        {"id": 3, "name": "Smart Bulb", "description": "LED smart lighting", "brand": "Helix", "price": 39.99, "country": "Germany", "inStock": True},
        {"id": 4, "name": "Laptop Bag", "description": "Padded laptop bag", "brand": "Nova", "price": 49.99, "country": "Canada", "inStock": True},
        {"id": 5, "name": "Phone Stand", "description": "Desktop phone holder", "brand": "Apex", "price": 15.99, "country": "USA", "inStock": False},
    ]
    
    app.state.search_index = BM25Index(test_products)
    
    return TestClient(app)


def test_search_returns_results(client):
    response = client.get("/search?q=phone&limit=5")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "query" in data
    assert "limit" in data
    assert "count" in data
    assert "results" in data
    assert data["query"] == "phone"
    assert data["limit"] == 5


def test_search_empty_query_fails(client):
    response = client.get("/search?q=   ")
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_search_result_structure(client):
    response = client.get("/search?q=cotton")
    
    assert response.status_code == 200
    data = response.json()
    
    if data["count"] > 0:
        result = data["results"][0]
        assert "score" in result
        assert "product" in result
        assert isinstance(result["score"], float)
        assert isinstance(result["product"], dict)


def test_search_limit_parameter(client):
    response = client.get("/search?q=pro&limit=3")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["results"]) <= 3


def test_search_case_insensitive(client):
    response1 = client.get("/search?q=PHONE")
    response2 = client.get("/search?q=phone")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    assert response1.json()["count"] == response2.json()["count"]


def test_search_no_results(client):
    response = client.get("/search?q=wasdddd")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["count"] == 0
    assert data["results"] == []
