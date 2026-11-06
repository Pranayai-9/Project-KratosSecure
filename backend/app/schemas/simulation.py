from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ScenarioInfo(BaseModel):
    scenario_code: str
    name: str
    description: str
    is_active: bool
    severity_level: str
    activated_at: Optional[datetime] = None
    parameters: Optional[Dict[str, Any]] = None
    class Config:
        from_attributes = True

class ScenarioTriggerRequest(BaseModel):
    scenario_code: str  # SCENARIO_A to SCENARIO_G
    parameters: Optional[Dict[str, Any]] = None

class ScenarioTriggerResponse(BaseModel):
    success: bool
    scenario_code: str
    message: str
    state_changes: Dict[str, Any]
    affected_departments: list[str]

class EnvironmentControlRequest(BaseModel):
    action: str  # influx, staff_shortage, change_capacity, toggle_subsystem, modify_workload
    target: Optional[str] = None
    value: Optional[Any] = None
