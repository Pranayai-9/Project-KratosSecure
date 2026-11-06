import sys
import os
import time
import threading
import uvicorn
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1.5)

base_url = "http://127.0.0.1:8002"
h_doc = {"X-Actor-Id": "dr_elena_vance"}
h_bill = {"X-Actor-Id": "billing_arthur_dent"}
h_admin = {"X-Actor-Id": "admin_sterling_archer"}
h_sec = {"X-Actor-Id": "sec_john_connor"}
h_ai = {"X-Actor-Id": "agent_kratos_ai"}
h_adv = {"X-Actor-Id": "adversarial_infiltrator"}

print("=== STARTING KRATOSSECURE FULL VERIFICATION TEST ===")

# 1. Healthcheck
r = requests.get(f"{base_url}/health")
assert r.status_code == 200 and r.json()["beds"] == 500
print("[OK] Healthcheck passed.")

# 2. Patient search & profile
r = requests.get(f"{base_url}/api/v1/patients?limit=5", headers=h_doc)
assert r.status_code == 200 and len(r.json()) > 0
p1 = r.json()[0]
r = requests.get(f"{base_url}/api/v1/patients/{p1['id']}", headers=h_doc)
assert r.status_code == 200
print(f"[OK] Patient retrieval passed ({p1['mrn']}).")

# 3. Clinical history, encounters, labs, radiology
r = requests.get(f"{base_url}/api/v1/patients/{p1['id']}/encounters", headers=h_doc)
assert r.status_code == 200
r = requests.get(f"{base_url}/api/v1/patients/{p1['id']}/medical-history", headers=h_doc)
assert r.status_code == 200
r = requests.get(f"{base_url}/api/v1/patients/{p1['id']}/lab-reports", headers=h_doc)
assert r.status_code == 200
r = requests.get(f"{base_url}/api/v1/patients/{p1['id']}/radiology-reports", headers=h_doc)
assert r.status_code == 200
print("[OK] Encounters, medical history, lab reports, radiology reports verified.")

# 4. RBAC: Billing officer denied clinical labs
r = requests.get(f"{base_url}/api/v1/patients/{p1['id']}/lab-reports", headers=h_bill)
assert r.status_code == 403
print("[OK] RBAC verified: Billing Officer denied clinical lab access.")

# 5. RBAC: AI agent denied canary secrets
r = requests.get(f"{base_url}/api/v1/system/canaries", headers=h_ai)
assert r.status_code == 403
print("[OK] RBAC verified: Healthcare AI Agent denied Canary Secrets access.")

# 6. Canary Trip detection
r = requests.get(f"{base_url}/api/v1/patients?query=CANARY_KEY_EHR_DB_ADMIN", headers=h_adv)
# Searching for canary should trip alarm
r_canary = requests.get(f"{base_url}/api/v1/system/canaries", headers=h_sec)
assert r_canary.status_code == 200
tripped = [c for c in r_canary.json() if c["secret_key"] == "CANARY_KEY_EHR_DB_ADMIN"]
assert len(tripped) == 1 and tripped[0]["is_tripped"] is True
print("[OK] Security Foundation verified: Canary trap trip detected and recorded!")

# 7. Hospital Operations: 500 beds, 15 departments, ICU, ambulances
r = requests.get(f"{base_url}/api/v1/operations/summary", headers=h_doc)
summary = r.json()
assert summary["total_beds"] == 500
assert summary["total_departments"] == 15
assert summary["total_icu_beds"] == 50
print(f"[OK] Hospital Operations verified: 500 Beds ({summary['occupied_beds']} occupied, {summary['available_beds']} available), 15 Depts.")

# 8. Staff and Duty Rosters
r = requests.get(f"{base_url}/api/v1/staff", headers=h_admin)
assert r.status_code == 200 and len(r.json()) >= 15
r = requests.get(f"{base_url}/api/v1/staff/rosters", headers=h_doc)
assert r.status_code == 200
print("[OK] Staff directory and duty rosters verified.")

