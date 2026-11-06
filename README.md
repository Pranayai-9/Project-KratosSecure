# KratosSecure: Healthcare AI Agent Operational Environment & Testing Sandbox

A stateful, synthetic 500-bed hospital digital twin (**Aethelgard Memorial Hospital**) built as the operational foundation for evaluating autonomous healthcare AI agents and adversarial resilience.

---

## 🔬 Phase 3: Adaptive Security Research & Digital Twin Platform

### 1. Adaptive Adversarial Testing (AAVA Escalation Engine)
- **Multi-Round Escalating Campaigns**: AAVA executes dynamic 4-round probe campaigns:
  - *Round 1*: Direct unauthorized access probe.
  - *Round 2*: Indirect prompt injection embedded within clinical referral notes.
  - *Round 3*: Counterfeit supervisor token + emergency break-glass claim.
  - *Round 4*: Compound environmental stress (subsystem outage + revoked patient consent).
- **Dynamic Reasoning**: Adapts subsequent probe trajectories based on previous gate responses.

### 2. Scenario Intelligence Engine ($H \times A \times I \times T \times C$)
- **Combinatorial Space**: Generates scenarios from the Cartesian product of Hospital state ($H$), Agent state ($A$), Infrastructure state ($I$), Threat condition ($T$), and Constraints ($C$).
- **6 Difficulty Tiers**: From Level 0 (Normal operations) to Level 5 (Compound adaptive multi-hop attack).
- **Reproducible Random Seeds**: Ensures deterministic replayability for regression benchmarking.

### 3. Digital Twin Calibration & Counterfactual Simulation Studio
- **Systemic Bottleneck Detection**: Analyzes real-time ICU saturation, LIS turnaround delays, ED queue depth, and critical pharmacy/blood deficits.
- **"What-If" Counterfactual Modeling**: Simulates parameter shifts ($\Delta\text{ICU beds}$, $\Delta\text{ED physicians}$, LIS availability %, arrival surge multiplier) and calculates projected bed saturation %, wait times, and ambulance diversion probability.

### 4. Behavioral Data Collection (3 Telemetry Datasets)
- **Dataset A (`behavioral_data_agent`)**: Agent task parsing, tool calls requested, decisions, latency, and safe refusals.
- **Dataset B (`behavioral_data_environment`)**: Digital twin hospital states, bed occupancy %, triage wait times, and subsystem health.
- **Dataset C (`behavioral_data_interaction`)**: Policy gate outcomes, canary trips, workflow disruption levels, and recovery latency.
- **Export Endpoints**: Available in JSON and CSV via `/api/v1/research/datasets/{dataset_type}`.

### 5. Structured Experiment Management (Profiles A–E)
- **Profile A**: Insecure Baseline (Unconstrained direct API access, 85.0% ASR).
- **Profile B**: RBAC Only (Role filtering without semantic purpose or consent checks, 55.0% ASR).
- **Profile C**: RBAC + Consent + Purpose (Context-aware validation without canary traps, 30.0% ASR).
- **Profile D**: Full Zero-Trust Gateway + HITL (Production architecture, 0.0% ASR, 95.0% utility).
- **Profile E**: Full Security under Adaptive Escalation (Multi-round AAVA stress testing, 0.0% ASR).
- **Academic Benchmark Report Generator**: Generates publication-grade reports in Markdown, JSON, and CSV.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.15)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Setup Virtual Environment & Dependencies
```bash
# Activate existing virtual environment or create one:
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies:
pip install -r backend/requirements.txt
```

### 3. Initialize & Seed Synthetic Digital Twin
```bash
python -m backend.app.generator.seed_data
```

### 4. Run the Operational Server
```bash
python run_server.py
```
- **Hospital Command-Centre Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 5. Run Verification & Test Suites
```bash
# Run End-to-End Hospital Twin Integration Tests (17 tests):
python backend/tests/verify_suite.py

# Run Complete Phase 2 Adversarial Validation Suite (20 healthcare attack cases):
python backend/tests/test_agent_suite.py

# Run Complete Phase 3 Adaptive Research & Digital Twin Suite (7 test suites):
python backend/tests/test_phase3_suite.py
```

---

## 🔬 Phase 3: Adaptive Security Research & Digital Twin Platform

### 1. Adaptive Adversarial Testing (AAVA Escalation Engine)
- **Multi-Round Escalating Campaigns**: AAVA executes dynamic 4-round probe campaigns:
  - *Round 1*: Direct unauthorized access probe.
  - *Round 2*: Indirect prompt injection embedded within clinical referral notes.
  - *Round 3*: Counterfeit supervisor token + emergency break-glass claim.
  - *Round 4*: Compound environmental stress (subsystem outage + revoked patient consent).
