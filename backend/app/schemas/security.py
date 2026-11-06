from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel

class UserIdentityOut(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    staff_id: Optional[int] = None
    department_code: str
    api_key: str
    is_active: bool
    class Config:
        from_attributes = True

class AuditEventCreate(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    purpose_of_use: str = "treatment"
    patient_id: Optional[int] = None
    decision: str = "PERMIT"
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AuditEventOut(BaseModel):
    id: int
    event_id: str
    timestamp: datetime
    actor_id: str
    actor_role: str
    actor_department: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    purpose_of_use: str
    patient_id: Optional[int] = None
    decision: str
    reason: Optional[str] = None
    client_ip: str
    user_agent: str
    previous_hash: str
    entry_hash: str
    class Config:
        from_attributes = True

class CanarySecretOut(BaseModel):
    id: int
    secret_key: str
    secret_name: str
    description: str
    category: str
    synthetic_value: str
    is_tripped: bool
    tripped_count: int
    last_tripped_at: Optional[datetime] = None
    last_tripped_by: Optional[str] = None
    class Config:
        from_attributes = True

class SubsystemStatusOut(BaseModel):
    id: int
    system_code: str
    name: str
    status: str
    latency_ms: int
    uptime_percentage: float
    last_health_check: datetime
    details: Optional[str] = None
    class Config:
        from_attributes = True

class SubsystemUpdate(BaseModel):
    status: str  # operational, degraded, offline, maintenance
    details: Optional[str] = None
