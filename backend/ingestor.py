import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import yaml
from pathlib import Path

# Import database and scrapers
from db import SessionLocal, upsert_job, init_db, Job
from scrapers import lever as lever_scraper
from scrapers import greenhouse as greenhouse_scraper
from scrapers import ycombinator as yc_scraper
from scrapers import workday as workday_scraper
from scrapers import angellist as angellist_scraper
from scrapers import bamboo as bamboo_scraper
from scrapers import comprehensive as comprehensive_scraper
from scrapers import talentbrew as talentbrew_scraper
from util import score_job

def load_companies():
    """Load companies from the single companies.yaml file."""
    companies = []
    current_dir = Path(__file__).parent
    companies_file = current_dir / "companies.yaml"
    
    try:
        with open(companies_file, 'r') as f:
            company_data = yaml.safe_load(f)
            if isinstance(company_data, dict):
                # e.g. {"greenhouse": [...], "lever": [...]}
                for source, entries in company_data.items():
                    for entry in entries:
                        entry["source"] = source
                        companies.append(entry)
        print(f"Loaded {len(companies)} companies from {companies_file.name}")
    except Exception as e:
        print(f"Error loading {companies_file}: {e}")
        # Fallback to companies_all.yaml if companies.yaml doesn't exist
        fallback_file = current_dir / "companies_all.yaml"
        try:
            with open(fallback_file, 'r') as f:
                company_data = yaml.safe_load(f)
                if isinstance(company_data, dict):
                    for source, entries in company_data.items():
                        for entry in entries:
                            entry["source"] = source
                            companies.append(entry)
            print(f"Loaded {len(companies)} companies from fallback {fallback_file.name}")
        except Exception as e2:
            print(f"Error loading fallback file {fallback_file}: {e2}")
    
    return companies

def derive_careers_url(entry):
    """Derive careers_url from entry fields if not explicitly given."""
    if "careers_url" in entry:
        return entry["careers_url"]
    source = entry.get("source")
    company = entry.get("company")
    if source == "greenhouse":
        return f"https://boards.greenhouse.io/{company}"
    elif source == "lever":
        return f"https://jobs.lever.co/{company}"
    return None

def get_job_urls():
    """Extract job URLs from company data."""
    companies = load_companies()
    urls = []
    
    for company in companies:
        url = derive_careers_url(company)
        if url:
            urls.append(url)
    
    return urls

# limit to 5 requests per second
limiter = AsyncLimiter(max_rate=5, time_period=1)

async def fetch(session, url):
    async with limiter:  # ensures rate limit
        try:
            async with session.get(url, timeout=20) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"⚠️ Error {response.status} for {url}")
        except Exception as e:
            print(f"❌ Request failed for {url}: {e}")
        return None

async def scrape_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def run_ingestion_with_cleanup():
    """Run job ingestion and clean up obsolete jobs."""
    # Initialize database tables
    init_db()
    
    companies = load_companies()
    print(f"Found {len(companies)} companies to ingest")
    db = SessionLocal()
    total_jobs = 0
    all_current_urls = set()  # Track all URLs found in current scraping
    
    for entry in companies:
        source = entry.get("source")
        company = entry.get("company")
        jobs = []
        try:
            if source == "lever":
                # Extract token from host field (format: jobs.lever.co/TOKEN)
                if "host" in entry:
                    host = entry["host"]
                    company_token = host.split("/")[-1] if "/" in host else host
                else:
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
            elif source == "comprehensive":
                company_token = entry.get("token", company)
                jobs = asyncio.run(comprehensive_scraper.fetch_company_jobs(company_token))
            elif source == "talentbrew":
                company_token = entry.get("token", company)
                jobs = asyncio.run(talentbrew_scraper.fetch_company_jobs(company_token))
            # Add more sources here if needed
        except Exception as e:
            print(f"❌ Error fetching jobs for {company} ({source}): {e}")
        
        for job in jobs:
            job["score"] = score_job(job)  # Use default scoring for ingestion
            upsert_job(db, job)
            all_current_urls.add(job["url"])
        
        print(f"{company}: {len(jobs)} jobs ingested.")
        total_jobs += len(jobs)
    
    # Clean up obsolete jobs
    print("🧹 Cleaning up obsolete job postings...")
    obsolete_jobs = db.query(Job).filter(~Job.url.in_(all_current_urls)).all()
    obsolete_count = len(obsolete_jobs)
    
    if obsolete_count > 0:
        # Delete obsolete jobs
        db.query(Job).filter(~Job.url.in_(all_current_urls)).delete(synchronize_session=False)
        db.commit()
        print(f"🗑️  Removed {obsolete_count} obsolete job postings")
    else:
        print("✅ No obsolete jobs found")
    
    db.close()
    print(f"Total jobs ingested: {total_jobs}")
    print(f"Active jobs in database: {total_jobs}")

if __name__ == "__main__":
    run_ingestion_with_cleanup()
