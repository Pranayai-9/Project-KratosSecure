from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.models.patient import Patient, Encounter, LabReport, RadiologyReport, MedicationRequest, DischargeSummary, Consent
from backend.app.models.staff import StaffMember
from backend.app.models.security import AuditEvent
from backend.app.services.fhir_exporter import FHIRExporter
from backend.app.security.rbac import check_permission

router = APIRouter(prefix="/fhir", tags=["HL7 FHIR R4 Interoperability"])

@router.get("/Patient/{patient_id}")
def get_fhir_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Patient in HL7 FHIR R4 format."""
    check_permission(
        db=db,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        actor_department=actor.department_code,
        resource_type="Patient",
        action="READ",
        resource_id=str(patient_id),
        patient_id=patient_id,
        purpose_of_use=actor.purpose_of_use,
        client_ip=actor.client_ip
    )
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return FHIRExporter.patient_to_fhir(p)

@router.get("/Practitioner/{staff_id}")
def get_fhir_practitioner(
    staff_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Practitioner in HL7 FHIR R4 format."""
    s = db.query(StaffMember).filter(StaffMember.id == staff_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return FHIRExporter.practitioner_to_fhir(s)

@router.get("/Encounter/{encounter_id}")
def get_fhir_encounter(
    encounter_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Encounter in HL7 FHIR R4 format."""
    e = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return FHIRExporter.encounter_to_fhir(e)

@router.get("/Observation/{lab_id}")
def get_fhir_observation(
    lab_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Laboratory Observation in HL7 FHIR R4 format."""
    l = db.query(LabReport).filter(LabReport.id == lab_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Observation not found")
    return FHIRExporter.lab_to_fhir_observation(l)

@router.get("/DiagnosticReport/{rad_id}")
def get_fhir_diagnostic_report(
    rad_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Radiology DiagnosticReport in HL7 FHIR R4 format."""
    r = db.query(RadiologyReport).filter(RadiologyReport.id == rad_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="DiagnosticReport not found")
    return FHIRExporter.radiology_to_fhir_diagnostic_report(r)

@router.get("/MedicationRequest/{med_id}")
def get_fhir_medication_request(
    med_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export MedicationRequest in HL7 FHIR R4 format."""
    m = db.query(MedicationRequest).filter(MedicationRequest.id == med_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="MedicationRequest not found")
    return FHIRExporter.medication_to_fhir(m)

@router.get("/DocumentReference/{doc_id}")
def get_fhir_document_reference(
    doc_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Discharge Summary DocumentReference in HL7 FHIR R4 format."""
    d = db.query(DischargeSummary).filter(DischargeSummary.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="DocumentReference not found")
    return FHIRExporter.discharge_to_fhir_document(d)

@router.get("/Consent/{consent_id}")
def get_fhir_consent(
    consent_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export Consent in HL7 FHIR R4 format."""
    c = db.query(Consent).filter(Consent.id == consent_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consent not found")
    return FHIRExporter.consent_to_fhir(c)

@router.get("/AuditEvent/{audit_id}")
def get_fhir_audit_event(
    audit_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Export AuditEvent in HL7 FHIR R4 format."""
    a = db.query(AuditEvent).filter(AuditEvent.id == audit_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="AuditEvent not found")
    return FHIRExporter.audit_event_to_fhir(a)
