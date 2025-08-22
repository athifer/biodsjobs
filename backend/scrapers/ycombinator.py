import httpx
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

async def fetch_company_jobs(company: str) -> List[Dict]:
    """Fetch jobs from Y Combinator's Work at a Startup platform."""
    
    # YC has moved to a centralized job board - try to search for the company
    try:
        # Use the Work at a Startup search
        search_url = "https://www.workatastartup.com/companies"
        
        async with httpx.AsyncClient(timeout=20) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Search for the company
            params = {'search': company}
            r = await client.get(search_url, headers=headers, params=params)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = []
            
            # Look for job listings related to this company
            # This is a simplified approach since YC's job board structure may vary
            company_elements = soup.select('[data-company]') or soup.select('.company-card')
            
            for company_elem in company_elements:
                company_name = company_elem.get('data-company', '').lower()
                if company.lower() in company_name or company_name in company.lower():
                    # Found the company, now look for jobs
                    job_links = company_elem.select('a[href*="/jobs/"]')
                    
                    for job_link in job_links[:5]:  # Limit to 5 jobs per company
                        try:
                            title = job_link.get_text(strip=True)
                            job_url = job_link.get('href')
                            
                            if job_url and not job_url.startswith('http'):
                                job_url = "https://www.workatastartup.com" + job_url
                            
                            if title:
                                jobs.append({
                                    "title": title,
                                    "company": company,
                                    "location": "Remote",  # YC jobs often remote-friendly
                                    "url": job_url or f"https://www.workatastartup.com/companies/{company}",
                                    "source": "ycombinator",
                                    "posted_at": datetime.utcnow(),
                                    "description": f"Position at {company} (YC company) - {title}",
                                })
                        except Exception:
                            continue
            
            # If no jobs found through search, return empty list
            # YC has moved away from individual company job pages
            return jobs
            
    except Exception as e:
        # If all else fails, return empty list
        return []
