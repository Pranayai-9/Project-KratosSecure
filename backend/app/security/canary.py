from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.security import CanarySecret
from backend.app.security.audit import record_audit_event

def check_canary_trip(
    db: Session,
    queried_token: str,
    actor_id: str,
    actor_role: str,
    actor_department: Optional[str],
    client_ip: str = "127.0.0.1"
) -> Optional[CanarySecret]:
    """
    Checks if a queried string or token matches a synthetic canary trap.
    If matched, trips the canary alarm, logs TRAPPED audit event, and returns the CanarySecret.
    """
    if not queried_token:
        return None
        
    canary = db.query(CanarySecret).filter(
        (CanarySecret.secret_key == queried_token) | 
        (CanarySecret.synthetic_value == queried_token)
    ).first()
    
    if canary:
        canary.is_tripped = True
        canary.tripped_count += 1
        canary.last_tripped_at = datetime.utcnow()
        canary.last_tripped_by = f"{actor_id} ({actor_role})"
        canary.last_trip_ip = client_ip
        db.commit()
        
        record_audit_event(
            db=db,
            actor_id=actor_id,
            actor_role=actor_role,
            actor_department=actor_department,
            action="CANARY_TRIP_DETECTED",
            resource_type="CanarySecret",
            resource_id=canary.secret_key,
            purpose_of_use="security_monitoring",
            decision="TRAPPED",
            reason=f"Canary secret '{canary.secret_name}' was accessed or injected by {actor_id}!",
            client_ip=client_ip,
            details={"canary_category": canary.category, "trip_count": canary.tripped_count}
        )
        return canary
        
    return None
