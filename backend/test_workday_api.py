#!/usr/bin/env python3
"""
Test different approaches to scrape JavaScript-heavy Workday sites
"""

import asyncio
import httpx
import json
from bs4 import BeautifulSoup

async def test_workday_api_endpoints():
    print("TESTING WORKDAY API ENDPOINTS")
    print("=" * 60)
    
    test_companies = [
        ("Illumina", "https://illumina.wd1.myworkdayjobs.com/illumina-careers"),
        ("Pfizer", "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers"),
    ]
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
        }
    ) as client:
        
        for company, base_url in test_companies:
            print(f"\n🔍 Testing {company} - {base_url}")
            
            # Try common Workday API endpoints
            api_endpoints = [
                f"{base_url}/jobs",
                f"{base_url}/job",
                f"{base_url}/search",
                base_url.replace('.com/', '.com/wday/cxs/') + '/jobs',
                base_url + '/fs/browse',
                base_url + '/refreshFacet/318c8bb6f553100021d223d9780d30be',
                base_url + '/jobs/search',
            ]
            
            for endpoint in api_endpoints:
                try:
                    print(f"  Trying: {endpoint}")
                    response = await client.get(endpoint)
                    print(f"    Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        print(f"    Content-Type: {content_type}")
                        print(f"    Content Length: {len(response.text)}")
                        
                        if 'json' in content_type:
                            try:
                                data = response.json()
                                print(f"    JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                                if isinstance(data, dict) and 'jobPostings' in data:
                                    print(f"    Found job postings: {len(data['jobPostings'])}")
                                elif isinstance(data, dict) and 'total' in data:
                                    print(f"    Total items: {data.get('total')}")
                            except json.JSONDecodeError:
                                print(f"    Invalid JSON response")
                        else:
                            # Check for job-related content in HTML
                            soup = BeautifulSoup(response.text, 'html.parser')
                            job_elements = soup.find_all(string=lambda text: text and 'scientist' in text.lower())
                            print(f"    Elements with 'scientist': {len(job_elements)}")
                            
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            # Try POST request to search endpoint (common Workday pattern)
            try:
                search_url = base_url + '/refreshFacet/318c8bb6f553100021d223d9780d30be'
                search_payload = {
                    "appliedFacets": {},
                    "limit": 20,
                    "offset": 0,
                    "searchText": ""
                }
                
                print(f"\n  Trying POST to search endpoint...")
                response = await client.post(search_url, json=search_payload)
                print(f"    POST Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    POST JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        if isinstance(data, dict) and 'jobPostings' in data:
                            jobs = data['jobPostings']
                            print(f"    Found {len(jobs)} jobs via POST!")
                            if jobs:
                                print(f"    Sample job: {jobs[0].get('title', 'No title')}")
                    except json.JSONDecodeError:
                        print(f"    POST returned non-JSON")
                        
            except Exception as e:
                print(f"    ❌ POST Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_workday_api_endpoints())
