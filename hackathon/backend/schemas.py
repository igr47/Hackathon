from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class JobStatusEnum(str, Enum):
    RECEIVED = "RECEIVED"
    WASHING = "WASHING"
    QUALITY_CHECK = "QUALITY CHECK"
    READY = "READY"
    PAID = "PAID"
    COLLECTED = "COLLECTED"


# ---------- Service ----------
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal

class ServiceCreate(ServiceBase):
    pass

class ServiceOut(ServiceBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# ---------- Job ----------
class JobCreate(BaseModel):
    customer_name: str
    customer_phone: str
    plate_number: str
    vehicle_model: Optional[str] = None
    service_name: str
    price: Decimal
    operator: Optional[str] = None
    payment_status: str = "Pending"


class JobStatusUpdate(BaseModel):
    status: JobStatusEnum


class JobRatingUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)


class JobOut(BaseModel):
    id: int
    job_code: str
    service_code: str
    customer_name: str
    customer_phone: str
    plate_number: str
    vehicle_model: Optional[str]
    service_name: str
    price: Decimal
    operator: Optional[str]
    status: JobStatusEnum
    payment_status: str
    rating: int
    time_in: datetime
    time_out: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    in_bay: int
    ready: int
    completed: int
    total_revenue: Decimal
    total_jobs: int
