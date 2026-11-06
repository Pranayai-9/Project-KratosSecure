from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.infrastructure import (
    Bed, Department, OperatingTheatre, DiagnosticEquipment,
    MedicalEquipment, Ambulance, BloodInventory, MedicineInventory
)
from backend.app.models.staff import StaffMember
from backend.app.models.patient import Encounter
from backend.app.security.rbac import check_permission
from backend.app.api.deps import ActorContext

class OperationsService:
    @staticmethod
    def get_bed_availability(db: Session, actor: ActorContext) -> Dict[str, Any]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Bed",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        total_beds = db.query(Bed).count()
        occupied_beds = db.query(Bed).filter(Bed.is_occupied == True).count()
        available_beds = total_beds - occupied_beds
        occupancy_rate = round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0.0

        # Breakdown by Department
        depts = db.query(Department).all()
        dept_breakdown = []
        for d in depts:
            d_total = db.query(Bed).filter(Bed.department_id == d.id).count()
            d_occupied = db.query(Bed).filter(Bed.department_id == d.id, Bed.is_occupied == True).count()
            dept_breakdown.append({
                "department_code": d.code,
                "department_name": d.name,
                "building": d.building,
                "total_beds": d_total,
                "occupied_beds": d_occupied,
                "available_beds": d_total - d_occupied,
                "occupancy_rate": round((d_occupied / d_total * 100), 1) if d_total > 0 else 0.0
            })

        return {
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "occupancy_rate_percentage": occupancy_rate,
            "departments": dept_breakdown
        }

    @staticmethod
    def get_icu_capacity(db: Session, actor: ActorContext) -> Dict[str, Any]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Bed",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        icu_beds = db.query(Bed).filter(Bed.bed_type == "icu").all()
        total_icu = len(icu_beds)
        occupied_icu = sum(1 for b in icu_beds if b.is_occupied)
        available_icu = total_icu - occupied_icu
        icu_rate = round((occupied_icu / total_icu * 100), 2) if total_icu > 0 else 0.0

        # Mechanical Ventilator Status
        ventilators_total = db.query(MedicalEquipment).filter(MedicalEquipment.equipment_type == "ventilator").count()
        ventilators_in_use = db.query(MedicalEquipment).filter(MedicalEquipment.equipment_type == "ventilator", MedicalEquipment.status == "in_use").count()

        return {
            "total_icu_beds": total_icu,
            "occupied_icu_beds": occupied_icu,
            "available_icu_beds": available_icu,
            "occupancy_rate_percentage": icu_rate,
            "ventilators_total": ventilators_total,
            "ventilators_in_use": ventilators_in_use,
            "ventilators_available": ventilators_total - ventilators_in_use,
            "status": "CRITICAL" if icu_rate >= 90.0 else ("ELEVATED" if icu_rate >= 75.0 else "NOMINAL")
        }

    @staticmethod
    def get_staff_availability(db: Session, actor: ActorContext) -> Dict[str, Any]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="StaffMember",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        staff = db.query(StaffMember).all()
        total = len(staff)
        available = sum(1 for s in staff if s.is_available)
        
        # Group by role
        roles = {}
        for s in staff:
            if s.role not in roles:
                roles[s.role] = {"total": 0, "available": 0}
            roles[s.role]["total"] += 1
            if s.is_available:
                roles[s.role]["available"] += 1

        return {
            "total_staff": total,
            "available_staff": available,
            "availability_percentage": round((available / total * 100), 1) if total > 0 else 0.0,
            "by_role": roles
        }

    @staticmethod
    def get_department_status(db: Session, actor: ActorContext) -> List[Department]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Department",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        return db.query(Department).all()

    @staticmethod
    def get_medical_inventory(db: Session, actor: ActorContext) -> Dict[str, Any]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="MedicineInventory",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        blood = db.query(BloodInventory).all()
        medicines = db.query(MedicineInventory).all()
        low_stock_medicines = [m for m in medicines if m.stock_quantity <= m.reorder_level]
        low_stock_blood = [b for b in blood if b.units_available <= b.critical_threshold]

        return {
            "blood_units": blood,
            "medicines": medicines,
            "low_stock_medicines_count": len(low_stock_medicines),
            "low_stock_blood_types_count": len(low_stock_blood),
            "alert": len(low_stock_medicines) > 0 or len(low_stock_blood) > 0
        }

    @staticmethod
    def get_emergency_workload(db: Session, actor: ActorContext) -> Dict[str, Any]:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Department",
            action="READ",
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        ed_dept = db.query(Department).filter(Department.code == "EMERGENCY").first()
        active_ed_encounters = db.query(Encounter).filter(
            Encounter.department_id == ed_dept.id,
            Encounter.status == "in-progress"
        ).all() if ed_dept else []

        ambulances = db.query(Ambulance).all()
        avail_ambulances = sum(1 for a in ambulances if a.status == "available")

        acuity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for enc in active_ed_encounters:
            ac = enc.triage_acuity or 3
            acuity_counts[ac] = acuity_counts.get(ac, 0) + 1

        return {
            "department_status": ed_dept.status if ed_dept else "operational",
            "current_workload": ed_dept.current_workload if ed_dept else "normal",
            "active_patients_count": len(active_ed_encounters),
            "wait_time_minutes": ed_dept.wait_time_minutes if ed_dept else 15,
            "triage_breakdown": {
                "Level_1_Resuscitation": acuity_counts[1],
                "Level_2_Emergent": acuity_counts[2],
                "Level_3_Urgent": acuity_counts[3],
                "Level_4_Semi_Urgent": acuity_counts[4],
                "Level_5_Non_Urgent": acuity_counts[5]
            },
            "ambulances_available": avail_ambulances,
            "ambulances_total": len(ambulances)
        }
