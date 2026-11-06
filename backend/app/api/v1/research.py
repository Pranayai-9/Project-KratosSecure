from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_actor, ActorContext
from backend.app.agent.intelligence import ScenarioIntelligenceEngine, IntelligentScenario
from backend.app.agent.aava import AAVA
from backend.app.agent.experiments import ExperimentManagementEngine, EXPERIMENT_PROFILES
from backend.app.services.calibration_service import CalibrationService
from backend.app.services.report_generator import ResearchReportGenerator
from backend.app.models.research import ExperimentRecord

router = APIRouter(prefix="/research", tags=["Phase 3: Research & Digital Twin Platform"])

# Request / Response Schemas
class ScenarioGenerateRequest(BaseModel):
    difficulty_level: int = Field(3, ge=0, le=5, description="Difficulty level 0 to 5")
    seed: Optional[int] = Field(None, description="Optional reproducible random seed")
    custom_dimensions: Optional[Dict[str, Any]] = None

class AdaptiveCampaignRequest(BaseModel):
    target_patient_id: int = Field(1, description="Target patient identifier for probe campaign")
    total_rounds: int = Field(4, ge=1, le=6, description="Total escalation rounds")

class CounterfactualSimulationRequest(BaseModel):
    icu_capacity_delta: int = Field(0, description="Change in total ICU bed capacity (e.g. +10 or -5)")
    ed_doctor_delta: int = Field(0, description="Change in Emergency Department physician count (e.g. +2 or -2)")
    lis_availability_pct: float = Field(100.0, ge=0.0, le=100.0, description="LIS subsystem availability percentage")
    patient_arrival_multiplier: float = Field(1.0, ge=0.1, le=5.0, description="Surge arrival rate multiplier")
    simulation_duration_hours: int = Field(24, ge=1, le=168, description="Simulated time window in hours")

class ExperimentRunRequest(BaseModel):
    test_case_ids: Optional[List[str]] = Field(None, description="Optional subset of test case IDs to run")

# --- Endpoints ---

@router.post("/intelligence/generate", summary="Generate Combinatorial Scenario (H x A x I x T x C)")
def generate_scenario(
    req: ScenarioGenerateRequest,
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Synthesizes a reproducible, multi-dimensional test scenario using the
    Scenario Space formulation: H x A x I x T x C across Difficulty Levels 0-5.
    """
    scenario = ScenarioIntelligenceEngine.generate_scenario(
        difficulty_level=req.difficulty_level,
        seed=req.seed,
        custom_dimensions=req.custom_dimensions
    )
    return scenario

@router.post("/aava/adaptive-campaign", summary="Execute Multi-Round Adaptive Adversarial Campaign")
def run_adaptive_campaign(
    req: AdaptiveCampaignRequest,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Executes an escalating 4-round adaptive red-team campaign against HOSA.
    AAVA adapts each subsequent probe based on previous containment outcomes.
    """
    result = AAVA.run_adaptive_campaign(
        db=db,
        target_patient_id=req.target_patient_id,
        total_rounds=req.total_rounds
    )
    return result

@router.get("/bottlenecks", summary="Real-Time Hospital Bottleneck & Stress Assessment")
def get_bottlenecks(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Analyzes digital twin telemetry to detect systemic bottlenecks (ICU occupancy,
    LIS delay, ED queue, inventory deficits) and calculates systemic stress score.
    """
    analysis = CalibrationService.analyze_bottlenecks(db)
    return analysis

@router.post("/counterfactual/simulate", summary="Execute Counterfactual 'What-If' Simulation")
def simulate_counterfactual(
    req: CounterfactualSimulationRequest,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Simulates operational dynamics under hypothetical infrastructure parameter shifts
    (e.g., ICU capacity delta, surge arrivals, LIS downtime) and predicts diversion risk.
    """
    sim_result = CalibrationService.run_counterfactual_simulation(db, req.dict())
    return sim_result

@router.post("/experiments/run/{profile_code}", summary="Execute Comparative Research Experiment")
def run_experiment(
    profile_code: str,
    req: ExperimentRunRequest = ExperimentRunRequest(),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Runs a structured benchmark evaluation under one of the 5 Profiles:
    - PROFILE_A: Insecure Baseline
    - PROFILE_B: RBAC Only
    - PROFILE_C: RBAC + Consent + Purpose
    - PROFILE_D: Full Zero-Trust Gateway + HITL
    - PROFILE_E: Full Security under Adaptive Testing
    """
    code = profile_code.upper()
    if code not in EXPERIMENT_PROFILES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile code '{profile_code}'. Valid codes: {list(EXPERIMENT_PROFILES.keys())}"
        )
    record = ExperimentManagementEngine.run_experiment(
        db=db,
        profile_code=code,
        test_case_ids=req.test_case_ids
    )
    return {
        "status": "COMPLETED",
        "experiment_id": record.experiment_id,
        "profile_name": record.profile_name,
        "profile_code": record.profile_code,
        "attack_success_rate": record.attack_success_rate,
        "unauthorized_access_count": record.unauthorized_access_count,
        "utility_score": record.composite_utility_score,
        "avg_latency_ms": record.avg_detection_latency_ms,
        "total_tests": record.total_tests_run,
        "breached_tests": int(record.total_tests_run * (record.attack_success_rate / 100)),
        "created_at": record.created_at.isoformat() if record.created_at else None
    }

@router.get("/experiments", summary="List All Executed Experiment Records")
def list_experiments(
    limit: int = 50,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Returns history of executed benchmark experiments with quantitative outcomes.
    """
    records = db.query(ExperimentRecord).order_by(ExperimentRecord.created_at.desc()).limit(limit).all()
    return [
        {
            "experiment_id": r.experiment_id,
            "profile_code": r.profile_code,
            "profile_name": r.profile_name,
            "total_tests": r.total_tests_run,
            "breached_tests": int(r.total_tests_run * (r.attack_success_rate / 100)),
            "attack_success_rate": r.attack_success_rate,
            "unauthorized_access_count": r.unauthorized_access_count,
            "utility_score": r.composite_utility_score,
            "avg_latency_ms": r.avg_detection_latency_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]

@router.get("/experiments/comparison", summary="Get 5-Profile Comparative Benchmark Matrix")
def get_experiment_comparison(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Generates side-by-side comparative matrix across Profiles A, B, C, D, and E
    evaluating ASR reduction, utility retention, and latency overhead.
    """
    comparison = ExperimentManagementEngine.get_comparative_matrix(db)
    return comparison

@router.get("/datasets/{dataset_type}", summary="Export Behavioral Research Telemetry (Datasets A, B, C)")
def export_dataset(
    dataset_type: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Exports structured research telemetry datasets:
    - 'agent': Dataset A (Agent Behavior Telemetry)
    - 'environment': Dataset B (Hospital Digital Twin State Telemetry)
    - 'interaction': Dataset C (Agent-Environment Policy Interaction Telemetry)
    """
    content, media_type = ResearchReportGenerator.export_dataset(db, dataset_type, export_format=format, limit=limit)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=behavioral_data_{dataset_type}.{format}"}
    )

@router.get("/reports/{experiment_id}", summary="Export Academic Research Experiment Report")
def export_report(
    experiment_id: str,
    format: str = Query("markdown", pattern="^(markdown|json|csv)$"),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Generates a publication-grade academic research benchmark report
    for the specified experiment in Markdown, JSON, or CSV.
    """
    content, media_type = ResearchReportGenerator.generate_experiment_report(db, experiment_id, report_format=format)
    ext = "md" if format == "markdown" else format
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=experiment_report_{experiment_id}.{ext}"}
    )
