"""
Comprehensive job scraper that handles various company sites and APIs.
Enhanced with advanced scraping techniques for JavaScript-heavy sites.
"""

import asyncio
import httpx
import re
import sys
import os
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import json

# Add parent directory to path to import advanced_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from advanced_scraper import AdvancedScraper

if __name__ == "__main__":
    # Test the enhanced scraper
    async def test():
        jobs = await fetch_company_jobs("abbott")
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
            location = job_data.get('location') or job_data.get('primaryLocation', 'Not specified')
            job_url = job_data.get('url') or job_data.get('jobUrl') or base_url
            
            # Filter for biotech relevance
            if title and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                jobs.append({
                    "title": title[:200],
                    "company": company_name,
                    "location": location,
                    "url": job_url,
                    "source": "comprehensive",
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
    Fetch jobs from companies using comprehensive scraping strategies.
    Now enhanced with advanced scraping techniques.
    """
    
    # Load company configuration from companies.yaml
    from pathlib import Path
    import yaml
    
    # Strategy 1: Custom companies with specific implementations
    custom_companies = {
        "23andme": {
            "name": "23andMe", 
            "careers_url": "https://www.23andme.com/careers/jobs/",
            "api_pattern": "json"
        },
        "guardanthealth": {
            "name": "Guardant Health",
            "careers_url": "https://www.guardanthealth.com/careers/jobs/",
            "api_pattern": "javascript"
        }
    }
    
    company_info = custom_companies.get(company_token)
    
    # If not in custom list, try to load from companies.yaml
    if not company_info:
        try:
            current_dir = Path(__file__).parent.parent
            companies_file = current_dir / "companies.yaml"
            with open(companies_file, 'r') as f:
                companies_data = yaml.safe_load(f)
            
            # Find the company in comprehensive section
            if "comprehensive" in companies_data:
                for company in companies_data["comprehensive"]:
                    if company.get("token") == company_token or company.get("company", "").lower().replace(" ", "") == company_token:
                        company_info = {
                            "name": company.get("company"),
                            "careers_url": company.get("careers_url"),
                            "api_pattern": "general"
                        }
                        break
        except Exception as e:
            print(f"Error loading companies.yaml: {e}")
    
    if not company_info:
        return []
    
    # Use the advanced scraper for sophisticated scraping
    advanced_scraper = AdvancedScraper()
    jobs = await advanced_scraper.scrape_company_advanced(
        company_info['name'], 
        company_info['careers_url']
    )
    
    return jobs

if __name__ == "__main__":
    # Test the scraper
    async def test():
        jobs = await fetch_company_jobs("23andme")
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"- {job['title']} at {job['company']}")
    
    asyncio.run(test())
