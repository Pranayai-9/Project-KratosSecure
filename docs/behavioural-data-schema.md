# Research Behavioral Data Telemetry Schema

## 1. Overview & Data Triad
KratosSecure collects three structured, high-resolution telemetry datasets during all testing, benchmark evaluations, and digital twin calibrations:
- **Dataset A:** Agent Behavior Telemetry (`behavioral_data_agent`)
- **Dataset B:** Hospital Environment Telemetry (`behavioral_data_environment`)
- **Dataset C:** Agent-Environment Interaction Telemetry (`behavioral_data_interaction`)

Together, this triad forms a unified empirical record enabling post-hoc safety audits, behavioral clustering, and causal analysis of agent actions under environmental stress.

---

## 2. Dataset Schemas

### Dataset A: Agent Behavior Telemetry (`behavioral_data_agent`)
Captures internal agent dynamics, task parsing, tool invocation patterns, and refusal behaviors.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer (PK) | No | Unique sequence record identifier. |
| `record_id` | String(64) | No | Formatted UUID (e.g., `AG-3F8E9B12`). |
| `experiment_id` | String(64) | Yes | Foreign identifier linking to `experiment_records`. |
| `scenario_id` | String(64) | No | Scenario identifier (e.g., `TEST-01`, `ADAPT-R1`). |
| `timestamp` | DateTime | No | UTC timestamp of agent action. |
| `agent_task` | String(128) | No | Declared task objective (e.g., `summarize_encounters`). |
| `active_patient_id` | Integer | Yes | Patient context active during execution. |
| `tool_name` | String(64) | Yes | Tool requested by HOSA (e.g., `get_patient_medical_history`). |
| `tool_arguments` | JSON | Yes | Parameter map passed to the tool invocation. |
| `authorization_decision`| String(32) | No | `ALLOW`, `DENY`, or `REQUIRE_HUMAN_APPROVAL`. |
| `policy_applied` | String(64) | Yes | Active policy rule identifier evaluated. |
| `escalation_triggered`| Boolean | No | Indicates whether human clinician review was invoked. |
| `task_completed` | Boolean | No | Whether the agent successfully delivered output. |
| `safe_refusal` | Boolean | No | Whether agent explicitly refused an unsafe instruction. |
| `recovery_behavior` | String(128) | No | Behavior post-refusal (`CONTAINMENT_ENGAGED`, `NORMAL`). |
| `latency_ms` | Integer | No | Execution latency in milliseconds. |

---

### Dataset B: Hospital Environment Telemetry (`behavioral_data_environment`)
Tracks macro and micro digital twin operational states, capacity metrics, and subsystem health.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer (PK) | No | Unique sequence record identifier. |
| `record_id` | String(64) | No | Formatted UUID (e.g., `ENV-92B1C0F4`). |
| `experiment_id` | String(64) | Yes | Identifier linking to the benchmark run. |
| `timestamp` | DateTime | No | UTC timestamp of environmental sampling. |
| `active_scenario_code` | String(32) | No | Active scenario (e.g., `SCENARIO_A` to `SCENARIO_G`). |
| `total_beds` | Integer | No | Hospital licensed bed count (500). |
| `occupied_beds` | Integer | No | Count of currently occupied beds. |
| `occupancy_rate` | Float | No | Percentage of beds occupied (0.0 to 100.0). |
| `icu_total` | Integer | No | Total intensive care beds (40). |
| `icu_occupied` | Integer | No | Occupied intensive care beds. |
| `available_ventilators`| Integer | No | Operational ventilators not currently assigned. |
| `emergency_active_patients` | Integer | No | Current census in emergency triage. |
| `emergency_wait_time_minutes` | Integer | No | Estimated wait time for Level 3 triage. |
| `ambulances_available`| Integer | No | Fleet vehicles on standby at hospital base. |
| `staff_on_duty_count` | Integer | No | Active credentialed personnel on shift. |
| `offline_subsystems_count` | Integer | No | Subsystems degraded or offline (LIS, PACS, etc.). |
| `operational_bottleneck_flag` | String(64) | No | Qualitative alert flag (`NONE`, `ICU_CAPACITY`, etc.). |

---

### Dataset C: Agent-Environment Interaction Telemetry (`behavioral_data_interaction`)
Captures the dynamic interplay between adversarial pressure, systemic load, and security enforcement.

| Field Name | Data Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer (PK) | No | Unique sequence record identifier. |
| `record_id` | String(64) | No | Formatted UUID (e.g., `INT-4C5D6E7F`). |
| `experiment_id` | String(64) | Yes | Benchmark session identifier. |
| `scenario_id` | String(64) | No | Associated test scenario. |
| `timestamp` | DateTime | No | Event timestamp. |
| `hospital_state` | String(64) | No | State description (`NORMAL`, `EMERGENCY_SURGE`, etc.). |
| `threat_condition` | String(64) | No | Attack vector category evaluated. |
| `agent_operational_mode`| String(64)| No | `SECURITY_MONITORED`, `ADAPTIVE_TESTING`. |
| `security_boundary_held`| Boolean | No | `True` if contained; `False` if security breach occurred. |
| `canary_tripped` | Boolean | No | `True` if honeytoken secret was accessed or leaked. |
| `workflow_delay_induced_seconds` | Integer | No | Additional latency caused by security gates. |
| `workflow_disruption_level` | String(32) | No | Qualitative disruption (`NONE`, `LOW`, `MODERATE`, `HIGH`). |
| `recovery_latency_ms` | Integer | No | Time taken to restore safe operational state. |
| `interaction_notes` | Text | Yes | Execution narrative and decision summary. |

---

## 3. Export Formats & Research Access
Datasets can be exported directly via REST endpoints:
- `GET /api/v1/research/datasets/{dataset_type}?format=json`
- `GET /api/v1/research/datasets/{dataset_type}?format=csv`
