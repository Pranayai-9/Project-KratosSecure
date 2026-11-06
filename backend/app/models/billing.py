import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Insurance(Base):
    __tablename__ = "insurances"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    provider_name = Column(String(128), nullable=False)  # BlueCross, Aetna, Medicare, Cigna, UnitedHealth
    policy_number = Column(String(64), nullable=False)
    group_number = Column(String(64), nullable=True)
    coverage_type = Column(String(64), default="Comprehensive")  # Comprehensive, Inpatient Only, Emergency Only
    copay_amount = Column(Float, default=50.0)
    deductible_remaining = Column(Float, default=500.0)
    status = Column(String(32), default="active")  # active, expired, pending_verification
    valid_until = Column(String(16), nullable=False)

    patient = relationship("Patient")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(32), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True)
    total_amount = Column(Float, default=0.0)
    insurance_covered_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    patient_responsibility = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    outstanding_balance = Column(Float, default=0.0)
    status = Column(String(32), default="draft")  # draft, pending_insurance, approved, paid, partially_paid, disputed, written_off
    billing_officer_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    due_date = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="invoices")
    encounter = relationship("Encounter", back_populates="invoices")
    billing_officer = relationship("StaffMember", foreign_keys=[billing_officer_id])
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    service_code = Column(String(32), nullable=False)  # CPT code / internal billing code
    description = Column(String(256), nullable=False)
    department = Column(String(64), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(32), unique=True, index=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(32), default="Insurance Direct")  # Insurance Direct, Credit Card, Bank Transfer, Cash
    payment_reference = Column(String(64), nullable=True)
    status = Column(String(32), default="completed")  # completed, refunded, pending
    payment_date = Column(DateTime, default=datetime.datetime.utcnow)
    processed_by = Column(String(64), default="Automated Clearinghouse")

    invoice = relationship("Invoice", back_populates="payments")
    patient = relationship("Patient")
