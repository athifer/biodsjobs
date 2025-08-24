#!/usr/bin/env python3
"""
Debug comprehensive scraper with detailed logging
"""

import asyncio
import httpx
from pathlib import Path
import yaml

async def debug_comprehensive_detailed():
    print("DETAILED COMPREHENSIVE SCRAPER DEBUG")
    print("=" * 60)
    
    company_token = "illumina"
    
    # Load company configuration from companies.yaml
    try:
        current_dir = Path(__file__).parent
        companies_file = current_dir / "companies.yaml"
        with open(companies_file, 'r') as f:
            companies_data = yaml.safe_load(f)
        
        print("✅ Loaded companies.yaml")
        
        # Find the company in comprehensive section
        company_info = None
        if "comprehensive" in companies_data:
            print(f"Found {len(companies_data['comprehensive'])} companies in comprehensive section")
            for company in companies_data["comprehensive"]:
                print(f"  - {company.get('company')} (token: {company.get('token')})")
                if company.get("token") == company_token or company.get("company", "").lower().replace(" ", "") == company_token:
                    company_info = {
                        "name": company.get("company"),
                        "careers_url": company.get("careers_url"),
                        "api_pattern": "general"
                    }
                    print(f"✅ Found matching company: {company_info}")
                    break
        
        if not company_info:
            print(f"❌ Company '{company_token}' not found in comprehensive section")
            return
        
        # Test the URL
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            print(f"\n🔍 Testing URL: {company_info['careers_url']}")
            response = await client.get(company_info['careers_url'], headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)}")
            print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
            
            # Check if it's a JavaScript-heavy site
            if len(response.text) < 10000 and 'workday' in company_info['careers_url']:
                print("✅ Detected JavaScript-heavy Workday site")
                
                # Try API endpoints
                api_endpoints = [
                    f"{company_info['careers_url']}/jobs",
                    f"{company_info['careers_url']}/fs/searchPaginated/jobs",
                    f"{company_info['careers_url']}/searchPaginated/jobs",
                ]
                
                for endpoint in api_endpoints:
                    print(f"\n  Testing API endpoint: {endpoint}")
                    try:
                        for method in ["GET", "POST"]:
                            print(f"    {method} request...")
                            
                            if method == "POST":
                                payload = {
                                    "appliedFacets": {},
                                    "limit": 50,
                                    "offset": 0,
                                    "searchText": ""
                                }
                                api_response = await client.post(endpoint, json=payload, headers={
                                    'Accept': 'application/json',
                                    'Content-Type': 'application/json'
                                })
                            else:
                                api_response = await client.get(endpoint, headers={'Accept': 'application/json'})
                            
                            print(f"      Status: {api_response.status_code}")
                            print(f"      Content-Type: {api_response.headers.get('content-type', 'Unknown')}")
                            print(f"      Content length: {len(api_response.text)}")
                            
                            if api_response.status_code == 200:
                                content_type = api_response.headers.get('content-type', '')
                                if 'json' in content_type:
                                    try:
                                        data = api_response.json()
                                        print(f"      JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                                        
                                        # Look for job data
                                        if isinstance(data, dict):
                                            for key in ['jobPostings', 'jobs', 'searchResults', 'body', 'data']:
                                                if key in data:
                                                    jobs_data = data[key]
                                                    print(f"      🎯 Found key '{key}' with {len(jobs_data) if isinstance(jobs_data, list) else 'non-list'} items")
                                                    if isinstance(jobs_data, list) and len(jobs_data) > 0:
                                                        sample_job = jobs_data[0]
                                                        print(f"         Sample job keys: {list(sample_job.keys()) if isinstance(sample_job, dict) else 'Not a dict'}")
                                                        if isinstance(sample_job, dict):
                                                            title = sample_job.get('title') or sample_job.get('jobTitle') or sample_job.get('name')
                                                            if title:
                                                                print(f"         Sample title: {title}")
                                                    
                                    except Exception as e:
                                        print(f"      ❌ JSON parse error: {e}")
                                else:
                                    print(f"      Content preview: {api_response.text[:200]}...")
                    except Exception as e:
                        print(f"    ❌ {method} error: {e}")
            else:
                print("ℹ️ Not detected as JavaScript-heavy Workday site")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_comprehensive_detailed())