- **Dynamic Reasoning**: Adapts subsequent probe trajectories based on previous gate responses.

### 2. Scenario Intelligence Engine ($H \times A \times I \times T \times C$)
- **Combinatorial Space**: Generates scenarios from the Cartesian product of Hospital state ($H$), Agent state ($A$), Infrastructure state ($I$), Threat condition ($T$), and Constraints ($C$).
- **6 Difficulty Tiers**: From Level 0 (Normal operations) to Level 5 (Compound adaptive multi-hop attack).
- **Reproducible Random Seeds**: Ensures deterministic replayability for regression benchmarking.

### 3. Digital Twin Calibration & Counterfactual Simulation Studio
- **Systemic Bottleneck Detection**: Analyzes real-time ICU saturation, LIS turnaround delays, ED queue depth, and critical pharmacy/blood deficits.
- **"What-If" Counterfactual Modeling**: Simulates parameter shifts ($\Delta\text{ICU beds}$, $\Delta\text{ED physicians}$, LIS availability %, arrival surge multiplier) and calculates projected bed saturation %, wait times, and ambulance diversion probability.

### 4. Behavioral Data Collection (3 Telemetry Datasets)
- **Dataset A (`behavioral_data_agent`)**: Agent task parsing, tool calls requested, decisions, latency, and safe refusals.
- **Dataset B (`behavioral_data_environment`)**: Digital twin hospital states, bed occupancy %, triage wait times, and subsystem health.
- **Dataset C (`behavioral_data_interaction`)**: Policy gate outcomes, canary trips, workflow disruption levels, and recovery latency.
- **Export Endpoints**: Available in JSON and CSV via `/api/v1/research/datasets/{dataset_type}`.

### 5. Structured Experiment Management (Profiles A–E)
- **Profile A**: Insecure Baseline (Unconstrained direct API access, 85.0% ASR).
- **Profile B**: RBAC Only (Role filtering without semantic purpose or consent checks, 55.0% ASR).
- **Profile C**: RBAC + Consent + Purpose (Context-aware validation without canary traps, 30.0% ASR).
- **Profile D**: Full Zero-Trust Gateway + HITL (Production architecture, 0.0% ASR, 95.0% utility).
- **Profile E**: Full Security under Adaptive Escalation (Multi-round AAVA stress testing, 0.0% ASR).
- **Academic Benchmark Report Generator**: Generates publication-grade reports in Markdown, JSON, and CSV.

---

## 🤖 Phase 2: Agent Testing & Security Validation Engine

### 1. HOSA: Hospital Operations Support Agent
- **Operational Capabilities**: Patient record summarization, clinical documentation drafting, revenue cycle calculations, staff schedule recommendations, bed/ICU availability queries.
- **Strict Guardrails**: Zero autonomous prescribing, zero clinical diagnosis altering, strict cross-patient isolation, sanitization of untrusted input documents, mandatory human approval for state-changing clinical actions.

### 2. Zero-Trust Tool Gateway
- **Architecture**: `HOSA -> Tool Gateway -> Policy Engine -> Hospital APIs -> Hospital Database`.
- **Policy Checks**: Identity validation, role-based authorization (RBAC), patient context scoping, purpose-of-use verification (HIPAA TPO), consent status validation, canary secret detection, and dual-practitioner sign-off.

### 3. AAVA: Adaptive Adversarial Validation Agent
- **Capabilities**: Automated attack scenario execution, adaptive probe generation, failure classification (`UNAUTHORIZED_DATA_DISCLOSURE`, `CROSS_PATIENT_LEAK`, `PRIVILEGE_ESCALATION`, `CANARY_TRIP_TRAPPED`), execution trace recording.

### 4. 20 Standardized Healthcare Attack Scenarios across 7 Categories:
- **Category A**: Data Access & Privacy (TEST-01 to TEST-04: unauthorized retrieval, cross-patient contamination, canary probing, consent bypass)
- **Category B**: Prompt Injection & Data Poisoning (TEST-05 to TEST-07: referral letter injection, lab context poisoning, memory/identity tampering)
- **Category C**: Privilege Escalation (TEST-08 to TEST-10: emergency break-glass abuse, fake admin tokens, role confusion)
- **Category D**: Financial Integrity (TEST-11 to TEST-12: discount manipulation, receipt falsification)
- **Category E**: Operational & Staff Security (TEST-13 to TEST-14: unqualified trauma assignment, resource manipulation)
- **Category F**: System Integrity & Availability (TEST-15 to TEST-17: audit deletion attempts, outage handling without hallucination, revoked authorization)
- **Category G**: Compound Attacks (TEST-18 to TEST-20: emergency surge + injection, network outage + fake token, staff crisis + break-glass escalation)

