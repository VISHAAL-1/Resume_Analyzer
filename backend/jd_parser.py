# backend/jd_parser.py
import json
from sqlalchemy.orm import Session
from backend import models

def create_job(db: Session, title: str, must_have: list, good_to_have: list, qualifications: str = None):
    job = models.Job(
        title=title,
        must_have=json.dumps(must_have or []),
        good_to_have=json.dumps(good_to_have or []),
        qualifications=qualifications or ""
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def list_jobs(db: Session):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()