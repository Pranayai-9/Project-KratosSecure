import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_doctor_can_read_patient():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/patients/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "allergies" in data
    assert "conditions" in data

def test_billing_officer_cannot_read_lab_reports():
    # Billing officer is restricted from unrestricted clinical lab reports
    headers = {"X-Actor-Id": "billing_arthur_dent"}
    response = client.get("/api/v1/patients/1/lab-reports", headers=headers)
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]

def test_adversarial_agent_is_denied():
    # Adversarial persona has zero clinical permissions
    headers = {"X-Actor-Id": "adversarial_infiltrator"}
    response = client.get("/api/v1/patients/1", headers=headers)
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]

def test_ai_agent_cannot_access_unauthorized_admin():
    # AI agent cannot access canary secrets or modify user roles
    headers = {"X-Actor-Id": "agent_kratos_ai"}
    response = client.get("/api/v1/system/canaries", headers=headers)
    assert response.status_code == 403
