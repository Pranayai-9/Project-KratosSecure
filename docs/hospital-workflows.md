# KratosSecure: Hospital Operational Workflows

## 1. Overview
This document specifies the deterministic state-transition workflows implemented across Aethelgard Memorial Hospital. These workflows ensure that any state modification (such as patient admission, medication prescription, or staff shortage) deterministically updates downstream hospital resources.

---

## 2. Core Clinical & Operational Workflows

### Workflow 1: Emergency Patient Admission & Bed Allocation
```
[ Patient Arrival (Ambulance or Walk-in) ]
                   |
                   v
       [ Triage Acuity Assessment ]
         Level 1 (Resuscitation) -> Level 5 (Non-urgent)
                   |
                   v
       [ Check Bed Availability ]
                   |
     +-------------+-------------+
     |                           |
[ Bed Available ]         [ ED Saturated ]
     |                           |
     v                           v
Allocate ED Bay           Trigger ED Diversion Alert
Update Bed -> Occupied    Escalate Wait Times
Assign Attending Doctor   Log Resource Deficit
Create Encounter Record
```

- **State Changes**:
  - `beds.is_occupied` becomes `True`.
  - `encounters` record created with status `in-progress`.
  - Department wait time recalculated based on active queue length.

---

### Workflow 2: Clinical Diagnostics & Lab Orders
```
[ Attending Doctor ] ---> Drafts Lab Order (LOINC 58410-2)
                                 |
                                 v
                     [ Validate RBAC & Consent ]
                                 |
                   +-------------+-------------+
                   |                           |
               [ Permitted ]               [ Denied ]
                   |                           |
                   v                           v
        Order Dispatched to LIS        Return 403 Forbidden
                   |                   Log DENY Audit Event
                   v
        [ Check LIS Subsystem ]
        If LIS == 'offline':
          Queue in local buffer; alert physician of delay.
        If LIS == 'operational':
          Lab Tech inputs specimen results -> Status becomes 'final'.
```

---

### Workflow 3: Pharmacy Dispensing & Controlled Substances
```
[ Doctor Prescribes Medication ]
               |
               v
  [ Is Controlled Substance? ]
       |                |
     [ NO ]           [ YES ]
       |                |
       |         +------v-----------------------------+
       |         | Human Pharmacist Verification      |
       |         | AI Agent cannot bypass human check |
       |         +------+-----------------------------+
       |                |
       +-------> +------v------+
                 | Deduct Stock| (MedicineInventory.stock_quantity -= 1)
                 | Log Dispense|
                 +-------------+
```

---

### Workflow 4: Patient Discharge & Billing Clearance
```
[ Attending Doctor signs Discharge Summary ]
                   |
                   v
       [ Update Encounter: discharged ]
                   |
                   v
       [ Free Inpatient Bed ] (is_occupied = False)
                   |
                   v
       [ Compile Itemized Billing Records ]
       - Room charges, labs, medications, procedural fees
                   |
                   v
       [ Apply Insurance Copay & Deductible Rules ]
       - Calculate Patient Responsibility
                   |
                   v
       [ Process Payment / Generate Receipt Draft ]
```

---

## 3. Baseline Simulation Scenarios Workflows

| Scenario Code | Trigger Event | Primary State Shifts | Recovery Path |
| :--- | :--- | :--- | :--- |
| **SCENARIO_A** | System Initialization | Occupancy at 75%, nominal wait times, all 8 subsystems online. | Baseline steady state. |
| **SCENARIO_B** | Mass Casualty / Surge | ED occupancy 100%, wait times jump from 25m to 95m, all ambulances dispatched. | Divert incoming trauma, call off-duty triage staff. |
| **SCENARIO_C** | Critical Care Saturation | ICU beds 100% full, 0 ventilators available, critical admissions halted. | Transfer stable ICU patients to step-down IPD beds. |
| **SCENARIO_D** | Staffing Epidemic / Strike | 50% staff absence, department wait times triple, nursing deficit alerts. | Re-assign non-clinical administrative staff, emergency shifts. |
| **SCENARIO_E** | LIS Server Failure | LIS status offline, latency 9999ms, diagnostic turnarounds blocked. | Switch to paper requisitions, reboot DB connection pools. |
| **SCENARIO_F** | Core Network Disruption | 42% packet loss, PACS offline, EHR latency 850ms, failover engaged. | Activate disaster recovery routing, isolated local EHR mode. |
| **SCENARIO_G** | Financial Bottleneck | Billing subsystem degraded, discharge clearance queue stalls, bed turnover delay. | Deploy offline billing approval protocol, deferred invoicing. |
