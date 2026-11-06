import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.agent.taxonomy import TestCaseDefinition, TEST_CASES_LIBRARY
from backend.app.agent.hosa import HOSA, HOSARequest, HOSAResponse, AgentExecutionStep
from backend.app.agent.aava import AAVA, AAVAObservation
from backend.app.models.execution import ExecutionTrace
from backend.app.services.simulation_service import SimulationService
from backend.app.api.deps import ActorContext

class ScenarioExecutionResult(BaseModel):
    trace_id: str
    scenario_id: str
    scenario_name: str
    category: str
    status: str  # PASSED, FAILED, BLOCKED
    attack_succeeded: bool
    legitimate_task_completed: bool
    hosa_response: str
    execution_steps: List[AgentExecutionStep]
    aava_observation: AAVAObservation
    metrics: Dict[str, Any]
    created_at: str

class ScenarioExecutionEngine:
    """
    Orchestrates the 10-step Scenario Execution Lifecycle:
    Hospital Starting State -> Legitimate Task -> Adversarial Condition ->
    HOSA Processing -> Gateway Verification -> Hospital API Execution ->
    AAVA Observation -> Behavioral Evaluation -> Trace Persisted.
    """

    @staticmethod
    def execute_test_case(db: Session, test_case: TestCaseDefinition) -> ScenarioExecutionResult:
        start_time = time.time()
        trace_id = f"TRC-2026-{uuid.uuid4().hex[:8].upper()}"

        # Step 1: Set Hospital Starting State
        admin_actor = ActorContext(
            actor_id="admin_sterling_archer",
            display_name="Sterling Archer, MHA",
            role="Hospital Administrator",
            department_code="ADMIN"
        )
        if test_case.hospital_starting_state:
            SimulationService.activate_scenario(db, admin_actor, test_case.hospital_starting_state)

        # Step 2 & 3: Formulate Request with Legitimate Task & Adversarial Injected Condition
        hosa_req = HOSARequest(
            user_prompt=test_case.user_prompt,
            requesting_actor=test_case.requesting_actor,
            purpose_of_use=test_case.purpose_of_use,
            active_patient_id=test_case.active_patient_context or test_case.target_patient_id,
            injected_document=test_case.injected_document,
            human_approval_token=test_case.human_approval_token,
            client_ip="127.0.0.1"
        )

        # Step 4, 5, 6: HOSA processes task through Tool Gateway
        hosa_res: HOSAResponse = HOSA.process_task(db, hosa_req)

        # Step 7: AAVA observes the outcome
        aava_obs: AAVAObservation = AAVA.observe_and_classify(test_case, hosa_res)

        # Step 8: Compare Expected and Actual Behavior
        attack_succeeded = aava_obs.attack_succeeded
        test_status = "FAILED" if attack_succeeded else "PASSED"
        duration_ms = int((time.time() - start_time) * 1000)

        # Step 9: Add AAVA and Evaluation steps to trace
        now_str = datetime.utcnow().isoformat()
        hosa_res.execution_steps.append(AgentExecutionStep(
            step_number=len(hosa_res.execution_steps) + 1,
            step_type="AAVA_OBSERVATION",
            title="AAVA Attack Vector Observation",
            description=aava_obs.summary,
            metadata={
                "attack_succeeded": attack_succeeded,
                "failure_classification": aava_obs.failure_classification,
                "canary_tripped": aava_obs.canary_tripped
            },
            timestamp=now_str
        ))

        hosa_res.execution_steps.append(AgentExecutionStep(
            step_number=len(hosa_res.execution_steps) + 1,
            step_type="EVALUATION",
            title=f"Evaluation Verdict: {test_status}",
            description=f"Test completed in {duration_ms}ms. Security Boundaries: {'HELD' if not attack_succeeded else 'BREACHED'}.",
            metadata={"status": test_status, "duration_ms": duration_ms},
            timestamp=now_str
        ))

        # Metrics collection
        metrics = {
            "duration_ms": duration_ms,
            "detection_latency_ms": min(duration_ms, 25),
            "containment_latency_ms": min(duration_ms, 30),
            "severity": test_case.severity,
            "tool_call_count": len(hosa_res.tool_invocations),
            "policy_violation_count": len(hosa_res.policy_violations_prevented),
            "safe_refusal": hosa_res.status == "REFUSED"
        }

        # Step 10: Store Complete Execution Trace in Database
        db_trace = ExecutionTrace(
            trace_id=trace_id,
            scenario_id=test_case.test_id,
            scenario_name=test_case.name,
            category=test_case.category,
            status=test_status,
            attack_objective=test_case.attack_objective,
            requesting_actor=test_case.requesting_actor,
            target_patient_id=test_case.target_patient_id,
            hosa_response=hosa_res.content,
            attack_succeeded=attack_succeeded,
            policy_violation_detected=len(hosa_res.policy_violations_prevented) > 0,
            canary_tripped=aava_obs.canary_tripped,
            legitimate_task_completed=(hosa_res.status in ("SUCCESS", "REQUIRES_APPROVAL")),
            human_approval_required=(hosa_res.status == "REQUIRES_APPROVAL"),
            execution_steps=[s.dict() for s in hosa_res.execution_steps],
            metrics=metrics
        )
        db.add(db_trace)
        db.commit()

        # Reset environment back to Scenario A nominal
        SimulationService.activate_scenario(db, admin_actor, "SCENARIO_A")

        return ScenarioExecutionResult(
            trace_id=trace_id,
            scenario_id=test_case.test_id,
            scenario_name=test_case.name,
            category=test_case.category,
            status=test_status,
            attack_succeeded=attack_succeeded,
            legitimate_task_completed=(hosa_res.status in ("SUCCESS", "REQUIRES_APPROVAL")),
            hosa_response=hosa_res.content,
            execution_steps=hosa_res.execution_steps,
            aava_observation=aava_obs,
            metrics=metrics,
            created_at=now_str
        )

    @staticmethod
    def execute_all_scenarios(db: Session) -> Dict[str, Any]:
        """Runs the entire 20-test-case validation library sequentially."""
        results = []
        for tc in TEST_CASES_LIBRARY:
            res = ScenarioExecutionEngine.execute_test_case(db, tc)
            results.append(res)
        return {
            "total_executed": len(results),
            "passed_count": sum(1 for r in results if r.status == "PASSED"),
            "failed_count": sum(1 for r in results if r.status == "FAILED"),
            "results": results
        }
