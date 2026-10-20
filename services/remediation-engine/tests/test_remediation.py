import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "k8s_connected" in data

@patch("app.main.verify_service_recovery", new_callable=AsyncMock)
@patch("app.main.k8s_manager.rollout_restart_deployment")
def test_manual_trigger(mock_rollout, mock_verify):
    mock_rollout.return_value = True
    mock_verify.return_value = {
        "success": True,
        "stage": "TRANSACTION_VERIFIED",
        "transaction_id": "TEST-TX-123",
        "auth_code": "AUTH-999999",
        "duration_sec": 1.25,
        "message": "Zero-Touch Recovery complete",
    }

    res = client.post("/api/v1/remediation/trigger", json={"reason": "Unit Test Trigger"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["verification"]["success"] is True

def test_get_history():
    res = client.get("/api/v1/remediation/history")
    assert res.status_code == 200
    data = res.json()
    assert "history" in data
