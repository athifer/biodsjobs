#!/usr/bin/env python3
"""
Try to find the correct Workday API pattern by testing common structures
"""

import asyncio
import httpx
import json

async def test_workday_api_patterns():
    print("TESTING KNOWN WORKDAY API PATTERNS")
    print("=" * 60)
    
    test_companies = [
        {
            "name": "Illumina",
            "base": "https://illumina.wd1.myworkdayjobs.com/illumina-careers",
            "site_id": "illumina",
            "job_site": "illumina-careers"
        },
        {
            "name": "Pfizer", 
            "base": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers",
            "site_id": "pfizer",
            "job_site": "PfizerCareers"
        }
    ]
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }
    ) as client:
        
        for company in test_companies:
            print(f"\n🔍 Testing {company['name']}")
            
            # Common Workday API patterns I've seen
            api_patterns = [
                # Pattern 1: Using job site name in path
                f"https://{company['site_id']}.wd1.myworkdayjobs.com/{company['job_site']}/refreshFacet/318c8bb6f553100021d223d9780d30be",
                
                # Pattern 2: Different facet IDs
                f"{company['base']}/refreshFacet/318c8bb6f553100021d223d9780d30be",
                f"{company['base']}/refreshFacet/1f8ba41731f1472b9c48efc76ac35267", 
                f"{company['base']}/refreshFacet/9c3a5b8e2d5e4c5ab7a8e0c8b7e5d4f3",
                
                # Pattern 3: Jobs API
                f"{company['base']}/jobPostings",
                f"{company['base']}/api/jobPostings",
                f"{company['base']}/api/v1/jobs",
                
                # Pattern 4: CXS endpoints
                f"https://{company['site_id']}.wd1.myworkdayjobs.com/wday/cxs/{company['job_site']}/jobs",
                f"https://{company['site_id']}.wd1.myworkdayjobs.com/wday/cxs/{company['job_site']}/refreshFacet/318c8bb6f553100021d223d9780d30be",
            ]
            
            for pattern in api_patterns:
                try:
                    print(f"  Testing: {pattern}")
                    
                    # Try both GET and POST
                    for method in ['GET', 'POST']:
                        payload = None
                        if method == 'POST':
                            payload = {
                                "appliedFacets": {},
                                "limit": 20,
                                "offset": 0,
                                "searchText": ""
                            }
                        
                        try:
                            if method == 'POST' and payload:
                                response = await client.post(pattern, json=payload)
                            else:
                                response = await client.get(pattern)
                            
                            if response.status_code == 200:
                                content_type = response.headers.get('content-type', '')
                                print(f"    ✅ {method} {response.status_code} - {content_type}")
                                
                                if 'json' in content_type:
                                    try:
                                        data = response.json()
                                        if isinstance(data, dict):
                                            print(f"      JSON keys: {list(data.keys())}")
                                            
                                            # Look for job data
                                            job_fields = ['jobPostings', 'jobs', 'searchResults', 'data', 'body']
                                            for field in job_fields:
                                                if field in data:
                                                    jobs_data = data[field]
                                                    if isinstance(jobs_data, list):
                                                        print(f"      🎯 FOUND {len(jobs_data)} items in '{field}'!")
                                                        if jobs_data:
                                                            sample = jobs_data[0]
                                                            if isinstance(sample, dict):
                                                                print(f"         Sample keys: {list(sample.keys())}")
                                                                title = sample.get('title') or sample.get('jobTitle') or sample.get('name')
                                                                if title:
                                                                    print(f"         Sample title: {title}")
                                                        return data  # Found working endpoint!
                                                    elif isinstance(jobs_data, dict) and 'children' in jobs_data:
                                                        children = jobs_data['children']
                                                        print(f"      🎯 FOUND nested structure with {len(children)} children!")
                                                        
                                    except json.JSONDecodeError:
                                        print(f"      ❌ Invalid JSON")
                                else:
                                    # Check for job content in non-JSON response
                                    content = response.text.lower()
                                    job_indicators = ['scientist', 'engineer', 'data', 'research']
                                    found_indicators = sum(1 for indicator in job_indicators if indicator in content)
                                    if found_indicators > 0:
                                        print(f"      🎯 Found {found_indicators} job indicators in response!")
                                        print(f"      Content length: {len(response.text)}")
                            
                            elif response.status_code != 404:
                                print(f"    ⚠️  {method} {response.status_code}")
                                
                        except Exception as e:
                            if "422" not in str(e):  # Skip common validation errors
                                print(f"    ❌ {method} Error: {e}")
                
                except Exception as e:
                    print(f"  ❌ Pattern error: {e}")

if __name__ == "__main__":
    asyncio.run(test_workday_api_patterns())
