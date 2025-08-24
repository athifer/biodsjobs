#!/usr/bin/env python3
"""
Analyze how Amgen works and try to replicate for other companies
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import json
import re

async def analyze_working_sites():
    print("ANALYZING WORKING VS NON-WORKING SITES")
    print("=" * 60)
    
    sites = [
        ("Amgen (Working)", "https://careers.amgen.com/"),
        ("Illumina (Not Working)", "https://illumina.wd1.myworkdayjobs.com/illumina-careers"),
        ("Pfizer (Not Working)", "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers"),
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
        
        for name, url in sites:
            print(f"\n🔍 {name}")
            print(f"URL: {url}")
            
            try:
                response = await client.get(url)
                print(f"Status: {response.status_code}")
                print(f"Content Length: {len(response.text)}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Analyze the structure
                print(f"\nStructure Analysis:")
                
                # Check for different types of job elements
                automation_elements = soup.find_all(attrs={'data-automation-id': True})
                print(f"  Elements with data-automation-id: {len(automation_elements)}")
                
                # Look for job-specific selectors
                job_selectors = [
                    '[data-automation-id*="job"]',
                    '.job-item', '.job-card', '.position', '.opening',
                    '[class*="job"]', '[class*="position"]', '[class*="career"]',
                    'li[role="listitem"]', 'article'
                ]
                
                for selector in job_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"  Found {len(elements)} elements with selector: {selector}")
                        
                        # Show sample content
                        if elements and len(elements[0].get_text(strip=True)) > 20:
                            sample_text = elements[0].get_text(strip=True)[:100]
                            print(f"    Sample: {sample_text}...")
                
                # Look for job links
                all_links = soup.find_all('a', href=True)
                job_links = []
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if any(pattern in href.lower() for pattern in ['/job/', 'position', 'career']) or \
                       any(word in text.lower() for word in ['scientist', 'engineer', 'data', 'research']) and len(text) > 20:
                        job_links.append((href, text[:50]))
                
                print(f"  Job-related links found: {len(job_links)}")
                if job_links:
                    for href, text in job_links[:3]:
                        print(f"    {href} - {text}...")
                
                # Check for AJAX/API indicators
                scripts = soup.find_all('script')
                api_indicators = []
                for script in scripts:
                    script_text = script.get_text()
                    if any(term in script_text for term in ['api', 'ajax', 'fetch', 'xhr', 'graphql']):
                        # Extract potential API URLs
                        urls = re.findall(r'["\']([^"\']*(?:api|search|job|posting)[^"\']*)["\']', script_text)
                        api_indicators.extend(urls[:5])  # Limit to prevent spam
                
                if api_indicators:
                    print(f"  Potential API endpoints found: {len(api_indicators)}")
                    for api_url in api_indicators[:3]:
                        print(f"    {api_url}")
                
                # Special analysis for Amgen (working site)
                if "amgen" in url.lower():
                    print(f"\n🎯 AMGEN SPECIAL ANALYSIS:")
                    
                    # Look for the actual job content structure
                    job_containers = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'job|position|career', re.I))
                    print(f"  Job containers by class: {len(job_containers)}")
                    
                    # Check for automation IDs that our scraper might be finding
                    found_automation_ids = set()
                    for elem in soup.find_all(attrs={'data-automation-id': True}):
                        aid = elem.get('data-automation-id')
                        if any(pattern in aid.lower() for pattern in ['job', 'posting', 'searchresult', 'listitem', 'card']):
                            found_automation_ids.add(aid)
                    
                    if found_automation_ids:
                        print(f"  Working automation IDs: {list(found_automation_ids)}")
                    
                    # Try to find the exact elements our scraper would detect
                    workday_style_elements = soup.find_all(['li', 'div', 'tr'], attrs={
                        'data-automation-id': lambda x: x and any(pattern in x.lower() for pattern in 
                            ['job', 'posting', 'searchresult', 'listitem', 'card'])
                    })
                    print(f"  Elements our scraper would find: {len(workday_style_elements)}")
                    
                    if workday_style_elements:
                        for i, elem in enumerate(workday_style_elements[:2]):
                            print(f"    Element {i+1}: {elem.get('data-automation-id')}")
                            title_text = elem.get_text(strip=True)[:100]
                            print(f"      Content: {title_text}...")
                
            except Exception as e:
                print(f"❌ Error analyzing {name}: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_working_sites())
