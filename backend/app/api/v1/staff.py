from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.schemas.staff import StaffMemberOut, DutyRosterOut, DutyRosterCreate
from backend.app.services.staff_service import StaffService

router = APIRouter(prefix="/staff", tags=["Staff Management"])

@router.get("", response_model=List[StaffMemberOut])
def get_staff_directory(
    department_id: Optional[int] = Query(None),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve hospital staff directory, credentials, and departmental assignments."""
    return StaffService.get_all_staff(db, actor, department_id, role)

@router.get("/rosters", response_model=List[DutyRosterOut])
def get_duty_rosters(
    shift_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve scheduled duty rosters across departments."""
    return StaffService.get_duty_rosters(db, actor, shift_date)

@router.post("/rosters", response_model=DutyRosterOut)
def create_duty_roster_draft(
    data: DutyRosterCreate,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Create a draft shift roster assignment."""
    return StaffService.create_duty_roster_draft(db, actor, data)

@router.get("/{staff_id}", response_model=StaffMemberOut)
def get_staff_details(
    staff_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve detailed staff profile and qualifications."""
    return StaffService.get_staff_details(db, actor, staff_id)
