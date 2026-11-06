import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    mrn = Column(String(32), unique=True, index=True, nullable=False)  # Medical Record Number
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    dob = Column(String(16), nullable=False)
    gender = Column(String(16), nullable=False)
    phone = Column(String(32), nullable=False)
    email = Column(String(128), nullable=False)
    address = Column(String(256), nullable=False)
    blood_group = Column(String(8), nullable=False)
    emergency_contact = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    allergies = relationship("Allergy", back_populates="patient", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="patient", cascade="all, delete-orphan")
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("MedicationRequest", back_populates="patient", cascade="all, delete-orphan")
    lab_reports = relationship("LabReport", back_populates="patient", cascade="all, delete-orphan")
    radiology_reports = relationship("RadiologyReport", back_populates="patient", cascade="all, delete-orphan")
    discharge_summaries = relationship("DischargeSummary", back_populates="patient", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="patient", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="patient", cascade="all, delete-orphan")


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    allergen = Column(String(128), nullable=False)
    reaction = Column(String(256), nullable=False)
    severity = Column(String(32), default="Moderate")  # Mild, Moderate, Severe, Life-Threatening
    recorded_date = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="allergies")


class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    code = Column(String(32), nullable=False)  # ICD-10
    name = Column(String(256), nullable=False)
    category = Column(String(64), nullable=False)
    clinical_status = Column(String(32), default="active")  # active, resolved, recurrence
    onset_date = Column(String(32), nullable=True)

    patient = relationship("Patient", back_populates="conditions")


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    encounter_number = Column(String(32), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    attending_doctor_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True, index=True)
    encounter_type = Column(String(32), nullable=False)  # emergency, inpatient, outpatient, icu
    status = Column(String(32), default="in-progress")  # planned, arrived, in-progress, discharged, transferred, cancelled
    chief_complaint = Column(Text, nullable=False)
    admission_date = Column(DateTime, default=datetime.datetime.utcnow)
    discharge_date = Column(DateTime, nullable=True)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)
    triage_acuity = Column(Integer, default=3)  # 1 (Resuscitation) to 5 (Non-urgent)

    patient = relationship("Patient", back_populates="encounters")
    department = relationship("Department", foreign_keys=[department_id])
    attending_doctor = relationship("StaffMember", foreign_keys=[attending_doctor_id])
    bed = relationship("Bed", foreign_keys=[bed_id])
    medications = relationship("MedicationRequest", back_populates="encounter")
    lab_reports = relationship("LabReport", back_populates="encounter")
    radiology_reports = relationship("RadiologyReport", back_populates="encounter")
    discharge_summary = relationship("DischargeSummary", back_populates="encounter", uselist=False)
    invoices = relationship("Invoice", back_populates="encounter")


class MedicationRequest(Base):
    __tablename__ = "medication_requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True)
    prescriber_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    medication_name = Column(String(128), nullable=False)
    rxnorm_code = Column(String(32), nullable=True)
    dosage = Column(String(64), nullable=False)
    frequency = Column(String(64), nullable=False)
    route = Column(String(32), default="oral")
    status = Column(String(32), default="active")  # active, completed, stopped, held
    is_controlled_substance = Column(Boolean, default=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="medications")
    encounter = relationship("Encounter", back_populates="medications")
    prescriber = relationship("StaffMember", foreign_keys=[prescriber_id])


class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(32), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True)
    order_doctor_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    performer_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    test_code = Column(String(32), nullable=False)  # LOINC code
    test_name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)  # hematology, biochemistry, microbiology, pathology
    status = Column(String(32), default="final")  # ordered, processing, final, amended
    specimen = Column(String(64), nullable=True)
    collection_time = Column(DateTime, default=datetime.datetime.utcnow)
    result_data = Column(JSON, nullable=False)  # Detailed parameters, values, units, reference range
    interpretation = Column(String(32), default="Normal")  # Normal, High, Low, Critical
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="lab_reports")
    encounter = relationship("Encounter", back_populates="lab_reports")
    order_doctor = relationship("StaffMember", foreign_keys=[order_doctor_id])
    performer = relationship("StaffMember", foreign_keys=[performer_id])


class RadiologyReport(Base):
    __tablename__ = "radiology_reports"

    id = Column(Integer, primary_key=True, index=True)
    accession_number = Column(String(32), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True)
    order_doctor_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    radiologist_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    modality = Column(String(16), nullable=False)  # CT, MRI, X-RAY, US, PET
    study_name = Column(String(128), nullable=False)
    findings = Column(Text, nullable=False)
    impression = Column(Text, nullable=False)
    status = Column(String(32), default="reported")  # scheduled, acquired, reported
    urgent_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="radiology_reports")
    encounter = relationship("Encounter", back_populates="radiology_reports")
    order_doctor = relationship("StaffMember", foreign_keys=[order_doctor_id])
    radiologist = relationship("StaffMember", foreign_keys=[radiologist_id])


class DischargeSummary(Base):
    __tablename__ = "discharge_summaries"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), unique=True, nullable=False)
    author_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    admission_diagnosis = Column(String(256), nullable=False)
    discharge_diagnosis = Column(String(256), nullable=False)
    summary_text = Column(Text, nullable=False)
    discharge_instructions = Column(Text, nullable=False)
    follow_up_plan = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="discharge_summaries")
    encounter = relationship("Encounter", back_populates="discharge_summary")
    author = relationship("StaffMember", foreign_keys=[author_id])


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    consent_type = Column(String(64), nullable=False)  # treatment, data_sharing_research, external_disclosure, billing_audit
    status = Column(String(32), default="active")  # active, revoked, expired
    scope = Column(String(128), default="all_clinical_data")
    granted_by = Column(String(64), default="patient")  # patient, legal_guardian, power_of_attorney
    valid_from = Column(DateTime, default=datetime.datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="consents")
