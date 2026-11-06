from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class InsuranceOut(BaseModel):
    id: int
    patient_id: int
    provider_name: str
    policy_number: str
    group_number: Optional[str] = None
    coverage_type: str
    copay_amount: float
    deductible_remaining: float
    status: str
    valid_until: str
    class Config:
        from_attributes = True

class InvoiceItemBase(BaseModel):
    service_code: str
    description: str
    department: str
    quantity: int = 1
    unit_price: float

class InvoiceItemOut(InvoiceItemBase):
    id: int
    total_price: float
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    amount: float
    payment_method: str = "Insurance Direct"
    payment_reference: Optional[str] = None

class PaymentOut(PaymentBase):
    id: int
    receipt_number: str
    invoice_id: int
    patient_id: int
    status: str
    payment_date: datetime
    processed_by: str
    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    items: List[InvoiceItemBase]
    discount_amount: float = 0.0
    notes: Optional[str] = None

class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    patient_id: int
    encounter_id: Optional[int] = None
    total_amount: float
    insurance_covered_amount: float
    discount_amount: float
    patient_responsibility: float
    paid_amount: float
    outstanding_balance: float
    status: str
    billing_officer_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    items: List[InvoiceItemOut] = []
    payments: List[PaymentOut] = []
    class Config:
        from_attributes = True