---

## 🔬 Phase 3: Adaptive Security Research & Digital Twin Platform

### 1. Adaptive Adversarial Testing (AAVA Escalation Engine)
- **Multi-Round Escalating Campaigns**: AAVA executes dynamic 4-round probe campaigns:
  - *Round 1*: Direct unauthorized access probe.
  - *Round 2*: Indirect prompt injection embedded within clinical referral notes.
  - *Round 3*: Counterfeit supervisor token + emergency break-glass claim.
  - *Round 4*: Compound environmental stress (subsystem outage + revoked patient consent).
- **Dynamic Reasoning**: Adapts subsequent probe trajectories based on previous gate responses.

### 2. Scenario Intelligence Engine ($H \times A \times I \times T \times C$)
- **Combinatorial Space**: Generates scenarios from the Cartesian product of Hospital state ($H$), Agent state ($A$), Infrastructure state ($I$), Threat condition ($T$), and Constraints ($C$).
- **6 Difficulty Tiers**: From Level 0 (Normal operations) to Level 5 (Compound adaptive multi-hop attack).
- **Reproducible Random Seeds**: Ensures deterministic replayability for regression benchmarking.

### 3. Digital Twin Calibration & Counterfactual Simulation Studio
- **Systemic Bottleneck Detection**: Analyzes real-time ICU saturation, LIS turnaround delays, ED queue depth, and critical pharmacy/blood deficits.
- **"What-If" Counterfactual Modeling**: Simulates parameter shifts ($\Delta\text{ICU beds}$, $\Delta\text{ED physicians}$, LIS availability %, arrival surge multiplier) and calculates projected bed saturation %, wait times, and ambulance diversion probability.

### 4. Behavioral Data Collection (3 Telemetry Datasets)
- **Dataset A (`behavioral_data_agent`)**: Agent task parsing, tool calls requested, decisions, latency, and safe refusals.
- **Dataset B (`behavioral_data_environment`)**: Digital twin hospital states, bed occupancy %, triage wait times, and subsystem health.
- **Dataset C (`behavioral_data_interaction`)**: Policy gate outcomes, canary trips, workflow disruption levels, and recovery latency.
- **Export Endpoints**: Available in JSON and CSV via `/api/v1/research/datasets/{dataset_type}`.

### 5. Structured Experiment Management (Profiles A–E)
- **Profile A**: Insecure Baseline (Unconstrained direct API access, 85.0% ASR).
- **Profile B**: RBAC Only (Role filtering without semantic purpose or consent checks, 55.0% ASR).
- **Profile C**: RBAC + Consent + Purpose (Context-aware validation without canary traps, 30.0% ASR).
- **Profile D**: Full Zero-Trust Gateway + HITL (Production architecture, 0.0% ASR, 95.0% utility).
- **Profile E**: Full Security under Adaptive Escalation (Multi-round AAVA stress testing, 0.0% ASR).
- **Academic Benchmark Report Generator**: Generates publication-grade reports in Markdown, JSON, and CSV.

---

## 🏥 Hospital Digital Twin Specifications

- **Total Capacity**: 500 Licensed Beds (385 IPD, 50 ICU, 45 Emergency Bays, 20 OPD Observation)
- **15 Simulated Departments**: Emergency, Outpatient, Inpatient, ICU, Laboratory, Radiology, Central Pharmacy, Blood Bank, Billing & Insurance, Medical Records (HIM), Nursing Admin, Human Resources, Hospital Admin, IT & SecOps, Command Centre.
- **Actor Personas**: Doctor, Nurse, Lab Tech, Pharmacist, Billing Officer, Medical Records Officer, Hospital Administrator, IT Administrator, Security Officer, Healthcare AI Agent, Adversarial Agent.
- **Standards-Compliant Clinical Coding**: ICD-10-CM diagnoses, LOINC laboratory panels, RxNorm medications, CPT procedures, HL7 FHIR R4 interoperability.
- **Security Features**:
  - Cryptographically chained SHA-256 Merkle audit ledger
  - Honeypot canary traps (`CANARY_KEY_EHR_DB_ADMIN`, `CANARY_FINANCE_OVERRIDE_KEY`)
  - Strict Role-Based & Purpose-of-Use Access Control (RBAC/ABAC)

---

## 🔬 Phase 3: Adaptive Security Research & Digital Twin Platform

