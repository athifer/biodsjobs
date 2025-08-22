from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from db import SessionLocal, init_db, Job
from models import JobOut, JobIn
from util import score_job
from scrapers import lever as lever_scraper
from scrapers import greenhouse as greenhouse_scraper
from scheduler import start_scheduler, stop_scheduler

# Global scheduler variable
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    global scheduler
    # Startup
    init_db()
    scheduler = start_scheduler()
    yield
    # Shutdown
    stop_scheduler(scheduler)

app = FastAPI(title="biodsjobs API", version="0.1.0", lifespan=lifespan)

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

@app.get("/api/locations")
def get_locations(db: Session = Depends(get_db)):
    """Get all unique locations from jobs for location filter dropdown."""
    locations = db.query(Job.location).distinct().filter(Job.location != "").all()
    location_list = [loc[0] for loc in locations if loc[0]]
    
    # Add common location groupings
    common_locations = [
        "Remote",
        "San Francisco Bay Area", 
        "Boston/Cambridge",
        "New York City",
        "Seattle",
        "Los Angeles",
        "San Diego",
        "Chicago",
        "Washington DC"
    ]
    
    # Combine and sort
    all_locations = common_locations + [loc for loc in location_list if loc not in common_locations]
    return sorted(set(all_locations))

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get summary statistics about jobs in the database."""
    from sqlalchemy import func
    
    total_jobs = db.query(Job).count()
    total_companies = db.query(Job.company).distinct().count()
    total_sources = db.query(Job.source).distinct().count()
    
    # Get jobs by source
    sources = db.query(Job.source, func.count(Job.id).label('count')).group_by(Job.source).all()
    source_stats = {source: count for source, count in sources}
    
    # Get most recent job date
    latest_job = db.query(Job.posted_at).order_by(Job.posted_at.desc()).first()
    latest_date = latest_job[0] if latest_job else None
    
    return {
        "total_jobs": total_jobs,
        "total_companies": total_companies,
        "total_sources": total_sources,
        "sources": source_stats,
        "latest_job_date": latest_date
    }

@app.get("/api/jobs", response_model=List[JobOut])
def list_jobs(
    q: Optional[str] = Query(None, description="search query"),
    source: Optional[List[str]] = Query(None, description="lever|greenhouse|... (can be multiple)"),
    location: Optional[List[str]] = Query(None, description="filter by location (e.g., 'san francisco', 'remote', 'boston') (can be multiple)"),
    days: Optional[int] = Query(None, description="filter jobs posted in last N days"),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if q:
        like = f"%{q}%"
        query = query.filter((Job.title.ilike(like)) | (Job.description.ilike(like)) | (Job.company.ilike(like)))
    
    if source:
        # Handle multiple sources with OR condition
        source_conditions = [Job.source == s for s in source]
        query = query.filter(or_(*source_conditions))
    
    if location:
        # Handle multiple locations with OR condition
        all_location_conditions = []
        
        for loc in location:
            location_lower = loc.lower()
            location_patterns = []
            
            # Bay Area variations
            if any(term in location_lower for term in ['bay area', 'san francisco', 'sf', 'silicon valley', 'palo alto', 'mountain view', 'cupertino', 'sunnyvale']):
                location_patterns.extend([
                    '%san francisco%', '%sf%', '%bay area%', '%silicon valley%',
                    '%palo alto%', '%mountain view%', '%cupertino%', '%sunnyvale%',
                    '%redwood city%', '%menlo park%', '%fremont%', '%oakland%',
                    '%berkeley%', '%san jose%', '%santa clara%'
                ])
            
            # Remote variations
            elif 'remote' in location_lower:
                location_patterns.extend(['%remote%', '%anywhere%', '%work from home%', '%wfh%'])
            
            # Boston area variations  
            elif any(term in location_lower for term in ['boston', 'cambridge', 'massachusetts']):
                location_patterns.extend(['%boston%', '%cambridge%', '%massachusetts%', '%ma%'])
            
            # NYC area variations
            elif any(term in location_lower for term in ['new york', 'nyc', 'manhattan', 'brooklyn']):
                location_patterns.extend(['%new york%', '%nyc%', '%manhattan%', '%brooklyn%', '%ny%'])
            
            # Seattle area variations
            elif any(term in location_lower for term in ['seattle', 'washington']):
                location_patterns.extend(['%seattle%', '%washington%', '%wa%', '%bellevue%', '%redmond%'])
            
            # Los Angeles area variations
            elif any(term in location_lower for term in ['los angeles', 'la', 'california']):
                location_patterns.extend(['%los angeles%', '%la%', '%california%', '%ca%', '%santa monica%', '%pasadena%'])
            
            # If no predefined patterns, use the search term directly
            else:
                location_patterns = [f'%{location_lower}%']
            
            # Add this location's conditions to the overall list
            for pattern in location_patterns:
                all_location_conditions.append(Job.location.ilike(pattern))
        
        # Apply all location filters with OR conditions
        if all_location_conditions:
            query = query.filter(or_(*all_location_conditions))
    
    if days:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Job.posted_at >= cutoff_date)
    
    # Order by relevance score first, then by most recent date
    # Recalculate scores based on search query if provided
    jobs_with_scores = []
    for job in query.order_by(Job.posted_at.desc()).limit(limit * 2).all():  # Get more jobs to re-score
        job_dict = {
            "title": job.title,
            "description": job.description,
            "company": job.company,
            "location": job.location,
            "url": job.url,
            "source": job.source,
            "posted_at": job.posted_at
        }
        
        # Recalculate score based on search query, or use None if no search query
        if q and q.strip():
            new_score = score_job(job_dict, q)
        else:
            new_score = None  # No search query, so no relevance score
        
        jobs_with_scores.append({
            "job": job,
            "score": new_score
        })
    
    # Sort by new score (None values go to end) and take the requested limit
    if q and q.strip():
        jobs_with_scores.sort(key=lambda x: (x["score"] or 0, x["job"].posted_at), reverse=True)
    else:
        # No search query, just sort by date
        jobs_with_scores.sort(key=lambda x: x["job"].posted_at, reverse=True)
    
    rows = [item["job"] for item in jobs_with_scores[:limit]]
    return [JobOut(
        id=r.id, title=r.title, company=r.company, location=r.location, url=r.url,
        source=r.source, posted_at=r.posted_at, description=r.description, 
        score=next(item["score"] for item in jobs_with_scores if item["job"].id == r.id)
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
        j["score"] = score_job(j)  # Use default scoring for manual ingestion
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
