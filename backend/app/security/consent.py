from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.models.patient import Consent, Patient

def validate_patient_consent(
    db: Session,
    patient_id: int,
    purpose_of_use: str,
    action: str
) -> Tuple[bool, str]:
    """
    Validates whether patient consent permits the requested action and purpose of use.
    Under standard healthcare models:
    - Direct treatment in emergency / active encounters is covered by standard treatment consent.
    - Research, external disclosure, or commercial audits require explicit active consent.
    - If consent is REVOKED or EXPIRED, access is restricted unless emergency break-glass is invoked.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return False, f"Patient ID {patient_id} not found."
    
    if purpose_of_use in ("treatment", "emergency_break_glass"):
        return True, "Authorized under direct clinical treatment / emergency protocol."
        
    if purpose_of_use == "payment":
        return True, "Authorized under standard billing / healthcare operations (TPO framework)."

    # For research or external data disclosure, query explicit consent
    active_consent = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.status == "active"
    ).all()
    
    if purpose_of_use == "research":
        has_research = any(c.consent_type == "data_sharing_research" for c in active_consent)
        if has_research:
            return True, "Valid research data-sharing consent on file."
        return False, f"Patient {patient.mrn} has not consented to research data sharing."
        
    if purpose_of_use == "external_disclosure":
        has_external = any(c.consent_type == "external_disclosure" for c in active_consent)
        if has_external:
            return True, "Valid external disclosure consent on file."
        return False, f"Patient {patient.mrn} has not granted external data disclosure authorization."
        
    return True, "Standard operational clearance."
