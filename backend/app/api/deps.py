from typing import Optional
from fastapi import Header, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.database import get_db
from backend.app.models.security import UserIdentity

class ActorContext(BaseModel):
    actor_id: str
    display_name: str
    role: str
    department_code: str
    purpose_of_use: str = "treatment"
    client_ip: str = "127.0.0.1"
    user_agent: str = "KratosSecure-Client/1.0"

def get_current_actor(
    request: Request,
    db: Session = Depends(get_db),
    x_actor_id: Optional[str] = Header(None, alias="X-Actor-Id"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_purpose_of_use: Optional[str] = Header("treatment", alias="X-Purpose-Of-Use")
) -> ActorContext:
    """
    Extracts and authenticates the active actor.
    If headers are omitted in the UI, defaults to 'dr_elena_vance' (Doctor role)
    to facilitate smooth exploration, while enabling instant role switching.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "KratosSecure-Client/1.0")
    
    actor_key = x_actor_id or x_api_key or "dr_elena_vance"
    
    # Query database for user identity
    user = db.query(UserIdentity).filter(
        (UserIdentity.username == actor_key) | 
        (UserIdentity.api_key == actor_key)
    ).first()
    
    if not user:
        # Check if it matches known standard persona names
        standard_personas = {
            "dr_elena_vance": ("Doctor", "MED", "Dr. Elena Vance, MD"),
            "dr_marcus_brody": ("Doctor", "EMERGENCY", "Dr. Marcus Brody, MD"),
            "nurse_sarah_connor": ("Nurse", "ICU", "Nurse Sarah Connor, RN"),
            "nurse_david_kim": ("Nurse", "IPD", "Nurse David Kim, BSN"),
            "tech_rachel_zane": ("Lab Technician", "LAB", "Rachel Zane, MLS"),
            "pharm_james_wilson": ("Pharmacist", "PHARMACY", "Dr. James Wilson, PharmD"),
            "billing_arthur_dent": ("Billing Officer", "BILLING", "Arthur Dent"),
            "mro_diana_prince": ("Medical Records Officer", "HIM", "Diana Prince, RHIA"),
            "admin_sterling_archer": ("Hospital Administrator", "ADMIN", "Sterling Archer, MHA"),
            "it_elliot_alderson": ("IT Administrator", "IT_SEC", "Elliot Alderson"),
            "sec_john_connor": ("Security Officer", "IT_SEC", "John Connor, CISSP"),
            "agent_kratos_ai": ("Healthcare AI Agent", "COMMAND_CTR", "Kratos Operational AI"),
            "adversarial_infiltrator": ("Adversarial Agent", "EXTERNAL", "Unknown External Entity"),
        }
        
        if actor_key in standard_personas:
            role, dept, dname = standard_personas[actor_key]
            return ActorContext(
                actor_id=actor_key,
                display_name=dname,
                role=role,
                department_code=dept,
                purpose_of_use=x_purpose_of_use or "treatment",
                client_ip=client_ip,
                user_agent=user_agent
            )
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Actor identity '{actor_key}' not recognized."
        )

    return ActorContext(
        actor_id=user.username,
        display_name=user.display_name,
        role=user.role,
        department_code=user.department_code,
        purpose_of_use=x_purpose_of_use or "treatment",
        client_ip=client_ip,
        user_agent=user_agent
    )
