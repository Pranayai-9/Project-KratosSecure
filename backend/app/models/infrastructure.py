import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    building = Column(String(64), nullable=False)  # Building A, Building B, Building C
    floor = Column(String(16), nullable=False)
    head_of_department = Column(String(128), nullable=True)
    total_beds = Column(Integer, default=0)
    status = Column(String(32), default="operational")  # operational, degraded, closed, emergency_mode
    current_workload = Column(String(32), default="normal")  # low, normal, high, critical
    wait_time_minutes = Column(Integer, default=15)
    description = Column(Text, nullable=True)

    beds = relationship("Bed", back_populates="department")
    staff = relationship("StaffMember", back_populates="department")


class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    bed_number = Column(String(32), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    room_number = Column(String(32), nullable=False)
    bed_type = Column(String(32), default="standard")  # standard, icu, emergency, isolation, pediatric, post_op
    is_occupied = Column(Boolean, default=False)
    current_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    has_ventilator = Column(Boolean, default=False)
    has_cardiac_monitor = Column(Boolean, default=True)
    status = Column(String(32), default="available")  # available, occupied, maintenance, cleaning

    department = relationship("Department", back_populates="beds")
    current_patient = relationship("Patient", foreign_keys=[current_patient_id])


class OperatingTheatre(Base):
    __tablename__ = "operating_theatres"

    id = Column(Integer, primary_key=True, index=True)
    ot_code = Column(String(32), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    ot_type = Column(String(64), default="General Surgery")  # Trauma, Cardiac, Neuro, General, Ortho
    status = Column(String(32), default="available")  # available, in_use, sanitizing, maintenance
    current_surgeon = Column(String(128), nullable=True)
    current_procedure = Column(String(256), nullable=True)


class DiagnosticEquipment(Base):
    __tablename__ = "diagnostic_equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_code = Column(String(32), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    modality = Column(String(32), nullable=False)  # MRI, CT, X-RAY, US, PET
    location = Column(String(64), nullable=False)
    status = Column(String(32), default="available")  # available, in_use, maintenance, offline
    calibration_date = Column(DateTime, default=datetime.datetime.utcnow)
    scheduled_procedures_today = Column(Integer, default=0)


class MedicalEquipment(Base):
    __tablename__ = "medical_equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_code = Column(String(32), unique=True, nullable=False)
    equipment_type = Column(String(64), nullable=False)  # ventilator, infusion_pump, dialysis_machine, defibrillator
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    status = Column(String(32), default="available")  # available, in_use, maintenance, faulty
    battery_level = Column(Integer, default=100)

    department = relationship("Department")


class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(32), unique=True, nullable=False)
    ambulance_type = Column(String(32), default="ALS")  # ALS (Advanced Life Support), BLS (Basic Life Support)
    status = Column(String(32), default="available")  # available, dispatched, en_route_hospital, maintenance
    driver_name = Column(String(64), nullable=False)
    paramedic_name = Column(String(64), nullable=False)
    current_location = Column(String(128), default="Hospital Base")


class BloodInventory(Base):
    __tablename__ = "blood_inventory"

    id = Column(Integer, primary_key=True, index=True)
    blood_group = Column(String(8), unique=True, nullable=False)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    units_available = Column(Integer, default=0)
    units_reserved = Column(Integer, default=0)
    critical_threshold = Column(Integer, default=10)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class MedicineInventory(Base):
    __tablename__ = "medicine_inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(32), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)  # Antibiotic, Analgesic, Cardiovascular, Emergency, Anticoagulant
    stock_quantity = Column(Integer, default=100)
    reorder_level = Column(Integer, default=20)
    unit = Column(String(32), default="tablets")  # vials, ampoules, tablets, infusions
    is_controlled_substance = Column(Boolean, default=False)
    batch_number = Column(String(32), nullable=False)
    expiration_date = Column(String(16), nullable=False)
    location = Column(String(64), default="Central Pharmacy - Bin A")
