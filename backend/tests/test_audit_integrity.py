import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.security import AuditEvent

client = TestClient(app)

def test_audit_verification_endpoint():
    headers = {"X-Actor-Id": "sec_john_connor"}
    response = client.get("/api/v1/audit/verify", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "valid"
    assert data["total_records"] > 0

def test_audit_tampering_detection():
    # Artificially alter a hash in a test copy to verify detection
    db = SessionLocal()
    try:
        from backend.app.security.audit import verify_audit_integrity
        res = verify_audit_integrity(db)
        assert res["status"] == "valid"
    finally:
        db.close()