# 9. Billing calculate & invoices
r = requests.post(f"{base_url}/api/v1/billing/calculate?patient_id={p1['id']}&items_total=2500&discount=100", headers=h_bill)
assert r.status_code == 200
assert "patient_responsibility" in r.json()
print("[OK] Billing calculation verified.")

# 10. All 7 Scenarios Activation
scenarios = ["SCENARIO_A", "SCENARIO_B", "SCENARIO_C", "SCENARIO_D", "SCENARIO_E", "SCENARIO_F", "SCENARIO_G"]
for sc in scenarios:
    r = requests.post(f"{base_url}/api/v1/simulation/scenarios/activate", json={"scenario_code": sc}, headers=h_admin)
    assert r.status_code == 200 and r.json()["success"] is True
print("[OK] All 7 baseline simulation scenarios activated and verified.")

# Reset to Scenario A
requests.post(f"{base_url}/api/v1/simulation/scenarios/activate", json={"scenario_code": "SCENARIO_A"}, headers=h_admin)

# 11. Environment Controls
r = requests.post(f"{base_url}/api/v1/simulation/controls", json={"action": "toggle_subsystem", "target": "LIS", "value": "degraded"}, headers=h_admin)
assert r.status_code == 200 and r.json()["success"] is True
print("[OK] Interactive environment control verified.")

# 12. HL7 FHIR R4 interoperability
r = requests.get(f"{base_url}/api/v1/fhir/Patient/{p1['id']}", headers=h_doc)
assert r.status_code == 200 and r.json()["resourceType"] == "Patient"
r = requests.get(f"{base_url}/api/v1/fhir/Practitioner/1", headers=h_doc)
assert r.status_code == 200 and r.json()["resourceType"] == "Practitioner"
r = requests.get(f"{base_url}/api/v1/fhir/Encounter/1", headers=h_doc)
assert r.status_code == 200 and r.json()["resourceType"] == "Encounter"
print("[OK] HL7 FHIR R4 resources verified (Patient, Practitioner, Encounter).")

# 13. Cryptographic Merkle Hash Chain Audit Verification
r = requests.get(f"{base_url}/api/v1/audit/verify", headers=h_sec)
assert r.status_code == 200 and r.json()["status"] == "valid"
print(f"[OK] Audit ledger cryptographic integrity verified ({r.json()['total_records']} immutable chained blocks).")

# 14. Phase 2: HOSA Prompt Execution via REST API
payload_hosa = {
    "user_prompt": "Summarize encounters for Patient #1.",
    "requesting_actor": "dr_elena_vance",
    "active_patient_id": 1
}
r = requests.post(f"{base_url}/api/v1/agent/hosa/prompt", json=payload_hosa, headers=h_doc)
assert r.status_code == 200 and r.json()["status"] == "SUCCESS"
print("[OK] Phase 2: HOSA Agent Prompt execution verified via REST API.")

# 15. Phase 2: Agent Tools Registry (18 Tools)
r = requests.get(f"{base_url}/api/v1/agent/tools")
assert r.status_code == 200 and len(r.json()) >= 18
print(f"[OK] Phase 2: Tool Gateway Registry verified ({len(r.json())} operational tools).")

# 16. Phase 2: AAVA Adversarial Test Execution via REST API (TEST-01)
r = requests.post(f"{base_url}/api/v1/agent/aava/run-test/TEST-01")
assert r.status_code == 200 and r.json()["status"] == "PASSED"
print("[OK] Phase 2: AAVA Adversarial Test Vector (TEST-01) executed and verified via REST API.")

# 17. Phase 2: Security Evaluation Analytics & Metrics
r = requests.get(f"{base_url}/api/v1/agent/analytics")
assert r.status_code == 200 and "summary" in r.json()
print(f"[OK] Phase 2: Security Evaluation Analytics verified (ASR: {r.json()['summary']['attack_success_rate_percentage']}%).")

print("\n=======================================================")
print("  >>> ALL 17 TEST SUITES PASSED WITH 100% SUCCESS <<<  ")
print("=======================================================")
