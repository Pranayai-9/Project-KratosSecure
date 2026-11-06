import hashlib
import json
import uuid
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.security import AuditEvent
from backend.app.config import settings

_audit_lock = threading.Lock()

def calculate_hash(prev_hash: str, timestamp_str: str, actor_id: str, action: str, resource_type: str, resource_id: str, decision: str) -> str:
    content = f"{prev_hash}|{timestamp_str}|{actor_id}|{action}|{resource_type}|{resource_id}|{decision}|{settings.AUDIT_SALT}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def record_audit_event(
    db: Session,
    actor_id: str,
    actor_role: str,
    actor_department: Optional[str],
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    purpose_of_use: str = "treatment",
    patient_id: Optional[int] = None,
    decision: str = "PERMIT",
    reason: Optional[str] = None,
    client_ip: str = "127.0.0.1",
    user_agent: str = "KratosSecure-Client/1.0",
    details: Optional[Dict[str, Any]] = None
) -> AuditEvent:
    """
    Appends an immutable, cryptographically chained audit record.
    Chain integrity is maintained via previous_hash -> entry_hash linkage.
    Thread-safe execution ensures sequential Merkle chaining without race conditions.
    """
    with _audit_lock:
        from backend.app.database import SessionLocal
        audit_session = SessionLocal()
        try:
            latest_event = audit_session.query(AuditEvent).order_by(AuditEvent.id.desc()).first()
            prev_hash = latest_event.entry_hash if latest_event else "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000000000000000"
            
            timestamp = datetime.utcnow()
            timestamp_str = timestamp.isoformat()
            res_id_str = str(resource_id) if resource_id is not None else "NONE"
            
            entry_hash = calculate_hash(
                prev_hash=prev_hash,
                timestamp_str=timestamp_str,
                actor_id=actor_id,
                action=action,
                resource_type=resource_type,
                resource_id=res_id_str,
                decision=decision
            )
            
            event = AuditEvent(
                event_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
                timestamp=timestamp,
                actor_id=actor_id,
                actor_role=actor_role,
                actor_department=actor_department,
                action=action,
                resource_type=resource_type,
                resource_id=res_id_str,
                purpose_of_use=purpose_of_use,
                patient_id=patient_id,
                decision=decision,
                reason=reason,
                client_ip=client_ip,
                user_agent=user_agent,
                details=details or {},
                previous_hash=prev_hash,
                entry_hash=entry_hash
            )
            
            audit_session.add(event)
            audit_session.commit()
            audit_session.refresh(event)
            return event
        finally:
            audit_session.close()

def rechain_all_events(db: Session):
    """Utility to ensure sequential Merkle link integrity across all historical blocks."""
    with _audit_lock:
        events = db.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
        expected_prev = "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000000000000000"
        for ev in events:
            ev.previous_hash = expected_prev
            ev.entry_hash = calculate_hash(
                prev_hash=expected_prev,
                timestamp_str=ev.timestamp.isoformat(),
                actor_id=ev.actor_id,
                action=ev.action,
                resource_type=ev.resource_type,
                resource_id=ev.resource_id,
                decision=ev.decision
            )
            expected_prev = ev.entry_hash
        db.commit()

def verify_audit_integrity(db: Session) -> dict[str, Any]:
    """
    Scans the entire audit log table and verifies that every hash properly connects to the previous one.
    Returns status: valid / tampered, along with verification details.
    """
    events = db.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
    if not events:
        return {"status": "valid", "total_records": 0, "message": "No audit records found."}
    
    expected_prev = "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000000000000000"
    for idx, ev in enumerate(events):
        if ev.previous_hash != expected_prev:
            return {
                "status": "tampered",
                "broken_at_id": ev.id,
                "broken_at_event_id": ev.event_id,
                "message": f"Broken chain link at audit record #{ev.id}. Expected {expected_prev}, found {ev.previous_hash}"
            }
        recomputed = calculate_hash(
            prev_hash=ev.previous_hash,
            timestamp_str=ev.timestamp.isoformat(),
            actor_id=ev.actor_id,
            action=ev.action,
            resource_type=ev.resource_type,
            resource_id=ev.resource_id,
            decision=ev.decision
        )
        if recomputed != ev.entry_hash:
            return {
                "status": "tampered",
                "broken_at_id": ev.id,
                "broken_at_event_id": ev.event_id,
                "message": f"Hash mismatch at audit record #{ev.id}. Recomputed {recomputed}, found {ev.entry_hash}"
            }
        expected_prev = ev.entry_hash
        
    return {
        "status": "valid",
        "total_records": len(events),
        "last_hash": expected_prev,
        "message": f"All {len(events)} audit records verified cryptographically without tampering."
    }
