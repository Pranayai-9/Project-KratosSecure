from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class QualificationOut(BaseModel):
    id: int
    degree: str
    institution: str
    year: int
    certifications: Optional[str] = None
    class Config:
        from_attributes = True

class DutyRosterBase(BaseModel):
    staff_id: int
    department_id: int
    shift_date: str
    shift_type: str
    status: str = "scheduled"
    notes: Optional[str] = None

class DutyRosterCreate(DutyRosterBase):
    pass

class DutyRosterOut(DutyRosterBase):
    id: int
    class Config:
        from_attributes = True

class StaffMemberBase(BaseModel):
    first_name: str
    last_name: str
    role: str
    department_id: int
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    email: str
    phone: str
    is_available: bool = True
    current_shift: str = "Morning"
    security_clearance: str = "Level 2"

class StaffMemberOut(StaffMemberBase):
    id: int
    employee_id: str
    created_at: datetime
    qualifications: List[QualificationOut] = []
    class Config:
        from_attributes = True
