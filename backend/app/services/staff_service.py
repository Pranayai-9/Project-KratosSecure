from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.staff import StaffMember, Qualification, DutyRoster
from backend.app.schemas.staff import DutyRosterCreate
from backend.app.security.rbac import check_permission
from backend.app.api.deps import ActorContext

class StaffService:
    @staticmethod
    def get_all_staff(db: Session, actor: ActorContext, department_id: Optional[int] = None, role: Optional[str] = None) -> List[StaffMember]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="StaffMember" if actor.role == "Hospital Administrator" else "DutyRoster",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        q = db.query(StaffMember)
        if department_id:
            q = q.filter(StaffMember.department_id == department_id)
        if role:
            q = q.filter(StaffMember.role == role)
        return q.all()

    @staticmethod
    def get_staff_details(db: Session, actor: ActorContext, staff_id: int) -> StaffMember:
        member = db.query(StaffMember).filter(StaffMember.id == staff_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Staff member not found")

        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="StaffMember" if actor.role == "Hospital Administrator" else "DutyRoster",
            action="READ",
            resource_id=str(staff_id),
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        return member

    @staticmethod
    def get_duty_rosters(db: Session, actor: ActorContext, shift_date: Optional[str] = None) -> List[DutyRoster]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="DutyRoster",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        q = db.query(DutyRoster)
        if shift_date:
            q = q.filter(DutyRoster.shift_date == shift_date)
        return q.all()

    @staticmethod
    def create_duty_roster_draft(db: Session, actor: ActorContext, data: DutyRosterCreate) -> DutyRoster:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="DutyRoster",
            action="CREATE",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        roster = DutyRoster(
            staff_id=data.staff_id,
            department_id=data.department_id,
            shift_date=data.shift_date,
            shift_type=data.shift_type,
            status="scheduled",
            notes=data.notes
        )
        db.add(roster)
        db.commit()
        db.refresh(roster)
        return roster
