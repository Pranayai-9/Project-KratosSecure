from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.agent.hosa import HOSA, HOSARequest, HOSAResponse
from backend.app.agent.gateway import ToolGateway, GatewayInvocationRequest, GatewayDecision
from backend.app.agent.tools import AVAILABLE_TOOLS, ToolDefinition
from backend.app.agent.taxonomy import TEST_CASES_LIBRARY, ATTACK_CATEGORIES, TestCaseDefinition
from backend.app.agent.aava import AAVA
from backend.app.agent.scenarios import ScenarioExecutionEngine, ScenarioExecutionResult
from backend.app.agent.evaluator import SecurityEvaluationEngine
from backend.app.models.execution import ExecutionTrace

router = APIRouter(prefix="/agent", tags=["Agent Security & Adversarial Engine"])

# 1. HOSA Interaction
@router.post("/hosa/prompt", response_model=HOSAResponse)
def send_hosa_prompt(
    request: HOSARequest,
    db: Session = Depends(get_db)
):
    """
    Direct prompt interface to HOSA (Hospital Operations Support Agent).
    Processes user request through safety guardrails and the Tool Gateway.
    """
    return HOSA.process_task(db, request)

# 2. Tool Gateway Registry & Invocation
@router.get("/tools", response_model=Dict[str, ToolDefinition])
def get_available_tools():
    """Retrieve all operational tools available to HOSA with parameter schemas."""
    return AVAILABLE_TOOLS

@router.post("/gateway/invoke", response_model=GatewayDecision)
def invoke_gateway_tool(
    request: GatewayInvocationRequest,
    db: Session = Depends(get_db)
):
    """Directly invokes the Zero-Trust Tool Gateway with policy evaluation."""
    return ToolGateway.invoke_tool(db, request)

# 3. Attack Taxonomy & Test Cases Library
@router.get("/taxonomy")
def get_attack_taxonomy(
    category: Optional[str] = Query(None, description="Filter by category (CATEGORY_A to CATEGORY_G)"),
    severity: Optional[str] = Query(None)
):
    """Retrieve structured attack taxonomy and searchable test case library (20 test cases)."""
    cases = TEST_CASES_LIBRARY
    if category:
        cases = [c for c in cases if c.category == category]
    if severity:
        cases = [c for c in cases if c.severity == severity]
    return {
        "categories": ATTACK_CATEGORIES,
        "total_test_cases": len(cases),
        "test_cases": cases
    }

# 4. AAVA Adversarial Test Execution
@router.post("/aava/run-test/{test_id}", response_model=ScenarioExecutionResult)
def run_adversarial_test(
    test_id: str,
    db: Session = Depends(get_db)
):
    """
    Executes a single test case (e.g. TEST-01 to TEST-20) through the
    10-step Scenario Execution Lifecycle.
    """
    tc = AAVA.get_test_case(test_id)
    if not tc:
        raise HTTPException(status_code=404, detail=f"Test case '{test_id}' not found.")
    return ScenarioExecutionEngine.execute_test_case(db, tc)

@router.post("/aava/run-suite")
def run_full_validation_suite(db: Session = Depends(get_db)):
    """Runs all 20 test cases in the validation library and persists execution traces."""
    return ScenarioExecutionEngine.execute_all_scenarios(db)

@router.post("/aava/adaptive-probe", response_model=ScenarioExecutionResult)
def run_adaptive_probe(
    category: str = Query("CATEGORY_B"),
    difficulty: str = Query("medium"),
    db: Session = Depends(get_db)
):
    """AAVA synthesizes and executes an adaptive attack variation."""
    adaptive_case = AAVA.generate_adaptive_probe(category, difficulty)
    return ScenarioExecutionEngine.execute_test_case(db, adaptive_case)

# 5. Execution Traces
@router.get("/traces")
def get_execution_traces(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve past scenario execution traces."""
    traces = db.query(ExecutionTrace).order_by(ExecutionTrace.id.desc()).limit(limit).all()
    return [{
        "trace_id": t.trace_id,
        "scenario_id": t.scenario_id,
        "scenario_name": t.scenario_name,
        "category": t.category,
        "status": t.status,
        "attack_succeeded": t.attack_succeeded,
        "created_at": t.created_at.isoformat()
    } for t in traces]

@router.get("/traces/{trace_id}")
def get_trace_details(
    trace_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full chronological execution steps and metadata for a test trace."""
    trace = db.query(ExecutionTrace).filter(ExecutionTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Execution trace not found.")
    return {
        "trace_id": trace.trace_id,
        "scenario_id": trace.scenario_id,
        "scenario_name": trace.scenario_name,
        "category": trace.category,
        "status": trace.status,
        "attack_objective": trace.attack_objective,
        "requesting_actor": trace.requesting_actor,
        "hosa_response": trace.hosa_response,
        "attack_succeeded": trace.attack_succeeded,
        "policy_violation_detected": trace.policy_violation_detected,
        "canary_tripped": trace.canary_tripped,
        "legitimate_task_completed": trace.legitimate_task_completed,
        "execution_steps": trace.execution_steps,
        "metrics": trace.metrics,
        "created_at": trace.created_at.isoformat()
    }

# 6. Security Evaluation & Analytics
@router.get("/analytics")
def get_evaluation_analytics(db: Session = Depends(get_db)):
    """Computes full Security, Agent Utility, and Operational Metrics."""
    return SecurityEvaluationEngine.compute_evaluation_report(db)
