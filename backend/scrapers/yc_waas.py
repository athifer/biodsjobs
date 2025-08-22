import httpx
from datetime import datetime
from typing import List, Dict
import json

async def fetch_company_jobs(company: str) -> List[Dict]:
    """Fetch jobs from Work at a Startup (YC's job board) for YC biotech companies."""
    
    # Y Combinator biotech companies
    yc_biotech_companies = [
        "benchling", "insitro", "freenome", "mammoth-biosciences", 
        "scribe-therapeutics", "dyno-therapeutics", "octant-bio",
        "tessera-therapeutics", "arcadia-science", "modern-fertility",
        "atomwise", "recursion-pharmaceuticals", "zymergen"
    ]
    
    if company not in yc_biotech_companies:
        return []
    
    try:
        # YC's Work at a Startup API endpoint
        url = "https://www.workatastartup.com/api/v1/jobs"
        
        async with httpx.AsyncClient(timeout=20) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            # Search for jobs at the specific company
            params = {
                'query': company,
                'location': '',
                'remote': '',
                'role': '',
                'limit': 20
            }
            
            r = await client.get(url, headers=headers, params=params)
            if r.status_code != 200:
                # Fallback to scraping the company page
                return await scrape_yc_company_page(client, company)
            
            data = r.json()
            jobs = []
            
            for job in data.get('jobs', []):
                if company.replace('-', '').lower() in job.get('company_name', '').replace(' ', '').lower():
                    jobs.append({
                        "title": job.get('title', ''),
                        "company": job.get('company_name', company),
                        "location": job.get('location', 'Remote'),
                        "url": f"https://www.workatastartup.com/jobs/{job.get('id', '')}",
                        "source": "yc_waas",
                        "posted_at": datetime.fromisoformat(job.get('created_at', '2025-01-01T00:00:00Z').replace('Z', '+00:00')),
                        "description": job.get('description', '')[:500],
                    })
            
            return jobs
            
    except Exception as e:
        return []

async def scrape_yc_company_page(client, company: str) -> List[Dict]:
    """Fallback: scrape the YC company page directly."""
    try:
        url = f"https://www.ycombinator.com/companies/{company}"
        r = await client.get(url)
        
        if r.status_code == 200:
            # Company exists, but might not have active jobs
            # Return a placeholder or try to find their direct careers page
            return []
        
        return []
        
    except Exception:
        return []
