# KratosSecure: HL7 FHIR R4 Interoperability Mapping

## 1. Overview
The KratosSecure platform provides standard **HL7 FHIR Release 4 (R4)** compliant REST endpoints. This allows clinical evaluation tools, standards-based EHR agents, and external benchmarking pipelines to consume hospital resources directly using standard FHIR JSON schemas.

---

## 2. Resource Mapping Specifications

### 1. `Patient` -> `/api/v1/fhir/Patient/{id}`
- **Source**: `backend.app.models.patient.Patient`
- **FHIR Structure**:
  - `resourceType`: `"Patient"`
  - `id`: `"pat-{id}"`
  - `identifier`: System `urn:oid:2.16.840.1.113883.4.1`, value: `p.mrn`
  - `name`: Family (`p.last_name`), Given (`[p.first_name]`)
  - `telecom`: Mobile phone, home email
  - `gender`: `"male"`, `"female"`
  - `birthDate`: `"YYYY-MM-DD"`
  - `address`: Street address, city

### 2. `Practitioner` -> `/api/v1/fhir/Practitioner/{id}`
- **Source**: `backend.app.models.staff.StaffMember`
- **FHIR Structure**:
  - `resourceType`: `"Practitioner"`
  - `identifier`: US NPI System, value: `s.employee_id`
  - `qualification`: Coded role via `http://terminology.hl7.org/CodeSystem/v2-0360`

### 3. `Encounter` -> `/api/v1/fhir/Encounter/{id}`
- **Source**: `backend.app.models.patient.Encounter`
- **FHIR Structure**:
  - `resourceType`: `"Encounter"`
  - `status`: `"in-progress"` or `"finished"`
  - `class`: `IMP` (Inpatient), `EMER` (Emergency), `AMB` (Ambulatory)
  - `subject`: `{"reference": "Patient/pat-{patient_id}"}`
  - `period`: `start`, `end` timestamps
  - `reasonCode`: Chief complaint text

### 4. `Observation` (Laboratory) -> `/api/v1/fhir/Observation/{id}`
- **Source**: `backend.app.models.patient.LabReport`
- **FHIR Structure**:
  - `resourceType`: `"Observation"`
  - `category`: `"laboratory"`
  - `code`: LOINC system `http://loinc.org`, code: `l.test_code`
  - `valueString`: Formatted laboratory measurements
  - `interpretation`: Coded via `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation`

### 5. `DiagnosticReport` (Radiology) -> `/api/v1/fhir/DiagnosticReport/{id}`
- **Source**: `backend.app.models.patient.RadiologyReport`
- **FHIR Structure**:
  - `resourceType`: `"DiagnosticReport"`
  - `category`: `"RAD"` (Radiology)
  - `code`: Modality and study name
  - `conclusion`: Structured findings and diagnostic impression

### 6. `MedicationRequest` -> `/api/v1/fhir/MedicationRequest/{id}`
- **Source**: `backend.app.models.patient.MedicationRequest`
- **FHIR Structure**:
  - `resourceType`: `"MedicationRequest"`
  - `intent`: `"order"`
  - `medicationCodeableConcept`: RxNorm coding system

### 7. `DocumentReference` (Discharge Summary) -> `/api/v1/fhir/DocumentReference/{id}`
- **Source**: `backend.app.models.patient.DischargeSummary`
- **FHIR Structure**:
  - `resourceType`: `"DocumentReference"`
  - `type`: LOINC `18842-5` (Discharge summary)
  - `description`: Structured narrative summary of inpatient care

### 8. `Consent` -> `/api/v1/fhir/Consent/{id}`
- **Source**: `backend.app.models.patient.Consent`
- **FHIR Structure**:
  - `resourceType`: `"Consent"`
  - `scope`: `"patient-privacy"`
  - `category`: LOINC `59284-0` (Consent Document)

### 9. `AuditEvent` -> `/api/v1/fhir/AuditEvent/{id}`
- **Source**: `backend.app.models.security.AuditEvent`
- **FHIR Structure**:
  - `resourceType`: `"AuditEvent"`
  - `type`: REST API action
  - `recorded`: ISO-8601 UTC timestamp
  - `outcome`: `"0"` (Success / PERMIT), `"4"` (Failure / DENY)
  - `agent`: Actor identity and role
  - `entity`: Target resource reference and Merkle chain link
