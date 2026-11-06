import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.generator.seed_data import init_db
from backend.app.api.v1.patients import router as patients_router
from backend.app.api.v1.operations import router as operations_router
from backend.app.api.v1.billing import router as billing_router
from backend.app.api.v1.staff import router as staff_router
from backend.app.api.v1.system import router as system_router
from backend.app.api.v1.simulation import router as simulation_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.fhir import router as fhir_router
from backend.app.api.v1.agent import router as agent_router
from backend.app.api.v1.research import router as research_router

# Initialize database on startup
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## KratosSecure: Healthcare Operational Environment Digital Twin
    
    A realistic, stateful, synthetic hospital environment acting as the operational
    foundation for healthcare AI agent security and resilience testing.
    
    ### Key Capabilities:
    * **15 Simulated Departments & 500-Bed Infrastructure**
    * **Stateful Synthetic Patient & Clinical Records (LOINC, ICD-10, RxNorm)**
    * **Strict Role-Based & Attribute-Based Access Control (RBAC/ABAC)**
    * **Cryptographic Tamper-Evident Hash Chained Audit Ledger**
    * **Active Canary Trap Secrets for Adversary Detection**
    * **7 Baseline Operational Scenarios (Normal, Emergency Surge, ICU Shortage, etc.)**
    * **HL7 FHIR R4 Compliant Interoperability Endpoints**
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(patients_router, prefix="/api/v1")
app.include_router(operations_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(staff_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(fhir_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")

# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "KratosSecure Healthcare Operational Environment API Active. Visit /docs for OpenAPI specifications."}

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "hospital": settings.HOSPITAL_NAME,
        "beds": settings.TOTAL_BEDS,
        "version": settings.APP_VERSION
    }
