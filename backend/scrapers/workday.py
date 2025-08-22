import httpx
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

async def fetch_company_jobs(company_token: str) -> List[Dict]:
    """Fetch jobs from Workday for a given company.
    Workday format: https://{company}.wd1.myworkdayjobs.com/{careers_site}
    """
    # Map company tokens to their workday URLs
    workday_urls = {
        "gilead": "https://gilead.wd1.myworkdayjobs.com/gileadcareers",
        "amgen": "https://careers.amgen.com/en/search-jobs",
        "merck": "https://jobs.merck.com/us/en", 
        "pfizer": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers",
        "bms": "https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS",
        "moderna": "https://modernatx.wd1.myworkdayjobs.com/M_US",
        "alnylam": "https://alnylam.wd5.myworkdayjobs.com/Alnylam_Careers",
        "lilly": "https://eli-lilly.wd1.myworkdayjobs.com/LillyJobs",
        "abbvie": "https://abbvie.wd1.myworkdayjobs.com/External",
        "jnj": "https://jnj.wd1.myworkdayjobs.com/Careers",
        "incyte": "https://incyte.wd1.myworkdayjobs.com/IncyteCareers"
    }
    
    base_url = workday_urls.get(company_token)
    if not base_url:
        return []
    
    # Try to get jobs from Workday's JSON API if available
    try:
        # Some Workday sites have JSON APIs, but they're often protected
        # For now, we'll scrape the HTML and look for specific biotech-related terms
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Try the main jobs page first
            r = await client.get(base_url, headers=headers)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = []
            
            # Look for job listings - Workday uses various selectors
            job_selectors = [
                '[data-automation-id="jobTitle"]',
                '.css-ur1szg',
                '[data-automation-id="searchResultItem"]',
                '.PNXV4EXC4NI-1-WP',
                'tr[data-automation-id]'
            ]
            
            for selector in job_selectors:
                job_elements = soup.select(selector)
                if job_elements:
                    break
            
            for job_elem in job_elements[:20]:  # Limit to first 20 jobs
                try:
                    # Extract job title
                    title_elem = job_elem.select_one('[data-automation-id="jobTitle"]') or job_elem.select_one('a')
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Extract job URL
                    link_elem = job_elem.select_one('a')
                    job_url = ""
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('/'):
                            job_url = base_url.split('/')[0] + '//' + base_url.split('/')[2] + href
                        else:
                            job_url = href
                    
                    # Extract location
                    location_selectors = ['[data-automation-id="jobLocation"]', '.css-1dimb5e', '.location']
                    location = ""
                    for loc_sel in location_selectors:
                        loc_elem = job_elem.select_one(loc_sel)
                        if loc_elem:
                            location = loc_elem.get_text(strip=True)
                            break
                    
                    # Only include jobs that seem biotech-related
                    biotech_keywords = [
                        'bioinformatics', 'computational biology', 'genomics', 'proteomics', 
                        'data scientist', 'biostatistics', 'clinical', 'research', 'scientist',
                        'biologist', 'biomedical', 'pharma', 'drug discovery', 'translational',
                        'machine learning', 'AI', 'software engineer', 'data engineer'
                    ]
                    
                    if title and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                        jobs.append({
                            "title": title,
                            "company": company_token.upper(),
                            "location": location or "Not specified",
                            "url": job_url or base_url,
                            "source": "workday",
                            "posted_at": datetime.utcnow(),
                            "description": f"Position at {company_token.upper()} - {title}",
                        })
                        
                except Exception as e:
                    continue
            
            return jobs
            
    except Exception as e:
        # If scraping fails, return empty list
        return []
