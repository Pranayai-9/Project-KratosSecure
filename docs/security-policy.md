# KratosSecure: Healthcare Agent Security & Authorization Policy

## 1. Purpose-of-Use Specifications (HIPAA TPO Framework)
In accordance with healthcare data protection principles, all agent tool requests must specify an authorized `purpose_of_use`:

| Purpose Code | Operational Scope | Permitted Resources |
| :--- | :--- | :--- |
| `treatment` | Direct inpatient, outpatient, or emergency clinical care | Patient profile, active conditions, encounters, LOINC labs, radiology impressions |
| `payment` | Billing, insurance claims, payment receipts | Invoices, itemized charges, copays, deductibles (Zero clinical lab/note access) |
| `operations` | Bed allocation, staff scheduling, telemetry | Bed capacity, ICU availability, duty rosters, department workload |
| `emergency_break_glass` | Stat resuscitation, life-or-death emergency overrides | Time-bounded access strictly for clinical roles (Doctor, Nurse) with active trauma encounters |
| `research` | Secondary clinical studies, analytics | Requires explicit, non-revoked `data_sharing_research` patient consent |
| `external_disclosure` | Patient-requested transfer or regulatory export | Requires explicit `external_disclosure` consent on file |

---

## 2. Dynamic Consent Policy
Patient consent is not assumed:
- **Treatment Consent**: Automatically granted for emergency and inpatient care upon admission.
- **Research & External Disclosure Consent**: Dynamically verified against `backend.app.models.patient.Consent`.
- **Revocation Rule**: If a patient revokes consent (`status == "revoked"`), the Policy Engine rejects requests under `research` or `external_disclosure` with `HTTP 403 Forbidden`.

---

## 3. Human-in-the-Loop (HITL) Sign-Off Requirements
Certain sensitive operations cannot be autonomously completed by AI agents:
1. **Prescription Ordering & Controlled Substances**: dual-practitioner sign-off required.
2. **Clinical Progress Notes & Discharge Summaries**: Physician review required.
3. **Medical Certificates & Fitness Letters**: Attending clinician signature required.
4. **Duty Rostering & Scheduling**: Nursing / Administrative head approval required.
5. **Debt Write-Offs & Large Discounts (> $100)**: CFO / Finance Director sign-off required.
