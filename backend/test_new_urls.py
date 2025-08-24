#!/usr/bin/env python3
"""
Test the comprehensive scraper with debug output for new URLs
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from pathlib import Path
import yaml

async def test_comprehensive_with_new_urls():
    print("TESTING COMPREHENSIVE SCRAPER WITH NEW URLS")
    print("=" * 60)
    
    test_companies = ["pfizer", "moderna"]
    
    # Load company configuration
    current_dir = Path(__file__).parent
    companies_file = current_dir / "companies.yaml"
    with open(companies_file, 'r') as f:
        companies_data = yaml.safe_load(f)
    
    for company_token in test_companies:
        print(f"\n🔍 Testing {company_token}")
        
        # Find company info
        company_info = None
        if "comprehensive" in companies_data:
            for company in companies_data["comprehensive"]:
                if company.get("token") == company_token:
                    company_info = {
                        "name": company.get("company"),
                        "careers_url": company.get("careers_url"),
                        "api_pattern": "general"
                    }
                    break
        
        if not company_info:
            print(f"❌ Company not found")
            continue
            
        print(f"URL: {company_info['careers_url']}")
        
        # Test the URL manually
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
            
            try:
                response = await client.get(company_info['careers_url'], headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Content length: {len(response.text)}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job listing elements like the comprehensive scraper does
                job_links = soup.find_all('a', href=True)
                print(f"Total links found: {len(job_links)}")
                
                potential_jobs = []
                for job_link in job_links[:50]:  # Limit for testing
                    try:
                        text = job_link.get_text(strip=True)
                        href = job_link.get('href')
                        
                        if not text or not href or len(text) < 10 or len(text) > 120:
                            continue
                        
                        # Skip bad patterns
                        bad_patterns = ['clinical-studies', 'about', 'contact', 'news', 'press', 'privacy', 
                                      'terms', 'cookies', 'social', 'linkedin', 'twitter', 'facebook']
                        if any(pattern in href.lower() for pattern in bad_patterns):
                            continue
                        
                        # Filter for biotech relevance
                        biotech_keywords = ['scientist', 'research', 'data', 'computational', 'bioinformatics', 
                                          'clinical trial', 'genomics', 'biostatistics', 'biologist', 'engineer',
                                          'analyst', 'director', 'manager', 'associate', 'principal', 'lead']
                        
                        is_biotech_relevant = any(keyword.lower() in text.lower() for keyword in biotech_keywords)
                        is_job_link = ('job' in href.lower() or 'career' in href.lower() or 'position' in href.lower())
                        
                        if is_biotech_relevant and (is_job_link or 'openings' in href.lower()):
                            potential_jobs.append((text, href))
                            
                    except Exception as e:
                        continue
                
                print(f"Potential biotech jobs found: {len(potential_jobs)}")
                for i, (title, url) in enumerate(potential_jobs[:5]):
                    print(f"  {i+1}. {title[:60]}... -> {url[:80]}...")
                
                if len(potential_jobs) == 0:
                    # Debug: Show some sample links
                    print("\nSample links found:")
                    for i, job_link in enumerate(job_links[:10]):
                        text = job_link.get_text(strip=True)
                        href = job_link.get('href', '')
                        if text and len(text) > 5:
                            print(f"  {i+1}. {text[:50]}... -> {href[:50]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_with_new_urls())
