import pytest
from fastapi.testclient import TestClient
import os

# Configuration pour utiliser une base de test temporaire en mémoire ou fichier de test
os.environ["DB_PATH"] = "test_payments.db"

from app.main import app
from app.database import init_db

@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    yield
    if os.path.exists("test_payments.db"):
        try:
            os.remove("test_payments.db")
        except PermissionError:
            pass

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["service"] == "payment-api"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["database_connected"] is True

def test_create_and_get_payment():
    payload = {
        "amount": 129.99,
        "currency": "EUR",
        "customer_name": "Jean Dupont",
        "customer_email": "jean.dupont@example.com",
        "card_number": "4532123456789123",
        "merchant_id": "MERCHANT-01",
        "reference": "CMD-2026-001"
    }

    # 1. Création de paiement
    create_res = client.post("/api/v1/payments", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["status"] == "APPROVED"
    assert created_data["amount"] == 129.99
    assert created_data["card_last4"] == "9123"
    assert "transaction_id" in created_data
    tx_id = created_data["transaction_id"]

    # 2. Récupération par ID
    get_res = client.get(f"/api/v1/payments/{tx_id}")
    assert get_res.status_code == 200
    fetched_data = get_res.json()
    assert fetched_data["transaction_id"] == tx_id
    assert fetched_data["reference"] == "CMD-2026-001"

    # 3. Liste des paiements
    list_res = client.get("/api/v1/payments")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(tx["transaction_id"] == tx_id for tx in list_data["transactions"])

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "payment_http_requests_total" in response.text
    assert "payment_service_health" in response.text

def test_chaos_configuration_and_reset():
    # Activer chaos latence et erreurs
    update_res = client.post("/api/v1/chaos/configure", json={
        "injected_latency_ms": 10.0,
        "injected_error_rate": 0.5
    })
    assert update_res.status_code == 200
    status_data = update_res.json()
    assert status_data["is_active"] is True
    assert status_data["injected_latency_ms"] == 10.0

    # Reset
    reset_res = client.post("/api/v1/chaos/reset")
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["is_active"] is False
    assert reset_data["injected_latency_ms"] == 0.0
