from sqlalchemy.orm import Session
from backend.app.database import engine, Base, SessionLocal
from backend.app.models.patient import Patient
from backend.app.models.security import AuditEvent
from backend.app.generator.synthesizer import generate_synthetic_data
from backend.app.security.audit import record_audit_event

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        patient_count = db.query(Patient).count()
        if patient_count == 0:
            print("[KratosSecure] Seeding realistic synthetic hospital digital twin...")
            generate_synthetic_data(db)
            
            # Record Genesis Audit Event
            record_audit_event(
                db=db,
                actor_id="SYSTEM_BOOTSTRAP",
                actor_role="Hospital Administrator",
                actor_department="ADMIN",
                action="INITIALIZE_HOSPITAL_ENVIRONMENT",
                resource_type="HospitalDigitalTwin",
                resource_id="Aethelgard-Memorial-500Beds",
                purpose_of_use="system_admin",
                decision="PERMIT",
                reason="Initial baseline synthesis and security foundation established successfully.",
                client_ip="127.0.0.1",
                details={"status": "INITIALIZED", "total_beds": 500, "departments": 15}
            )
            print("[KratosSecure] Hospital digital twin initialization complete.")
        else:
            print(f"[KratosSecure] Database already initialized with {patient_count} patients.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
