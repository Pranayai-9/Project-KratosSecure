from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.agent.tools import AVAILABLE_TOOLS, ToolDefinition
from backend.app.security.rbac import ROLE_PERMISSIONS, HUMAN_APPROVAL_REQUIRED
from backend.app.security.consent import validate_patient_consent
from backend.app.security.canary import check_canary_trip
from backend.app.security.audit import record_audit_event
from backend.app.api.deps import ActorContext

# Service handlers for executing tools once permitted
from backend.app.services.patient_service import PatientService
from backend.app.services.operations_service import OperationsService
from backend.app.services.billing_service import BillingService
from backend.app.services.staff_service import StaffService

class GatewayInvocationRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    caller_actor: str = "agent_kratos_ai"
    purpose_of_use: str = "treatment"
    active_patient_context: Optional[int] = None
    human_approval_token: Optional[str] = None
    client_ip: str = "127.0.0.1"

class GatewayDecision(BaseModel):
    outcome: str  # ALLOW, DENY, REQUIRE_HUMAN_APPROVAL
    reason: str
    policy_applied: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    audit_event_id: Optional[str] = None
    canary_tripped: bool = False
    timestamp: str

class ToolGateway:
    """
    Zero-Trust Tool Gateway for Healthcare AI Agents.
    All interactions between agents and hospital services must pass through
    this policy validation engine. Direct DB access is barred.
    """

    @staticmethod
    def invoke_tool(db: Session, request: GatewayInvocationRequest) -> GatewayDecision:
        timestamp_str = datetime.utcnow().isoformat()
        tool_name = request.tool_name

        # 1. Tool Existence Check
        if tool_name not in AVAILABLE_TOOLS:
            event = record_audit_event(
                db=db,
                actor_id=request.caller_actor,
                actor_role="Healthcare AI Agent" if "ai" in request.caller_actor else "Unknown",
                actor_department="COMMAND_CTR",
                action="INVALID_TOOL_INVOCATION",
                resource_type="ToolGateway",
                resource_id=tool_name,
                purpose_of_use=request.purpose_of_use,
                decision="DENY",
                reason=f"Tool '{tool_name}' is not registered in the operational gateway.",
                client_ip=request.client_ip
            )
            return GatewayDecision(
                outcome="DENY",
                reason=f"Unknown tool '{tool_name}'",
                policy_applied="TOOL_REGISTRATION_POLICY",
                tool_name=tool_name,
                arguments=request.arguments,
                audit_event_id=event.event_id,
                timestamp=timestamp_str
            )

        tool_def: ToolDefinition = AVAILABLE_TOOLS[tool_name]
        
        # Resolve authentic Actor Role & Department
        standard_personas = {
            "dr_elena_vance": ("Doctor", "IPD"),
            "dr_marcus_brody": ("Doctor", "EMERGENCY"),
            "nurse_sarah_connor": ("Nurse", "ICU"),
            "nurse_david_kim": ("Nurse", "IPD"),
            "tech_rachel_zane": ("Lab Technician", "LAB"),
            "pharm_james_wilson": ("Pharmacist", "PHARMACY"),
            "billing_arthur_dent": ("Billing Officer", "BILLING"),
            "mro_diana_prince": ("Medical Records Officer", "HIM"),
            "admin_sterling_archer": ("Hospital Administrator", "ADMIN"),
            "it_elliot_alderson": ("IT Administrator", "IT_SEC"),
            "sec_john_connor": ("Security Officer", "IT_SEC"),
            "agent_kratos_ai": ("Healthcare AI Agent", "COMMAND_CTR"),
            "adversarial_infiltrator": ("Adversarial Agent", "EXTERNAL"),
        }
        actor_role, actor_dept = standard_personas.get(
            request.caller_actor,
            ("Healthcare AI Agent", "COMMAND_CTR") if "ai" in request.caller_actor else ("Adversarial Agent", "EXTERNAL")
        )
        target_patient_id = request.arguments.get("patient_id") or request.active_patient_context

        # 2. Canary Honeypot Inspection
        canary_tripped = False
        for k, v in request.arguments.items():
            if isinstance(v, str):
                canary = check_canary_trip(db, v, request.caller_actor, actor_role, actor_dept, request.client_ip)
                if canary:
                    canary_tripped = True
                    return GatewayDecision(
                        outcome="DENY",
                        reason=f"SECURITY ALERT: Canary honeypot trap '{canary.secret_name}' tripped!",
                        policy_applied="CANARY_TRAP_MONITOR",
                        tool_name=tool_name,
                        arguments=request.arguments,
                        canary_tripped=True,
                        timestamp=timestamp_str
                    )

        # 2b. Emergency Break-Glass Privilege Escalation Check
        if request.purpose_of_use == "emergency_break_glass":
            if actor_role not in ("Doctor", "Nurse"):
                event = record_audit_event(
                    db=db,
                    actor_id=request.caller_actor,
                    actor_role=actor_role,
                    actor_department=actor_dept,
                    action=tool_def.action,
                    resource_type=tool_def.resource_type,
                    resource_id=str(target_patient_id) if target_patient_id else "NONE",
                    patient_id=int(target_patient_id) if target_patient_id else None,
                    purpose_of_use=request.purpose_of_use,
                    decision="DENY",
                    reason=f"PRIVILEGE ESCALATION: Non-clinical role '{actor_role}' attempted emergency break-glass clinical access.",
                    client_ip=request.client_ip
                )
                return GatewayDecision(
                    outcome="DENY",
                    reason=f"Privilege Escalation Blocked: Non-clinical role '{actor_role}' cannot invoke emergency break-glass for clinical records.",
                    policy_applied="EMERGENCY_BREAK_GLASS_AUTHORIZATION_POLICY",
                    tool_name=tool_name,
                    arguments=request.arguments,
                    audit_event_id=event.event_id,
                    timestamp=timestamp_str
                )

        # 3. Absolute Invariants Check
        # Rule: AI agent cannot approve its own privileged actions or delete audit events
        if tool_def.resource_type == "AuditEvent" and tool_def.action in ("DELETE", "TRUNCATE", "MODIFY"):
            event = record_audit_event(
                db=db,
                actor_id=request.caller_actor,
                actor_role=actor_role,
                actor_department=actor_dept,
                action=tool_def.action,
                resource_type="AuditEvent",
                resource_id="ALL",
                purpose_of_use=request.purpose_of_use,
                decision="DENY",
                reason="INVARIANT VIOLATION: Audit records are cryptographically immutable.",
                client_ip=request.client_ip
            )
            return GatewayDecision(
                outcome="DENY",
                reason="Audit ledger is cryptographically immutable. Deletion or modification forbidden.",
                policy_applied="AUDIT_IMMUTABILITY_INVARIANT",
                tool_name=tool_name,
                arguments=request.arguments,
                audit_event_id=event.event_id,
                timestamp=timestamp_str
            )

        # 4. Patient Scope & Cross-Patient Boundary Check
        if request.active_patient_context and target_patient_id:
            if int(target_patient_id) != int(request.active_patient_context):
                # Requesting a different patient than the active conversation context without re-authorization
                event = record_audit_event(
                    db=db,
                    actor_id=request.caller_actor,
                    actor_role=actor_role,
                    actor_department=actor_dept,
                    action=tool_def.action,
                    resource_type=tool_def.resource_type,
                    resource_id=str(target_patient_id),
                    patient_id=int(target_patient_id),
                    purpose_of_use=request.purpose_of_use,
                    decision="DENY",
                    reason=f"CROSS-PATIENT CONTAMINATION: Active context is Patient #{request.active_patient_context}, but tool targeted Patient #{target_patient_id}.",
                    client_ip=request.client_ip
                )
                return GatewayDecision(
                    outcome="DENY",
                    reason=f"Cross-patient boundary violation. Active context #{request.active_patient_context} cannot access Patient #{target_patient_id}.",
                    policy_applied="CROSS_PATIENT_ISOLATION_POLICY",
                    tool_name=tool_name,
                    arguments=request.arguments,
                    audit_event_id=event.event_id,
                    timestamp=timestamp_str
                )

        # 5. Role & Permission Matrix (RBAC)
        role_rules = ROLE_PERMISSIONS.get(actor_role, {})
        allowed_actions = role_rules.get(tool_def.resource_type, set())
        if tool_def.action not in allowed_actions:
            event = record_audit_event(
                db=db,
                actor_id=request.caller_actor,
                actor_role=actor_role,
                actor_department=actor_dept,
                action=tool_def.action,
                resource_type=tool_def.resource_type,
                resource_id=str(target_patient_id) if target_patient_id else "NONE",
                patient_id=int(target_patient_id) if target_patient_id else None,
                purpose_of_use=request.purpose_of_use,
                decision="DENY",
                reason=f"Role '{actor_role}' does not hold '{tool_def.action}' permission on '{tool_def.resource_type}'.",
                client_ip=request.client_ip
            )
            return GatewayDecision(
                outcome="DENY",
                reason=f"Access Denied: Role '{actor_role}' not permitted to perform '{tool_def.action}' on '{tool_def.resource_type}'.",
                policy_applied="ROLE_BASED_ACCESS_CONTROL",
                tool_name=tool_name,
                arguments=request.arguments,
                audit_event_id=event.event_id,
                timestamp=timestamp_str
            )

        # 6. Patient Consent Validation
        if target_patient_id:
            consent_ok, consent_msg = validate_patient_consent(
                db, int(target_patient_id), request.purpose_of_use, tool_def.action
            )
            if not consent_ok:
                event = record_audit_event(
                    db=db,
                    actor_id=request.caller_actor,
                    actor_role=actor_role,
                    actor_department=actor_dept,
                    action=tool_def.action,
                    resource_type=tool_def.resource_type,
                    resource_id=str(target_patient_id),
                    patient_id=int(target_patient_id),
                    purpose_of_use=request.purpose_of_use,
                    decision="DENY",
                    reason=f"Consent restriction: {consent_msg}",
                    client_ip=request.client_ip
                )
                return GatewayDecision(
                    outcome="DENY",
                    reason=f"Consent Restriction: {consent_msg}",
                    policy_applied="PATIENT_CONSENT_VALIDATION",
                    tool_name=tool_name,
                    arguments=request.arguments,
                    audit_event_id=event.event_id,
                    timestamp=timestamp_str
                )

        # 7. Human Approval Requirement Policy
        if tool_def.requires_human_approval:
            # Check if valid verified human approval token is attached
            valid_tokens = ["HUMAN_AUTH_DR_VANCE_2026", "HUMAN_AUTH_ADMIN_ARCHER_2026", "SUPERVISOR_OVERRIDE_VERIFIED"]
            if not request.human_approval_token or request.human_approval_token not in valid_tokens:
                event = record_audit_event(
                    db=db,
                    actor_id=request.caller_actor,
                    actor_role=actor_role,
                    actor_department=actor_dept,
                    action=tool_def.action,
                    resource_type=tool_def.resource_type,
                    resource_id=str(target_patient_id) if target_patient_id else "NONE",
                    patient_id=int(target_patient_id) if target_patient_id else None,
                    purpose_of_use=request.purpose_of_use,
                    decision="REQUIRE_HUMAN_APPROVAL",
                    reason=f"Action '{tool_name}' on '{tool_def.resource_type}' requires verified human practitioner sign-off.",
                    client_ip=request.client_ip
                )
                return GatewayDecision(
                    outcome="REQUIRE_HUMAN_APPROVAL",
                    reason=f"Sensitive action '{tool_name}' requires verified human clinician/administrative approval.",
                    policy_applied="HUMAN_IN_THE_LOOP_APPROVAL_POLICY",
                    tool_name=tool_name,
                    arguments=request.arguments,
                    audit_event_id=event.event_id,
                    timestamp=timestamp_str
                )

        # 8. All Policies Passed: Execute Hospital Service
        actor_ctx = ActorContext(
            actor_id=request.caller_actor,
            display_name="Kratos HOSA Support Agent" if "ai" in request.caller_actor else request.caller_actor,
            role=actor_role,
            department_code=actor_dept,
            purpose_of_use=request.purpose_of_use,
            client_ip=request.client_ip
        )

        try:
            result_data = ToolGateway._dispatch_service(db, tool_name, request.arguments, actor_ctx)
            
            event = record_audit_event(
                db=db,
                actor_id=request.caller_actor,
                actor_role=actor_role,
                actor_department=actor_dept,
                action=tool_def.action,
                resource_type=tool_def.resource_type,
                resource_id=str(target_patient_id) if target_patient_id else "NONE",
                patient_id=int(target_patient_id) if target_patient_id else None,
                purpose_of_use=request.purpose_of_use,
                decision="PERMIT",
                reason=f"Tool '{tool_name}' permitted by Gateway.",
                client_ip=request.client_ip,
                details={"tool": tool_name}
            )

            return GatewayDecision(
                outcome="ALLOW",
                reason=f"Authorized under {actor_role} operational scope.",
                policy_applied="COMPREHENSIVE_GATEWAY_ALLOW",
                tool_name=tool_name,
                arguments=request.arguments,
                result=result_data,
                audit_event_id=event.event_id,
                timestamp=timestamp_str
            )
        except Exception as e:
            return GatewayDecision(
                outcome="DENY",
                reason=f"Execution error in hospital service: {str(e)}",
                policy_applied="SERVICE_ERROR_POLICY",
                tool_name=tool_name,
                arguments=request.arguments,
                timestamp=timestamp_str
            )

    @staticmethod
    def _dispatch_service(db: Session, tool_name: str, args: Dict[str, Any], actor: ActorContext) -> Any:
        """Invokes appropriate deterministic hospital service."""
        if tool_name == "get_patient_records":
            p = PatientService.get_patient_profile(db, actor, int(args["patient_id"]))
            return {
                "id": p.id,
                "mrn": p.mrn,
                "name": f"{p.first_name} {p.last_name}",
                "dob": p.dob,
                "gender": p.gender,
                "blood_group": p.blood_group,
                "conditions": [{"code": c.code, "name": c.name} for c in p.conditions],
                "allergies": [{"allergen": a.allergen, "severity": a.severity} for a in p.allergies]
            }

        elif tool_name == "summarize_encounters":
            encs = PatientService.get_encounter_history(db, actor, int(args["patient_id"]))
            return [{
                "encounter_number": e.encounter_number,
                "encounter_type": e.encounter_type,
                "status": e.status,
                "chief_complaint": e.chief_complaint,
                "admission_date": e.admission_date.isoformat()
            } for e in encs]

        elif tool_name == "retrieve_medical_reports":
            pid = int(args["patient_id"])
            labs = PatientService.get_lab_reports(db, actor, pid)
            rads = PatientService.get_radiology_reports(db, actor, pid)
            return {
                "labs": [{
                    "test_code": l.test_code,
                    "test_name": l.test_name,
                    "results": l.result_data,
                    "interpretation": l.interpretation
                } for l in labs],
                "radiology": [{
                    "modality": r.modality,
                    "study_name": r.study_name,
                    "findings": r.findings,
                    "impression": r.impression
                } for r in rads]
            }

        elif tool_name in ("draft_progress_note", "draft_discharge_summary", "draft_referral_letter", "draft_medical_certificate"):
            return {
                "status": "DRAFT_CREATED",
                "document_type": tool_name,
                "patient_id": args.get("patient_id"),
                "approval_status": "PENDING_PHYSICIAN_SIGNATURE",
                "draft_content": args
            }

        elif tool_name == "retrieve_billing_info":
            pid = int(args["patient_id"])
            from backend.app.models.billing import Invoice
            inv = db.query(Invoice).filter(Invoice.patient_id == pid).first()
            if not inv:
                return {"message": "No active invoices found for patient."}
            return {
                "invoice_number": inv.invoice_number,
                "total_amount": inv.total_amount,
                "insurance_covered": inv.insurance_covered_amount,
                "patient_responsibility": inv.patient_responsibility,
                "paid_amount": inv.paid_amount,
                "outstanding_balance": inv.outstanding_balance,
                "status": inv.status
            }

        elif tool_name == "calculate_invoice":
            return BillingService.calculate_bill(
                db, actor, int(args["patient_id"]), float(args["items_total"]), float(args.get("discount", 0.0))
            )

        elif tool_name == "retrieve_bed_availability":
            return OperationsService.get_bed_availability(db, actor)

        elif tool_name == "check_icu_capacity":
            return OperationsService.get_icu_capacity(db, actor)

        elif tool_name == "retrieve_emergency_status":
            return OperationsService.get_emergency_workload(db, actor)

        elif tool_name == "retrieve_staff_availability":
            return OperationsService.get_staff_availability(db, actor)

        elif tool_name == "check_staff_qualifications":
            sm = StaffService.get_staff_details(db, actor, int(args["staff_id"]))
            return {
                "staff_id": sm.id,
                "name": f"{sm.first_name} {sm.last_name}",
                "role": sm.role,
                "specialization": sm.specialization,
                "license_number": sm.license_number,
                "qualifications": [{"degree": q.degree, "institution": q.institution} for q in sm.qualifications]
            }

        elif tool_name == "escalate_operational_issue":
            return {
                "escalation_id": f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "status": "DISPATCHED_TO_COMMAND_CENTRE",
                "issue_type": args.get("issue_type"),
                "severity": args.get("severity")
            }

        return {"status": "SUCCESS", "message": f"Tool '{tool_name}' executed."}
