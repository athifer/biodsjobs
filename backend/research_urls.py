#!/usr/bin/env python3
"""
Research and test actual career page URLs for major biotech companies
"""

import yaml
import asyncio
import httpx
from pathlib import Path

async def validate_url(url: str) -> tuple[bool, int]:
    """Check if a URL is accessible and return status code"""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url)
            return 200 <= response.status_code < 400, response.status_code
    except Exception as e:
        return False, 0

def get_researched_urls():
    """Return researched actual career page URLs"""
    return [
        # Research these actual URLs from company websites
        {
            'company': 'BioMarin',
            'urls_to_test': [
                'https://biomarin.com/careers/',
                'https://careers.biomarin.com/',
                'https://biomarin.wd1.myworkdayjobs.com/en-US/BioMarin',
                'https://boards.greenhouse.io/biomarin'
            ]
        },
        {
            'company': 'Seagen',
            'urls_to_test': [
                'https://www.seagen.com/careers',
                'https://seagen.wd1.myworkdayjobs.com/en-US/Seagen',
                'https://boards.greenhouse.io/seagen',
                'https://careers.seagen.com/'
            ]
        },
        {
            'company': 'Alnylam',
            'urls_to_test': [
                'https://www.alnylam.com/careers',
                'https://alnylam.wd1.myworkdayjobs.com/en-US/Alnylam',
                'https://boards.greenhouse.io/alnylam',
                'https://careers.alnylam.com/'
            ]
        },
        {
            'company': 'Biogen',
            'urls_to_test': [
                'https://www.biogen.com/en_us/careers.html',
                'https://biogen.wd1.myworkdayjobs.com/en-US/Biogen',
                'https://careers.biogen.com/',
                'https://boards.greenhouse.io/biogen'
            ]
        },
        {
            'company': 'Recursion',
            'urls_to_test': [
                'https://www.recursion.com/careers',
                'https://boards.greenhouse.io/recursion',
                'https://boards.greenhouse.io/recursionpharma',
                'https://jobs.lever.co/recursion'
            ]
        },
        {
            'company': 'Tempus',
            'urls_to_test': [
                'https://www.tempus.com/careers/',
                'https://boards.greenhouse.io/tempus',
                'https://tempus.wd5.myworkdayjobs.com/en-US/Tempus',
                'https://jobs.lever.co/tempus'
            ]
        },
        {
            'company': 'Invitae',
            'urls_to_test': [
                'https://www.invitae.com/careers',
                'https://boards.greenhouse.io/invitae',
                'https://invitae.wd1.myworkdayjobs.com/en-US/Invitae',
                'https://careers.invitae.com/'
            ]
        },
        {
            'company': 'Exact Sciences',
            'urls_to_test': [
                'https://www.exactsciences.com/careers',
                'https://exactsciences.wd1.myworkdayjobs.com/Exact_Sciences',
                'https://boards.greenhouse.io/exactsciences',
                'https://careers.exactsciences.com/'
            ]
        },
        {
            'company': 'Merck',
            'urls_to_test': [
                'https://jobs.merck.com/us/en',
                'https://merck.wd1.myworkdayjobs.com/en-US/SearchJobs',
                'https://msd.wd1.myworkdayjobs.com/SearchJobs',
                'https://www.merck.com/careers/'
            ]
        },
        {
            'company': 'Danaher',
            'urls_to_test': [
                'https://jobs.danaher.com/',
                'https://danaher.wd1.myworkdayjobs.com/DanaherCareers',
                'https://boards.greenhouse.io/danaher',
                'https://careers.danaher.com/'
            ]
        }
    ]

async def main():
    """Research and test actual career page URLs"""
    print("RESEARCHING ACTUAL CAREER PAGE URLS")
    print("=" * 60)
    
    companies_to_research = get_researched_urls()
    working_urls = {}
    
    for company_info in companies_to_research:
        company_name = company_info['company']
        print(f"\\n🔍 Researching {company_name}:")
        
        working_url = None
        working_source = None
        
        for url in company_info['urls_to_test']:
            print(f"  Testing: {url}")
            is_valid, status_code = await validate_url(url)
            
            if is_valid:
                print(f"    ✅ WORKING (Status: {status_code})")
                if not working_url:  # Take the first working URL
                    working_url = url
                    # Determine source type
                    if 'greenhouse.io' in url:
                        working_source = 'greenhouse'
                    elif 'myworkdayjobs.com' in url:
                        working_source = 'workday' 
                    elif 'lever.co' in url:
                        working_source = 'lever'
                    else:
                        working_source = 'comprehensive'
            else:
                print(f"    ❌ Not accessible (Status: {status_code})")
        
        if working_url:
            working_urls[company_name] = {
                'url': working_url,
                'source': working_source
            }
            print(f"  🎯 Best URL: {working_url} ({working_source})")
        else:
            print(f"  ⚠️  No working URLs found")
    
    print(f"\\n{'='*60}")
    print("RESEARCH RESULTS")
    print(f"{'='*60}")
    
    if working_urls:
        print("✅ Working URLs found:")
        for company, info in working_urls.items():
            print(f"  {company}: {info['url']} ({info['source']})")
        
        # Save results to a file
        backend_dir = Path(__file__).parent
        results_file = backend_dir / "researched_urls.yaml"
        
        with open(results_file, 'w') as f:
            yaml.dump(working_urls, f, default_flow_style=False, indent=2)
        
        print(f"\\n📝 Results saved to researched_urls.yaml")
    else:
        print("❌ No working URLs found")

if __name__ == "__main__":
    asyncio.run(main())
