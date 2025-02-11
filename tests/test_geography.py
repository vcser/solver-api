from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_geography_endpoint():
    response = client.get("/geography/?lat=-33.45&lon=-70.67")
    assert response.status_code == 200
    assert "slope" in response.json()
    assert "fuel_model" in response.json()