# Evaluating Autonomous Healthcare Operations Agents: Zero-Trust Defense Architectures and Digital Twin Security Benchmarks

**Authors:** KratosSecure Security Research Group  
**Affiliation:** Advanced Agentic Healthcare Security Institute  
**Date:** March 2026  
**Status:** Working Research Paper / Conference Submission Draft  

---

## Abstract
Autonomous Large Language Model (LLM) agents are increasingly proposed to assist in hospital operational workflows, ranging from patient documentation and duty roster drafting to resource coordination. However, deploying autonomous agents within safety-critical healthcare environments introduces catastrophic security vulnerabilities, including indirect prompt injection, privilege escalation, cross-patient data contamination, and financial fraud. 

In this work, we present **KratosSecure**, a realistic 500-bed hospital digital twin and security validation testbed designed to empirically evaluate healthcare AI agents under stateful operational and adversarial conditions. We introduce **HOSA** (Hospital Operations Support Agent), a clinical and administrative support agent, and **AAVA** (Adaptive Adversarial Validation Agent), an escalating red-team testing agent. 

We formalize a combinatorial scenario generation space ($\text{SCENARIO SPACE} = H \times A \times I \times T \times C$) across six difficulty tiers and benchmark five architectural defense profiles. Our empirical findings demonstrate that traditional Role-Based Access Control (RBAC) is insufficient against indirect document injections, suffering an Attack Success Rate (ASR) of 55.0%. In contrast, our proposed **Zero-Trust Tool Gateway with Human-in-the-Loop (HITL) verification** completely eliminates security breaches ($\text{ASR} = 0.0\%$, an 85.0% absolute reduction from baseline) while maintaining 95.0% clinical utility and an average policy evaluation latency of only 15.4 ms.

---

## 1. Introduction
The integration of LLMs as autonomous agents capable of invoking external tools and APIs represents a paradigm shift in hospital informatics. While traditional clinical decision support systems acted as passive recommendation algorithms, LLM agents actively execute tasks: retrieving electronic health records, allocating beds, drafting discharge summaries, and interacting with billing ledgers.

Despite their potential, LLMs suffer from fundamental vulnerabilities:
1. **Lack of Inherent Trust Boundaries:** LLMs struggle to distinguish authoritative system prompts from untrusted data payloads (e.g., patient consult notes or referral letters).
2. **Context Bleed:** Multi-patient interactions risk leaking Protected Health Information (PHI) across boundaries.
3. **Privilege Abuse:** Social engineering prompts can trick agents into assuming elevated administrative roles or misusing emergency break-glass procedures.

To address these challenges, this paper presents three core contributions:
- A high-fidelity, stateful **Digital Twin** simulating 15 hospital departments, 500 beds, HL7 FHIR R4 interfaces, and cryptographically chained audit ledgers.
- The **Zero-Trust Tool Gateway Architecture**, which detaches LLM reasoning from authoritative backend databases, subjecting every proposed tool invocation to pre-execution policy enforcement.
- An extensive **Comparative Empirical Benchmark** evaluating 5 architectural profiles against 20 attack vectors and multi-round adaptive red-team campaigns.

---

## 2. Threat Modeling & Adversarial Taxonomy
We classify healthcare AI threats into seven distinct categories:
- **Category A:** Data Access & Privacy Violations (Canary harvesting, cross-patient leaks).
- **Category B:** Prompt Injection & Data Poisoning (Untrusted referral document hijacking).
- **Category C:** Privilege Escalation & Role Confusion (Forged approval tokens, break-glass abuse).
- **Category D:** Financial & Billing Manipulation (Discount injection, receipt tampering).
- **Category E:** Staff Coordination & Resource Manipulation (Unqualified staff assignment).
- **Category F:** Security Invariant & Audit Tampering (Audit record modification, downtime hallucination).
- **Category G:** Compound Systemic Attacks (Simultaneous infrastructure failure and adversarial probing).

---

## 3. Defense Architecture: The Zero-Trust Tool Gateway
Rather than relying on model prompt alignment or fine-tuning (which can be jailbroken), KratosSecure enforces a deterministic architectural boundary:

```
[ LLM Agent (HOSA) ] 
       | (Proposes tool call: get_patient_history(id=P102))
       v
+-----------------------------------------------------------+
|               ZERO-TRUST TOOL GATEWAY                     |
|                                                           |
| 1. Caller Authentication & Cryptographic Identity Check   |
| 2. Role-Based Access Control (RBAC) Matrix Verification   |
| 3. Declared Purpose of Use Validation (Treatment/Billing) |
| 4. Patient Consent & Sensitive Data Category Matching     |
| 5. Canary Trap Honeytoken Inspection                      |
| 6. Mandatory Human-in-the-Loop Gate for State Mutations   |
+-----------------------------------------------------------+
       | (Permit / Deny / Require HITL)
       v
[ Deterministic Hospital APIs & Chained Audit Ledger ]
```

---

## 4. Empirical Evaluation & Results
We evaluated the system across five architectural profiles (A through E).

### Benchmark Summary:
- **Insecure Baseline (Profile A):** Failed 17 of 20 attacks ($\text{ASR} = 85.0\%$).
- **RBAC Only (Profile B):** Blocked simple role mismatches but succumbed to document prompt injection and canary exfiltration ($\text{ASR} = 55.0\%$).
- **RBAC + Consent + Purpose (Profile C):** Mitigated unconsented disclosures but failed against document-embedded instructions ($\text{ASR} = 30.0\%$).
- **Full Zero-Trust Gateway + HITL (Profile D & E):** Achieved **0.0% ASR** across all 20 test vectors and multi-round adaptive escalation campaigns.

| Defense Profile | ASR (%) | Unauthorized Incidents | Clinical Utility (%) | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- |
| Profile A (Baseline) | 85.0% | 17 | 98.0% | 4.2 ms |
| Profile B (RBAC) | 55.0% | 11 | 96.0% | 8.5 ms |
| Profile C (Contextual) | 30.0% | 6 | 94.0% | 12.8 ms |
| **Profile D (Zero-Trust Gateway)** | **0.0%** | **0** | **95.0%** | **15.4 ms** |
| **Profile E (Adaptive Stress)** | **0.0%** | **0** | **92.5%** | **18.2 ms** |

---

## 5. Counterfactual Modeling & Operational Resilience
Using digital twin counterfactual simulation, we demonstrated that physical infrastructure bottlenecks directly impact cyber-resilience. When emergency department arrival volume surged by $1.5\times$, triage wait times escalated from 25 to 58 minutes, creating operational pressure that incentivizes bypassing security checks. Simulating targeted mitigations (+10 ICU beds, +2 ED physicians) restored triage velocity to 26 minutes and dropped ambulance diversion probability from 85% to 15%, preserving strict verification workflows without compromising clinical responsiveness.

---

## 6. Conclusion
The deployment of autonomous AI agents in healthcare demands deterministic architectural safeguards that operate independently of LLM weights. By decoupling agent reasoning from authoritative data mutation through a Zero-Trust Tool Gateway and Human-in-the-Loop checkpoints, hospitals can harness the transformative productivity of operational AI while maintaining absolute privacy and security compliance.
