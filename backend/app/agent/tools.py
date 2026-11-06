from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Structured schemas for Agent Tools
class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str # patient, documentation, billing, staff, operations
    parameters: Dict[str, Any]
    requires_human_approval: bool = False
    resource_type: str
    action: str

AVAILABLE_TOOLS: Dict[str, ToolDefinition] = {
    # 1. Patient Record Operations
    "get_patient_records": ToolDefinition(
        name="get_patient_records",
        description="Retrieve authorized clinical and demographic profile for an active patient.",
        category="patient",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer", "description": "Unique identifier of the patient."}
            },
            "required": ["patient_id"]
        },
        resource_type="Patient",
        action="READ"
    ),
    "summarize_encounters": ToolDefinition(
        name="summarize_encounters",
        description="Retrieve chronological encounter history and clinical complaints for a patient.",
        category="patient",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer", "description": "Unique identifier of the patient."}
            },
            "required": ["patient_id"]
        },
        resource_type="Encounter",
        action="READ"
    ),
    "retrieve_medical_reports": ToolDefinition(
        name="retrieve_medical_reports",
        description="Retrieve diagnostic laboratory panels (LOINC) or radiology reports for a patient.",
        category="patient",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer", "description": "Unique identifier of the patient."},
                "report_type": {"type": "string", "enum": ["lab", "radiology", "all"], "description": "Type of report to fetch."}
            },
            "required": ["patient_id"]
        },
        resource_type="LabReport",
        action="READ"
    ),

    # 2. Documentation
    "draft_progress_note": ToolDefinition(
        name="draft_progress_note",
        description="Draft a clinical progress note for physician review and sign-off.",
        category="documentation",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer", "description": "Target patient ID."},
                "encounter_id": {"type": "integer", "description": "Active encounter ID."},
                "note_text": {"type": "string", "description": "Clinical progress note content."}
            },
            "required": ["patient_id", "note_text"]
        },
        requires_human_approval=True,
        resource_type="Encounter",
        action="UPDATE"
    ),
    "draft_discharge_summary": ToolDefinition(
        name="draft_discharge_summary",
        description="Draft an authoritative inpatient discharge summary for attending physician sign-off.",
        category="documentation",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer", "description": "Target patient ID."},
                "encounter_id": {"type": "integer", "description": "Active encounter ID."},
                "admission_diagnosis": {"type": "string"},
                "discharge_diagnosis": {"type": "string"},
                "summary_text": {"type": "string"},
                "discharge_instructions": {"type": "string"},
                "follow_up_plan": {"type": "string"}
            },
            "required": ["patient_id", "encounter_id", "admission_diagnosis", "discharge_diagnosis", "summary_text"]
        },
        requires_human_approval=True,
        resource_type="DischargeSummary",
        action="CREATE"
    ),
    "draft_referral_letter": ToolDefinition(
        name="draft_referral_letter",
        description="Draft an inter-departmental or specialist referral letter.",
        category="documentation",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer"},
                "target_department": {"type": "string"},
                "reason_for_referral": {"type": "string"},
                "clinical_summary": {"type": "string"}
            },
            "required": ["patient_id", "target_department", "reason_for_referral"]
        },
        requires_human_approval=True,
        resource_type="Encounter",
        action="CREATE"
    ),
    "draft_medical_certificate": ToolDefinition(
        name="draft_medical_certificate",
        description="Draft a patient medical fitness or absence certificate.",
        category="documentation",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer"},
                "diagnosis": {"type": "string"},
                "recommended_leave_days": {"type": "integer"},
                "fitness_status": {"type": "string"}
            },
            "required": ["patient_id", "diagnosis", "recommended_leave_days"]
        },
        requires_human_approval=True,
        resource_type="DischargeSummary",
        action="CREATE"
    ),

    # 3. Billing & Revenue Cycle
    "retrieve_billing_info": ToolDefinition(
        name="retrieve_billing_info",
        description="Retrieve invoice details, payment balance, and itemized charges.",
        category="billing",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer"},
                "invoice_id": {"type": "integer"}
            },
            "required": ["patient_id"]
        },
        resource_type="Invoice",
        action="READ"
    ),
    "calculate_invoice": ToolDefinition(
        name="calculate_invoice",
        description="Calculate estimated patient responsibility based on active insurance coverage and copays.",
        category="billing",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer"},
                "items_total": {"type": "number"},
                "discount": {"type": "number", "default": 0.0}
            },
            "required": ["patient_id", "items_total"]
        },
        resource_type="Invoice",
        action="CALCULATE"
    ),
    "draft_invoice": ToolDefinition(
        name="draft_invoice",
        description="Draft a patient billing invoice for revenue cycle review.",
        category="billing",
        parameters={
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer"},
                "encounter_id": {"type": "integer"},
                "items": {"type": "array"},
                "discount_amount": {"type": "number", "default": 0.0},
                "notes": {"type": "string"}
            },
            "required": ["patient_id", "items"]
        },
        requires_human_approval=True,
        resource_type="Invoice",
        action="DRAFT_INVOICE"
    ),
    "check_payment_status": ToolDefinition(
        name="check_payment_status",
        description="Check verified payment and clearinghouse status for an invoice.",
        category="billing",
        parameters={
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer"}
            },
            "required": ["invoice_id"]
        },
        resource_type="Invoice",
        action="READ"
    ),
    "generate_receipt_draft": ToolDefinition(
        name="generate_receipt_draft",
        description="Generate a draft receipt reflecting verified transactions.",
        category="billing",
        parameters={
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer"},
                "amount_paid": {"type": "number"},
                "payment_method": {"type": "string"}
            },
            "required": ["invoice_id", "amount_paid"]
        },
        requires_human_approval=True,
        resource_type="Payment",
        action="CREATE"
    ),

    # 4. Staff Coordination
    "retrieve_staff_availability": ToolDefinition(
        name="retrieve_staff_availability",
        description="Check on-duty staff numbers and department shift coverage.",
        category="staff",
        parameters={
            "type": "object",
            "properties": {
                "department_id": {"type": "integer"},
                "role": {"type": "string"}
            }
        },
        resource_type="StaffMember",
        action="READ"
    ),
    "check_staff_qualifications": ToolDefinition(
        name="check_staff_qualifications",
        description="Verify personnel credentials, certifications, and clinical licenses.",
        category="staff",
        parameters={
            "type": "object",
            "properties": {
                "staff_id": {"type": "integer"}
            },
            "required": ["staff_id"]
        },
        resource_type="StaffMember",
        action="READ"
    ),
    "recommend_duty_assignment": ToolDefinition(
        name="recommend_duty_assignment",
        description="Recommend certified personnel for an upcoming shift based on department requirements.",
        category="staff",
        parameters={
            "type": "object",
            "properties": {
                "department_code": {"type": "string"},
                "shift_date": {"type": "string"},
                "shift_type": {"type": "string"},
                "role_required": {"type": "string"}
            },
            "required": ["department_code", "role_required"]
        },
        resource_type="DutyRoster",
        action="READ"
    ),
    "draft_duty_roster": ToolDefinition(
        name="draft_duty_roster",
        description="Draft a shift schedule assignment for administrative approval.",
        category="staff",
        parameters={
            "type": "object",
            "properties": {
                "staff_id": {"type": "integer"},
                "department_id": {"type": "integer"},
                "shift_date": {"type": "string"},
                "shift_type": {"type": "string"},
                "notes": {"type": "string"}
            },
            "required": ["staff_id", "department_id", "shift_date", "shift_type"]
        },
        requires_human_approval=True,
        resource_type="DutyRoster",
        action="CREATE"
    ),

    # 5. Hospital Operations
    "retrieve_bed_availability": ToolDefinition(
        name="retrieve_bed_availability",
        description="Retrieve total hospital bed occupancy and departmental breakdowns.",
        category="operations",
        parameters={"type": "object", "properties": {}},
        resource_type="Bed",
        action="READ"
    ),
    "check_icu_capacity": ToolDefinition(
        name="check_icu_capacity",
        description="Check ICU bed availability, mechanical ventilator status, and capacity alerts.",
        category="operations",
        parameters={"type": "object", "properties": {}},
        resource_type="Bed",
        action="READ"
    ),
    "retrieve_emergency_status": ToolDefinition(
        name="retrieve_emergency_status",
        description="Retrieve Emergency Department workload, triage acuity distribution, and ambulance availability.",
        category="operations",
        parameters={"type": "object", "properties": {}},
        resource_type="Department",
        action="READ"
    ),
    "escalate_operational_issue": ToolDefinition(
        name="escalate_operational_issue",
        description="Escalate capacity deficits or clinical bottlenecks to Hospital Command Centre.",
        category="operations",
        parameters={
            "type": "object",
            "properties": {
                "issue_type": {"type": "string"},
                "department": {"type": "string"},
                "severity": {"type": "string", "enum": ["ELEVATED", "HIGH", "CRITICAL"]},
                "details": {"type": "string"}
            },
            "required": ["issue_type", "department", "severity", "details"]
        },
        resource_type="SystemStatus",
        action="READ"
    )
}
