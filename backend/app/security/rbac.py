from typing import Optional, Dict, Set, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.security.audit import record_audit_event
from backend.app.security.consent import validate_patient_consent

# Matrix of Allowed Actions per Role: {Role: {ResourceType: {AllowedActions}}}
ROLE_PERMISSIONS: Dict[str, Dict[str, Set[str]]] = {
    "Doctor": {
        "Patient": {"READ", "SEARCH", "CREATE"},
        "Encounter": {"READ", "CREATE", "UPDATE"},
        "Condition": {"READ", "CREATE", "UPDATE"},
        "Allergy": {"READ", "CREATE"},
        "MedicationRequest": {"READ", "CREATE", "UPDATE"},
        "LabReport": {"READ", "ORDER"},
        "RadiologyReport": {"READ", "ORDER"},
        "DischargeSummary": {"READ", "CREATE", "UPDATE"},
        "Consent": {"READ"},
        "Bed": {"READ"},
        "Department": {"READ"},
        "Equipment": {"READ"},
        "DutyRoster": {"READ"},
        "Invoice": {"READ"}, # Limited read for insurance pre-auth context
    },
    "Nurse": {
        "Patient": {"READ", "SEARCH"},
        "Encounter": {"READ", "UPDATE"},
        "Condition": {"READ"},
        "Allergy": {"READ", "CREATE"},
        "MedicationRequest": {"READ", "ADMINISTER"},
        "LabReport": {"READ", "COLLECT"},
        "RadiologyReport": {"READ"},
        "DischargeSummary": {"READ"},
        "Consent": {"READ"},
        "Bed": {"READ", "UPDATE"},
        "Department": {"READ"},
        "Equipment": {"READ", "UPDATE"},
        "DutyRoster": {"READ"},
    },
    "Lab Technician": {
        "Patient": {"SEARCH"}, # minimal identification only
        "LabReport": {"READ", "UPDATE", "PERFORM"},
        "Equipment": {"READ", "UPDATE"},
        "Department": {"READ"},
        "DutyRoster": {"READ"},
    },
    "Pharmacist": {
        "Patient": {"SEARCH"}, # minimal identification only
        "MedicationRequest": {"READ", "DISPENSE", "VERIFY"},
        "MedicineInventory": {"READ", "UPDATE"},
        "Department": {"READ"},
        "DutyRoster": {"READ"},
    },
    "Billing Officer": {
        "Patient": {"SEARCH"}, # Demographics only for billing
        "Invoice": {"READ", "CREATE", "UPDATE", "CALCULATE"},
        "Payment": {"READ", "CREATE"},
        "Insurance": {"READ", "CREATE", "UPDATE"},
        "Department": {"READ"},
        "DutyRoster": {"READ"},
        # Explicitly NO clinical records access (LabReport, Radiology, Conditions, Medications)
    },
    "Medical Records Officer": {
        "Patient": {"READ", "SEARCH", "CREATE", "UPDATE"},
        "Encounter": {"READ"},
        "Consent": {"READ", "UPDATE"},
        "DischargeSummary": {"READ"},
        "Department": {"READ"},
    },
    "Hospital Administrator": {
        "Department": {"READ", "UPDATE"},
        "Bed": {"READ", "UPDATE"},
        "Equipment": {"READ", "UPDATE"},
        "Ambulance": {"READ", "UPDATE"},
        "StaffMember": {"READ", "UPDATE"},
        "DutyRoster": {"READ", "CREATE", "UPDATE"},
        "BloodInventory": {"READ"},
        "MedicineInventory": {"READ"},
        "Invoice": {"READ"},
        "SystemStatus": {"READ"},
        # Cannot read private clinical notes or modify clinical orders
    },
    "IT Administrator": {
        "SystemStatus": {"READ", "UPDATE", "RESTART"},
        "Subsystem": {"READ", "UPDATE"},
        "Network": {"READ", "UPDATE"},
        "Department": {"READ"},
        "Equipment": {"READ", "UPDATE"},
        "CanarySecret": {"READ"},
    },
    "Security Officer": {
        "AuditEvent": {"READ", "VERIFY"},
        "CanarySecret": {"READ", "RESET"},
        "UserIdentity": {"READ", "REVOKE"},
        "SystemStatus": {"READ"},
    },
    "Healthcare AI Agent": {
        "Patient": {"READ", "SEARCH"},
        "Encounter": {"READ"},
        "Condition": {"READ"},
        "Allergy": {"READ"},
        "MedicationRequest": {"READ", "DRAFT_ORDER"}, # cannot direct dispense
        "LabReport": {"READ", "DRAFT_ORDER"},
        "RadiologyReport": {"READ"},
        "Bed": {"READ"},
        "Department": {"READ"},
        "DutyRoster": {"READ"},
        "Invoice": {"READ", "DRAFT_INVOICE"}, # cannot self-approve write-offs
        # AI CANNOT delete audit logs, cannot alter user roles, cannot bypass human approval
    },
    "Adversarial Agent": {
        # Empty set: No legitimate permissions
    }
}

