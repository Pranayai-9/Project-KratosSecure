from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.schemas.infrastructure import DepartmentOut, HospitalCapacitySummary
from backend.app.services.operations_service import OperationsService

router = APIRouter(prefix="/operations", tags=["Hospital Operations"])

@router.get("/beds")
def check_bed_availability(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Check total bed occupancy and availability breakdown across all departments."""
    return OperationsService.get_bed_availability(db, actor)

@router.get("/icu")
def check_icu_capacity(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Check critical care bed availability, ventilator utilization, and acuity alerts."""
    return OperationsService.get_icu_capacity(db, actor)

@router.get("/staff")
def check_staff_availability(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Check active workforce availability across departments and roles."""
    return OperationsService.get_staff_availability(db, actor)

@router.get("/departments", response_model=List[DepartmentOut])
def check_department_status(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve operational status, workload, and wait times for all 15 hospital departments."""
    return OperationsService.get_department_status(db, actor)

@router.get("/inventory")
def check_medical_inventory(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Check blood bank units and pharmacy medication stock levels."""
    return OperationsService.get_medical_inventory(db, actor)

@router.get("/emergency")
def check_emergency_workload(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Check emergency department triage acuity, wait times, and ambulance fleet availability."""
    return OperationsService.get_emergency_workload(db, actor)

@router.get("/summary", response_model=HospitalCapacitySummary)
def get_hospital_capacity_summary(
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Consolidated KPI overview for hospital command-centre telemetry."""
    beds_data = OperationsService.get_bed_availability(db, actor)
    icu_data = OperationsService.get_icu_capacity(db, actor)
    ed_data = OperationsService.get_emergency_workload(db, actor)
    depts = OperationsService.get_department_status(db, actor)

    operational_depts = sum(1 for d in depts if d.status == "operational")

    return HospitalCapacitySummary(
        total_beds=beds_data["total_beds"],
        occupied_beds=beds_data["occupied_beds"],
        available_beds=beds_data["available_beds"],
        occupancy_rate_percentage=beds_data["occupancy_rate_percentage"],
        total_icu_beds=icu_data["total_icu_beds"],
        occupied_icu_beds=icu_data["occupied_icu_beds"],
        available_icu_beds=icu_data["available_icu_beds"],
        icu_occupancy_rate_percentage=icu_data["occupancy_rate_percentage"],
        emergency_admissions_active=ed_data["active_patients_count"],
        emergency_wait_time_minutes=ed_data["wait_time_minutes"],
        available_ambulances=ed_data["ambulances_available"],
        total_ambulances=ed_data["ambulances_total"],
        operational_departments=operational_depts,
        total_departments=len(depts)
    )
