import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from backend.app.database import Base

class SubsystemStatus(Base):
    __tablename__ = "subsystem_statuses"

    id = Column(Integer, primary_key=True, index=True)
    system_code = Column(String(32), unique=True, index=True, nullable=False)  # EHR, LIS, PACS, PDS, BILLING, NETWORK, TELEMETRY, BLOOD_BANK
    name = Column(String(128), nullable=False)
    status = Column(String(32), default="operational")  # operational, degraded, offline, maintenance
    latency_ms = Column(Integer, default=12)
    uptime_percentage = Column(Float, default=99.98)
    last_health_check = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    details = Column(Text, nullable=True)


class SimulationScenarioState(Base):
    __tablename__ = "simulation_scenario_states"

    id = Column(Integer, primary_key=True, index=True)
    scenario_code = Column(String(32), unique=True, index=True, nullable=False)  # SCENARIO_A to SCENARIO_G
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    activated_at = Column(DateTime, nullable=True)
    severity_level = Column(String(32), default="nominal")  # nominal, elevated, high, critical
    parameters = Column(Text, nullable=True)  # JSON string of active modifiers
