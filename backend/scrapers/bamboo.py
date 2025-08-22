import httpx
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

async def fetch_company_jobs(company_token: str) -> List[Dict]:
    """Fetch jobs from BambooHR for companies that use this platform."""
    
    # Map company tokens to their BambooHR career pages
    bamboo_urls = {
        "23andme": "https://23andme.bamboohr.com/careers/",
        "color": "https://color.bamboohr.com/careers/",
        "twist": "https://twistbioscience.bamboohr.com/careers/",
        "synthetic": "https://syntheticbiologyone.bamboohr.com/careers/"
    }
    
    base_url = bamboo_urls.get(company_token)
    if not base_url:
        return []
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            r = await client.get(base_url, headers=headers)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = []
            
            # BambooHR typically uses these selectors
            job_elements = soup.select('.BambooHR-AtsJobListing-Job') or soup.select('.opening')
            
            for job_elem in job_elements:
                try:
                    # Extract title
                    title_elem = job_elem.select_one('.BambooHR-AtsJobListing-Job-Title') or job_elem.select_one('h3') or job_elem.select_one('.title')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Extract URL
                    link_elem = job_elem.select_one('a')
                    job_url = ""
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('/'):
                            job_url = base_url.rstrip('/') + href
                        else:
                            job_url = href
                    
                    # Extract location
                    location_elem = job_elem.select_one('.BambooHR-AtsJobListing-Job-Location') or job_elem.select_one('.location')
                    location = location_elem.get_text(strip=True) if location_elem else ""
                    
                    if title:
                        jobs.append({
                            "title": title,
                            "company": company_token,
                            "location": location or "Remote",
                            "url": job_url or base_url,
                            "source": "bamboo",
                            "posted_at": datetime.utcnow(),
                            "description": f"Position at {company_token} - {title}",
                        })
                        
                except Exception as e:
                    continue
            
            return jobs
            
    except Exception as e:
        return []
