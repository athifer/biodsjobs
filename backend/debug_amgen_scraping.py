#!/usr/bin/env python3
"""
Test what our Workday scraper is actually finding for Amgen
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def debug_amgen_scraping():
    print("DEBUGGING AMGEN WORKDAY SCRAPING")
    print("=" * 60)
    
    # This is what our workday scraper uses for Amgen
    url = "https://careers.amgen.com/"
    
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
        
        print(f"Testing: {url}")
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Replicate exactly what our scraper does:
        
        print("\n1. Strategy 1: Look for automation ID job cards")
        job_cards = soup.find_all(['li', 'div', 'tr'], attrs={
            'data-automation-id': lambda x: x and any(pattern in x.lower() for pattern in 
                ['job', 'posting', 'searchresult', 'listitem', 'card'])
        })
        print(f"Found {len(job_cards)} job cards with automation IDs")
        
        print("\n2. Strategy 1b: Alternative automation ID selectors")
        if not job_cards:
            job_cards = soup.select('[data-automation-id*="job"]')
            print(f"Found {len(job_cards)} with [data-automation-id*=\"job\"]")
        
        print("\n3. Strategy 1c: CSS selectors")
        if not job_cards:
            job_cards = soup.select('.css-1d6urnp, .css-k008qs, [class*="job"], [class*="posting"]')
            print(f"Found {len(job_cards)} with CSS selectors")
            if job_cards:
                for i, card in enumerate(job_cards[:3]):
                    print(f"  Card {i+1}: class='{card.get('class')}', text='{card.get_text(strip=True)[:100]}...'")
        
        print("\n4. Strategy 2: Look for job-related links")
        if not job_cards:
            all_links = soup.find_all('a', href=True)
            job_cards = [link for link in all_links if 
                       any(pattern in link.get('href', '').lower() for pattern in 
                           ['/job/', 'jobdetail', 'posting', 'position']) and
                       len(link.get_text(strip=True)) > 10]
            print(f"Found {len(job_cards)} potential job links")
            if job_cards:
                for i, card in enumerate(job_cards[:3]):
                    print(f"  Link {i+1}: href='{card.get('href')}', text='{card.get_text(strip=True)[:50]}...'")
        
        print("\n5. Strategy 3: Look for biotech keywords")
        if not job_cards:
            import re
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
            
            if job_cards:
                for i, card in enumerate(job_cards[:3]):
                    print(f"  Keyword element {i+1}: tag='{card.name}', text='{card.get_text(strip=True)[:100]}...'")
        
        print(f"\n6. Processing found elements ({len(job_cards)} total)")
        
        processed_jobs = 0
        for i, job_card in enumerate(job_cards[:30]):
            try:
                # Extract title (replicate scraper logic)
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
                        if len(title) > 5:
                            break
                
                if not title or len(title) < 5:
                    title = job_card.get_text(strip=True)
                    lines = [line.strip() for line in title.split('\n') if line.strip()]
                    title = lines[0] if lines else ""
                
                # Filter for biotech relevance
                biotech_keywords = [
                    'scientist', 'research', 'data', 'computational', 'bioinformatics', 
                    'clinical', 'genomics', 'biostatistics', 'biologist', 'engineer',
                    'analyst', 'director', 'manager', 'associate', 'principal', 'lead',
                    'machine learning', 'ai', 'software', 'informatics', 'statistics'
                ]
                
                if title and len(title) > 5 and any(keyword.lower() in title.lower() for keyword in biotech_keywords):
                    processed_jobs += 1
                    print(f"  ✅ Job {processed_jobs}: {title[:50]}...")
                elif title:
                    print(f"  ❌ Filtered out: {title[:50]}... (not biotech relevant)")
                    
            except Exception as e:
                print(f"  ❌ Error processing element {i}: {e}")
        
        print(f"\nFinal result: {processed_jobs} biotech-relevant jobs found")

if __name__ == "__main__":
    asyncio.run(debug_amgen_scraping())
