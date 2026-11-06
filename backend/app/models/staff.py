import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base

class StaffMember(Base):
    __tablename__ = "staff_members"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(32), unique=True, index=True, nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    role = Column(String(64), nullable=False)  # Doctor, Nurse, Lab Technician, Pharmacist, Billing Officer, Medical Records Officer, Hospital Administrator, IT Administrator, Security Officer, Healthcare AI Agent, Adversarial Agent
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    specialization = Column(String(128), nullable=True)
    license_number = Column(String(64), nullable=True)
    email = Column(String(128), unique=True, nullable=False)
    phone = Column(String(32), nullable=False)
    is_available = Column(Boolean, default=True)
    current_shift = Column(String(32), default="Morning")  # Morning, Evening, Night, On-Call, Off-Duty
    security_clearance = Column(String(32), default="Level 2")  # Level 1 (Basic), Level 2 (Clinical/Operational), Level 3 (Admin), Level 4 (SecOps)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    department = relationship("Department", back_populates="staff")
    qualifications = relationship("Qualification", back_populates="staff", cascade="all, delete-orphan")
    duty_rosters = relationship("DutyRoster", back_populates="staff", cascade="all, delete-orphan")


class Qualification(Base):
    __tablename__ = "qualifications"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_members.id"), nullable=False, index=True)
    degree = Column(String(128), nullable=False)
    institution = Column(String(256), nullable=False)
    year = Column(Integer, nullable=False)
    certifications = Column(String(256), nullable=True)

    staff = relationship("StaffMember", back_populates="qualifications")


class DutyRoster(Base):
    __tablename__ = "duty_rosters"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_members.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    shift_date = Column(String(16), nullable=False)  # YYYY-MM-DD
    shift_type = Column(String(32), nullable=False)  # Morning (07:00-15:00), Evening (15:00-23:00), Night (23:00-07:00)
    status = Column(String(32), default="scheduled")  # scheduled, on-duty, completed, absent, on-call
    notes = Column(Text, nullable=True)

    staff = relationship("StaffMember", back_populates="duty_rosters")
    department = relationship("Department")
