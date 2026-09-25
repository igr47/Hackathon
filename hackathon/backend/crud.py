import random
import string
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas


# ---------- Code Generation ----------
def _random_token(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_job_code(db: Session) -> str:
    now = datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    count_today = (
        db.query(models.Job)
        .filter(func.date(models.Job.time_in) == now.date())
        .count()
    )
    seq = f"{count_today + 1:04d}"
    return f"JOB-{year}-{month}{day}-{seq}"


def generate_service_code(plate: str) -> str:
    clean = "".join(c for c in plate if c.isalnum()).upper()
    return f"VBCW-{clean}-{_random_token(4)}"


def generate_cw_code(plate: str) -> str:
    clean = "".join(c for c in plate if c.isalnum()).upper()
    rand = _random_token(4)
    ts = str(int(datetime.now().timestamp()))[-3:]
    return f"CW-{clean}-{rand}{ts}"


# ---------- Services ----------
def get_services(db: Session):
    return db.query(models.Service).filter(models.Service.is_active == True).all()


def create_service(db: Session, payload: schemas.ServiceCreate):
    svc = models.Service(**payload.dict())
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return svc


# ---------- Jobs ----------
def create_job(db: Session, payload: schemas.JobCreate, prefix: str = "VBCW") -> models.Job:
    plate = payload.plate_number.strip().upper()

    # Lookup or create customer
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.phone == payload.customer_phone)
        .first()
    )
    if not customer:
        customer = models.Customer(name=payload.customer_name, phone=payload.customer_phone)
        db.add(customer)
        db.commit()
        db.refresh(customer)

    # Lookup service
    service = (
        db.query(models.Service)
        .filter(models.Service.name == payload.service_name)
        .first()
    )

    job = models.Job(
        job_code=generate_job_code(db),
        service_code=generate_service_code(plate) if prefix == "VBCW" else generate_cw_code(plate),
        customer_id=customer.id,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        plate_number=plate,
        vehicle_model=payload.vehicle_model,
        service_id=service.id if service else None,
        service_name=payload.service_name,
        price=payload.price,
        operator=payload.operator,
        status=models.JobStatus.RECEIVED,
        payment_status=payload.payment_status,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    log = models.JobStatusLog(job_id=job.id, status=job.status)
    db.add(log)
    db.commit()
    return job


def get_jobs(db: Session, limit: int = 200):
    return (
        db.query(models.Job)
        .order_by(models.Job.time_in.desc())
        .limit(limit)
        .all()
    )


def get_job_by_code(db: Session, job_code: str):
    return db.query(models.Job).filter(models.Job.job_code == job_code).first()


def get_job_by_service_code(db: Session, service_code: str):
    return db.query(models.Job).filter(models.Job.service_code == service_code).first()


def search_jobs(db: Session, query: str):
    like = f"%{query}%"
    return (
        db.query(models.Job)
        .filter(
            (models.Job.plate_number.ilike(like))
            | (models.Job.customer_phone.ilike(like))
            | (models.Job.job_code.ilike(like))
            | (models.Job.customer_name.ilike(like))
        )
        .order_by(models.Job.time_in.desc())
        .all()
    )


def advance_job_status(db: Session, job_code: str):
    job = get_job_by_code(db, job_code)
    if not job:
        return None

    order = list(models.JobStatus)
    idx = order.index(job.status)
    if idx < len(order) - 1:
        job.status = order[idx + 1]
        if job.status == models.JobStatus.COLLECTED:
            job.time_out = datetime.utcnow()

        log = models.JobStatusLog(job_id=job.id, status=job.status)
        db.add(log)
        db.commit()
        db.refresh(job)
    return job


def set_job_status(db: Session, job_code: str, status: models.JobStatus):
    job = get_job_by_code(db, job_code)
    if not job:
        return None
    job.status = status
    if status == models.JobStatus.COLLECTED:
        job.time_out = datetime.utcnow()
    log = models.JobStatusLog(job_id=job.id, status=status)
    db.add(log)
    db.commit()
    db.refresh(job)
    return job


def set_job_payment(db: Session, job_code: str, payment_status: str):
    job = get_job_by_code(db, job_code)
    if not job:
        return None
    job.payment_status = payment_status
    if payment_status.lower().startswith("paid") and job.status != models.JobStatus.COLLECTED:
        job.status = models.JobStatus.PAID
    db.commit()
    db.refresh(job)
    return job


def set_job_rating(db: Session, job_code: str, rating: int):
    job = get_job_by_code(db, job_code)
    if not job:
        return None
    job.rating = rating
    db.commit()
    db.refresh(job)
    return job


# ---------- Dashboard ----------
def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    in_bay = (
        db.query(models.Job)
        .filter(models.Job.status.in_([
            models.JobStatus.RECEIVED,
            models.JobStatus.WASHING,
            models.JobStatus.QUALITY_CHECK,
        ]))
        .count()
    )
    ready = db.query(models.Job).filter(models.Job.status == models.JobStatus.READY).count()
    completed = (
        db.query(models.Job)
        .filter(models.Job.status.in_([models.JobStatus.PAID, models.JobStatus.COLLECTED]))
        .count()
    )
    revenue = (
        db.query(func.coalesce(func.sum(models.Job.price), 0))
        .filter(models.Job.status.in_([models.JobStatus.PAID, models.JobStatus.COLLECTED]))
        .scalar()
    )
    total = db.query(models.Job).count()

    return schemas.DashboardStats(
        in_bay=in_bay,
        ready=ready,
        completed=completed,
        total_revenue=Decimal(str(revenue or 0)),
        total_jobs=total,
    )
