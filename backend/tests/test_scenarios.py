import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_scenarios():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/simulation/scenarios", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    codes = [s["scenario_code"] for s in data]
    for c in ["SCENARIO_A", "SCENARIO_B", "SCENARIO_C", "SCENARIO_D", "SCENARIO_E", "SCENARIO_F", "SCENARIO_G"]:
        assert c in codes

def test_activate_scenario_b_emergency_influx():
    headers = {"X-Actor-Id": "admin_sterling_archer"}
    payload = {"scenario_code": "SCENARIO_B"}
    response = client.post("/api/v1/simulation/scenarios/activate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["state_changes"]["emergency_workload"] == "CRITICAL"
    assert data["state_changes"]["ambulances"] == "ALL_DISPATCHED"

def test_activate_scenario_c_icu_shortage():
    headers = {"X-Actor-Id": "admin_sterling_archer"}
    payload = {"scenario_code": "SCENARIO_C"}
    response = client.post("/api/v1/simulation/scenarios/activate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["state_changes"]["available_icu_beds"] == 0

def test_reset_scenario_a_normal():
    headers = {"X-Actor-Id": "admin_sterling_archer"}
    payload = {"scenario_code": "SCENARIO_A"}
    response = client.post("/api/v1/simulation/scenarios/activate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["state_changes"]["overall_status"] == "NORMAL_OPERATIONS"
