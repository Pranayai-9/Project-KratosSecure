from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.patient import (
    Patient, Allergy, Condition, Encounter, MedicationRequest,
    LabReport, RadiologyReport, DischargeSummary, Consent
)
from backend.app.models.infrastructure import Bed, Department
from backend.app.security.rbac import check_permission
from backend.app.security.canary import check_canary_trip
from backend.app.api.deps import ActorContext

class PatientService:
    @staticmethod
    def search_patients(
        db: Session,
        actor: ActorContext,
        query: Optional[str] = None,
        limit: int = 50
    ) -> List[Patient]:
        # Canary check on search string
        if query:
            check_canary_trip(db, query, actor.actor_id, actor.role, actor.department_code, actor.client_ip)

        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Patient",
            action="SEARCH",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        
        q = db.query(Patient)
        if query:
            q = q.filter(
                or_(
                    Patient.mrn.ilike(f"%{query}%"),
                    Patient.first_name.ilike(f"%{query}%"),
                    Patient.last_name.ilike(f"%{query}%"),
                    Patient.phone.ilike(f"%{query}%")
                )
            )
        return q.limit(limit).all()

    @staticmethod
    def get_patient_profile(db: Session, actor: ActorContext, patient_id: int) -> Patient:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Patient",
            action="READ",
            patient_id=patient_id,
            resource_id=str(patient_id),
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")
        return patient

    @staticmethod
    def get_encounter_history(db: Session, actor: ActorContext, patient_id: int) -> List[Encounter]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Encounter",
            action="READ",
            patient_id=patient_id,
            resource_id=str(patient_id),
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        return db.query(Encounter).filter(Encounter.patient_id == patient_id).order_by(Encounter.admission_date.desc()).all()

    @staticmethod
    def get_medical_history(db: Session, actor: ActorContext, patient_id: int) -> dict:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Condition",
            action="READ",
            patient_id=patient_id,
            resource_id=str(patient_id),
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        conditions = db.query(Condition).filter(Condition.patient_id == patient_id).all()
        allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
        medications = db.query(MedicationRequest).filter(MedicationRequest.patient_id == patient_id).all()
        return {
            "patient_id": patient_id,
            "conditions": conditions,
            "allergies": allergies,
            "medications": medications
        }

    @staticmethod
    def get_lab_reports(db: Session, actor: ActorContext, patient_id: int) -> List[LabReport]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="LabReport",
            action="READ",
            patient_id=patient_id,
            resource_id=str(patient_id),
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        return db.query(LabReport).filter(LabReport.patient_id == patient_id).order_by(LabReport.collection_time.desc()).all()

    @staticmethod
    def get_radiology_reports(db: Session, actor: ActorContext, patient_id: int) -> List[RadiologyReport]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="RadiologyReport",
            action="READ",
            patient_id=patient_id,
            resource_id=str(patient_id),
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        return db.query(RadiologyReport).filter(RadiologyReport.patient_id == patient_id).order_by(RadiologyReport.created_at.desc()).all()
