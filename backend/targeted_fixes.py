#!/usr/bin/env python3
"""
Targeted fixes for specific high-priority companies showing 0 jobs
"""

import yaml
import asyncio
import httpx
from pathlib import Path

async def validate_url(url: str) -> bool:
    """Check if a URL is accessible"""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(url)
            return 200 <= response.status_code < 400
    except Exception:
        return False

def get_priority_fixes():
    """Return high-priority company fixes based on known working URLs"""
    return [
        # Workday companies with correct URLs
        {
            'company': 'BioMarin',
            'token': 'biomarin',
            'careers_url': 'https://biomarin.wd1.myworkdayjobs.com/en-US/BioMarin_External',
            'source': 'workday',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Seagen',
            'token': 'seagen', 
            'careers_url': 'https://seagen.wd1.myworkdayjobs.com/en-US/Seagen_External',
            'source': 'workday',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Alnylam',
            'token': 'alnylam',
            'careers_url': 'https://alnylam.wd1.myworkdayjobs.com/en-US/Alnylam-External',
            'source': 'workday',
            'old_source': 'workday'
        },
        {
            'company': 'Biogen',
            'token': 'biogen',
            'careers_url': 'https://biogen.wd1.myworkdayjobs.com/en-US/Biogen-External',
            'source': 'workday',
            'old_source': 'workday'
        },
        
        # Greenhouse companies
        {
            'company': 'Recursion',
            'token': 'recursion',
            'careers_url': 'https://boards.greenhouse.io/recursionpharma',
            'source': 'greenhouse',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Tempus',
            'token': 'tempus',
            'careers_url': 'https://boards.greenhouse.io/tempus',
            'source': 'greenhouse', 
            'old_source': 'comprehensive'
        },
        {
            'company': 'Invitae',
            'token': 'invitae',
            'careers_url': 'https://boards.greenhouse.io/invitae',
            'source': 'greenhouse',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Denali Therapeutics',
            'token': 'denali',
            'careers_url': 'https://boards.greenhouse.io/denalitherapeutics',
            'source': 'greenhouse',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Mirati Therapeutics',
            'token': 'mirati', 
            'careers_url': 'https://boards.greenhouse.io/mirati',
            'source': 'greenhouse',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Ionis Pharmaceuticals',
            'token': 'ionis',
            'careers_url': 'https://boards.greenhouse.io/ionis',
            'source': 'greenhouse',
            'old_source': 'comprehensive'
        },
        
        # Lever companies
        {
            'company': 'Owkin',
            'token': 'owkin',
            'careers_url': 'https://jobs.lever.co/owkin',
            'host': 'jobs.lever.co/owkin',
            'source': 'lever',
            'old_source': 'comprehensive'
        },
        {
            'company': 'Insilico Medicine',
            'token': 'insilico',
            'careers_url': 'https://jobs.lever.co/insilico',
            'host': 'jobs.lever.co/insilico',
            'source': 'lever',
            'old_source': 'comprehensive'
        }
    ]

async def main():
    """Apply targeted fixes for priority companies"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    
    print("TARGETED FIXES FOR HIGH-PRIORITY COMPANIES")
    print("=" * 60)
    
    # Load current companies
    with open(companies_file, 'r') as f:
        current_data = yaml.safe_load(f)
    
    fixes = get_priority_fixes()
    
    # Function to remove company from old source
    def remove_company_from_source(company_name, source):
        if source in current_data:
            original_count = len(current_data[source])
            current_data[source] = [c for c in current_data[source] if c['company'] != company_name]
            new_count = len(current_data[source])
            return original_count > new_count
        return False
    
    # Function to add company to new source
    def add_company_to_source(company_data, source):
        if source not in current_data:
            current_data[source] = []
        current_data[source].append(company_data)
    
    successful_fixes = []
    failed_fixes = []
    
    # Process each fix
    for fix in fixes:
        company_name = fix['company']
        print(f"\\nTesting {company_name}: {fix['careers_url']}")
        
        # Test the URL first
        is_valid = await validate_url(fix['careers_url'])
        
        if is_valid:
            print(f"✅ {company_name} URL is valid")
            
            # Remove from old source
            removed = remove_company_from_source(company_name, fix['old_source'])
            
            if removed or fix['source'] == fix['old_source']:
                # Add to new source
                company_entry = {
                    'company': fix['company'],
                    'token': fix['token'],
                    'careers_url': fix['careers_url']
                }
                
                # Add host field for lever companies
                if fix['source'] == 'lever' and 'host' in fix:
                    company_entry['host'] = fix['host']
                
                add_company_to_source(company_entry, fix['source'])
                
                action = "Updated" if fix['source'] == fix['old_source'] else f"Moved from {fix['old_source']} to {fix['source']}"
                successful_fixes.append(f"{company_name}: {action}")
                print(f"   {action}")
            else:
                print(f"   ⚠️  Company not found in {fix['old_source']}")
        else:
            print(f"❌ {company_name} URL is not accessible")
            failed_fixes.append(company_name)
    
    # Sort companies within each source
    for source in current_data:
        if current_data[source]:
            current_data[source].sort(key=lambda x: x['company'])
    
    # Save updated file
    with open(companies_file, 'w') as f:
        yaml.dump(current_data, f, default_flow_style=False, sort_keys=False,
                 allow_unicode=True, indent=2)
    
    # Print summary
    total_companies = sum(len(companies) for companies in current_data.values())
    
    print(f"\\n{'='*60}")
    print("TARGETED FIXES SUMMARY")
    print(f"{'='*60}")
    print(f"Total companies: {total_companies}")
    print(f"Successful fixes: {len(successful_fixes)}")
    print(f"Failed fixes: {len(failed_fixes)}")
    print()
    
    for source, companies in current_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
    
    if successful_fixes:
        print(f"\\n✅ Successful fixes:")
        for fix in successful_fixes:
            print(f"  • {fix}")
    
    if failed_fixes:
        print(f"\\n❌ Failed fixes:")
        for fix in failed_fixes:
            print(f"  • {fix}")

if __name__ == "__main__":
    asyncio.run(main())
