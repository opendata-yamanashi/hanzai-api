from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_read_keys():
    response = client.get("/keys")
    assert response.status_code == 200

def test_read_values():
    response = client.get("/values/罪名")
    assert response.status_code == 200

def test_read_counts():
    response = client.get("/counts/罪名")
    assert response.status_code == 200

