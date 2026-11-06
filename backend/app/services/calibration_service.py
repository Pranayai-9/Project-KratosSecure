import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.infrastructure import (
    Department, Bed, DiagnosticEquipment, BloodInventory, MedicineInventory, Ambulance
)
from backend.app.models.staff import StaffMember
from backend.app.models.system import SubsystemStatus
from backend.app.models.research import (
    CounterfactualSimulationRecord,
    BehavioralDataEnvironment,
    BehavioralDataInteraction
)

class CalibrationService:
    """
    Digital Twin Operational Calibration and Counterfactual Simulation Service.
    Analyzes systemic bottlenecks, evaluates operational risk states,
    and runs predictive 'what-if' counterfactual simulations.
    """

    @staticmethod
    def analyze_bottlenecks(db: Session) -> Dict[str, Any]:
        """
        Inspects real-time hospital digital twin state to detect systemic bottlenecks:
        - ICU bed saturation
        - LIS / PACS subsystem degradation
        - Emergency Department workload & queue
        - Critical medicine and blood bank inventory alerts
        """
        timestamp = datetime.utcnow().isoformat()
        bottlenecks = []
        mitigations = []

        # 1. ICU and Inpatient Bed Saturation
        icu_dept = db.query(Department).filter(Department.name.ilike("%Intensive Care%")).first()
        icu_dept_id = icu_dept.id if icu_dept else None

        total_icu_beds = db.query(Bed).filter(Bed.department_id == icu_dept_id).count() if icu_dept_id else 0
        occupied_icu_beds = db.query(Bed).filter(Bed.department_id == icu_dept_id, Bed.is_occupied == True).count() if icu_dept_id else 0
        icu_saturation_pct = round((occupied_icu_beds / total_icu_beds * 100), 1) if total_icu_beds > 0 else 0.0

        if icu_saturation_pct >= 90.0:
            bottlenecks.append({
                "component": "ICU_CAPACITY",
                "severity": "CRITICAL" if icu_saturation_pct >= 98.0 else "HIGH",
                "metric": f"{occupied_icu_beds}/{total_icu_beds} beds ({icu_saturation_pct}%)",
                "detail": "ICU capacity is at or near saturation threshold, creating severe downstream admission bottlenecks."
            })
            mitigations.append("Activate step-down transfer protocols and surge capacity beds in PACU.")
        elif icu_saturation_pct >= 75.0:
            bottlenecks.append({
                "component": "ICU_CAPACITY",
                "severity": "MODERATE",
                "metric": f"{occupied_icu_beds}/{total_icu_beds} beds ({icu_saturation_pct}%)",
                "detail": "ICU bed occupancy is approaching elevated warning threshold."
            })

        # 2. Subsystem Availability (LIS, PACS, Pharmacy, EHR)
        degraded_subsystems = db.query(SubsystemStatus).filter(SubsystemStatus.status != "operational").all()
        for sub in degraded_subsystems:
            bottlenecks.append({
                "component": f"SUBSYSTEM_{sub.name.upper()}",
                "severity": "CRITICAL" if sub.status == "offline" else "HIGH",
                "metric": f"Status: {sub.status}, Latency: {sub.latency_ms}ms",
                "detail": f"{sub.name} is currently {sub.status}; introduces delays in clinical decision loop."
            })
            mitigations.append(f"Failover {sub.name} to secondary redundant mirror or engage manual paper-run contingency.")

        # 3. Emergency Department Workload
        ed_dept = db.query(Department).filter(Department.name.ilike("%Emergency%")).first()
        ed_status = (ed_dept.current_workload or "normal").upper() if ed_dept else "NOMINAL"
        if ed_status in ["HIGH", "CRITICAL", "SATURATED"]:
            bottlenecks.append({
                "component": "EMERGENCY_DEPARTMENT",
                "severity": "CRITICAL" if ed_status == "SATURATED" else "HIGH",
                "metric": f"Workload: {ed_status}",
                "detail": "ED arrival volume exceeds triage velocity; acute diversion risk."
            })
            mitigations.append("Deploy fast-track minor illness stream and call on-call emergency physicians.")

        # 4. Critical Inventory (Blood & Pharmacy)
        low_blood = db.query(BloodInventory).filter(BloodInventory.units_available < 5).all()
        for b in low_blood:
            bottlenecks.append({
                "component": f"BLOOD_BANK_{b.blood_group}",
                "severity": "HIGH",
                "metric": f"{b.units_available} units available",
                "detail": f"Critical reserve of {b.blood_group} blood is critically low."
            })
            mitigations.append(f"Issue urgent regional blood bank replenishment order for {b.blood_group}.")

        low_meds = db.query(MedicineInventory).filter(MedicineInventory.stock_quantity < 20).all()
        for m in low_meds:
            bottlenecks.append({
                "component": f"MEDICINE_{m.medication_name}",
                "severity": "HIGH",
                "metric": f"{m.stock_quantity} {m.unit} in stock",
                "detail": f"Stock level for essential drug {m.medication_name} is below buffer limit."
            })
            mitigations.append(f"Expedite pharmacy restocking order for {m.medication_name}.")

        # Calculate systemic operational stress score (0-100)
        stress_score = min(100.0, (
            (icu_saturation_pct * 0.4) +
            (len(degraded_subsystems) * 15.0) +
            (25.0 if ed_status in ["HIGH", "CRITICAL", "SATURATED"] else 5.0) +
            (len(low_blood) * 5.0) +
            (len(low_meds) * 3.0)
        ))

        # Persist environmental telemetry event (Dataset B)
        env_telemetry = BehavioralDataEnvironment(
            record_id=f"ENV-{uuid.uuid4().hex[:8].upper()}",
            experiment_id="SYSTEM_MONITOR",
            active_scenario_code="SCENARIO_A",
            total_beds=500,
            occupied_beds=int(500 * (icu_saturation_pct / 100)),
            occupancy_rate=icu_saturation_pct,
            icu_total=total_icu_beds,
            icu_occupied=occupied_icu_beds,
            available_ventilators=18,
            emergency_active_patients=35 if ed_status == "HIGH" else 20,
            emergency_wait_time_minutes=45 if ed_status == "HIGH" else 20,
            ambulances_available=db.query(Ambulance).filter(Ambulance.status == "available").count(),
            staff_on_duty_count=db.query(StaffMember).filter(StaffMember.is_available == True).count(),
            offline_subsystems_count=len(degraded_subsystems),
            operational_bottleneck_flag="CRITICAL_BOTTLENECK" if stress_score >= 80 else ("ELEVATED_STRESS" if stress_score >= 50 else "NONE"),
            timestamp=datetime.utcnow()
        )
        db.add(env_telemetry)
        db.commit()

        return {
            "timestamp": timestamp,
            "overall_stress_score": round(stress_score, 1),
            "stress_level": "CRITICAL" if stress_score >= 80 else ("ELEVATED" if stress_score >= 50 else "NOMINAL"),
            "icu_saturation_percentage": icu_saturation_pct,
            "emergency_workload": ed_status,
            "bottlenecks_detected_count": len(bottlenecks),
            "bottlenecks": bottlenecks,
            "recommended_mitigations": mitigations
        }

    @staticmethod
    def run_counterfactual_simulation(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a counterfactual 'what-if' simulation on the digital twin.
        Evaluates system dynamics under hypothetical parameter shifts:
        - icu_capacity_delta: int (e.g. +10, -5 beds)
        - ed_doctor_delta: int (e.g. +2, -2 doctors)
        - lis_availability_pct: float (e.g. 100% vs 50%)
        - patient_arrival_multiplier: float (e.g. 1.0 vs 1.6x surge)
        - simulation_duration_hours: int (default 24)
        """
        sim_id = f"CF-SIM-{uuid.uuid4().hex[:8].upper()}"

        icu_dept = db.query(Department).filter(Department.name.ilike("%Intensive Care%")).first()
        icu_dept_id = icu_dept.id if icu_dept else None
        base_icu_total = db.query(Bed).filter(Bed.department_id == icu_dept_id).count() if icu_dept_id else 40
        base_icu_occupied = db.query(Bed).filter(Bed.department_id == icu_dept_id, Bed.is_occupied == True).count() if icu_dept_id else 32
        base_icu_pct = round((base_icu_occupied / base_icu_total * 100), 1) if base_icu_total > 0 else 80.0

        base_ed_wait = 25  # baseline minutes
        base_diversion_risk = 0.15

        # Extract shift parameters
        icu_delta = int(params.get("icu_capacity_delta", 0))
        ed_doctor_delta = int(params.get("ed_doctor_delta", 0))
        lis_avail = float(params.get("lis_availability_pct", 100.0))
        arrival_multiplier = float(params.get("patient_arrival_multiplier", 1.0))
        duration_hours = int(params.get("simulation_duration_hours", 24))

        # Counterfactual projections
        counterfactual_icu_total = max(5, base_icu_total + icu_delta)
        projected_icu_demand = base_icu_occupied * arrival_multiplier
        projected_icu_pct = min(100.0, round((projected_icu_demand / counterfactual_icu_total * 100), 1))

        staffing_factor = max(0.4, 1.0 - (ed_doctor_delta * 0.15))
        projected_ed_wait = int(round(base_ed_wait * arrival_multiplier * staffing_factor))

        risk_score = 0.0
        if projected_icu_pct >= 95.0:
            risk_score += 0.5
        elif projected_icu_pct >= 85.0:
            risk_score += 0.25

        if projected_ed_wait > 60:
            risk_score += 0.35
        elif projected_ed_wait > 40:
            risk_score += 0.2

        if lis_avail < 60.0:
            risk_score += 0.15

        projected_diversion_risk = min(1.0, round(risk_score, 2))
        resilience_delta = round(15.0 - (projected_diversion_risk * 30.0) + (icu_delta * 0.5) + (ed_doctor_delta * 1.5), 1)

        summary = (
            f"Counterfactual simulation ({duration_hours}h window): "
            f"Under {arrival_multiplier}x arrival volume, ICU delta of {icu_delta:+d} beds, and ED staffing {ed_doctor_delta:+d}, "
            f"ICU saturation projects to {projected_icu_pct}%, ED wait time to {projected_ed_wait} min, "
            f"and ambulance diversion probability is {int(projected_diversion_risk*100)}%."
        )

        mitigated_bottlenecks = []
        if icu_delta > 0 and projected_icu_pct < 85.0:
            mitigated_bottlenecks.append("ICU_CAPACITY_OVERFLOW")
        if ed_doctor_delta > 0 and projected_ed_wait <= 30:
            mitigated_bottlenecks.append("ED_TRIAGE_DELAY")
        if lis_avail >= 95.0:
            mitigated_bottlenecks.append("LIS_DIAGNOSTIC_DELAY")

        # Persist simulation result in CounterfactualSimulationRecord
        cf_record = CounterfactualSimulationRecord(
            simulation_id=sim_id,
            hypothesis=f"What-if: ICU {icu_delta:+d} beds, ED staff {ed_doctor_delta:+d}, arrival x{arrival_multiplier}",
            baseline_scenario="SCENARIO_A",
            modified_parameters=params,
            baseline_ed_wait_minutes=base_ed_wait,
            simulated_ed_wait_minutes=projected_ed_wait,
            baseline_icu_occupancy_pct=base_icu_pct,
            simulated_icu_occupancy_pct=projected_icu_pct,
            workflow_delay_change_pct=round(((projected_ed_wait - base_ed_wait) / max(1, base_ed_wait)) * 100, 1),
            agent_task_completion_rate=98.5 if projected_diversion_risk < 0.4 else 91.0,
            bottlenecks_mitigated=mitigated_bottlenecks,
            system_resilience_delta_score=resilience_delta,
            created_at=datetime.utcnow()
        )
        db.add(cf_record)

        # Record interaction telemetry (Dataset C)
        interaction_log = BehavioralDataInteraction(
            record_id=f"INT-{uuid.uuid4().hex[:8].upper()}",
            experiment_id=sim_id,
            scenario_id="COUNTERFACTUAL_SIMULATION",
            hospital_state="COUNTERFACTUAL_TESTING",
            threat_condition="INFRASTRUCTURE_STRESS_TEST",
            agent_operational_mode="ANALYTICAL_SUPPORT",
            security_boundary_held=True,
            canary_tripped=False,
            workflow_delay_induced_seconds=max(0, (projected_ed_wait - base_ed_wait) * 60),
            workflow_disruption_level="SEVERE" if projected_diversion_risk > 0.6 else ("MODERATE" if projected_diversion_risk > 0.3 else "LOW"),
            recovery_latency_ms=18,
            state_drift_detected=False,
            interaction_notes=summary,
            timestamp=datetime.utcnow()
        )
        db.add(interaction_log)
        db.commit()

        return {
            "simulation_id": sim_id,
            "parameters": params,
            "baseline": {
                "icu_occupancy_pct": base_icu_pct,
                "ed_wait_minutes": base_ed_wait,
                "diversion_risk": base_diversion_risk
            },
            "counterfactual_projections": {
                "projected_icu_occupancy_pct": projected_icu_pct,
                "projected_ed_wait_minutes": projected_ed_wait,
                "projected_diversion_risk": projected_diversion_risk,
                "resilience_delta_score": resilience_delta,
                "bottlenecks_mitigated": mitigated_bottlenecks
            },
            "summary": summary
        }
