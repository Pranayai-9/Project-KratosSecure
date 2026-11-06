from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class FHIRMeta(BaseModel):
    versionId: str = "1"
    lastUpdated: str
    source: str = "KratosSecure-Hospital-Twin"

class FHIRCoding(BaseModel):
    system: str
    code: str
    display: str

class FHIRCodeableConcept(BaseModel):
    coding: List[FHIRCoding] = []
    text: Optional[str] = None

class FHIRReference(BaseModel):
    reference: str
    display: Optional[str] = None

# FHIR Patient
class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: List[Dict[str, Any]] = []
    active: bool = True
    name: List[Dict[str, Any]] = []
    telecom: List[Dict[str, Any]] = []
    gender: str
    birthDate: str
    address: List[Dict[str, Any]] = []

# FHIR Practitioner
class FHIRPractitioner(BaseModel):
    resourceType: str = "Practitioner"
    id: str
    meta: Optional[FHIRMeta] = None
    identifier: List[Dict[str, Any]] = []
    active: bool = True
    name: List[Dict[str, Any]] = []
    qualification: List[Dict[str, Any]] = []

# FHIR Encounter
class FHIREncounter(BaseModel):
    resourceType: str = "Encounter"
    id: str
    meta: Optional[FHIRMeta] = None
    status: str
    class_: Dict[str, Any] = Field(alias="class")
    subject: FHIRReference
    period: Dict[str, str] = {}
    reasonCode: List[FHIRCodeableConcept] = []

# FHIR Observation (Laboratory / Vitals)
class FHIRObservation(BaseModel):
    resourceType: str = "Observation"
    id: str
    meta: Optional[FHIRMeta] = None
    status: str = "final"
    category: List[FHIRCodeableConcept] = []
    code: FHIRCodeableConcept
    subject: FHIRReference
    effectiveDateTime: str
    valueString: Optional[str] = None
    interpretation: List[FHIRCodeableConcept] = []

# FHIR DiagnosticReport (Radiology / Lab Panels)
class FHIRDiagnosticReport(BaseModel):
    resourceType: str = "DiagnosticReport"
    id: str
    meta: Optional[FHIRMeta] = None
    status: str
    category: List[FHIRCodeableConcept] = []
    code: FHIRCodeableConcept
    subject: FHIRReference
    effectiveDateTime: str
    conclusion: Optional[str] = None

# FHIR MedicationRequest
class FHIRMedicationRequest(BaseModel):
    resourceType: str = "MedicationRequest"
    id: str
    meta: Optional[FHIRMeta] = None
    status: str
    intent: str = "order"
    medicationCodeableConcept: FHIRCodeableConcept
    subject: FHIRReference
    authoredOn: str

# FHIR DocumentReference (Discharge Summary / Clinical Notes)
class FHIRDocumentReference(BaseModel):
    resourceType: str = "DocumentReference"
    id: str
    meta: Optional[FHIRMeta] = None
    status: str = "current"
    type: FHIRCodeableConcept
    subject: FHIRReference
    date: str
    description: str

# FHIR Consent
class FHIRConsent(BaseModel):
    resourceType: str = "Consent"
    id: str
    meta: Optional[FHIRMeta] = None
    status: str
    scope: FHIRCodeableConcept
    category: List[FHIRCodeableConcept] = []
    patient: FHIRReference
    dateTime: str

# FHIR AuditEvent
class FHIRAuditEvent(BaseModel):
    resourceType: str = "AuditEvent"
    id: str
    meta: Optional[FHIRMeta] = None
    type: FHIRCoding
    action: str
    recorded: str
    outcome: str
    agent: List[Dict[str, Any]] = []
    source: Dict[str, Any] = {}
    entity: List[Dict[str, Any]] = []

# FHIR Provenance
class FHIRProvenance(BaseModel):
    resourceType: str = "Provenance"
    id: str
    meta: Optional[FHIRMeta] = None
    target: List[FHIRReference] = []
    recorded: str
    reason: List[FHIRCodeableConcept] = []
    agent: List[Dict[str, Any]] = []
