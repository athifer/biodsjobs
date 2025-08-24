#!/usr/bin/env python3
"""
Debug the HTML structure of Workday sites to understand why jobs aren't being found
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def debug_workday_html():
    print("DEBUGGING WORKDAY HTML STRUCTURE")
    print("=" * 60)
    
    test_urls = [
        ("Illumina", "https://illumina.wd1.myworkdayjobs.com/illumina-careers"),
        ("Amgen", "https://careers.amgen.com/"),  # This one worked
        ("Pfizer", "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers"),
    ]
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    ) as client:
        
        for company, url in test_urls:
            print(f"\n🔍 {company} - {url}")
            
            try:
                response = await client.get(url)
                print(f"Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"Content Length: {len(response.text)}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for various elements
                print("\n📋 HTML Analysis:")
                
                # Check for automation IDs
                automation_elements = soup.find_all(attrs={'data-automation-id': True})
                print(f"  Elements with data-automation-id: {len(automation_elements)}")
                if automation_elements:
                    automation_ids = [elem.get('data-automation-id') for elem in automation_elements[:10]]
                    print(f"  Sample automation IDs: {automation_ids}")
                
                # Check for job-related text
                job_keywords = ['job', 'position', 'career', 'opening']
                for keyword in job_keywords:
                    elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
                    print(f"  Elements containing '{keyword}': {len(elements)}")
                
                # Look for links
                links = soup.find_all('a', href=True)
                job_links = [link for link in links if any(pattern in link.get('href', '').lower() for pattern in ['/job/', 'posting', 'detail'])]
                print(f"  Total links: {len(links)}")
                print(f"  Job-related links: {len(job_links)}")
                
                # Check for JavaScript/dynamic content indicators
                scripts = soup.find_all('script')
                print(f"  Script tags: {len(scripts)}")
                
                # Look for specific Workday indicators
                workday_indicators = soup.find_all(string=lambda text: text and 'workday' in text.lower())
                print(f"  Workday references: {len(workday_indicators)}")
                
                # Save a snippet of the HTML for manual inspection
                print(f"\n📄 HTML Snippet (first 1000 chars):")
                print("-" * 40)
                print(response.text[:1000])
                print("-" * 40)
                
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_workday_html())
