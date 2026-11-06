# KratosSecure: Healthcare Actor Permission Matrix

## 1. Role Definitions & Operational Scopes

The digital twin models 12 distinct actor personas. Each actor operates under least-privilege boundaries enforced deterministically by `backend/app/security/rbac.py`.

```
========================================================================================
ACTOR ROLE               PRIMARY FUNCTION                     RESTRICTION BOUNDARY
========================================================================================
Doctor                   Direct Clinical Diagnosis & Care     No billing edits; no audit deletion
Nurse                    Bedside Inpatient Care               No controlled Rx; no billing
Lab Technician           Specimen Diagnostic Processing       No psychiatric/billing access
Pharmacist               Medication Dispensing & Formulary    No diagnostic modifications
Billing Officer          Revenue Cycle & Claims Filing        ZERO clinical record access (403)
Medical Records Officer  Identity & Legal Disclosure Mgmt     No active clinical treatment edits
Hospital Administrator   Capacity & Operational Management    No unconsented PHI inspection
IT Administrator         Subsystem Uptime & Zero-Trust GW     No cleartext patient record access
Security Officer         Audit Ledger & Incident Monitoring   Cannot alter clinical/audit logs
Healthcare AI Agent      Autonomous Clinical Support          Scoped tools only; human approvals required
Adversarial Agent        Simulated Infiltration Probe         Zero legitimate permissions (All 403)
========================================================================================
```

---

## 2. Granular Resource Authorization Table

| Actor Role | Patient Core | Clinical Notes | Lab & Radiology | Medications | Invoices & Billing | Subsystems | Audit Ledger |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Doctor** | READ, SEARCH | READ, WRITE | ORDER, READ | PRESCRIBE | READ (Limited) | READ | NO ACCESS |
| **Nurse** | READ, SEARCH | UPDATE (Vitals) | READ, COLLECT | ADMINISTER | DENIED (403) | READ | NO ACCESS |
| **Lab Technician** | SEARCH (ID Only)| DENIED (403) | PERFORM, UPDATE | DENIED (403) | DENIED (403) | READ | NO ACCESS |
| **Pharmacist** | SEARCH (ID Only)| DENIED (403) | DENIED (403) | VERIFY, DISPENSE| DENIED (403) | READ | NO ACCESS |
| **Billing Officer** | SEARCH (Demogr)| **DENIED (403)**| **DENIED (403)**| **DENIED (403)**| CREATE, UPDATE | READ | NO ACCESS |
| **Medical Records** | READ, UPDATE | READ (Archive)| READ | READ | READ | READ | NO ACCESS |
| **Hospital Admin** | READ (Aggreg) | DENIED (403) | DENIED (403) | DENIED (403) | READ (Aggreg) | READ, UPDATE | NO ACCESS |
| **IT Administrator** | DENIED (403) | DENIED (403) | DENIED (403) | DENIED (403) | DENIED (403) | RESTART, UPDATE| READ |
| **Security Officer** | DENIED (403) | DENIED (403) | DENIED (403) | DENIED (403) | DENIED (403) | READ | READ, VERIFY |
| **Healthcare AI Agent** | READ (Scoped)| READ (Scoped) | DRAFT ORDER | DRAFT ORDER | DRAFT INVOICE | READ | DENIED (403) |
| **Adversarial Agent** | **DENIED (403)**| **DENIED (403)**| **DENIED (403)**| **DENIED (403)**| **DENIED (403)**| **DENIED (403)**| **DENIED (403)**|

---

## 3. Operations Requiring Human Authorization

The following high-risk actions cannot be autonomously executed by AI agents or automated scripts without human practitioner sign-off:

1. `("MedicationRequest", "DISPENSE_CONTROLLED_SUBSTANCE")`: Schedule II opioids require physical dual-practitioner sign-off.
2. `("Invoice", "WRITE_OFF_DEBT")`: Financial debt write-offs above $500 require human CFO/Billing Officer approval.
3. `("Patient", "PURGE_RECORD")`: Permanent record deletion is strictly barred.
4. `("AuditEvent", "DELETE_LOG")`: **Absolute invariant**: Audit records are cryptographically immutable and cannot be deleted or truncated by any role.
