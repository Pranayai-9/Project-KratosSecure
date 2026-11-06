from datetime import datetime
from typing import Dict, Any, List
from backend.app.models.patient import Patient, Encounter, LabReport, RadiologyReport, MedicationRequest, DischargeSummary, Consent
from backend.app.models.staff import StaffMember
from backend.app.models.security import AuditEvent

class FHIRExporter:
    @staticmethod
    def patient_to_fhir(p: Patient) -> Dict[str, Any]:
        return {
            "resourceType": "Patient",
            "id": f"pat-{p.id}",
            "meta": {
                "versionId": "1",
                "lastUpdated": (p.updated_at or p.created_at or datetime.utcnow()).isoformat(),
                "source": "KratosSecure-Hospital-Twin"
            },
            "identifier": [
                {
                    "system": "urn:oid:2.16.840.1.113883.4.1",
                    "value": p.mrn,
                    "use": "official"
                }
            ],
            "active": p.is_active,
            "name": [
                {
                    "use": "official",
                    "family": p.last_name,
                    "given": [p.first_name]
                }
            ],
            "telecom": [
                {"system": "phone", "value": p.phone, "use": "mobile"},
                {"system": "email", "value": p.email, "use": "home"}
            ],
            "gender": p.gender.lower(),
            "birthDate": p.dob,
            "address": [
                {"line": [p.address], "use": "home"}
            ]
        }

    @staticmethod
    def practitioner_to_fhir(s: StaffMember) -> Dict[str, Any]:
        return {
            "resourceType": "Practitioner",
            "id": f"prac-{s.id}",
            "identifier": [
                {"system": "http://hl7.org/fhir/sid/us-npi", "value": s.employee_id}
            ],
            "active": s.is_available,
            "name": [
                {"family": s.last_name, "given": [s.first_name], "prefix": ["Dr." if s.role == "Doctor" else ""]}
            ],
            "qualification": [
                {
                    "code": {
                        "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0360", "code": s.role, "display": s.specialization or s.role}]
                    }
                }
            ]
        }

    @staticmethod
    def encounter_to_fhir(e: Encounter) -> Dict[str, Any]:
        return {
            "resourceType": "Encounter",
            "id": f"enc-{e.id}",
            "status": "in-progress" if e.status == "in-progress" else "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "IMP" if e.encounter_type == "inpatient" else ("EMER" if e.encounter_type == "emergency" else "AMB"),
                "display": e.encounter_type.capitalize()
            },
            "subject": {"reference": f"Patient/pat-{e.patient_id}"},
            "period": {
                "start": e.admission_date.isoformat(),
                "end": e.discharge_date.isoformat() if e.discharge_date else None
            },
            "reasonCode": [
                {"text": e.chief_complaint}
            ]
        }

    @staticmethod
    def lab_to_fhir_observation(l: LabReport) -> Dict[str, Any]:
        return {
            "resourceType": "Observation",
            "id": f"obs-{l.id}",
            "status": l.status,
            "category": [
                {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory", "display": "Laboratory"}]
                }
            ],
            "code": {
                "coding": [{"system": "http://loinc.org", "code": l.test_code, "display": l.test_name}],
                "text": l.test_name
            },
            "subject": {"reference": f"Patient/pat-{l.patient_id}"},
            "effectiveDateTime": l.collection_time.isoformat(),
            "valueString": str(l.result_data),
            "interpretation": [
                {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", "code": l.interpretation}]
                }
            ]
        }

    @staticmethod
    def radiology_to_fhir_diagnostic_report(r: RadiologyReport) -> Dict[str, Any]:
        return {
            "resourceType": "DiagnosticReport",
            "id": f"diag-{r.id}",
            "status": "final" if r.status == "reported" else "preliminary",
            "category": [
                {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "RAD", "display": "Radiology"}]
                }
            ],
            "code": {
                "text": f"{r.modality} - {r.study_name}"
            },
            "subject": {"reference": f"Patient/pat-{r.patient_id}"},
            "effectiveDateTime": r.created_at.isoformat(),
            "conclusion": f"FINDINGS: {r.findings} | IMPRESSION: {r.impression}"
        }

    @staticmethod
    def medication_to_fhir(m: MedicationRequest) -> Dict[str, Any]:
        return {
            "resourceType": "MedicationRequest",
            "id": f"med-{m.id}",
            "status": m.status,
            "intent": "order",
            "medicationCodeableConcept": {
                "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": m.rxnorm_code or "99999", "display": m.medication_name}],
                "text": f"{m.medication_name} ({m.dosage}, {m.frequency}, {m.route})"
            },
            "subject": {"reference": f"Patient/pat-{m.patient_id}"},
            "authoredOn": m.start_date.isoformat()
        }

    @staticmethod
    def discharge_to_fhir_document(d: DischargeSummary) -> Dict[str, Any]:
        return {
            "resourceType": "DocumentReference",
            "id": f"doc-{d.id}",
            "status": "current",
            "type": {
                "coding": [{"system": "http://loinc.org", "code": "18842-5", "display": "Discharge summary"}],
                "text": "Discharge Summary"
            },
            "subject": {"reference": f"Patient/pat-{d.patient_id}"},
            "date": d.created_at.isoformat(),
            "description": f"Admission Diagnosis: {d.admission_diagnosis} | Discharge Diagnosis: {d.discharge_diagnosis}\n{d.summary_text}"
        }

    @staticmethod
    def consent_to_fhir(c: Consent) -> Dict[str, Any]:
        return {
            "resourceType": "Consent",
            "id": f"con-{c.id}",
            "status": c.status,
            "scope": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/consentscope", "code": "patient-privacy", "display": "Privacy Consent"}]
            },
            "category": [
                {"coding": [{"system": "http://loinc.org", "code": "59284-0", "display": c.consent_type}]}
            ],
            "patient": {"reference": f"Patient/pat-{c.patient_id}"},
            "dateTime": c.created_at.isoformat()
        }

    @staticmethod
    def audit_event_to_fhir(a: AuditEvent) -> Dict[str, Any]:
        return {
            "resourceType": "AuditEvent",
            "id": f"audit-{a.id}",
            "type": {
                "system": "http://terminology.hl7.org/CodeSystem/audit-event-type",
                "code": "rest",
                "display": a.action
            },
            "action": a.action,
            "recorded": a.timestamp.isoformat(),
            "outcome": "0" if a.decision == "PERMIT" else "4",
            "agent": [
                {
                    "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType", "code": a.actor_role}]},
                    "who": {"display": a.actor_id},
                    "requestor": True
                }
            ],
            "source": {
                "observer": {"display": "KratosSecure-Core-Engine"}
            },
            "entity": [
                {
                    "what": {"reference": f"{a.resource_type}/{a.resource_id}"},
                    "type": {"system": "http://terminology.hl7.org/CodeSystem/audit-entity-type", "code": a.resource_type}
                }
            ]
        }
