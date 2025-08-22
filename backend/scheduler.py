import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from db import SessionLocal, upsert_job, init_db, Job
from ingestor import load_companies
from scrapers import lever as lever_scraper
from scrapers import greenhouse as greenhouse_scraper
from scrapers import ycombinator as yc_scraper
from scrapers import workday as workday_scraper
from scrapers import angellist as angellist_scraper
from scrapers import bamboo as bamboo_scraper
from util import score_job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_job_ingestion():
    """Run job ingestion for all companies in the background with cleanup."""
    try:
        logger.info("Starting scheduled job ingestion...")
        companies = load_companies()
        db = SessionLocal()
        total_jobs = 0
        all_current_urls = set()  # Track all URLs found in current scraping
        
        for entry in companies:
            source = entry.get("source")
            company = entry.get("company")
            jobs = []
            
            try:
                if source == "lever":
                    company_token = entry.get("token", company)
                    jobs = asyncio.run(lever_scraper.fetch_company_jobs(company_token))
                elif source == "greenhouse":
                    company_token = entry.get("token", company)
                    jobs = asyncio.run(greenhouse_scraper.fetch_company_jobs(company_token))
                elif source == "ycombinator":
                    jobs = asyncio.run(yc_scraper.fetch_company_jobs(company))
                elif source == "workday":
                    company_token = entry.get("token", company)
                    jobs = asyncio.run(workday_scraper.fetch_company_jobs(company_token))
                elif source == "angellist":
                    company_token = entry.get("token", company)
                    jobs = asyncio.run(angellist_scraper.fetch_company_jobs(company_token))
                elif source == "bamboo":
                    company_token = entry.get("token", company)
                    jobs = asyncio.run(bamboo_scraper.fetch_company_jobs(company_token))
            except Exception as e:
                logger.error(f"Error fetching jobs for {company} ({source}): {e}")
                continue
            
            for job in jobs:
                job["score"] = score_job(job)  # Use default scoring for scheduled ingestion
                upsert_job(db, job)
                all_current_urls.add(job["url"])
            
            logger.info(f"{company}: {len(jobs)} jobs processed.")
            total_jobs += len(jobs)
        
        # Clean up obsolete jobs
        logger.info("Cleaning up obsolete job postings...")
        obsolete_count = db.query(Job).filter(~Job.url.in_(all_current_urls)).count()
        
        if obsolete_count > 0:
            # Delete obsolete jobs
            db.query(Job).filter(~Job.url.in_(all_current_urls)).delete(synchronize_session=False)
            db.commit()
            logger.info(f"Removed {obsolete_count} obsolete job postings")
        else:
            logger.info("No obsolete jobs found")
        
        db.close()
        logger.info(f"Scheduled ingestion completed. Total jobs processed: {total_jobs}")
        
    except Exception as e:
        logger.error(f"Error during scheduled job ingestion: {e}")

def start_scheduler():
    """Start the background scheduler for automatic job updates."""
    scheduler = BackgroundScheduler()
    
    # Schedule job ingestion every 4 hours
    scheduler.add_job(
        func=run_job_ingestion,
        trigger=IntervalTrigger(hours=4),
        id='job_ingestion',
        name='Automatic job ingestion every 4 hours',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Job scheduler started - automatic updates every 4 hours")
    return scheduler

def stop_scheduler(scheduler):
    """Stop the background scheduler."""
    if scheduler:
        scheduler.shutdown()
        logger.info("Job scheduler stopped")
