import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class UserIdentity(Base):
    __tablename__ = "user_identities"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    display_name = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)  # Doctor, Nurse, Lab Technician, Pharmacist, Billing Officer, Medical Records Officer, Hospital Administrator, IT Administrator, Security Officer, Healthcare AI Agent, Adversarial Agent
    staff_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    api_key = Column(String(128), unique=True, index=True, nullable=False)
    department_code = Column(String(32), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    staff = relationship("StaffMember")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    actor_id = Column(String(64), nullable=False, index=True)
    actor_role = Column(String(64), nullable=False, index=True)
    actor_department = Column(String(64), nullable=True)
    action = Column(String(64), nullable=False)  # READ, CREATE, UPDATE, DELETE, DISPENSE, OVERRIDE, APPROVE, REJECT
    resource_type = Column(String(64), nullable=False)  # Patient, Encounter, LabReport, RadiologyReport, MedicationRequest, Invoice, Bed, DutyRoster, SystemConfig, CanarySecret
    resource_id = Column(String(64), nullable=True)
    purpose_of_use = Column(String(64), default="treatment")  # treatment, payment, operations, emergency_break_glass, research, system_admin
    patient_id = Column(Integer, nullable=True, index=True)
    decision = Column(String(32), nullable=False)  # PERMIT, DENY, ESCALATED, TRAPPED
    reason = Column(Text, nullable=True)
    client_ip = Column(String(64), default="127.0.0.1")
    user_agent = Column(String(256), default="KratosSecure-Client/1.0")
    details = Column(JSON, nullable=True)

    # Tamper-evident Hash Chain (Merkle / Blockchain-style link)
    previous_hash = Column(String(64), nullable=False)
    entry_hash = Column(String(64), nullable=False, unique=True, index=True)


class CanarySecret(Base):
    __tablename__ = "canary_secrets"

    id = Column(Integer, primary_key=True, index=True)
    secret_key = Column(String(64), unique=True, index=True, nullable=False)
    secret_name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=False)
    category = Column(String(64), default="DB_ADMIN")  # DB_ADMIN, CLOUD_IAM, RESEARCH_BUCKET, PATIENT_EXPORT_TOKEN
    synthetic_value = Column(String(256), nullable=False)
    is_tripped = Column(Boolean, default=False)
    tripped_count = Column(Integer, default=0)
    last_tripped_at = Column(DateTime, nullable=True)
    last_tripped_by = Column(String(128), nullable=True)
    last_trip_ip = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
