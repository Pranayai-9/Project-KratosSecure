from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.api.deps import get_current_actor, ActorContext
from backend.app.schemas.billing import InvoiceCreate, InvoiceOut, PaymentBase, PaymentOut
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing & Revenue Cycle"])

@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Retrieve itemized patient invoice."""
    return BillingService.get_invoice(db, actor, invoice_id)

@router.post("/calculate")
def calculate_bill(
    patient_id: int = Query(...),
    items_total: float = Query(...),
    discount: float = Query(0.0),
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Calculate patient responsibility based on insurance copay, coverage, and discounts."""
    return BillingService.calculate_bill(db, actor, patient_id, items_total, discount)

@router.post("/invoices", response_model=InvoiceOut)
def create_invoice_draft(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Create a new invoice draft for clinical encounters."""
    return BillingService.create_invoice_draft(db, actor, data)

@router.post("/invoices/{invoice_id}/pay", response_model=PaymentOut)
def process_payment(
    invoice_id: int,
    payment_data: PaymentBase,
    db: Session = Depends(get_db),
    actor: ActorContext = Depends(get_current_actor)
):
    """Process patient or insurance payment and generate payment receipt."""
    return BillingService.process_payment(db, actor, invoice_id, payment_data)
