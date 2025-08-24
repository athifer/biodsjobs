#!/usr/bin/env python3
"""
Investigate the Workday jobs endpoint to find the correct API
"""

import asyncio
import httpx
import json

async def investigate_workday_jobs_api():
    print("INVESTIGATING WORKDAY JOBS API")
    print("=" * 60)
    
    test_urls = [
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
        
        for company, base_url in test_urls:
            print(f"\n🔍 {company} - {base_url}")
            
            # Get the jobs endpoint response
            jobs_url = base_url + "/jobs"
            response = await client.get(jobs_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Jobs API response: {json.dumps(data, indent=2)}")
                    
                    # Check if there's an externalSpa URL we should use
                    if 'externalSpa' in data and data['externalSpa']:
                        external_url = data['externalSpa']
                        print(f"\nTrying external SPA URL: {external_url}")
                        
                        ext_response = await client.get(external_url)
                        print(f"External SPA status: {ext_response.status_code}")
                        print(f"External SPA content length: {len(ext_response.text)}")
                        
                        # Look for job content
                        if 'scientist' in ext_response.text.lower():
                            print("✅ Found 'scientist' in external SPA content!")
                            
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
            
            # Try the common Workday GraphQL/API patterns
            api_endpoints = [
                base_url + "/graphql",
                base_url.replace('/illumina-careers', '/wday/cxs/illumina-careers/jobs') if 'illumina' in base_url else base_url.replace('/PfizerCareers', '/wday/cxs/PfizerCareers/jobs'),
                base_url + "/jobPostings",
                base_url + "/postings",
            ]
            
            for endpoint in api_endpoints:
                try:
                    print(f"\nTrying: {endpoint}")
                    response = await client.get(endpoint)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text
                        print(f"Content length: {len(content)}")
                        
                        # Check for job-related content
                        job_indicators = ['scientist', 'engineer', 'data', 'research']
                        found = sum(1 for indicator in job_indicators if indicator in content.lower())
                        print(f"Job content indicators found: {found}/{len(job_indicators)}")
                        
                        if found > 2:
                            print(f"✅ This endpoint looks promising!")
                            # Show a snippet
                            print(f"Content snippet: {content[:500]}...")
                            
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(investigate_workday_jobs_api())
