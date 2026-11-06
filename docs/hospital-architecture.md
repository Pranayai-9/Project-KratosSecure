# KratosSecure: Hospital Digital Twin Architecture

## 1. Executive Overview

The **KratosSecure Virtual Healthcare Operational Environment** serves as a stateful, deterministic, high-fidelity digital twin of a 500-bed tertiary-care hospital (**Aethelgard Memorial Hospital**). Its primary objective is to function as an immutable, reproducible operational substrate for evaluating autonomous healthcare AI agents and simulating multi-vector adversarial challenges.

```
                      +---------------------------------------+
                      |       Hospital Command Centre         |
                      |  Telemetry, KPI & Scenario Controller |
                      +-------------------+-------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
+-------v-------+                 +-------v-------+                 +-------v-------+
|  Building A   |                 |  Building B   |                 |  Building C   |
| Trauma & ICU  |                 | Inpatient & Dx|                 | Ambulatory &  |
| Level 1: ED   |                 | Level G: Rad  |                 | Administration|
| Level 2: ICU  |                 | Level B1: Lab |                 | Level G: Pharm|
| Level 4: Cmd  |                 | Level 3-6: IPD|                 | Level 2: Bill |
+---------------+                 +---------------+                 +---------------+
```

---

## 2. Infrastructure & Capacity Specifications

| Infrastructure Component | Parameter / Specification | Operational Details |
| :--- | :--- | :--- |
| **Total Licensed Beds** | 500 Beds | Monitored across IPD, ICU, ED, and OPD Observation |
| **Inpatient Department (IPD)** | 385 Beds | Distributed across Levels 3-6 (Rooms 301-670) |
| **Intensive Care Unit (ICU)** | 50 Beds | 100% equipped with cardiac monitors & ventilators |
| **Emergency Department (ED)** | 45 Bays | Triage Levels 1 (Resuscitation) to 5 (Non-urgent) |
| **Ambulatory Day Care (OPD)** | 20 Beds | Pre-op observation and same-day recovery |
| **Operating Theatres (OR)** | 12 Suites | Trauma, Cardiac, Neuro, Ortho, Robotic, Transplant |
| **Mechanical Ventilators** | 60 Units | 45 allocated to ICU, 15 allocated to ED Trauma |
| **Infusion Pumps** | 40 Units | Centrally managed and battery-monitored |
| **Ambulance Fleet** | 8 Vehicles | 4 Advanced Life Support (ALS), 4 Basic Life Support (BLS) |
| **Diagnostic Imaging** | 8 Major Suites | 2x 3T/1.5T MRI, 2x 256/Dual CT, 2x Digital XR, 2x Echo/US |

---

## 3. Hospital Departments (15 Operational Units)

1. **Emergency Department (ED)**: Rapid triage, resuscitation, and trauma intake.
2. **Outpatient Department (OPD)**: Specialist clinics, ambulatory consultations, day observation.
3. **Inpatient Department (IPD)**: Medical-surgical inpatient floors (Levels 3 through 6).
4. **Intensive Care Unit (ICU)**: Multi-disciplinary critical care (Medical, Surgical, Cardiac, Neuro).
5. **Laboratory (Pathology & Biochemistry)**: Clinical chemistry, hematology, microbiology (LOINC standard).
6. **Radiology & Imaging**: CT, MRI, X-ray, Ultrasound (DICOM/PACS simulation).
7. **Central Pharmacy**: Formulary dispensing, controlled substance vault, RxNorm indexing.
8. **Transfusion & Blood Bank**: Type-specific unit inventory (A+, A-, B+, B-, AB+, AB-, O+, O-).
9. **Billing & Insurance**: Charge master, EDI 837 claim drafting, copay & deductible calculator.
10. **Medical Records Department (HIM)**: MRN registry, legal release of information, archive integrity.
11. **Nursing Administration**: Shift scheduling, nurse-to-patient staffing ratios.
12. **Human Resources (HR)**: Staff credentialing, licensure verification, credential records.
13. **Hospital Administration**: Executive command, capacity alerts, disaster divert protocols.
14. **IT & Security Operations (SecOps / SOC)**: Network monitoring, zero-trust gateway, canary traps.
15. **Hospital Command Centre**: Real-time cross-departmental telemetry and operational scenario execution.

---

## 4. Software Stack & System Topology

The digital twin backend is structured around a decoupled, asynchronous, zero-trust micro-architecture:

```
[ Client Browser / AI Agent / Adversary ]
                  |
                  | HTTP/REST (JSON + FHIR R4)
                  v
       +--------------------+
       |   FastAPI Server   |
       +---------+----------+
                 |
       +---------v----------+
       | Security Gateway   | <--- Role-Based Access Control (RBAC)
       | & Actor Interceptor| <--- Patient Consent & HIPAA TPO Checks
       +---------+----------+ <--- Canary Trap Detection Engine
                 |
       +---------v----------+
       | Operational Logic  | <--- Patient, Operations, Staff, Billing, Scenarios
       +---------+----------+
                 |
       +---------v----------+
       |  SQLAlchemy 2.0    |
       +---------+----------+
                 |
       +---------v----------+
       | Relational DB      | <--- SQLite (Default) / PostgreSQL (Enterprise)
       | (ACID Compliant)   | <--- Cryptographic Merkle Hash Chained Audit Ledger
       +--------------------+
```

---

## 5. Security & Boundary Architecture

1. **Immutable Merkle Audit Ledger**: Every action (READ, CREATE, UPDATE, DELETE, DISPENSE) is cryptographically chained to the previous record using `SHA-256(previous_hash + timestamp + actor + action + resource + salt)`. Row deletion or log alteration immediately breaks chain verification.
2. **Synthetic Canary Traps**: Decoy credentials (`CANARY_KEY_EHR_DB_ADMIN`, `CANARY_FINANCE_OVERRIDE_KEY`) are seeded throughout the environment. Any retrieval or injection of these tokens instantly trips an alarm and isolates the actor.
3. **Strict RBAC Invariants**: Role permissions are hard-coded in the security layer. Billing officers are mathematically denied clinical record access; AI agents are prevented from deleting audit logs or self-elevating permissions.
