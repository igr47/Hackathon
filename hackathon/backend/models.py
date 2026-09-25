from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Enum, Text, Boolean
)
from sqlalchemy.sql import func
from database import Base
import enum


class JobStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    WASHING = "WASHING"
    QUALITY_CHECK = "QUALITY CHECK"
    READY = "READY"
    PAID = "PAID"
    COLLECTED = "COLLECTED"


class PaymentMethod(str, enum.Enum):
    CASH = "Paid (Cash)"
    CARD = "Paid (Card)"
    MOBILE = "Paid (Mobile Money)"
    PENDING = "Pending"


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_code = Column(String(50), nullable=False, unique=True, index=True)
    service_code = Column(String(50), nullable=False, unique=True, index=True)

    customer_id = Column(Integer, nullable=True)
    customer_name = Column(String(120), nullable=False)
    customer_phone = Column(String(30), nullable=False, index=True)

    plate_number = Column(String(30), nullable=False, index=True)
    vehicle_model = Column(String(120), nullable=True)

    service_id = Column(Integer, nullable=True)
    service_name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    operator = Column(String(80), nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.RECEIVED, nullable=False)
    payment_status = Column(String(50), default="Pending", nullable=False)

    rating = Column(Integer, default=0)
    notes = Column(Text, nullable=True)

    time_in = Column(DateTime, server_default=func.now())
    time_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    time_out = Column(DateTime, nullable=True)


class JobStatusLog(Base):
    __tablename__ = "job_status_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, nullable=False, index=True)
    status = Column(Enum(JobStatus), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
