from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)




# =========================================================
# 1 Test Health Check
# =========================================================
def test_health_check():
    """Pastikan endpoint /health mengembalikan status OK"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
