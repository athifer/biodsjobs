#!/usr/bin/env python3
"""
Find the actual job search pages for these companies
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def find_job_search_pages():
    print("FINDING ACTUAL JOB SEARCH PAGES")
    print("=" * 60)
    
    companies = {
        "Pfizer": "https://www.pfizer.com/careers",
        "Moderna": "https://www.modernatx.com/careers",
        "Gilead": "https://www.gilead.com/careers",
        "Bristol Myers Squibb": "https://www.bms.com/careers",
        "Vertex": "https://www.vrtx.com/careers"
    }
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    ) as client:
        
        for company, url in companies.items():
            print(f"\n🔍 {company} - {url}")
            
            try:
                response = await client.get(url)
                print(f"Final URL: {response.url}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job search/portal links
                search_patterns = ['search job', 'view job', 'find job', 'job search', 'careers portal', 'open position', 'current opening']
                
                job_portal_links = []
                for link in soup.find_all('a', href=True):
                    text = link.get_text(strip=True).lower()
                    href = link.get('href')
                    
                    if any(pattern in text for pattern in search_patterns) or \
                       any(pattern in href.lower() for pattern in ['job', 'career', 'position', 'opening']):
                        if len(text) > 3 and len(text) < 100:  # Reasonable link text length
                            job_portal_links.append((text, href))
                
                print(f"Found {len(job_portal_links)} potential job portal links:")
                for i, (text, href) in enumerate(job_portal_links[:5]):
                    print(f"  {i+1}. '{text}' -> {href}")
                
                # Test the most promising links
                for text, href in job_portal_links[:3]:
                    if href.startswith('/'):
                        base_parts = str(response.url).split('/')[:3]
                        test_url = '/'.join(base_parts) + href
                    elif href.startswith('http'):
                        test_url = href
                    else:
                        continue
                    
                    try:
                        print(f"\n  Testing: {test_url}")
                        test_response = await client.get(test_url)
                        print(f"    Status: {test_response.status_code}, Length: {len(test_response.text)}")
                        
                        if test_response.status_code == 200:
                            test_soup = BeautifulSoup(test_response.text, 'html.parser')
                            
                            # Look for actual job listings
                            job_titles = test_soup.find_all(string=lambda text: text and 
                                                          any(word in text.lower() for word in ['scientist', 'engineer', 'data', 'research', 'analyst']) and
                                                          len(text.strip()) > 15 and len(text.strip()) < 80)
                            
                            if job_titles:
                                print(f"    🎯 Found {len(job_titles)} potential job titles!")
                                for i, title in enumerate(job_titles[:3]):
                                    print(f"      {i+1}. {title.strip()}")
                                    
                                # This might be the actual job portal URL
                                print(f"    ✅ Potential job portal URL: {test_url}")
                                
                    except Exception as e:
                        print(f"    ❌ Error testing link: {e}")
                
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(find_job_search_pages())
