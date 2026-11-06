import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "KratosSecure - Healthcare Operational Environment"
    APP_VERSION: str = "1.0.0"
    HOSPITAL_NAME: str = "Aethelgard Memorial Hospital"
    TOTAL_BEDS: int = 500
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:////tmp/kratos_hospital.db" if os.getenv("VERCEL") else "sqlite:///./kratos_hospital.db"
    )
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
    CORS_ORIGINS: list[str] = ["*"]
    
    # Audit Security
    AUDIT_SALT: str = os.getenv("AUDIT_SALT", "kratos_secure_merkle_salt_2026")

settings = Settings()
