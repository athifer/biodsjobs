import httpx
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

async def fetch_company_jobs(company: str) -> List[Dict]:
    """Fetch jobs from AngelList (Wellfound) for biotech startups."""
    
    # AngelList company URLs
    angellist_companies = {
        "newomics": "https://wellfound.com/company/newomics/jobs",
        "variant": "https://wellfound.com/company/variant-bio/jobs", 
        "recursion": "https://wellfound.com/company/recursion-pharmaceuticals/jobs",
        "tempus": "https://wellfound.com/company/tempus/jobs",
        "deepgenomics": "https://wellfound.com/company/deep-genomics/jobs",
        "atomwise": "https://wellfound.com/company/atomwise/jobs",
        "insilico": "https://wellfound.com/company/insilico-medicine/jobs",
        "owkin": "https://wellfound.com/company/owkin/jobs"
    }
    
    company_url = angellist_companies.get(company)
    if not company_url:
        return []
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            r = await client.get(company_url, headers=headers)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = []
            
            # AngelList job selectors
            job_elements = soup.select('[data-test="JobSearchCard"]') or soup.select('.job-listing')
            
            for job_elem in job_elements:
                try:
                    # Extract title
                    title_elem = job_elem.select_one('[data-test="JobTitle"]') or job_elem.select_one('h4') or job_elem.select_one('.title')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Extract URL
                    link_elem = job_elem.select_one('a')
                    job_url = ""
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('/'):
                            job_url = "https://wellfound.com" + href
                        else:
                            job_url = href
                    
                    # Extract location and salary info
                    location_elem = job_elem.select_one('[data-test="JobLocation"]') or job_elem.select_one('.location')
                    location = location_elem.get_text(strip=True) if location_elem else "Remote"
                    
                    # Extract description snippet if available
                    desc_elem = job_elem.select_one('[data-test="JobDescription"]') or job_elem.select_one('.description')
                    description = desc_elem.get_text(strip=True) if desc_elem else f"Position at {company} - {title}"
                    
                    if title:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "url": job_url or company_url,
                            "source": "angellist",
                            "posted_at": datetime.utcnow(),
                            "description": description[:500],  # Limit description length
                        })
                        
                except Exception as e:
                    continue
            
            return jobs
            
    except Exception as e:
        return []
