#!/usr/bin/env python3
"""
Fix Company URLs and Scraper Assignments
Corrects URLs and moves companies to appropriate scrapers based on their actual career pages
"""

import yaml
import asyncio
import httpx
from pathlib import Path

async def validate_url(url: str) -> bool:
    """Check if a URL is accessible"""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.head(url)
            return 200 <= response.status_code < 400
    except Exception:
        return False

def get_corrected_companies():
    """Return companies with corrected URLs and proper scraper assignments"""
    return {
        # Companies that should be moved to WORKDAY
        'workday_corrections': [
            {
                'company': 'Exact Sciences',
                'token': 'exactsciences',
                'careers_url': 'https://exactsciences.wd1.myworkdayjobs.com/Exact_Sciences',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Alnylam',
                'token': 'alnylam',
                'careers_url': 'https://alnylam.wd1.myworkdayjobs.com/en-US/Alnylam-External-Careers',
                'old_source': 'workday'
            },
            {
                'company': 'Amgen',
                'token': 'amgen',
                'careers_url': 'https://careers.amgen.com/en/jobs',
                'old_source': 'workday'
            },
            {
                'company': 'Biogen',
                'token': 'biogen',
                'careers_url': 'https://biogen.wd1.myworkdayjobs.com/en-US/Biogen_All_Jobs',
                'old_source': 'workday'
            },
            {
                'company': 'Merck',
                'token': 'merck',
                'careers_url': 'https://msd.wd1.myworkdayjobs.com/SearchJobs',
                'old_source': 'workday'
            },
            {
                'company': 'BioMarin',
                'token': 'biomarin',
                'careers_url': 'https://biomarin.wd1.myworkdayjobs.com/en-US/BioMarin',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Seagen',
                'token': 'seagen',
                'careers_url': 'https://seagen.wd1.myworkdayjobs.com/en-US/Seagen-Careers',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Danaher',
                'token': 'danaher',
                'careers_url': 'https://danaher.jobs/careers',
                'old_source': 'comprehensive'
            }
        ],
        
        # Companies that should be moved to GREENHOUSE
        'greenhouse_corrections': [
            {
                'company': 'Recursion',
                'token': 'recursion',
                'careers_url': 'https://boards.greenhouse.io/recursionpharma',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Tempus',
                'token': 'tempus',
                'careers_url': 'https://boards.greenhouse.io/tempus',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Invitae',
                'token': 'invitae',
                'careers_url': 'https://boards.greenhouse.io/invitae',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Natera',
                'token': 'natera',
                'careers_url': 'https://boards.greenhouse.io/natera',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Oxford Nanopore',
                'token': 'nanopore',
                'careers_url': 'https://boards.greenhouse.io/nanoporetech',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Personalis',
                'token': 'personalis',
                'careers_url': 'https://boards.greenhouse.io/personalis',
                'old_source': 'comprehensive'
            },
            {
                'company': 'NeoGenomics',
                'token': 'neogenomics',
                'careers_url': 'https://boards.greenhouse.io/neogenomics',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Denali Therapeutics',
                'token': 'denalitx',
                'careers_url': 'https://boards.greenhouse.io/denalitherapeutics',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Mirati Therapeutics',
                'token': 'mirati',
                'careers_url': 'https://boards.greenhouse.io/mirati',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Fate Therapeutics',
                'token': 'fatetherapeutics',
                'careers_url': 'https://boards.greenhouse.io/fatetherapeutics',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Ionis Pharmaceuticals',
                'token': 'ionis',
                'careers_url': 'https://boards.greenhouse.io/ionis',
                'old_source': 'comprehensive'
            }
        ],
        
        # Companies that should be moved to LEVER
        'lever_corrections': [
            {
                'company': 'Owkin',
                'token': 'owkin',
                'careers_url': 'https://jobs.lever.co/owkin',
                'host': 'jobs.lever.co/owkin',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Deep Genomics',
                'token': 'deepgenomics',
                'careers_url': 'https://jobs.lever.co/deepgenomics',
                'host': 'jobs.lever.co/deepgenomics',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Insilico Medicine',
                'token': 'insilicomedicine',
                'careers_url': 'https://jobs.lever.co/insilico',
                'host': 'jobs.lever.co/insilico',
                'old_source': 'comprehensive'
            }
        ],
        
        # Comprehensive URL corrections (staying in comprehensive)
        'comprehensive_corrections': [
            {
                'company': 'Thermo Fisher Scientific',
                'token': 'thermofisher',
                'careers_url': 'https://jobs.thermofisher.com/global/en',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Boston Scientific',
                'token': 'bostonscientific',
                'careers_url': 'https://jobs.bostonscientific.com/careers-home',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Edwards Lifesciences',
                'token': 'edwards',
                'careers_url': 'https://www.edwards.com/careers/job-search',
                'old_source': 'comprehensive'
            },
            {
                'company': 'Charles River Laboratories',
                'token': 'criver',
                'careers_url': 'https://jobs.criver.com/careers-home',
                'old_source': 'comprehensive'
            },
            {
                'company': 'IQVIA',
                'token': 'iqvia',
                'careers_url': 'https://jobs.iqvia.com/careers-home',
                'old_source': 'comprehensive'
            }
        ]
    }

