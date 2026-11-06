from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.models.security import AuditEvent
from backend.app.schemas.security import AuditEventOut
from backend.app.security.rbac import check_permission
from backend.app.security.audit import verify_audit_integrity

router = APIRouter(prefix="/audit", tags=["Security & Audit Ledger"])

@router.get("/events", response_model=List[AuditEventOut])
def get_audit_events(
    decision: Optional[str] = Query(None, description="Filter by decision: PERMIT, DENY, TRAPPED"),
    actor_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve immutable audit event trail.
    Strictly enforced RBAC: Security Officers, Administrators, and authorized actors.
    """
    check_permission(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        actor_department=actor.department_code,
        resource_type="AuditEvent",
        action="READ",
        purpose_of_use=actor.purpose_of_use,
        client_ip=actor.client_ip
    )
    q = db.query(AuditEvent)
    if decision:
        q = q.filter(AuditEvent.decision == decision)
    if actor_id:
        q = q.filter(AuditEvent.actor_id == actor_id)
    if resource_type:
        q = q.filter(AuditEvent.resource_type == resource_type)

    return q.order_by(AuditEvent.id.desc()).limit(limit).all()

@router.get("/verify")
def verify_audit_ledger(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Cryptographic verification endpoint.
    Recalculates SHA-256 Merkle link chain across every audit record from genesis to present.
    Detects any database tampering, row deletion, or unauthorized modification.
    """
    check_permission(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        actor_department=actor.department_code,
        resource_type="AuditEvent",
        action="VERIFY",
        purpose_of_use=actor.purpose_of_use,
        client_ip=actor.client_ip
    )
    return verify_audit_integrity(db)
