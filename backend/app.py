from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .db import SessionLocal, init_db, Job
from .models import JobOut, JobIn
from .util import score_job
from .scrapers import lever as lever_scraper
from .scrapers import greenhouse as greenhouse_scraper

init_db()
app = FastAPI(title="bioinfojobs API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.get("/api/jobs", response_model=List[JobOut])
def list_jobs(
    q: Optional[str] = Query(None, description="search query"),
    source: Optional[str] = Query(None, description="lever|greenhouse|..."),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if q:
        like = f"%{q}%"
        query = query.filter((Job.title.ilike(like)) | (Job.description.ilike(like)) | (Job.company.ilike(like)))
    if source:
        query = query.filter(Job.source == source)
    rows = query.order_by(Job.score.desc(), Job.posted_at.desc()).limit(limit).all()
    return [JobOut(
        id=r.id, title=r.title, company=r.company, location=r.location, url=r.url,
        source=r.source, posted_at=r.posted_at, description=r.description, score=r.score
    ) for r in rows]

@app.post("/api/jobs", response_model=JobOut)
def upsert_job(job: JobIn, db: Session = Depends(get_db)):
    existing = db.query(Job).filter(Job.url == job.url).first()
    if existing:
        for field, value in job.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        if not existing.score:
            existing.score = 0.0
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return JobOut(**existing.__dict__)
    row = Job(
        title=job.title, company=job.company, location=job.location, url=job.url,
        source=job.source, posted_at=job.posted_at or datetime.utcnow(),
        description=job.description, score=job.score or 0.0
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return JobOut(**row.__dict__)

@app.post("/api/ingest/{source}/{company}")
async def ingest_source_company(source: str, company: str, db: Session = Depends(get_db)):
    """Pull jobs for one company from a supported source."""
    if source == "lever":
        jobs = await lever_scraper.fetch_company_jobs(company)
    elif source == "greenhouse":
        jobs = await greenhouse_scraper.fetch_company_jobs(company)
    else:
        return {"status": "unsupported source", "source": source}

    saved = 0
    for j in jobs:
        j["score"] = score_job(j)
        existing = db.query(Job).filter(Job.url == j["url"]).first()
        if existing:
            # update if needed
            existing.title = j["title"]
            existing.company = j["company"]
            existing.location = j.get("location", "")
            existing.description = j.get("description", "")
            existing.posted_at = j.get("posted_at") or existing.posted_at
            existing.score = j.get("score", existing.score)
            db.add(existing)
        else:
            row = Job(
                title=j["title"], company=j["company"], location=j.get("location",""),
                url=j["url"], source=j["source"], posted_at=j.get("posted_at"),
                description=j.get("description",""), score=j.get("score", 0.0)
            )
            db.add(row); saved += 1
    db.commit()
    return {"status": "ok", "fetched": len(jobs), "inserted": saved}
