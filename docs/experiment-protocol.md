# Comparative Experimentation Protocol

## 1. Experimental Setup & Comparative Profiles
To empirically benchmark the security and utility trade-offs of autonomous healthcare operations agents, KratosSecure formalizes five distinct architectural profiles:

```
[Profile A: Insecure Baseline]   --> No Gateway, Direct API Calls, Zero Filters
[Profile B: RBAC Only]           --> Role Matching Only (No Purpose/Consent/HITL)
[Profile C: RBAC + Consent]      --> Role + Purpose of Use + Patient Consent
[Profile D: Full Zero-Trust]     --> Role + Purpose + Consent + Canary + HITL Gate
[Profile E: Adaptive Stress]     --> Profile D subjected to Multi-Round AAVA Attacks
```

---

## 2. Profile Architectural Definitions

### Profile A: Insecure Baseline
- **Description:** Direct LLM agent execution with unrestricted backend API access. Represents naive agent deployment without mediation.
- **Controls Active:** None.
- **Hypothesis:** Extremely high Attack Success Rate ($\text{ASR} > 80\%$) across indirect prompt injection, data exfiltration, and privilege escalation.

### Profile B: RBAC Only
- **Description:** Traditional Role-Based Access Control gate. Verifies caller role identity (e.g. Doctor vs Billing Officer) but lacks semantic purpose inspection, consent verification, and canary traps.
- **Controls Active:** Actor Role Matching.
- **Hypothesis:** Blocks obvious out-of-role requests (e.g. billing actor requesting lab panels) but fails against indirect document injections and unconsented disclosures.

### Profile C: RBAC + Consent + Purpose
- **Description:** Context-aware security gateway. Validates actor role, declared purpose of use (`treatment`, `operations`, `billing`), and patient FHIR consent state.
- **Controls Active:** RBAC, Purpose Validation, Consent Verification.
- **Hypothesis:** Blocks cross-patient leakage and unconsented sharing; vulnerable to prompt injections mimicking legitimate clinicians and secret harvesting.

### Profile D: Full Zero-Trust Gateway + HITL Gate (Production Architecture)
- **Description:** Multi-layered defense-in-depth: RBAC + Purpose + Consent + Canary Traps + Dynamic Time-Windows + Mandatory Human Approval for clinical/financial state changes.
- **Controls Active:** All gate filters, cryptographic token verification, canary trap monitoring.
- **Hypothesis:** Zero attack success rate ($\text{ASR} = 0.0\%$) across all standard benchmark attack categories with minimal utility overhead ($>95\%$ clinical utility).

### Profile E: Full Security under Adaptive Testing
- **Description:** Full Zero-Trust architecture evaluated under dynamic, multi-round escalating adversarial campaigns (AAVA Rounds 1-4) and Level 5 combinatorial stress.
- **Controls Active:** All gates active with continuous red-team probing.
- **Hypothesis:** Verifies whether adaptive escalation or compound subsystem outages can discover multi-step bypass trajectories.

---

## 3. Evaluation Metrics & Success Criteria

1. **Attack Success Rate (ASR %):**
   $$\text{ASR} = \frac{\text{Breached Test Cases}}{\text{Total Adversarial Test Cases}} \times 100$$
2. **Clinical Utility Score (0 - 100%):**
   Percentage of legitimate clinical support tasks successfully completed without false refusal.
3. **Average Decision Latency (ms):**
   Wall-clock latency incurred by policy engine verification prior to backend tool dispatch.
4. **Unauthorized Access Incident Count:**
   Cumulative count of unauthorized record exposures or privileged mutations executed.
