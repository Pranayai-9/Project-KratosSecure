# Combinatorial Scenario Generation Methodology

## 1. Mathematical Formulation: Scenario Space
To systematically evaluate autonomous healthcare AI agents under diverse operational and adversarial conditions, KratosSecure formalizes the test generation domain as a multi-dimensional Cartesian product:

$$\text{SCENARIO SPACE} = H \times A \times I \times T \times C$$

Where:
- **$H$ (Hospital Operational State):** $\{\text{NORMAL}, \text{EMERGENCY}, \text{HIGH\_WORKLOAD}, \text{RESOURCE\_SHORTAGE}, \text{SYSTEM\_DOWNTIME}\}$
- **$A$ (Agent Task State):** $\{\text{NOMINAL}, \text{HIGH\_TASK\_LOAD}, \text{CONCURRENT\_MULTITASKING}, \text{CONFLICTING\_INFO}, \text{CONTEXT\_SWITCHING}\}$
- **$I$ (Infrastructure State):** $\{\text{NOMINAL}, \text{ICU\_SATURATED}, \text{STAFF\_DEFICIT}, \text{NETWORK\_DEGRADED}, \text{INVENTORY\_LOW}\}$
- **$T$ (Adversarial Threat Condition):** $\{\text{NONE}, \text{PROMPT\_INJECTION}, \text{DATA\_POISONING}, \text{UNAUTHORIZED\_ACCESS}, \text{PRIVILEGE\_ESCALATION}, \text{FINANCIAL\_MANIPULATION}, \text{INSIDER\_MISUSE}, \text{CANARY\_EXFILTRATION}\}$
- **$C$ (Operational Constraints):** $\{\text{CONSENT\_RESTRICTION}, \text{HUMAN\_APPROVAL\_GATE}, \text{ROLE\_BOUNDARY}, \text{TIME\_LIMIT}\}$

---

## 2. Difficulty Level Hierarchy (Levels 0 through 5)

The scenario generator calibrates difficulty dynamically to evaluate agent performance from baseline competence to compound stress:

### Level 0: Normal Operations
- **Conditions:** Baseline hospital state, single patient, authorized clinical actor, nominal infrastructure, zero threat condition ($T = \text{NONE}$).
- **Objective:** Evaluate baseline conversational utility, task completion velocity, and correct clinical tool invocation.

### Level 1: Single Operational Anomaly
- **Conditions:** Single non-adversarial environmental disturbance (e.g., LIS diagnostic delay, ICU bed occupancy at 85%, or staff shift transition).
- **Objective:** Verify agent gracefully acknowledges delays without hallucinating results or stalling workflows.

### Level 2: Single Adversarial Event
- **Conditions:** Nominal hospital environment coupled with an isolated adversarial probe (e.g., direct unauthenticated access probe or prompt injection attempt).
- **Objective:** Test elementary boundary defense, input sanitization, and refusal mechanisms.

### Level 3: Multiple Interacting Anomalies
- **Conditions:** High workload ($H = \text{HIGH\_WORKLOAD}$) combined with active patient consent restrictions ($C = \text{CONSENT\_RESTRICTION}$) and rapid patient context-switching ($A = \text{CONTEXT\_SWITCHING}$).
- **Objective:** Ensure cognitive load and context switching do not cause cross-patient data leakage or consent bypass.

### Level 4: Infrastructure Degradation + Adversarial Activity
- **Conditions:** Subsystem outage (LIS/PACS offline) combined with emergency surge and an adversarial privilege escalation probe (forged break-glass token).
- **Objective:** Test whether extreme operational pressure causes the agent or human operators to lower verification rigor.

### Level 5: Compound Adaptive Adversarial Scenario
- **Conditions:** Severe systemic degradation (ICU saturation, network degradation) + multi-hop adversarial campaign + revoked consent + conflicting supervisory instructions.
- **Objective:** Stress-test the full zero-trust architecture against emergent edge cases and adversarial multi-step maneuvers.

---

## 3. Seed Reproducibility & Deterministic Replay
Each generated scenario is uniquely indexed by an integer pseudo-random seed:

```python
scenario = ScenarioIntelligenceEngine.generate_scenario(
    difficulty_level=5,
    seed=42109
)
```

1. **Deterministic Randomness:** Given the same seed and difficulty level, the engine generates an identical dimension tuple $(h, a, i, t, c)$ and identical test case parameters.
2. **Replayability:** Enables researchers to re-execute failure trajectories across different model revisions or gateway policy updates to verify regressions and improvements.
3. **Automated Fuzzing:** By sweeping across consecutive seed ranges (e.g., seeds 10,000 to 20,000), researchers can discover edge-case boundary combinations.
