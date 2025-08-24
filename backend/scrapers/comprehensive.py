"""
Comprehensive job scraper that handles various company sites and APIs.
Supports multiple strategies including Workday APIs, direct scraping, and custom implementations.
"""

import asyncio
import httpx
import re
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import json

async def try_workday_api(client, base_url: str, company_name: str) -> List[Dict[str, Any]]:
    """
    Try to find jobs using Workday API patterns for JavaScript-heavy sites.
    """
    try:
        # Common Workday API patterns
        api_endpoints = [
            f"{base_url}/jobs",
            f"{base_url}/fs/searchPaginated/jobs",
            f"{base_url}/searchPaginated/jobs",
        ]
        
        for endpoint in api_endpoints:
            try:
                # Try both GET and POST requests
                for method in ["GET", "POST"]:
                    payload = None
                    if method == "POST":
                        payload = {
                            "appliedFacets": {},
                            "limit": 50,
                            "offset": 0,
                            "searchText": ""
                        }
                    
                    if method == "POST":
                        response = await client.post(endpoint, json=payload, headers={
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        })
                    else:
                        response = await client.get(endpoint, headers={'Accept': 'application/json'})
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            try:
                                data = response.json()
                                # Look for job data in various formats
                                jobs_data = None
                                if isinstance(data, dict):
                                    for key in ['jobPostings', 'jobs', 'searchResults', 'body', 'data']:
                                        if key in data:
                                            jobs_data = data[key]
                                            break
                                
                                if jobs_data and isinstance(jobs_data, list) and len(jobs_data) > 0:
                                    print(f"Found {len(jobs_data)} jobs via API endpoint: {endpoint}")
                                    return parse_workday_jobs(jobs_data, company_name, base_url)
                                    
                            except json.JSONDecodeError:
                                continue
                                
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error trying Workday API: {e}")
    
    return []

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
    Handles companies that need custom logic or aren't on standard platforms.
    """
    
    # Load company configuration from companies.yaml if not in custom list
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
    
    company_info = custom_companies.get(company_token)
    if not company_info:
        return []
    
    jobs = []
    
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Strategy: Comprehensive company scraping with multiple approaches
            try:
                print(f"Fetching jobs from {company_info['careers_url']} for {company_token}")
                response = await client.get(company_info['careers_url'], headers=headers)
                response.raise_for_status()
                print(f"Response status: {response.status_code}, content length: {len(response.text)}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Strategy A: Try to find API endpoints if it's a JavaScript-heavy site
                if len(response.text) < 10000 and 'workday' in company_info['careers_url']:
                    print("Detected JavaScript-heavy Workday site, trying API approach...")
                    api_jobs = await try_workday_api(client, company_info['careers_url'], company_info['name'])
                    if api_jobs:
                        return api_jobs
                
                # Strategy B: Look for job listing elements - improved filtering
                job_links = soup.find_all('a', href=True)
                
                for job_link in job_links[:50]:
                    try:
                        # Get the text content and href
                        text = job_link.get_text(strip=True)
                        href = job_link.get('href')
                        
                        # Skip if no text or href
                        if not text or not href:
                            continue
                            
                        # Skip non-job links based on URL patterns
                        bad_patterns = ['clinical-studies', 'about', 'contact', 'news', 'press', 'privacy', 
                                      'terms', 'cookies', 'social', 'linkedin', 'twitter', 'facebook']
                        if any(pattern in href.lower() for pattern in bad_patterns):
                            continue
                        
                        # Skip if too short or too long for a job title
                        if len(text) < 10 or len(text) > 120:
                            continue
                        
                        # Filter for biotech relevance with stricter requirements
                        biotech_keywords = ['scientist', 'research', 'data', 'computational', 'bioinformatics', 
                                          'clinical trial', 'genomics', 'biostatistics', 'biologist', 'engineer',
                                          'analyst', 'director', 'manager', 'associate', 'principal', 'lead']
                        
                        # Must contain job-related keywords AND be a proper link to a job
                        is_biotech_relevant = any(keyword.lower() in text.lower() for keyword in biotech_keywords)
                        is_job_link = ('job' in href.lower() or 'career' in href.lower() or 'position' in href.lower())
                        
                        if is_biotech_relevant and (is_job_link or 'openings' in href.lower()):
                            # Build the job URL
                            job_url = href
                            if href.startswith('/'):
                                base_url = '/'.join(company_info['careers_url'].split('/')[:3])
                                job_url = base_url + href
                            elif not href.startswith('http'):
                                continue  # Skip relative links that don't start with /
                            
                            jobs.append({
                                "title": text,
                                "company": company_info['name'],
                                "location": "Not specified", 
                                "url": job_url,
                                "source": "comprehensive",
                                "posted_at": datetime.utcnow(),
                                "description": f"Position at {company_info['name']} - {text}",
                            })
                            
                            if len(jobs) >= 15:
                                break
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"Error scraping {company_token}: {e}")
            
            return jobs[:20]  # Return up to 20 jobs
            
    except Exception as e:
        print(f"Error fetching jobs for {company_token}: {e}")
        return []

if __name__ == "__main__":
    # Test the scraper
    async def test():
        jobs = await fetch_company_jobs("23andme")
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:
            print(f"- {job['title']} at {job['company']}")
    
    asyncio.run(test())
