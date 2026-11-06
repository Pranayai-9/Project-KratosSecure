from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.schemas.simulation import (
    ScenarioInfo, ScenarioTriggerRequest, ScenarioTriggerResponse,
    EnvironmentControlRequest
)
from backend.app.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulation", tags=["Simulation & Operational Scenarios"])

@router.get("/scenarios", response_model=List[ScenarioInfo])
def list_scenarios(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve all defined operational scenarios (Scenario A through Scenario G)."""
    return SimulationService.get_all_scenarios(db)

@router.post("/scenarios/activate", response_model=ScenarioTriggerResponse)
def activate_scenario(
    request: ScenarioTriggerRequest,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Trigger one of the 7 baseline operational scenarios:
    - SCENARIO_A: Normal hospital operations
    - SCENARIO_B: Emergency patient influx
    - SCENARIO_C: ICU capacity shortage
    - SCENARIO_D: Staff shortage
    - SCENARIO_E: Laboratory system unavailable
    - SCENARIO_F: Hospital network disruption
    - SCENARIO_G: High patient volume with simultaneous billing workload
    """
    return SimulationService.activate_scenario(db, actor, request.scenario_code)

@router.post("/controls")
def apply_environment_control(
    request: EnvironmentControlRequest,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """
    Interactive environment controls:
    - action='toggle_subsystem', target='LIS', value='offline'
    - action='admit_emergency'
    - action='discharge_random'
    """
    return SimulationService.apply_environment_control(
        db, actor, request.action, request.target, request.value
    )
