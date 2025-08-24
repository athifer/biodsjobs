#!/usr/bin/env python3
"""
Test different Illumina URLs to see if query parameters make a difference
"""

import asyncio
import httpx
import yaml

async def test_illumina_urls():
    print("TESTING ILLUMINA URLS")
    print("=" * 60)
    
    urls_to_test = [
        "https://illumina.wd1.myworkdayjobs.com/illumina-careers",
        "https://illumina.wd1.myworkdayjobs.com/illumina-careers?_gl=1*1cvyoee*_gcl_aw*R0NMLjE3NTYwNjIyNDUuQ2owS0NRanc4S3JGQmhEVUFSSXNBTXZJQXBZbHpmRGp5V29BczBfTTltV2llOXNwR3FIV1FKSllldGVBdUVqZEpIVFNLRTkxRDVrZl90Z2FBaXBPRUFMd193Y0I.*_gcl_au*MjcwNDYyMDU4LjE3NTU4ODgyNDI.*_ga*MTg5Mjk0MTEwMC4xNzU1ODg4MjQz*_ga_VVVPY8BDYL*czE3NTYwNjIyNDQkbzIkZzAkdDE3NTYwNjIyNDQkajYwJGwwJGgw"
    ]
    
    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    ) as client:
        
        for i, url in enumerate(urls_to_test, 1):
            print(f"\n{i}. Testing: {url[:100]}{'...' if len(url) > 100 else ''}")
            try:
                response = await client.get(url)
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"   Content Length: {len(response.text)}")
                
                # Look for job-related content
                content_lower = response.text.lower()
                job_indicators = ['job', 'career', 'position', 'opening', 'opportunity']
                found_indicators = [word for word in job_indicators if word in content_lower]
                print(f"   Job content indicators: {found_indicators}")
                
                # Look for specific Workday elements
                if 'workday' in content_lower:
                    print("   ✅ Contains Workday content")
                else:
                    print("   ❌ No Workday content detected")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Now checking what our current ingestor would see...")
    
    # Load companies.yaml and check Illumina entry
    with open('companies.yaml', 'r') as f:
        companies_data = yaml.safe_load(f)
    
    # Find Illumina in the data
    for source, companies in companies_data.items():
        for company in companies:
            if company.get('company') == 'Illumina':
                print(f"\nFound Illumina in source: {source}")
                print(f"Current URL: {company.get('careers_url')}")
                print(f"Token: {company.get('token')}")
                break

if __name__ == "__main__":
    asyncio.run(test_illumina_urls())
