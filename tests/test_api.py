import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_recommend_basic():
    response = client.get("/recommend?query=квартира")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "квартира"
    assert len(data["results"]) > 0

def test_recommend_with_filters():
    response = client.get("/recommend?query=москва&min_price=10000000&max_price=20000000")
    assert response.status_code == 200
    data = response.json()
    for item in data["results"]:
        assert 10000000 <= item["payload"]["price"] <= 20000000

def test_recommend_with_room_filter():
    response = client.get("/recommend?query=новостройка&rooms=3")
    assert response.status_code == 200
    data = response.json()
    for item in data["results"]:
        assert item["payload"]["rooms"] == 3