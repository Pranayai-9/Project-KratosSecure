from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.models.system import SubsystemStatus
from backend.app.models.security import CanarySecret
from backend.app.schemas.security import SubsystemStatusOut, SubsystemUpdate, CanarySecretOut
from backend.app.security.rbac import check_permission

router = APIRouter(prefix="/system", tags=["System Management & Telemetry"])

@router.get("/status", response_model=List[SubsystemStatusOut])
def get_system_status(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve operational health, latency, and uptime of hospital infrastructure subsystems."""
    check_permission(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        actor_department=actor.department_code,
        resource_type="SystemStatus",
        action="READ",
        purpose_of_use=actor.purpose_of_use,
        client_ip=actor.client_ip
    )
    return db.query(SubsystemStatus).all()

@router.patch("/subsystems/{code}", response_model=SubsystemStatusOut)
def update_subsystem_status(
    code: str,
    update: SubsystemUpdate,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Update subsystem health status (e.g. simulate offline or degraded state)."""
    check_permission(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        actor_department=actor.department_code,
        resource_type="Subsystem",
        action="UPDATE",
        purpose_of_use=actor.purpose_of_use,
        client_ip=actor.client_ip
    )
    sub = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == code.upper()).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subsystem not found")
        
    sub.status = update.status
    if update.details:
        sub.details = update.details
    if update.status == "degraded":
        sub.latency_ms = 450
    elif update.status == "offline":
        sub.latency_ms = 9999
    else:
        sub.latency_ms = 12

    db.commit()
    db.refresh(sub)
    return sub

@router.get("/canaries", response_model=List[CanarySecretOut])
def get_canary_secrets(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve canary secret traps status.
    Strictly restricted to Security Officer and IT Administrator.
    """
    check_permission(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        actor_department=actor.department_code,
        resource_type="CanarySecret",
        action="READ",
        purpose_of_use=actor.purpose_of_use,
        client_ip=actor.client_ip
    )
    return db.query(CanarySecret).all()
