"""
Enhanced Workday scraper using advanced techniques for JavaScript-heavy sites.
"""

import asyncio
import httpx
import re
import json
import sys
import os
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

# Add parent directory to path to import advanced_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from advanced_scraper import AdvancedScraper

if __name__ == "__main__":
    # Test the enhanced workday scraper
    async def test():
        jobs = await fetch_company_jobs("illumina")
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"- {job['title']} at {job['company']}")
    
    asyncio.run(test())

def parse_workday_jobs(jobs_data: List[Dict], company_name: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Parse job data from Workday API responses.
    """
    jobs = []
    biotech_keywords = [
        'scientist', 'research', 'data', 'computational', 'bioinformatics', 
        'clinical', 'genomics', 'biostatistics', 'biologist', 'engineer',
        'analyst', 'director', 'manager', 'associate', 'principal', 'lead',
        'machine learning', 'ai', 'software', 'informatics', 'statistics'
    ]
    
    for job_data in jobs_data[:30]:  # Limit processing
        try:
            title = job_data.get('title') or job_data.get('jobTitle') or job_data.get('name', '')
            location = job_data.get('location') or job_data.get('primaryLocation') or job_data.get('locationsText', 'Not specified')
            job_url = job_data.get('url') or job_data.get('jobUrl') or job_data.get('externalUrl') or base_url
            
            # Build full URL if relative
            if job_url and job_url.startswith('/'):
                base_parts = base_url.split('/')[:3]
                job_url = '/'.join(base_parts) + job_url
            
            # Filter for biotech relevance
            if title and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                jobs.append({
                    "title": title[:200],
                    "company": company_name,
                    "location": location,
                    "url": job_url,
                    "source": "workday",
                    "posted_at": datetime.utcnow(),
                    "description": f"Position at {company_name} - {title[:100]}",
                })
                
                if len(jobs) >= 15:
                    break
                    
        except Exception as e:
            continue
    
    return jobs

async def fetch_company_jobs(company_token: str) -> List[Dict[str, Any]]:
    """
    Fetch jobs from Workday career sites.
    """
    
    # Company configurations for Workday sites - matching companies_all.yaml
    workday_companies = {
        "illumina": {
            "url": "https://illumina.wd1.myworkdayjobs.com/illumina-careers",
            "company_name": "Illumina"
        },
        "gilead": {
            "url": "https://gilead.wd1.myworkdayjobs.com/gileadcareers", 
            "company_name": "Gilead"
        },
        "pfizer": {
            "url": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers",
            "company_name": "Pfizer"
        },
        "bms": {
            "url": "https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS",
            "company_name": "Bristol Myers Squibb"
        },
        "moderna": {
            "url": "https://modernatx.wd1.myworkdayjobs.com/M_tx",
            "company_name": "Moderna"
        },
        "vertex": {
            "url": "https://vrtx.wd501.myworkdayjobs.com/vertex_careers",
            "company_name": "Vertex"
        },
        "alnylam": {
            "url": "https://alnylam.wd5.myworkdayjobs.com/Alnylam_Careers",
            "company_name": "Alnylam"
        },
        "tempus": {
            "url": "https://tempus.wd5.myworkdayjobs.com/en-US/Tempus",
            "company_name": "Tempus"
        },
        "biogen": {
            "url": "https://biogen.wd1.myworkdayjobs.com/en-US/Biogen_External_Career_Site",
            "company_name": "Biogen"
        },
        "lilly": {
            "url": "https://lillycareers.wd5.myworkdayjobs.com/EliLillyJobs",
            "company_name": "Eli Lilly"
        },
        "abbvie": {
            "url": "https://abbvie.wd1.myworkdayjobs.com/External",
            "company_name": "AbbVie"
        },
        "jnj": {
            "url": "https://jobs.jnj.com/",
            "company_name": "Johnson & Johnson"
        },
        "incyte": {
            "url": "https://incyte.wd1.myworkdayjobs.com/en-US/IncyteCareers",
            "company_name": "Incyte"
        },
        "amgen": {
            "url": "https://careers.amgen.com/",
            "company_name": "Amgen"
        },
        "merck": {
            "url": "https://jobs.merck.com/",
            "company_name": "Merck"
        },
        "abbott": {
            "url": "https://abbott.wd5.myworkdayjobs.com/abbottcareers",
            "company_name": "Abbott"
        },
        "exactsciences": {
            "url": "https://exactsciences.wd1.myworkdayjobs.com/Exact_Sciences",
            "company_name": "Exact Sciences"
        },
        "kitepharma": {
            "url": "https://gilead.wd1.myworkdayjobs.com/en-US/gileadcareers",
            "company_name": "Kite Pharma"
        }
    }
    
    company_info = workday_companies.get(company_token)
    if not company_info:
        print(f"Company {company_token} not found in workday configuration")
        return []

    # Use the advanced scraper for sophisticated Workday scraping
    advanced_scraper = AdvancedScraper()
    jobs = await advanced_scraper.scrape_company_advanced(
        company_info['company_name'], 
        company_info['url']
    )
    
    return jobs

if __name__ == "__main__":
    # Test the scraper
    async def test():
        jobs = await fetch_company_jobs("illumina")
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"- {job['title']} at {job['company']}")
    
    asyncio.run(test())
