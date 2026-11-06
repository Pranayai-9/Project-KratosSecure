import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.billing import Invoice, InvoiceItem, Payment, Insurance
from backend.app.models.patient import Patient, Encounter
from backend.app.schemas.billing import InvoiceCreate, PaymentBase
from backend.app.security.rbac import check_permission
from backend.app.api.deps import ActorContext

class BillingService:
    @staticmethod
    def get_invoice(db: Session, actor: ActorContext, invoice_id: int) -> Invoice:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            raise HTTPException(status_code=404, detail=f"Invoice #{invoice_id} not found.")

        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Invoice",
            action="READ",
            resource_id=str(invoice_id),
            patient_id=inv.patient_id,
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        return inv

    @staticmethod
    def calculate_bill(db: Session, actor: ActorContext, patient_id: int, items_total: float, discount: float = 0.0) -> dict:
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Invoice",
            action="CALCULATE",
            patient_id=patient_id,
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )
        insurance = db.query(Insurance).filter(Insurance.patient_id == patient_id, Insurance.status == "active").first()
        
        covered = 0.0
        copay = 0.0
        if insurance:
            copay = insurance.copay_amount
            # 80% coverage after copay
            net = max(0.0, items_total - copay - discount)
            covered = round(net * 0.8, 2)
            patient_resp = round(items_total - covered - discount, 2)
        else:
            patient_resp = round(max(0.0, items_total - discount), 2)

        return {
            "gross_total": items_total,
            "insurance_provider": insurance.provider_name if insurance else "Self-Pay (Uninsured)",
            "insurance_covered": covered,
            "copay_amount": copay,
            "discount_amount": discount,
            "patient_responsibility": patient_resp
        }

    @staticmethod
    def create_invoice_draft(db: Session, actor: ActorContext, data: InvoiceCreate) -> Invoice:
        # Check permissions: AI agents can create drafts, but human approvals needed for write-offs
        action = "DRAFT_INVOICE" if actor.role == "Healthcare AI Agent" else "CREATE"
        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Invoice",
            action=action,
            patient_id=data.patient_id,
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )

        patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        total = sum(it.quantity * it.unit_price for it in data.items)
        calc = BillingService.calculate_bill(db, actor, data.patient_id, total, data.discount_amount)

        inv_num = f"INV-2026-{uuid.uuid4().hex[:6].upper()}"
        invoice = Invoice(
            invoice_number=inv_num,
            patient_id=data.patient_id,
            encounter_id=data.encounter_id,
            total_amount=total,
            insurance_covered_amount=calc["insurance_covered"],
            discount_amount=data.discount_amount,
            patient_responsibility=calc["patient_responsibility"],
            paid_amount=0.0,
            outstanding_balance=calc["patient_responsibility"],
            status="draft",
            notes=data.notes
        )
        db.add(invoice)
        db.flush()

        for it in data.items:
            db_item = InvoiceItem(
                invoice_id=invoice.id,
                service_code=it.service_code,
                description=it.description,
                department=it.department,
                quantity=it.quantity,
                unit_price=it.unit_price,
                total_price=it.quantity * it.unit_price
            )
            db.add(db_item)

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def process_payment(db: Session, actor: ActorContext, invoice_id: int, payment_data: PaymentBase) -> Payment:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            raise HTTPException(status_code=404, detail=f"Invoice #{invoice_id} not found")

        check_permission(
            db=db,
            actor_id=actor.actor_id,
            actor_role=actor.role,
            actor_department=actor.department_code,
            resource_type="Payment",
            action="CREATE",
            resource_id=str(invoice_id),
            patient_id=inv.patient_id,
            purpose_of_use=actor.purpose_of_use,
            client_ip=actor.client_ip
        )

        receipt_num = f"REC-2026-{uuid.uuid4().hex[:6].upper()}"
        payment = Payment(
            receipt_number=receipt_num,
            invoice_id=inv.id,
            patient_id=inv.patient_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            payment_reference=payment_data.payment_reference,
            status="completed",
            processed_by=actor.display_name
        )
        db.add(payment)

        # Update invoice balance
        inv.paid_amount += payment_data.amount
        inv.outstanding_balance = max(0.0, inv.patient_responsibility - inv.paid_amount)
        if inv.outstanding_balance == 0.0:
            inv.status = "paid"
        else:
            inv.status = "partially_paid"

        db.commit()
        db.refresh(payment)
        return payment
