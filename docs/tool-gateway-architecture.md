# KratosSecure: Zero-Trust Tool Gateway Architecture

## 1. Architectural Principles
Autonomous healthcare AI agents must **never** possess direct database access, network socket privileges, or unmediated file system permissions. All interactions between HOSA and the hospital digital twin pass through the **Zero-Trust Tool Gateway**.

```
+-------------------------------------------------------------+
|               HOSA (AI Operations Agent)                    |
+------------------------------+------------------------------+
                               |
                               | GatewayInvocationRequest
                               v
+-------------------------------------------------------------+
|                     Tool Gateway Engine                     |
|                                                             |
|   +-----------------------------------------------------+   |
|   | 1. Tool Registration & Schema Validation            |   |
|   | 2. Canary Honeypot Inspection                       |   |
|   | 3. Absolute Invariants Check (Audit Immutability)   |   |
|   | 4. Cross-Patient Context Isolation Check            |   |
|   | 5. Role-Based Access Control (RBAC) Matrix          |   |
|   | 6. Patient Consent Status & Purpose Validation      |   |
|   | 7. Human-in-the-Loop Approval Verification          |   |
|   +-----------------------------------------------------+   |
|                                                             |
|   Outcome: [ ALLOW | DENY | REQUIRE_HUMAN_APPROVAL ]        |
+------------------------------+------------------------------+
                               |
                               | Authorized Invocations Only
                               v
+-------------------------------------------------------------+
|       Hospital Operational APIs & Services (Deterministic)  |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|    Database & Cryptographic Merkle Audit Ledger (ACID)      |
+-------------------------------------------------------------+
```

---

## 2. Policy Enforcement Pipeline

When `ToolGateway.invoke_tool(db, request)` is called, the Gateway processes the request sequentially:

1. **Tool Registration & Parameter Validation**: Ensures the requested tool exists in `AVAILABLE_TOOLS` and arguments match Pydantic schemas.
2. **Honeypot Canary Trap Inspection**: Scans string parameters for synthetic canary secrets (`CANARY_KEY_EHR_DB_ADMIN`, `CANARY_FINANCE_OVERRIDE_KEY`). If found, trips canary alarm, records TRAPPED event, and halts execution.
3. **Audit Ledger Immutability Invariant**: Denies any attempt to call `DELETE` or `TRUNCATE` on `AuditEvent` records.
4. **Cross-Patient Isolation**: Validates that the targeted patient ID matches the active session context (`active_patient_context`). If an agent attempts to access Patient #2 while handling Patient #1, the request is denied.
5. **RBAC Authorization**: Validates caller role against `ROLE_PERMISSIONS`. Denies Billing Officers access to clinical reports, and denies unprivileged personas access to administrative tools.
6. **Patient Consent & HIPAA Purpose Validation**: Verifies that active consent exists in the database for research or external disclosure purposes.
7. **Human Approval Gate**: If the tool is designated as requiring human authorization (e.g. `draft_discharge_summary`), verifies that a valid cryptographically issued human approval token is attached. If absent, returns `REQUIRE_HUMAN_APPROVAL` and creates a pending draft.
8. **Cryptographic Merkle Audit Recording**: Every decision (ALLOW, DENY, REQUIRE_HUMAN_APPROVAL) is written to the immutable SHA-256 hash-chained audit ledger.
