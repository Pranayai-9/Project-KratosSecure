import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from backend.app.database import Base

class ExperimentRecord(Base):
    __tablename__ = "experiment_records"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. EXP-2026-PROFILE-A-001
    profile_code = Column(String(32), index=True, nullable=False) # PROFILE_A, PROFILE_B, PROFILE_C, PROFILE_D, PROFILE_E
    profile_name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    
    hosa_version = Column(String(32), default="HOSA-v2.1-Operational")
    aava_version = Column(String(32), default="AAVA-v2.5-Adaptive")
    security_policy_version = Column(String(32), default="SecPolicy-2026.3")
    
    hospital_starting_state = Column(String(32), default="SCENARIO_A")
    random_seed = Column(Integer, default=42)
    total_tests_run = Column(Integer, default=0)
    
    # Core Comparative Metrics
    attack_success_rate = Column(Float, default=0.0)
    unauthorized_access_count = Column(Integer, default=0)
    sensitive_data_exposure_count = Column(Integer, default=0)
    privilege_escalation_count = Column(Integer, default=0)
    legitimate_task_completion_rate = Column(Float, default=100.0)
    false_refusal_rate = Column(Float, default=0.0)
    avg_detection_latency_ms = Column(Float, default=15.0)
    avg_recovery_time_ms = Column(Float, default=25.0)
    composite_utility_score = Column(Float, default=95.0)
    
    # Serialized Execution Trace IDs and Detailed Report
    trace_ids = Column(JSON, nullable=False) # list of trace_ids
    evaluation_summary = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class BehavioralDataAgent(Base):
    """
    Dataset A: Agent Behaviour Data.
    Tracks agent task selection, tool calling patterns, escalations, and decisions.
    """
    __tablename__ = "behavioral_data_agent"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(64), unique=True, index=True, nullable=False)
    experiment_id = Column(String(64), index=True, nullable=True)
    scenario_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    agent_task = Column(String(128), nullable=False)
    active_patient_id = Column(Integer, nullable=True)
    tool_name = Column(String(64), nullable=True)
    tool_arguments = Column(JSON, nullable=True)
    authorization_decision = Column(String(32), nullable=False) # ALLOW, DENY, REQUIRE_HUMAN_APPROVAL
    policy_applied = Column(String(64), nullable=True)
    escalation_triggered = Column(Boolean, default=False)
    task_completed = Column(Boolean, default=True)
    safe_refusal = Column(Boolean, default=False)
    recovery_behavior = Column(String(128), default="NORMAL_CONTINUATION")
    latency_ms = Column(Integer, default=18)


class BehavioralDataEnvironment(Base):
    """
    Dataset B: Hospital Environment Data.
    Tracks digital twin operational state changes, bed saturation, and subsystem availability.
    """
    __tablename__ = "behavioral_data_environment"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(64), unique=True, index=True, nullable=False)
    experiment_id = Column(String(64), index=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    active_scenario_code = Column(String(32), default="SCENARIO_A")
    total_beds = Column(Integer, default=500)
    occupied_beds = Column(Integer, default=380)
    occupancy_rate = Column(Float, default=76.0)
    icu_total = Column(Integer, default=50)
    icu_occupied = Column(Integer, default=38)
    available_ventilators = Column(Integer, default=18)
    emergency_active_patients = Column(Integer, default=32)
    emergency_wait_time_minutes = Column(Integer, default=25)
    ambulances_available = Column(Integer, default=5)
    staff_on_duty_count = Column(Integer, default=15)
    offline_subsystems_count = Column(Integer, default=0)
    operational_bottleneck_flag = Column(String(64), default="NONE")


class BehavioralDataInteraction(Base):
    """
    Dataset C: Agent-Environment Interaction Data.
    Captures how the autonomous agent behaves in response to operational stress,
    changing infrastructure conditions, and adversarial pressure.
    """
    __tablename__ = "behavioral_data_interaction"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(64), unique=True, index=True, nullable=False)
    experiment_id = Column(String(64), index=True, nullable=True)
    scenario_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    hospital_state = Column(String(64), nullable=False)
    threat_condition = Column(String(64), nullable=False)
    agent_operational_mode = Column(String(64), default="STANDARD_SUPPORT")
    security_boundary_held = Column(Boolean, default=True)
    canary_tripped = Column(Boolean, default=False)
    workflow_delay_induced_seconds = Column(Integer, default=0)
    workflow_disruption_level = Column(String(32), default="LOW") # LOW, MODERATE, SEVERE
    recovery_latency_ms = Column(Integer, default=25)
    state_drift_detected = Column(Boolean, default=False)
    interaction_notes = Column(Text, nullable=True)


class CounterfactualSimulationRecord(Base):
    """
    Counterfactual Infrastructure Simulation Record ("What-If" Analysis).
    """
    __tablename__ = "counterfactual_simulations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(64), unique=True, index=True, nullable=False)
    hypothesis = Column(String(256), nullable=False)
    baseline_scenario = Column(String(32), default="SCENARIO_A")
    modified_parameters = Column(JSON, nullable=False) # e.g. {"icu_capacity_delta_pct": +10, "ed_doctors_delta": +2}
    
    # Comparative Results
    baseline_ed_wait_minutes = Column(Integer, default=25)
    simulated_ed_wait_minutes = Column(Integer, default=25)
    baseline_icu_occupancy_pct = Column(Float, default=76.0)
    simulated_icu_occupancy_pct = Column(Float, default=76.0)
    workflow_delay_change_pct = Column(Float, default=0.0)
    agent_task_completion_rate = Column(Float, default=100.0)
    bottlenecks_mitigated = Column(JSON, nullable=True)
    system_resilience_delta_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
