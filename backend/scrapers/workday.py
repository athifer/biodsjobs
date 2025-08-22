"""
Workday scraper for companies using Workday ATS platform.
"""

import asyncio
import httpx
import re
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

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
        }
    }
    
    company_info = workday_companies.get(company_token)
    if not company_info:
        print(f"Company {company_token} not found in workday configuration")
        return []

    jobs = []
    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        ) as client:
            
            print(f"Fetching jobs from {company_info['url']} for {company_token}")
            
            # Get the main jobs page 
            response = await client.get(company_info['url'])
            response.raise_for_status()
            
            print(f"Response status: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Multiple strategies to find jobs with better selectors
            
            # Strategy 1: Look for Workday job cards/items with more patterns
            job_cards = soup.find_all(['li', 'div', 'tr'], attrs={
                'data-automation-id': lambda x: x and any(pattern in x.lower() for pattern in 
                    ['job', 'posting', 'searchresult', 'listitem', 'card'])
            })
            
            # Also try common Workday selectors
            if not job_cards:
                job_cards = soup.select('[data-automation-id*="job"]')
            if not job_cards:
                job_cards = soup.select('.css-1d6urnp, .css-k008qs, [class*="job"], [class*="posting"]')
            
            print(f"Found {len(job_cards)} job cards with automation IDs")
            
            # Strategy 2: Look for links that contain job-related patterns
            if not job_cards:
                all_links = soup.find_all('a', href=True)
                job_cards = [link for link in all_links if 
                           any(pattern in link.get('href', '').lower() for pattern in 
                               ['/job/', 'jobdetail', 'posting', 'position']) and
                           len(link.get_text(strip=True)) > 10]
                print(f"Found {len(job_cards)} potential job links")
            
            # Strategy 3: Look for any text elements with job titles and biotech keywords
            if not job_cards:
                biotech_keywords = ['scientist', 'research', 'data', 'engineer', 'analyst', 'director', 
                                   'manager', 'bioinformatics', 'computational', 'clinical', 'genomics']
                all_text_elements = soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4'], 
                    string=re.compile(r'(' + '|'.join(biotech_keywords) + ')', re.I))
                job_cards = []
                for elem in all_text_elements:
                    parent = elem.find_parent(['li', 'div', 'tr', 'article'])
                    if parent and len(elem.get_text(strip=True)) > 10:
                        job_cards.append(parent)
                job_cards = list(set(job_cards))  # Remove duplicates
                print(f"Found {len(job_cards)} elements with biotech keywords")
            
            for job_card in job_cards[:30]:  # Process up to 30 items
                try:
                    # Extract title
                    title = ""
                    title_selectors = [
                        '[data-automation-id*="title"]',
                        '[data-automation-id="jobTitle"]',
                        'h3', 'h4', 'a'
                    ]
                    
                    for selector in title_selectors:
                        title_elem = job_card.select_one(selector)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if len(title) > 5:  # Valid title
                                break
                    
                    # If no good title found, try the job card text itself
                    if not title or len(title) < 5:
                        title = job_card.get_text(strip=True)
                        # Take first reasonable line as title
                        lines = [line.strip() for line in title.split('\n') if line.strip()]
                        title = lines[0] if lines else ""
                    
                    # Extract URL
                    job_url = ""
                    link_elem = job_card.find('a', href=True)
                    if link_elem:
                        href = link_elem.get('href')
                        if href.startswith('/'):
                            base_parts = company_info['url'].split('/')[:3]
                            job_url = '/'.join(base_parts) + href
                        elif href.startswith('http'):
                            job_url = href
                    
                    # Extract location
                    location = "Not specified"
                    location_selectors = [
                        '[data-automation-id*="location"]',
                        '[data-automation-id="jobLocation"]',
                        '.location', '.jobLocation'
                    ]
                    
                    for selector in location_selectors:
                        location_elem = job_card.select_one(selector)
                        if location_elem:
                            location = location_elem.get_text(strip=True)
                            break
                    
                    # Filter for biotech relevance
                    biotech_keywords = [
                        'scientist', 'research', 'data', 'computational', 'bioinformatics', 
                        'clinical', 'genomics', 'biostatistics', 'biologist', 'engineer',
                        'analyst', 'director', 'manager', 'associate', 'principal', 'lead',
                        'machine learning', 'ai', 'software', 'informatics', 'statistics'
                    ]
                    
                    if title and len(title) > 5 and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                        job_data = {
                            "title": title[:200],  # Limit title length
                            "company": company_info['company_name'],
                            "location": location,
                            "url": job_url or company_info['url'],
                            "source": "workday",
                            "posted_at": datetime.utcnow(),
                            "description": f"Position at {company_info['company_name']} - {title[:100]}",
                        }
                        jobs.append(job_data)
                        print(f"Added job: {title[:50]}...")
                        
                        if len(jobs) >= 15:  # Limit to 15 jobs
                            break
                            
                except Exception as e:
                    print(f"Error processing job card: {e}")
                    continue
            
            print(f"Total jobs found for {company_token}: {len(jobs)}")
            return jobs
            
    except Exception as e:
        print(f"Error fetching jobs for {company_token}: {e}")
        return []

if __name__ == "__main__":
    # Test the scraper
    async def test():
        jobs = await fetch_company_jobs("illumina")
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"- {job['title']} at {job['company']}")
    
    asyncio.run(test())
