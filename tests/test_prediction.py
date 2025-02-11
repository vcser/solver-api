from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_prediction_endpoint():
    test_data = {
        "timestamp": "2024-01-01T00:00:00",
        "num_incendios": 1,
        "incendios": [{
            "lat": -33.45,
            "lon": -70.67,
            "humedad_relativa": 50.0,
            "velocidad_viento": 10.0,
            "direccion_viento": 180.0,
            "temperatura": 25.0,
            "pendiente": 5.0,
            "factor_vpl": 0.5,
            "timestamp_inicio": "2024-01-01T00:00:00",
            "valor_rodal_usd": 10000.0,
            "modelo_combustible": "PCH1",
            "distancia_ciudad": 5000.0,
            "metros_construidos": 1000.0
        }],
        "num_recursos": 1,
        "recursos": [{
            "id": "r1",
            "tipo": "helicopter",
            "horas_trabajo": 8.0,
            "lat": -33.45,
            "lon": -70.67,
            "id_estado": 1,
            "agrupado": 1,
            "timestamps_eta": ["2024-01-01T01:00:00"]
        }]
    }
    response = client.post("/prediction/", json=test_data)
    assert response.status_code == 200
    assert "result" in response.json()