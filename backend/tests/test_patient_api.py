import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_search_patients():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/patients?limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "mrn" in data[0]

def test_get_patient_encounters():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/patients/1/encounters", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_patient_medical_history():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    response = client.get("/api/v1/patients/1/medical-history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "conditions" in data
    assert "allergies" in data
    assert "medications" in data

def test_get_patient_lab_and_radiology():
    headers = {"X-Actor-Id": "dr_elena_vance"}
    res_lab = client.get("/api/v1/patients/1/lab-reports", headers=headers)
    assert res_lab.status_code == 200
    
    res_rad = client.get("/api/v1/patients/1/radiology-reports", headers=headers)
    assert res_rad.status_code == 200
