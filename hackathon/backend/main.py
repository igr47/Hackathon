from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

import models
import schemas
import crud
from database import engine, get_db, Base
from config import settings

# Create tables automatically (or run init_db.sql manually)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Car Wash & Auto Detailing System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "online",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------- SERVICES ----------------
@app.get("/api/services", response_model=List[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return crud.get_services(db)


@app.post("/api/services", response_model=schemas.ServiceOut)
def add_service(payload: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return crud.create_service(db, payload)


# ---------------- JOBS ----------------
@app.post("/api/jobs", response_model=schemas.JobOut)
def create_job(
    payload: schemas.JobCreate,
    prefix: str = Query("VBCW", pattern="^(VBCW|CW)$"),
    db: Session = Depends(get_db),
):
    return crud.create_job(db, payload, prefix=prefix)


@app.get("/api/jobs", response_model=List[schemas.JobOut])
def list_jobs(limit: int = 200, db: Session = Depends(get_db)):
    return crud.get_jobs(db, limit=limit)


@app.get("/api/jobs/search", response_model=List[schemas.JobOut])
def search_jobs(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return crud.search_jobs(db, q)


@app.get("/api/jobs/{job_code}", response_model=schemas.JobOut)
def get_job(job_code: str, db: Session = Depends(get_db)):
    job = crud.get_job_by_code(db, job_code)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs/verify/{service_code}", response_model=schemas.JobOut)
def verify_service_code(service_code: str, db: Session = Depends(get_db)):
    job = crud.get_job_by_service_code(db, service_code)
    if not job:
        raise HTTPException(status_code=404, detail="Invalid service code")
    return job


@app.post("/api/jobs/{job_code}/advance", response_model=schemas.JobOut)
def advance_status(job_code: str, db: Session = Depends(get_db)):
    job = crud.advance_job_status(db, job_code)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.put("/api/jobs/{job_code}/status", response_model=schemas.JobOut)
def update_status(
    job_code: str, payload: schemas.JobStatusUpdate, db: Session = Depends(get_db)
):
    job = crud.set_job_status(db, job_code, models.JobStatus(payload.status.value))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.put("/api/jobs/{job_code}/payment", response_model=schemas.JobOut)
def update_payment(
    job_code: str, payment_status: str = Query(...), db: Session = Depends(get_db)
):
    job = crud.set_job_payment(db, job_code, payment_status)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.put("/api/jobs/{job_code}/rating", response_model=schemas.JobOut)
def update_rating(
    job_code: str, payload: schemas.JobRatingUpdate, db: Session = Depends(get_db)
):
    job = crud.set_job_rating(db, job_code, payload.rating)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------- DASHBOARD ----------------
@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


# ---------------- STATIC FRONTEND ----------------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

    @app.get("/ui")
    def ui_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