async def main():
    """Fix company URLs and scraper assignments"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    
    print("FIXING COMPANY URLS AND SCRAPER ASSIGNMENTS")
    print("=" * 60)
    
    # Load current companies
    with open(companies_file, 'r') as f:
        current_data = yaml.safe_load(f)
    
    corrections = get_corrected_companies()
    
    # Track changes
    moves_made = []
    url_fixes = []
    
    # Function to remove company from old source
    def remove_company_from_source(company_name, source):
        if source in current_data:
            current_data[source] = [c for c in current_data[source] if c['company'] != company_name]
    
    # Function to add company to new source
    def add_company_to_source(company_data, source):
        if source not in current_data:
            current_data[source] = []
        current_data[source].append(company_data)
    
    # Process Workday corrections
    print("\\nProcessing Workday corrections...")
    for correction in corrections['workday_corrections']:
        company_name = correction['company']
        old_source = correction['old_source']
        
        # Test URL
        is_valid = await validate_url(correction['careers_url'])
        if is_valid:
            print(f"✅ Moving {company_name} to Workday: {correction['careers_url']}")
            
            # Remove from old source
            remove_company_from_source(company_name, old_source)
            
            # Add to workday
            company_entry = {
                'company': correction['company'],
                'token': correction['token'],
                'careers_url': correction['careers_url']
            }
            add_company_to_source(company_entry, 'workday')
            moves_made.append(f"{company_name}: {old_source} → workday")
        else:
            print(f"❌ {company_name}: Invalid Workday URL")
    
    # Process Greenhouse corrections
    print("\\nProcessing Greenhouse corrections...")
    for correction in corrections['greenhouse_corrections']:
        company_name = correction['company']
        old_source = correction['old_source']
        
        # Test URL
        is_valid = await validate_url(correction['careers_url'])
        if is_valid:
            print(f"✅ Moving {company_name} to Greenhouse: {correction['careers_url']}")
            
            # Remove from old source
            remove_company_from_source(company_name, old_source)
            
            # Add to greenhouse
            company_entry = {
                'company': correction['company'],
                'token': correction['token'],
                'careers_url': correction['careers_url']
            }
            add_company_to_source(company_entry, 'greenhouse')
            moves_made.append(f"{company_name}: {old_source} → greenhouse")
        else:
            print(f"❌ {company_name}: Invalid Greenhouse URL")
    
    # Process Lever corrections
    print("\\nProcessing Lever corrections...")
    for correction in corrections['lever_corrections']:
        company_name = correction['company']
        old_source = correction['old_source']
        
        # Test URL
        is_valid = await validate_url(correction['careers_url'])
        if is_valid:
            print(f"✅ Moving {company_name} to Lever: {correction['careers_url']}")
            
            # Remove from old source
            remove_company_from_source(company_name, old_source)
            
            # Add to lever
            company_entry = {
                'company': correction['company'],
                'token': correction['token'],
                'careers_url': correction['careers_url'],
                'host': correction['host']
            }
            add_company_to_source(company_entry, 'lever')
            moves_made.append(f"{company_name}: {old_source} → lever")
        else:
            print(f"❌ {company_name}: Invalid Lever URL")
    
    # Process Comprehensive corrections
    print("\\nProcessing Comprehensive URL corrections...")
    for correction in corrections['comprehensive_corrections']:
        company_name = correction['company']
        
        # Test URL
        is_valid = await validate_url(correction['careers_url'])
        if is_valid:
            print(f"✅ Updating {company_name} URL: {correction['careers_url']}")
            
            # Update URL in comprehensive
            if 'comprehensive' in current_data:
                for company in current_data['comprehensive']:
                    if company['company'] == company_name:
                        old_url = company['careers_url']
                        company['careers_url'] = correction['careers_url']
                        url_fixes.append(f"{company_name}: {old_url} → {correction['careers_url']}")
                        break
        else:
            print(f"❌ {company_name}: Invalid updated URL")
    
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
    print("URL AND SCRAPER FIXES SUMMARY")
    print(f"{'='*60}")
    print(f"Total companies: {total_companies}")
    print(f"Companies moved between scrapers: {len(moves_made)}")
    print(f"URLs updated: {len(url_fixes)}")
    print()
    
    for source, companies in current_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
    
    if moves_made:
        print(f"\\nCompanies moved to correct scrapers:")
        for move in moves_made:
            print(f"  • {move}")
    
    if url_fixes:
        print(f"\\nURLs corrected:")
        for fix in url_fixes:
            print(f"  • {fix}")

if __name__ == "__main__":
    asyncio.run(main())
