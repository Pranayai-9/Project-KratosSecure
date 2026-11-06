from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AllergyBase(BaseModel):
    allergen: str
    reaction: str
    severity: str = "Moderate"

class AllergyOut(AllergyBase):
    id: int
    recorded_date: datetime
    class Config:
        from_attributes = True

class ConditionBase(BaseModel):
    code: str
    name: str
    category: str
    clinical_status: str = "active"
    onset_date: Optional[str] = None

class ConditionOut(ConditionBase):
    id: int
    class Config:
        from_attributes = True

class MedicationRequestBase(BaseModel):
    medication_name: str
    rxnorm_code: Optional[str] = None
    dosage: str
    frequency: str
    route: str = "oral"
    is_controlled_substance: bool = False

class MedicationRequestCreate(MedicationRequestBase):
    encounter_id: Optional[int] = None
    prescriber_id: Optional[int] = None

class MedicationRequestOut(MedicationRequestBase):
    id: int
    patient_id: int
    encounter_id: Optional[int] = None
    prescriber_id: Optional[int] = None
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    class Config:
        from_attributes = True

class LabReportBase(BaseModel):
    test_code: str
    test_name: str
    category: str
    specimen: Optional[str] = None
    result_data: dict[str, Any]
    interpretation: str = "Normal"
    notes: Optional[str] = None

class LabReportOut(LabReportBase):
    id: int
    report_number: str
    patient_id: int
    encounter_id: Optional[int] = None
    order_doctor_id: Optional[int] = None
    performer_id: Optional[int] = None
    status: str
    collection_time: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class RadiologyReportBase(BaseModel):
    modality: str
    study_name: str
    findings: str
    impression: str
    urgent_flag: bool = False

class RadiologyReportOut(RadiologyReportBase):
    id: int
    accession_number: str
    patient_id: int
    encounter_id: Optional[int] = None
    order_doctor_id: Optional[int] = None
    radiologist_id: Optional[int] = None
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class DischargeSummaryBase(BaseModel):
    admission_diagnosis: str
    discharge_diagnosis: str
    summary_text: str
    discharge_instructions: str
    follow_up_plan: str

class DischargeSummaryOut(DischargeSummaryBase):
    id: int
    patient_id: int
    encounter_id: int
    author_id: Optional[int] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ConsentBase(BaseModel):
    consent_type: str
    status: str = "active"
    scope: str = "all_clinical_data"
    granted_by: str = "patient"
    valid_to: Optional[datetime] = None

class ConsentOut(ConsentBase):
    id: int
    patient_id: int
    valid_from: datetime
    created_at: datetime
    class Config:
        from_attributes = True

class EncounterBase(BaseModel):
    encounter_type: str  # emergency, inpatient, outpatient, icu
    chief_complaint: str
    triage_acuity: int = 3

class EncounterCreate(EncounterBase):
    patient_id: int
    department_id: int
    attending_doctor_id: Optional[int] = None
    bed_id: Optional[int] = None

class EncounterOut(EncounterBase):
    id: int
    encounter_number: str
    patient_id: int
    department_id: int
    attending_doctor_id: Optional[int] = None
    bed_id: Optional[int] = None
    status: str
    admission_date: datetime
    discharge_date: Optional[datetime] = None
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    dob: str
    gender: str
    phone: str
    email: str
    address: str
    blood_group: str
    emergency_contact: Optional[str] = None

class PatientCreate(PatientBase):
    mrn: Optional[str] = None

class PatientSummary(PatientBase):
    id: int
    mrn: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class PatientProfile(PatientSummary):
    allergies: List[AllergyOut] = []
    conditions: List[ConditionOut] = []
    encounters: List[EncounterOut] = []
    medications: List[MedicationRequestOut] = []
    lab_reports: List[LabReportOut] = []
    radiology_reports: List[RadiologyReportOut] = []
    consents: List[ConsentOut] = []
    class Config:
        from_attributes = True
