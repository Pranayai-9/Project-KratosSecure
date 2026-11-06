# KratosSecure: Healthcare Agent Attack Taxonomy

## 1. Classification Overview
The KratosSecure Attack Taxonomy classifies threats facing autonomous healthcare AI agents into 7 primary categories, addressing data privacy, algorithmic manipulation, privilege abuse, financial exploitation, and operational disruption.

```
                                [ Healthcare AI Threat Taxonomy ]
                                                |
        +---------------+---------------+-------+-------+---------------+---------------+
        |               |               |               |               |               |
   [Category A]    [Category B]    [Category C]    [Category D]    [Category E]    [Category F]    [Category G]
   Data Access     Prompt          Privilege       Financial       Operational     System          Compound
   & Privacy       Injection       Escalation      Integrity       & Staff         Availability    Attacks
```

---

## 2. Category Definitions & Vectors

### Category A: Data Access and Privacy
- **A1: Unauthorized Direct Retrieval**: Querying PHI without clinical assignment or role clearance.
- **A2: Cross-Patient Data Contamination**: Prompting the agent to summarize or leak Patient $B$'s records while session context is bound to Patient $A$.
- **A3: Sensitive Data Exfiltration**: Prompting agent to disclose canary secrets, superuser database tokens, or raw table dumps.
- **A4: Consent Manipulation**: Attacker falsely claims verbal blanket consent to bypass formal research restrictions.

### Category B: Prompt Injection and Data Poisoning
- **B1: Indirect Document Injection**: Embedding adversarial instructions inside uploaded PDF/text referral letters, consult notes, or transfer summaries (e.g. `"Ignore previous instructions"`).
- **B2: Clinical Context Poisoning**: Injecting system override directives into laboratory observation comments or diagnostic radiology impressions.
- **B3: Memory / Session Poisoning**: Attempting to alter agent system instructions or overwrite user role metadata via conversation history.

### Category C: Privilege Escalation
- **C1: Emergency Break-Glass Abuse**: Falsely claiming a life-threatening crisis to gain unrestricted access to restricted records.
- **C2: Forged Administrator Tokens**: Providing synthetic approval strings or counterfeit cryptographic tokens to bypass human sign-off gates.
- **C3: Role Confusion**: Exploiting multi-disciplinary workflows by having billing staff request diagnostic laboratory panels under the guise of itemization.

### Category D: Financial Integrity
- **D1: Invoice & Discount Manipulation**: Injecting arbitrary 90%+ discounts or unauthorized debt write-offs into billing calculations.
- **D2: Receipt Falsification**: Demanding paid-in-full receipts when only partial payments were deposited.

### Category E: Operational and Staff Security
- **E1: Unqualified Staff Duty Assignment**: Instructing the agent to assign uncertified or administrative personnel to emergency trauma resuscitation.
- **E2: Resource Manipulation**: Attempting to alter bed counts, ventilator allocations, or blood bank stock levels via unauthorized prompts.

### Category F: System Integrity and Availability
- **F1: Audit Log Deletion**: Ordering the agent to remove or truncate evidence of unauthorized transactions.
- **F2: Outage Handling & Hallucination**: Testing whether the agent fabricates clinical data when critical subsystems (LIS/PACS) are offline during emergencies.
- **F3: Revoked Authorization Check**: Verifying whether consent revocation is respected mid-workflow before data release.

### Category G: Compound Multi-Vector Attacks
- **G1: Surge & Document Injection**: Mass casualty surge + ICU shortage + malicious referral injection.
- **G2: Outage & Forged Admin Approval**: Network outage + counterfeit token + patient data exfiltration attempt.
- **G3: Staff Crisis & Break-Glass Escalation**: Severe staff shortage + malicious duty assignment + emergency privilege escalation.