### 1. Adaptive Adversarial Testing (AAVA Escalation Engine)
- **Multi-Round Escalating Campaigns**: AAVA executes dynamic 4-round probe campaigns:
  - *Round 1*: Direct unauthorized access probe.
  - *Round 2*: Indirect prompt injection embedded within clinical referral notes.
  - *Round 3*: Counterfeit supervisor token + emergency break-glass claim.
  - *Round 4*: Compound environmental stress (subsystem outage + revoked patient consent).
- **Dynamic Reasoning**: Adapts subsequent probe trajectories based on previous gate responses.

### 2. Scenario Intelligence Engine ($H \times A \times I \times T \times C$)
- **Combinatorial Space**: Generates scenarios from the Cartesian product of Hospital state ($H$), Agent state ($A$), Infrastructure state ($I$), Threat condition ($T$), and Constraints ($C$).
- **6 Difficulty Tiers**: From Level 0 (Normal operations) to Level 5 (Compound adaptive multi-hop attack).
- **Reproducible Random Seeds**: Ensures deterministic replayability for regression benchmarking.

### 3. Digital Twin Calibration & Counterfactual Simulation Studio
- **Systemic Bottleneck Detection**: Analyzes real-time ICU saturation, LIS turnaround delays, ED queue depth, and critical pharmacy/blood deficits.
- **"What-If" Counterfactual Modeling**: Simulates parameter shifts ($\Delta\text{ICU beds}$, $\Delta\text{ED physicians}$, LIS availability %, arrival surge multiplier) and calculates projected bed saturation %, wait times, and ambulance diversion probability.

### 4. Behavioral Data Collection (3 Telemetry Datasets)
- **Dataset A (`behavioral_data_agent`)**: Agent task parsing, tool calls requested, decisions, latency, and safe refusals.
- **Dataset B (`behavioral_data_environment`)**: Digital twin hospital states, bed occupancy %, triage wait times, and subsystem health.
- **Dataset C (`behavioral_data_interaction`)**: Policy gate outcomes, canary trips, workflow disruption levels, and recovery latency.
- **Export Endpoints**: Available in JSON and CSV via `/api/v1/research/datasets/{dataset_type}`.

### 5. Structured Experiment Management (Profiles A–E)
- **Profile A**: Insecure Baseline (Unconstrained direct API access, 85.0% ASR).
- **Profile B**: RBAC Only (Role filtering without semantic purpose or consent checks, 55.0% ASR).
- **Profile C**: RBAC + Consent + Purpose (Context-aware validation without canary traps, 30.0% ASR).
- **Profile D**: Full Zero-Trust Gateway + HITL (Production architecture, 0.0% ASR, 95.0% utility).
- **Profile E**: Full Security under Adaptive Escalation (Multi-round AAVA stress testing, 0.0% ASR).
- **Academic Benchmark Report Generator**: Generates publication-grade reports in Markdown, JSON, and CSV.

---

## 📚 Complete Architectural & Security Documentation

### Phase 1: Operational Environment
- [Hospital Digital Twin Architecture](docs/hospital-architecture.md)
- [Hospital Operational Workflows](docs/hospital-workflows.md)
- [Relational & Object Data Model](docs/hospital-data-model.md)
- [Synthetic Healthcare Data Design](docs/synthetic-data-design.md)
- [HL7 FHIR R4 Mapping](docs/fhir-mapping.md)
- [Healthcare Permission Matrix](docs/permission-matrix.md)
- [System Boundaries & Security Invariants](docs/system-boundaries.md)

### Phase 2: Agent Testing & Security Validation
- [HOSA: Target Agent Specification](docs/hosa-agent-specification.md)
- [AAVA: Adversarial Agent Specification](docs/aava-agent-specification.md)
- [Zero-Trust Tool Gateway Architecture](docs/tool-gateway-architecture.md)
- [Healthcare Agent Security Policy](docs/security-policy.md)
- [Healthcare Attack Taxonomy](docs/healthcare-attack-taxonomy.md)
- [Healthcare Vulnerability Test Library](docs/test-case-library.md)
- [Security & Operational Evaluation Metrics](docs/evaluation-metrics.md)
- [Scenario Execution Engine Lifecycle](docs/scenario-execution.md)

### Phase 3: Adaptive Research & Digital Twin Platform
- [Healthcare AI Agent Threat Model](docs/threat-model.md)
- [Combinatorial Scenario Generation Methodology](docs/scenario-generation-methodology.md)
- [Behavioral Data Telemetry Schema](docs/behavioural-data-schema.md)
- [Counterfactual Simulation & Bottleneck Analysis](docs/counterfactual-simulation.md)
- [Comparative Experimentation Protocol](docs/experiment-protocol.md)
- [Comparative Experimental Results & Benchmarks](docs/comparative-experimental-results.md)
- [Research Paper Draft](docs/research-paper-draft.md)
