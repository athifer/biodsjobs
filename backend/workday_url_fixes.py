#!/usr/bin/env python3
"""
Comprehensive Workday URL validation and correction
Check all Workday companies and fix any broken URLs
"""

import yaml
import asyncio
import httpx
from pathlib import Path

async def validate_url(url: str) -> tuple[bool, int, str]:
    """Check if a URL is accessible and return status code and any redirect"""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url)
            return 200 <= response.status_code < 400, response.status_code, str(response.url)
    except Exception as e:
        return False, 0, str(e)

def get_workday_url_tests():
    """Return URLs to test for major Workday companies"""
    return {
        'Illumina': [
            'https://illumina.wd1.myworkdayjobs.com/illumina-careers',
            'https://illumina.wd1.myworkdayjobs.com/illumina-careers/',
            'https://careers.illumina.com/',
            'https://www.illumina.com/careers.html'
        ],
        'Amgen': [
            'https://careers.amgen.com/en/jobs',
            'https://amgen.wd1.myworkdayjobs.com/en-US/amgen-careers',
            'https://careers.amgen.com/',
            'https://www.amgen.com/careers'
        ],
        'Bristol Myers Squibb': [
            'https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS',
            'https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS/',
            'https://careers.bms.com/',
            'https://www.bms.com/careers.html'
        ],
        'Gilead': [
            'https://gilead.wd1.myworkdayjobs.com/gileadcareers',
            'https://gilead.wd1.myworkdayjobs.com/gileadcareers/',
            'https://careers.gilead.com/',
            'https://www.gilead.com/careers'
        ],
        'Moderna': [
            'https://modernatx.wd1.myworkdayjobs.com/M_tx',
            'https://modernatx.wd1.myworkdayjobs.com/M_tx/',
            'https://careers.modernatx.com/',
            'https://www.modernatx.com/careers'
        ],
        'Pfizer': [
            'https://pfizer.wd1.myworkdayjobs.com/PfizerCareers',
            'https://pfizer.wd1.myworkdayjobs.com/PfizerCareers/',
            'https://careers.pfizer.com/',
            'https://www.pfizer.com/careers'
        ],
        'Vertex': [
            'https://vrtx.wd501.myworkdayjobs.com/vertex_careers',
            'https://vrtx.wd501.myworkdayjobs.com/vertex_careers/',
            'https://careers.vrtx.com/',
            'https://www.vrtx.com/careers'
        ]
    }

async def main():
    """Test and fix Workday company URLs"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    
    print("COMPREHENSIVE WORKDAY URL VALIDATION")
    print("=" * 60)
    
    # Load current companies
    with open(companies_file, 'r') as f:
        current_data = yaml.safe_load(f)
    
    test_urls = get_workday_url_tests()
    corrections = {}
    
    # Test URLs for each company
    for company_name, urls_to_test in test_urls.items():
        print(f"\\n🔍 Testing {company_name}:")
        
        best_url = None
        best_source = None
        
        for url in urls_to_test:
            print(f"  Testing: {url}")
            is_valid, status_code, final_url = await validate_url(url)
            
            if is_valid:
                print(f"    ✅ WORKING (Status: {status_code})")
                if final_url != url:
                    print(f"    🔄 Redirects to: {final_url}")
                
                if not best_url:  # Take the first working URL
                    best_url = url
                    # Determine best source type
                    if 'myworkdayjobs.com' in url:
                        best_source = 'workday'
                    else:
                        best_source = 'comprehensive'
            else:
                print(f"    ❌ Failed (Status: {status_code})")
        
        if best_url:
            corrections[company_name] = {
                'url': best_url,
                'source': best_source
            }
            print(f"  🎯 Best URL: {best_url} ({best_source})")
        else:
            print(f"  ⚠️  No working URLs found")
    
    # Apply corrections
    print(f"\\n{'='*60}")
    print("APPLYING CORRECTIONS")
    print(f"{'='*60}")
    
    corrections_applied = []
    
    for company_name, correction in corrections.items():
        new_url = correction['url']
        target_source = correction['source']
        
        # Find the company in current data
        found = False
        for source in current_data:
            for company in current_data[source]:
                if company['company'] == company_name:
                    old_url = company['careers_url']
                    if old_url != new_url:
                        company['careers_url'] = new_url
                        corrections_applied.append(f"{company_name}: {old_url} → {new_url}")
                        print(f"✅ Updated {company_name}: {new_url}")
                    else:
                        print(f"ℹ️  {company_name}: URL already correct")
                    found = True
                    break
            if found:
                break
    
    # Sort companies within each source
    for source in current_data:
        if current_data[source]:
            current_data[source].sort(key=lambda x: x['company'])
    
    # Save updated file
    if corrections_applied:
        with open(companies_file, 'w') as f:
            yaml.dump(current_data, f, default_flow_style=False, sort_keys=False,
                     allow_unicode=True, indent=2)
        print(f"\\n💾 Saved {len(corrections_applied)} URL corrections")
    else:
        print(f"\\n✅ No corrections needed - all URLs are working")
    
    # Print summary
    total_companies = sum(len(companies) for companies in current_data.values())
    
    print(f"\\n{'='*60}")
    print("WORKDAY URL VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total companies: {total_companies}")
    print(f"Companies tested: {len(test_urls)}")
    print(f"Corrections applied: {len(corrections_applied)}")
    
    if corrections_applied:
        print(f"\\n🔧 URL corrections:")
        for correction in corrections_applied:
            print(f"  • {correction}")

if __name__ == "__main__":
    asyncio.run(main())
