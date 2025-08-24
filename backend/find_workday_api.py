#!/usr/bin/env python3
"""
Find the correct Workday API pattern by exploring different POST endpoints
"""

import asyncio
import httpx
import json

async def find_workday_api():
    print("FINDING WORKDAY API ENDPOINTS")
    print("=" * 60)
    
    # Test with Illumina first
    base_url = "https://illumina.wd1.myworkdayjobs.com/illumina-careers"
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Origin': 'https://illumina.wd1.myworkdayjobs.com',
            'Referer': base_url,
        }
    ) as client:
        
        print(f"🔍 Testing Illumina API endpoints")
        
        # Try different API patterns common in Workday
        api_tests = [
            # Standard search endpoint
            {
                'url': base_url + '/refreshFacet/318c8bb6f553100021d223d9780d30be',
                'method': 'POST',
                'payload': {
                    "appliedFacets": {},
                    "limit": 20,
                    "offset": 0,
                    "searchText": ""
                }
            },
            # Alternative facet ID
            {
                'url': base_url + '/refreshFacet/318c8bb6f553100021d223d9780d30be',
                'method': 'POST', 
                'payload': {
                    "appliedFacets": {},
                    "limit": 100,
                    "offset": 0
                }
            },
            # Try without specific facet ID
            {
                'url': base_url + '/refreshFacet',
                'method': 'POST',
                'payload': {
                    "appliedFacets": {},
                    "limit": 20,
                    "offset": 0
                }
            },
            # Try with different search structure
            {
                'url': base_url + '/search',
                'method': 'POST',
                'payload': {
                    "searchText": "",
                    "limit": 20,
                    "offset": 0
                }
            }
        ]
        
        for i, test in enumerate(api_tests, 1):
            print(f"\n{i}. Testing {test['method']} {test['url']}")
            print(f"   Payload: {json.dumps(test['payload'], indent=4)}")
            
            try:
                if test['method'] == 'POST':
                    response = await client.post(test['url'], json=test['payload'])
                else:
                    response = await client.get(test['url'])
                
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"   Content Length: {len(response.text)}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   JSON Response: {json.dumps(data, indent=4)[:500]}...")
                            
                            # Look for job data in response
                            if isinstance(data, dict):
                                if 'jobPostings' in data:
                                    jobs = data['jobPostings']
                                    print(f"   ✅ FOUND {len(jobs)} JOBS!")
                                    if jobs:
                                        sample_job = jobs[0]
                                        print(f"   Sample job title: {sample_job.get('title', 'No title')}")
                                        print(f"   Sample job keys: {list(sample_job.keys())}")
                                        return data  # Found it!
                                elif 'total' in data:
                                    print(f"   Total results: {data.get('total')}")
                                elif 'body' in data:
                                    print(f"   Has body field, checking content...")
                                    body = data['body']
                                    if isinstance(body, dict) and 'children' in body:
                                        print(f"   Body has children: {len(body['children'])}")
                                    
                        except json.JSONDecodeError:
                            print(f"   ❌ Invalid JSON")
                    else:
                        # Check HTML/XML content
                        if 'scientist' in response.text.lower():
                            print(f"   ✅ Contains 'scientist' keyword")
                        print(f"   Content preview: {response.text[:200]}...")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Try to get the page and look for hidden API endpoints in JavaScript
        print(f"\n5. Analyzing page JavaScript for API endpoints...")
        try:
            response = await client.get(base_url)
            if response.status_code == 200:
                # Look for API patterns in the HTML/JS
                content = response.text
                
                # Common patterns to find API endpoints
                patterns = [
                    'refreshFacet/',
                    'jobPostings',
                    '/search',
                    'api/',
                    'graphql',
                    'wday/',
                    'cxs/'
                ]
                
                for pattern in patterns:
                    if pattern in content:
                        print(f"   Found pattern '{pattern}' in page content")
                        
        except Exception as e:
            print(f"   ❌ Error analyzing page: {e}")

if __name__ == "__main__":
    asyncio.run(find_workday_api())
