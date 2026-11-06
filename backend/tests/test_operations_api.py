import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_bed_availability_500_beds():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/operations/beds", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_beds"] == 500
    assert data["occupied_beds"] > 0
    assert data["available_beds"] > 0
    assert data["occupancy_rate_percentage"] > 0

def test_icu_capacity():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/operations/icu", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_icu_beds"] == 50
    assert data["ventilators_total"] > 0

def test_emergency_workload():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/operations/emergency", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "triage_breakdown" in data
    assert "ambulances_available" in data

def test_department_status_all_15_departments():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/operations/departments", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 15

def test_medical_inventory():
    headers = {"X-Actor-Id": "pharm_james_wilson"}
    response = client.get("/api/v1/operations/inventory", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["blood_units"]) == 8  # 8 blood types
    assert len(data["medicines"]) >= 10
