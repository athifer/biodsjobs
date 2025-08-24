#!/usr/bin/env python3
"""
Follow redirects and test the actual final URLs
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_with_redirects():
    print("TESTING URLS WITH REDIRECT FOLLOWING")
    print("=" * 60)
    
    test_urls = [
        "https://www.pfizer.com/careers",
        "https://www.modernatx.com/careers"
    ]
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,  # Follow redirects
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    ) as client:
        
        for url in test_urls:
            print(f"\n🔍 Testing: {url}")
            
            try:
                response = await client.get(url)
                print(f"Final URL: {response.url}")
                print(f"Status: {response.status_code}")
                print(f"Content length: {len(response.text)}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for job-related content
                    job_keywords = ['job', 'career', 'position', 'opportunity', 'scientist', 'engineer', 'data']
                    
                    for keyword in job_keywords:
                        elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
                        if elements:
                            print(f"Found {len(elements)} instances of '{keyword}'")
                    
                    # Look for links
                    links = soup.find_all('a', href=True)
                    job_links = [link for link in links if 
                               any(pattern in link.get('href', '').lower() for pattern in 
                                   ['/job', 'position', 'career', 'opportunity'])]
                    print(f"Job-related links: {len(job_links)}")
                    
                    if job_links:
                        print("Sample job links:")
                        for i, link in enumerate(job_links[:3]):
                            text = link.get_text(strip=True)
                            href = link.get('href')
                            print(f"  {i+1}. {text[:50]}... -> {href}")
                    
                    # Look for biotech job titles
                    biotech_elements = soup.find_all(string=lambda text: text and 
                                                    any(word in text.lower() for word in ['scientist', 'engineer', 'data', 'research']) and
                                                    len(text.strip()) > 10 and len(text.strip()) < 100)
                    if biotech_elements:
                        print(f"Biotech job titles found: {len(biotech_elements)}")
                        for i, elem in enumerate(biotech_elements[:3]):
                            print(f"  {i+1}. {elem.strip()}")
                
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_redirects())
