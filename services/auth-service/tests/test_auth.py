import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

def test_login_success():
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "socadmin2026!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "SOC Administrator"

def test_login_failure():
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert res.status_code == 401

def test_verify_token():
    # 1. Login
    login_res = client.post("/api/v1/auth/login", json={
        "username": "operator",
        "password": "operator2026!"
    })
    token = login_res.json()["access_token"]

    # 2. Verify
    verify_res = client.get("/api/v1/auth/verify", headers={
        "Authorization": f"Bearer {token}"
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["valid"] is True
