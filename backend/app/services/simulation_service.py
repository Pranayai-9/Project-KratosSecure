import json
import random
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.system import SubsystemStatus, SimulationScenarioState
from backend.app.models.infrastructure import Department, Bed, Ambulance, MedicalEquipment
from backend.app.models.staff import StaffMember, DutyRoster
from backend.app.models.patient import Patient, Encounter
from backend.app.security.audit import record_audit_event
from backend.app.api.deps import ActorContext

class SimulationService:
    @staticmethod
    def get_all_scenarios(db: Session) -> List[SimulationScenarioState]:
        return db.query(SimulationScenarioState).all()

    @staticmethod
    def activate_scenario(db: Session, actor: ActorContext, scenario_code: str) -> Dict[str, Any]:
        # Reset all other scenarios
        db.query(SimulationScenarioState).update({SimulationScenarioState.is_active: False})
        
        scenario = db.query(SimulationScenarioState).filter(SimulationScenarioState.scenario_code == scenario_code).first()
        if not scenario:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_code} not found")

        scenario.is_active = True
        scenario.activated_at = datetime.utcnow()

        state_changes = {}
        affected_depts = []

        if scenario_code == "SCENARIO_A":
            # Normal hospital operations
            scenario.severity_level = "nominal"
            # Set all subsystems operational
            db.query(SubsystemStatus).update({
                SubsystemStatus.status: "operational",
                SubsystemStatus.latency_ms: 15
            })
            # Normalize department workloads
            db.query(Department).update({
                Department.status: "operational",
                Department.current_workload: "normal",
                Department.wait_time_minutes: 15
            })
            # Free some beds to ~75% occupancy
            beds = db.query(Bed).all()
            for idx, b in enumerate(beds):
                b.is_occupied = (idx % 4 != 0) # 75% occupied
                b.status = "occupied" if b.is_occupied else "available"
            
            # Make 90% staff available
            staff = db.query(StaffMember).all()
            for idx, s in enumerate(staff):
                s.is_available = (idx % 10 != 0)

            state_changes = {
                "overall_status": "NORMAL_OPERATIONS",
                "bed_occupancy_target": "75%",
                "subsystems": "ALL_ONLINE",
                "ed_wait_time": "15 min"
            }
            affected_depts = ["ALL"]

        elif scenario_code == "SCENARIO_B":
            # Emergency patient influx
            scenario.severity_level = "high"
            ed = db.query(Department).filter(Department.code == "EMERGENCY").first()
            if ed:
                ed.current_workload = "critical"
                ed.wait_time_minutes = 95
                ed.status = "emergency_mode"
                affected_depts.append("EMERGENCY")

            # Dispatch ambulances
            db.query(Ambulance).update({Ambulance.status: "dispatched"})

            # Fill ED and Trauma beds to 100%
            if ed:
                db.query(Bed).filter(Bed.department_id == ed.id).update({
                    Bed.is_occupied: True,
                    Bed.status: "occupied"
                })

            state_changes = {
                "emergency_workload": "CRITICAL",
                "ed_wait_time": "95 min",
                "ed_bed_occupancy": "100%",
                "ambulances": "ALL_DISPATCHED"
            }

        elif scenario_code == "SCENARIO_C":
            # ICU capacity shortage
            scenario.severity_level = "critical"
            icu = db.query(Department).filter(Department.code == "ICU").first()
            if icu:
                icu.current_workload = "critical"
                icu.status = "degraded"
                affected_depts.append("ICU")
                # 100% ICU beds occupied
                db.query(Bed).filter(Bed.department_id == icu.id).update({
                    Bed.is_occupied: True,
                    Bed.status: "occupied"
                })

            # Exhaust all mechanical ventilators
            db.query(MedicalEquipment).filter(MedicalEquipment.equipment_type == "ventilator").update({
                MedicalEquipment.status: "in_use"
            })

            state_changes = {
                "icu_bed_occupancy": "100%",
                "available_icu_beds": 0,
                "available_ventilators": 0,
                "icu_alert": "CODE_CRITICAL_CAPACITY"
            }

        elif scenario_code == "SCENARIO_D":
            # Staff shortage
            scenario.severity_level = "elevated"
            staff = db.query(StaffMember).all()
            for idx, s in enumerate(staff):
                s.is_available = (idx % 2 == 0) # 50% absence!
            
            # Departments workload rises
            db.query(Department).update({
                Department.current_workload: "high",
                Department.wait_time_minutes: 60
            })
            affected_depts = ["NURSING", "EMERGENCY", "IPD", "ICU"]
            state_changes = {
                "workforce_available_pct": "50%",
                "nurse_to_patient_ratio": "CRITICAL_DEFICIT",
                "all_departments_wait_time": "60 min"
            }

        elif scenario_code == "SCENARIO_E":
            # Laboratory system unavailable
            scenario.severity_level = "high"
            lis = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == "LIS").first()
            if lis:
                lis.status = "offline"
                lis.latency_ms = 9999
                lis.details = "LIS Core Database connection pool exhausted; orders queuing in local cache."

            lab = db.query(Department).filter(Department.code == "LAB").first()
            if lab:
                lab.status = "degraded"
                lab.wait_time_minutes = 180
                affected_depts.append("LAB")

            state_changes = {
                "subsystem_lis_status": "OFFLINE",
                "lab_turnaround_time": "SUSPENDED",
                "pending_orders": "QUEUED_MANUAL_DISPATCH"
            }

        elif scenario_code == "SCENARIO_F":
            # Hospital network disruption
            scenario.severity_level = "critical"
            net = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == "NETWORK").first()
            if net:
                net.status = "degraded"
                net.latency_ms = 1250
                net.details = "Core switch packet loss at 42%. Failover routing engaged."

            pacs = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == "PACS").first()
            if pacs:
                pacs.status = "offline"

            ehr = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == "EHR").first()
            if ehr:
                ehr.status = "degraded"
                ehr.latency_ms = 850

            affected_depts = ["IT_SEC", "RADIOLOGY", "COMMAND_CTR"]
            state_changes = {
                "network_gateway": "PACKET_LOSS_DEGRADED",
                "pacs_radiology": "OFFLINE",
                "ehr_latency": "850ms",
                "mode": "DISASTER_RECOVERY_FAILOVER"
            }

        elif scenario_code == "SCENARIO_G":
            # High patient volume with simultaneous billing workload
            scenario.severity_level = "elevated"
            billing = db.query(Department).filter(Department.code == "BILLING").first()
            if billing:
                billing.current_workload = "critical"
                billing.wait_time_minutes = 75
                affected_depts.append("BILLING")

            opd = db.query(Department).filter(Department.code == "OPD").first()
            if opd:
                opd.current_workload = "high"
                opd.wait_time_minutes = 80
                affected_depts.append("OPD")

            billing_sub = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == "BILLING").first()
            if billing_sub:
                billing_sub.status = "degraded"
                billing_sub.latency_ms = 450

            state_changes = {
                "billing_throughput": "BOTTLENECK",
                "opd_volume": "HIGH",
                "discharge_delay": "45 min per clearance"
            }

        db.commit()

        # Audit scenario activation
        record_audit_event(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            action="ACTIVATE_SCENARIO",
            resource_type="HospitalScenarioState",
            resource_id=scenario_code,
            purpose_of_use="operations",
            decision="PERMIT",
            reason=f"Scenario '{scenario.name}' activated.",
            client_ip=actor.client_ip,
            details={"state_changes": state_changes, "affected_departments": affected_depts}
        )

        return {
            "success": True,
            "scenario_code": scenario_code,
            "message": f"Scenario '{scenario.name}' is now active.",
            "state_changes": state_changes,
            "affected_departments": affected_depts
        }

    @staticmethod
    def apply_environment_control(db: Session, actor: ActorContext, action: str, target: str = None, value: Any = None) -> Dict[str, Any]:
        """
        Allows interactive manipulation of hospital environment variables:
        - toggle_subsystem: operational, degraded, offline
        - admit_emergency: simulate immediate trauma arrival
        - discharge_random: simulate patient discharge
        - staff_toggle: change staff availability
        """
        result = {}
        if action == "toggle_subsystem":
            sub = db.query(SubsystemStatus).filter(SubsystemStatus.system_code == target).first()
            if sub:
                sub.status = str(value)
                sub.latency_ms = 500 if value == "degraded" else (9999 if value == "offline" else 15)
                db.commit()
                result = {"system": sub.system_code, "status": sub.status, "latency": sub.latency_ms}
        
        elif action == "admit_emergency":
            # Find an available emergency bed
            ed_dept = db.query(Department).filter(Department.code == "EMERGENCY").first()
            bed = db.query(Bed).filter(Bed.department_id == ed_dept.id, Bed.is_occupied == False).first() if ed_dept else None
            if bed:
                bed.is_occupied = True
                bed.status = "occupied"
                db.commit()
                result = {"admitted": True, "bed_assigned": bed.bed_number, "department": "EMERGENCY"}
            else:
                result = {"admitted": False, "message": "No emergency beds available! Diversion needed."}

        elif action == "discharge_random":
            # Free up an occupied bed
            bed = db.query(Bed).filter(Bed.is_occupied == True).first()
            if bed:
                bed.is_occupied = False
                bed.status = "available"
                bed.current_patient_id = None
                db.commit()
                result = {"discharged": True, "freed_bed": bed.bed_number}
            else:
                result = {"discharged": False, "message": "All beds already free."}

        record_audit_event(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            action="ENV_CONTROL",
            resource_type="EnvironmentControl",
            resource_id=action,
            purpose_of_use="operations",
            decision="PERMIT",
            reason=f"Interactive control '{action}' applied.",
            client_ip=actor.client_ip,
            details={"action": action, "target": target, "value": value, "result": result}
        )

        return {"success": True, "action": action, "result": result}
