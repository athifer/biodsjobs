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

async def fetch_company_jobs(company_token: str) -> List[Dict[str, Any]]:
    """
    Fetch jobs from companies using comprehensive scraping strategies.
    Handles companies that need custom logic or aren't on standard platforms.
    """
    
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
    if not company_info:
        return []
    
    jobs = []
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Strategy: Custom company scraping
            try:
                response = await client.get(company_info['careers_url'], headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job listing elements - improved filtering
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
