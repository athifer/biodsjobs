"""
TalentBrew/PhenomPeople scraper for companies using TalentBrew ATS platform.
"""

import asyncio
import httpx
import re
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import json

async def fetch_company_jobs(company_token: str) -> List[Dict[str, Any]]:
    """
    Fetch jobs from TalentBrew/PhenomPeople career sites.
    """
    
    # Company configurations for TalentBrew sites
    talentbrew_companies = {
        "amgen": {
            "name": "Amgen",
            "base_url": "https://careers.amgen.com",
            "search_url": "https://careers.amgen.com/en/search-jobs",
            "api_url": "https://careers.amgen.com/api/jobs"
        },
        "merck": {
            "name": "Merck",
            "base_url": "https://jobs.merck.com",
            "search_url": "https://jobs.merck.com/us/en/search-jobs",
            "api_url": "https://jobs.merck.com/api/jobs"
        }
    }
    
    company_info = talentbrew_companies.get(company_token)
    if not company_info:
        return []
    
    jobs = []
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Strategy 1: Try API endpoint first
            try:
                search_params = {
                    'q': 'scientist OR bioinformatics OR computational OR data OR research OR clinical OR genomics',
                    'limit': 100,
                    'offset': 0,
                    'location': '',
                    'category': ''
                }
                
                api_response = await client.get(company_info['api_url'], params=search_params, headers=headers)
                
                if api_response.status_code == 200:
                    try:
                        api_data = api_response.json()
                        job_results = api_data.get('jobs', []) or api_data.get('searchResults', []) or api_data.get('data', [])
                        
                        for job_item in job_results:
                            try:
                                title = job_item.get('title', '').strip()
                                location = job_item.get('location', {}).get('name', '') or job_item.get('locationName', '') or 'Not specified'
                                job_id = job_item.get('id', '') or job_item.get('jobId', '')
                                
                                # Filter for biotech relevance
                                biotech_keywords = [
                                    'scientist', 'bioinformatics', 'computational', 'data', 'research', 
                                    'clinical', 'genomics', 'biostatistics', 'biologist', 'engineer',
                                    'analyst', 'director', 'manager', 'associate', 'principal', 'lead'
                                ]
                                
                                if title and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                                    # Construct job URL
                                    job_url = f"{company_info['base_url']}/jobs/{job_id}" if job_id else company_info['search_url']
                                    
                                    # Try to get more details
                                    description = job_item.get('description', '') or job_item.get('summary', '') or f"Position at {company_info['name']} - {title}"
                                    
                                    jobs.append({
                                        "title": title,
                                        "company": company_info['name'],
                                        "location": location,
                                        "url": job_url,
                                        "source": "talentbrew",
                                        "posted_at": datetime.utcnow(),
                                        "description": description[:500],  # Truncate description
                                    })
                                    
                            except Exception as e:
                                continue
                                
                    except json.JSONDecodeError:
                        pass
                        
            except Exception as e:
                pass
            
            # Strategy 2: Fallback to scraping search results page
            if len(jobs) == 0:
                try:
                    # Updated search strategy with proper URL encoding
                    search_keywords = ['scientist', 'bioinformatics', 'computational', 'data', 'research', 'clinical', 'genomics']
                    search_query = ' '.join(search_keywords)
                    
                    search_params = {
                        'q': search_query,
                        'location': '',
                        'sortBy': 'relevance'
                    }
                    
                    print(f"Searching jobs at {company_info['search_url']} with query: {search_query}")
                    search_response = await client.get(company_info['search_url'], params=search_params, headers=headers)
                    
                    if search_response.status_code == 404:
                        print(f"Error scraping search results for {company_token}: {search_response.status_code} {search_response.reason_phrase}")
                        return jobs
                        
                    search_response.raise_for_status()
                    
                    soup = BeautifulSoup(search_response.text, 'html.parser')
                    
                    # Look for job listing elements (common patterns in TalentBrew sites)
                    job_selectors = [
                        '[data-automation="job-item"]',
                        '.job-item',
                        '.job-result',
                        '.search-results-item',
                        '[class*="job"]',
                        'tr[data-job-id]'
                    ]
                    
                    job_elements = []
                    for selector in job_selectors:
                        elements = soup.select(selector)
                        if elements:
                            job_elements = elements
                            break
                    
                    # If no structured elements found, look for links with job-like patterns
                    if not job_elements:
                        job_elements = soup.find_all('a', href=re.compile(r'/(job|career|position)', re.I))
                    
                    for job_elem in job_elements[:30]:
                        try:
                            # Extract title
                            title_elem = job_elem.find(['h1', 'h2', 'h3', 'h4', 'a']) or job_elem
                            title = title_elem.get_text(strip=True)
                            
                            # Skip if title is too short or too long
                            if len(title) < 5 or len(title) > 120:
                                continue
                            
                            # Filter for biotech relevance
                            biotech_keywords = [
                                'scientist', 'bioinformatics', 'computational', 'data', 'research', 
                                'clinical', 'genomics', 'biostatistics', 'biologist', 'engineer',
                                'analyst', 'director', 'manager', 'associate', 'principal', 'lead'
                            ]
                            
                            if title and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                                # Extract job URL
                                job_url = company_info['search_url']  # Default fallback
                                if job_elem.name == 'a' and job_elem.get('href'):
                                    href = job_elem.get('href')
                                    if href.startswith('http'):
                                        job_url = href
                                    elif href.startswith('/'):
                                        job_url = company_info['base_url'] + href
                                elif title_elem.name == 'a' and title_elem.get('href'):
                                    href = title_elem.get('href')
                                    if href.startswith('http'):
                                        job_url = href
                                    elif href.startswith('/'):
                                        job_url = company_info['base_url'] + href
                                
                                # Extract location if available
                                location = "Not specified"
                                location_elem = job_elem.find(['span', 'div'], class_=re.compile(r'location', re.I))
                                if location_elem:
                                    location = location_elem.get_text(strip=True)
                                
                                jobs.append({
                                    "title": title,
                                    "company": company_info['name'],
                                    "location": location,
                                    "url": job_url,
                                    "source": "talentbrew",
                                    "posted_at": datetime.utcnow(),
                                    "description": f"Position at {company_info['name']} - {title}",
                                })
                                
                                if len(jobs) >= 20:
                                    break
                                    
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"Error scraping search results for {company_token}: {e}")
            
            return jobs[:20]  # Return up to 20 jobs
            
    except Exception as e:
        print(f"Error fetching jobs for {company_token}: {e}")
        return []

if __name__ == "__main__":
    # Test the scraper
    async def test():
        jobs = await fetch_company_jobs("amgen")
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"- {job['title']} at {job['company']}")
    
    asyncio.run(test())
