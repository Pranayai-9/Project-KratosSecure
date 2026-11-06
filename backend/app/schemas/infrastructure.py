from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class BedOut(BaseModel):
    id: int
    bed_number: str
    department_id: int
    room_number: str
    bed_type: str
    is_occupied: bool
    current_patient_id: Optional[int] = None
    has_ventilator: bool
    has_cardiac_monitor: bool
    status: str
    class Config:
        from_attributes = True

class DepartmentOut(BaseModel):
    id: int
    code: str
    name: str
    building: str
    floor: str
    head_of_department: Optional[str] = None
    total_beds: int
    status: str
    current_workload: str
    wait_time_minutes: int
    description: Optional[str] = None
    class Config:
        from_attributes = True

class OperatingTheatreOut(BaseModel):
    id: int
    ot_code: str
    name: str
    ot_type: str
    status: str
    current_surgeon: Optional[str] = None
    current_procedure: Optional[str] = None
    class Config:
        from_attributes = True

class DiagnosticEquipmentOut(BaseModel):
    id: int
    equipment_code: str
    name: str
    modality: str
    location: str
    status: str
    calibration_date: datetime
    scheduled_procedures_today: int
    class Config:
        from_attributes = True

class MedicalEquipmentOut(BaseModel):
    id: int
    equipment_code: str
    equipment_type: str
    department_id: int
    status: str
    battery_level: int
    class Config:
        from_attributes = True

class AmbulanceOut(BaseModel):
    id: int
    vehicle_number: str
    ambulance_type: str
    status: str
    driver_name: str
    paramedic_name: str
    current_location: str
    class Config:
        from_attributes = True

class BloodInventoryOut(BaseModel):
    id: int
    blood_group: str
    units_available: int
    units_reserved: int
    critical_threshold: int
    last_updated: datetime
    class Config:
        from_attributes = True

class MedicineInventoryOut(BaseModel):
    id: int
    item_code: str
    name: str
    category: str
    stock_quantity: int
    reorder_level: int
    unit: str
    is_controlled_substance: bool
    batch_number: str
    expiration_date: str
    location: str
    class Config:
        from_attributes = True

class HospitalCapacitySummary(BaseModel):
    total_beds: int
    occupied_beds: int
    available_beds: int
    occupancy_rate_percentage: float
    total_icu_beds: int
    occupied_icu_beds: int
    available_icu_beds: int
    icu_occupancy_rate_percentage: float
    emergency_admissions_active: int
    emergency_wait_time_minutes: int
    available_ambulances: int
    total_ambulances: int
    operational_departments: int
    total_departments: int
