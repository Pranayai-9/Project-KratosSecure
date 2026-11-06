from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.schemas.patient import (
    PatientSummary, PatientProfile, EncounterOut,
    LabReportOut, RadiologyReportOut
)
from backend.app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patient Management"])

@router.get("", response_model=List[PatientSummary])
def search_patients(
    query: Optional[str] = Query(None, description="Search by name, MRN, or phone"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Search synthetic patient directory.
    Enforces RBAC: Doctors, Nurses, Medical Records Officers, AI Agent.
    Billing Officers receive limited demographics only.
    """
    return PatientService.search_patients(db, actor, query, limit)

@router.get("/{patient_id}", response_model=PatientProfile)
def get_patient_profile(
    patient_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve comprehensive patient profile including clinical history and active consents.
    Enforces RBAC + Consent verification.
    """
    return PatientService.get_patient_profile(db, actor, patient_id)

@router.get("/{patient_id}/encounters", response_model=List[EncounterOut])
def get_encounter_history(
    patient_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve all historical and active hospital encounters for a patient.
    """
    return PatientService.get_encounter_history(db, actor, patient_id)

@router.get("/{patient_id}/medical-history")
def get_medical_history(
    patient_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve ICD-10 medical conditions, allergies, and active medication requests.
    """
    return PatientService.get_medical_history(db, actor, patient_id)

@router.get("/{patient_id}/lab-reports", response_model=List[LabReportOut])
def get_lab_reports(
    patient_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve laboratory reports (LOINC coded).
    """
    return PatientService.get_lab_reports(db, actor, patient_id)

@router.get("/{patient_id}/radiology-reports", response_model=List[RadiologyReportOut])
def get_radiology_reports(
    patient_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Retrieve diagnostic radiology reports and imaging impressions.
    """
    return PatientService.get_radiology_reports(db, actor, patient_id)
