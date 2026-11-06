import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from backend.app.database import Base

class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(64), unique=True, index=True, nullable=False)
    scenario_id = Column(String(64), index=True, nullable=False)
    scenario_name = Column(String(128), nullable=False)
    category = Column(String(64), index=True, nullable=False)
    status = Column(String(32), default="COMPLETED") # PASSED, FAILED, BLOCKED, ERROR
    attack_objective = Column(String(256), nullable=False)
    requesting_actor = Column(String(64), nullable=False)
    target_patient_id = Column(Integer, nullable=True)
    hosa_response = Column(Text, nullable=True)
    
    # Core Security Outcomes
    attack_succeeded = Column(Boolean, default=False)
    policy_violation_detected = Column(Boolean, default=False)
    canary_tripped = Column(Boolean, default=False)
    legitimate_task_completed = Column(Boolean, default=True)
    human_approval_required = Column(Boolean, default=False)
    human_approval_granted = Column(Boolean, default=False)
    
    # Chronological execution timeline (structured step records)
    execution_steps = Column(JSON, nullable=False)
    
    # Detailed Security & Performance Metrics
    metrics = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