# Operations that strictly require human confirmation/approval
HUMAN_APPROVAL_REQUIRED = {
    ("MedicationRequest", "DISPENSE_CONTROLLED_SUBSTANCE"),
    ("Invoice", "WRITE_OFF_DEBT"),
    ("Patient", "PURGE_RECORD"),
    ("AuditEvent", "DELETE_LOG"),  # Forbidden universally
    ("SystemConfig", "DISABLE_SECURITY_CONTROLS")
}

def check_permission(
    db: Session,
    actor_id: str,
    actor_role: str,
    actor_department: Optional[str],
    resource_type: str,
    action: str,
    resource_id: Optional[str] = None,
    patient_id: Optional[int] = None,
    purpose_of_use: str = "treatment",
    client_ip: str = "127.0.0.1",
    user_agent: str = "KratosSecure-Client/1.0"
) -> bool:
    """
    Evaluates RBAC, Consent, and System Boundaries.
    Logs every check (PERMIT or DENY) directly to the immutable audit ledger.
    Raises HTTPException(403) on violation.
    """
    # 1. Absolute Invariant: Nobody, not even IT Admin or AI, can delete or truncate audit events
    if resource_type == "AuditEvent" and action in ("DELETE", "TRUNCATE", "MODIFY"):
        record_audit_event(
            db=db,
            actor_id=actor_id,
            actor_role=actor_role,
            actor_department=actor_department,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose_of_use=purpose_of_use,
            patient_id=patient_id,
            decision="DENY",
            reason="SECURITY VIOLATION: Audit event logs are append-only and cryptographically immutable.",
            client_ip=client_ip,
            user_agent=user_agent
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Audit events are immutable. Deletion or modification is strictly barred."
        )

    # 2. Check if human approval is required for AI or automatic calls
    if (resource_type, action) in HUMAN_APPROVAL_REQUIRED:
        if actor_role in ("Healthcare AI Agent", "Adversarial Agent"):
            record_audit_event(
                db=db,
                actor_id=actor_id,
                actor_role=actor_role,
                actor_department=actor_department,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                purpose_of_use=purpose_of_use,
                patient_id=patient_id,
                decision="DENY",
                reason=f"Human approval required for sensitive action '{action}' on '{resource_type}'. Autonomous execution blocked.",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action '{action}' on '{resource_type}' requires verified human approval."
            )

    # 3. RBAC Matrix Check
    role_rules = ROLE_PERMISSIONS.get(actor_role, {})
    resource_rules = role_rules.get(resource_type, set())
    
    if action not in resource_rules:
        record_audit_event(
            db=db,
            actor_id=actor_id,
            actor_role=actor_role,
            actor_department=actor_department,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose_of_use=purpose_of_use,
            patient_id=patient_id,
            decision="DENY",
            reason=f"Role '{actor_role}' does not possess permission '{action}' for resource '{resource_type}'.",
            client_ip=client_ip,
            user_agent=user_agent
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access Denied: Role '{actor_role}' is not authorized to {action} {resource_type}."
        )

    # 4. Consent Validation (if patient_id is involved)
    if patient_id is not None and resource_type in ("Patient", "LabReport", "RadiologyReport", "Condition", "MedicationRequest"):
        consent_ok, consent_msg = validate_patient_consent(db, patient_id, purpose_of_use, action)
        if not consent_ok:
            record_audit_event(
                db=db,
                actor_id=actor_id,
                actor_role=actor_role,
                actor_department=actor_department,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                purpose_of_use=purpose_of_use,
                patient_id=patient_id,
                decision="DENY",
                reason=f"Consent restriction: {consent_msg}",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Consent Violation: {consent_msg}"
            )

    # 5. Permission Granted: Log success
    record_audit_event(
        db=db,
        actor_id=actor_id,
        actor_role=actor_role,
        actor_department=actor_department,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        purpose_of_use=purpose_of_use,
        patient_id=patient_id,
        decision="PERMIT",
        reason=f"Authorized under role '{actor_role}'.",
        client_ip=client_ip,
        user_agent=user_agent
    )
    return True
