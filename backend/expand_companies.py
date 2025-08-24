#!/usr/bin/env python3
"""
Expand Companies Database with Additional Biotech/Pharma Companies
Adds major publicly traded, private, and startup companies not currently in the list
"""

import yaml
import asyncio
import httpx
from pathlib import Path

async def validate_url(url: str) -> bool:
    """Check if a URL is accessible"""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.head(url)
            return 200 <= response.status_code < 400
    except Exception:
        return False

def get_additional_companies():
    """Return list of additional biotech/pharma companies to add"""
    return [
        # Major Publicly Traded Pharma Companies
        {
            'company': 'Roche',
            'token': 'roche',
            'careers_url': 'https://careers.roche.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Novartis',
            'token': 'novartis', 
            'careers_url': 'https://www.novartis.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Sanofi',
            'token': 'sanofi',
            'careers_url': 'https://en.sanofi.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'GSK',
            'token': 'gsk',
            'careers_url': 'https://www.gsk.com/en-gb/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'AstraZeneca',
            'token': 'astrazeneca',
            'careers_url': 'https://careers.astrazeneca.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Bayer',
            'token': 'bayer',
            'careers_url': 'https://career.bayer.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Takeda',
            'token': 'takeda',
            'careers_url': 'https://www.takeda.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'BioNTech',
            'token': 'biontech',
            'careers_url': 'https://biontech.de/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Regeneron',
            'token': 'regeneron',
            'careers_url': 'https://careers.regeneron.com/',
            'source': 'workday'
        },
        {
            'company': 'Alexion',
            'token': 'alexion',
            'careers_url': 'https://alexion.wd1.myworkdayjobs.com/en-US/Alexion_External',
            'source': 'workday'
        },
        
        # Major Biotech Companies on Greenhouse
        {
            'company': 'Moderna',
            'token': 'modernatx',
            'careers_url': 'https://boards.greenhouse.io/modernatx',
            'source': 'greenhouse'
        },
        {
            'company': 'BioMarin',
            'token': 'biomarin',
            'careers_url': 'https://boards.greenhouse.io/biomarin',
            'source': 'greenhouse'
        },
        {
            'company': 'Seagen',
            'token': 'seagen',
            'careers_url': 'https://boards.greenhouse.io/seagen',
            'source': 'greenhouse'
        },
        {
            'company': 'Exact Sciences',
            'token': 'exactsciences',
            'careers_url': 'https://boards.greenhouse.io/exactsciences',
            'source': 'greenhouse'
        },
        {
            'company': 'Danaher',
            'token': 'danaher',
            'careers_url': 'https://boards.greenhouse.io/danaher',
            'source': 'greenhouse'
        },
        {
            'company': 'Thermo Fisher Scientific',
            'token': 'thermofisher',
            'careers_url': 'https://boards.greenhouse.io/thermofisher',
            'source': 'greenhouse'
        },
        
        # Emerging Biotech Companies
        {
            'company': 'Sana Biotechnology',
            'token': 'sanabiotechnology',
            'careers_url': 'https://boards.greenhouse.io/sanabiotechnology',
            'source': 'greenhouse'
        },
        {
            'company': 'Allogene Therapeutics',
            'token': 'allogene',
            'careers_url': 'https://boards.greenhouse.io/allogene',
            'source': 'greenhouse'
        },
        {
            'company': 'Kite Pharma',
            'token': 'kitepharma',
            'careers_url': 'https://boards.greenhouse.io/kitepharma',
            'source': 'greenhouse'
        },
        {
            'company': 'Blueprint Medicines',
            'token': 'blueprintmedicines',
            'careers_url': 'https://boards.greenhouse.io/blueprintmedicines',
            'source': 'greenhouse'
        },
        {
            'company': 'Relay Therapeutics',
            'token': 'relaytx',
            'careers_url': 'https://boards.greenhouse.io/relaytx',
            'source': 'greenhouse'
        },
        {
            'company': 'Denali Therapeutics',
            'token': 'denalitherapeutics',
            'careers_url': 'https://boards.greenhouse.io/denalitherapeutics',
            'source': 'greenhouse'
        },
        {
            'company': 'Alnylam Pharmaceuticals',
            'token': 'alnylam',
            'careers_url': 'https://boards.greenhouse.io/alnylam',
            'source': 'greenhouse'
        },
        
        # Gene Therapy & Cell Therapy Companies
        {
            'company': 'Editas Medicine',
            'token': 'editasmedicine',
            'careers_url': 'https://boards.greenhouse.io/editasmedicine',
            'source': 'greenhouse'
        },
        {
            'company': 'CRISPR Therapeutics',
            'token': 'crisprtx',
            'careers_url': 'https://boards.greenhouse.io/crisprtx',
            'source': 'greenhouse'
        },
        {
            'company': 'Intellia Therapeutics',
            'token': 'intelliatx',
            'careers_url': 'https://boards.greenhouse.io/intelliatx',
            'source': 'greenhouse'
        },
        {
            'company': 'Beam Therapeutics',
            'token': 'beamtx',
            'careers_url': 'https://boards.greenhouse.io/beamtx',
            'source': 'greenhouse'
        },
        {
            'company': 'Prime Medicine',
            'token': 'primemedicine',
            'careers_url': 'https://boards.greenhouse.io/primemedicine',
            'source': 'greenhouse'
        },
        
        # AI/Computational Biology Companies
        {
            'company': 'Recursion',
            'token': 'recursion',
            'careers_url': 'https://jobs.lever.co/recursion',
            'source': 'lever',
            'host': 'jobs.lever.co/recursion'
        },
        {
            'company': 'Tempus',
            'token': 'tempus',
            'careers_url': 'https://jobs.lever.co/tempus',
            'source': 'lever',
            'host': 'jobs.lever.co/tempus'
        },
        {
            'company': 'Veracyte',
            'token': 'veracyte',
            'careers_url': 'https://jobs.lever.co/veracyte',
            'source': 'lever',
            'host': 'jobs.lever.co/veracyte'
        },
        {
            'company': 'Flatiron Health',
            'token': 'flatiron',
            'careers_url': 'https://flatiron.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Veeva Systems',
            'token': 'veeva',
            'careers_url': 'https://careers.veeva.com/',
            'source': 'comprehensive'
        },
        
        # Oncology Focused Companies
        {
            'company': 'Mirati Therapeutics',
            'token': 'mirati',
            'careers_url': 'https://boards.greenhouse.io/mirati',
            'source': 'greenhouse'
        },
        {
            'company': 'Exelixis',
            'token': 'exelixis',
            'careers_url': 'https://www.exelixis.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Guardant Health',
            'token': 'guardant',
            'careers_url': 'https://boards.greenhouse.io/guardant',
            'source': 'greenhouse'
        },
        {
            'company': 'Foundation Medicine',
            'token': 'foundationmedicine',
            'careers_url': 'https://careers.foundationmedicine.com/',
            'source': 'comprehensive'
        },
        
        # Emerging Startups and Private Companies
        {
            'company': 'NotCo',
            'token': 'notco',
            'careers_url': 'https://boards.greenhouse.io/notco',
            'source': 'greenhouse'
        },
        {
            'company': 'Memphis Meats',
            'token': 'memphismeats',
            'careers_url': 'https://jobs.lever.co/memphismeats',
            'source': 'lever',
            'host': 'jobs.lever.co/memphismeats'
        },
        {
            'company': 'Impossible Foods',
            'token': 'impossiblefoods',
            'careers_url': 'https://impossiblefoods.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Perfect Day',
            'token': 'perfectday',
            'careers_url': 'https://jobs.lever.co/perfectday',
            'source': 'lever',
            'host': 'jobs.lever.co/perfectday'
        },
        
        # Contract Research Organizations (CROs)
        {
            'company': 'IQVIA',
            'token': 'iqvia',
            'careers_url': 'https://jobs.iqvia.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Syneos Health',
            'token': 'syneoshealth',
            'careers_url': 'https://syneoshealth.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'PPD',
            'token': 'ppd',
            'careers_url': 'https://www.ppd.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Parexel',
            'token': 'parexel',
            'careers_url': 'https://careers.parexel.com/',
            'source': 'comprehensive'
        },
        
        # Medical Device Companies
        {
            'company': 'Medtronic',
            'token': 'medtronic',
            'careers_url': 'https://jobs.medtronic.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Abbott',
            'token': 'abbott',
            'careers_url': 'https://www.abbott.com/careers.html',
            'source': 'comprehensive'
        },
        {
            'company': 'Boston Scientific',
            'token': 'bostonscientific',
            'careers_url': 'https://jobs.bostonscientific.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Stryker',
            'token': 'stryker',
            'careers_url': 'https://careers.stryker.com/',
            'source': 'comprehensive'
        }
    ]

async def main():
    """Add additional companies to the master file"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    
    print("Adding additional biotech/pharma companies...")
    print("=" * 60)
    
    # Load current companies
    with open(companies_file, 'r') as f:
        current_data = yaml.safe_load(f)
    
    # Get current company names (normalized)
    current_companies = set()
    for source, companies in current_data.items():
        for company in companies:
            name = company.get('company', '').lower().strip()
            current_companies.add(name)
    
    print(f"Current companies in database: {len(current_companies)}")
    
    # Get additional companies
    additional_companies = get_additional_companies()
    print(f"Additional companies to evaluate: {len(additional_companies)}")
    
    # Filter out duplicates and validate URLs
    new_companies = []
    semaphore = asyncio.Semaphore(10)
    
    validation_tasks = []
    company_mappings = []
    
    for company in additional_companies:
        name = company['company'].lower().strip()
        if name not in current_companies:
            # Validate URL
            url = company['careers_url']
            task = validate_url(url)
            validation_tasks.append(task)
            company_mappings.append(company)
        else:
            print(f"⏭️  Skipping duplicate: {company['company']}")
    
    print(f"\nValidating {len(validation_tasks)} new company URLs...")
    
    if validation_tasks:
        results = await asyncio.gather(*validation_tasks)
        
        valid_companies = []
        for company, is_valid in zip(company_mappings, results):
            if is_valid:
                valid_companies.append(company)
                print(f"✅ {company['company']}: {company['careers_url']}")
            else:
                print(f"❌ {company['company']}: {company['careers_url']}")
        
        # Add valid companies to the data structure
        for company in valid_companies:
            source = company['source']
            if source not in current_data:
                current_data[source] = []
            
            company_entry = {
                'company': company['company'],
                'token': company['token'],
                'careers_url': company['careers_url']
            }
            
            # Add host field for lever companies
            if source == 'lever' and 'host' in company:
                company_entry['host'] = company['host']
            
            current_data[source].append(company_entry)
        
        # Sort companies within each source
        for source in current_data:
            current_data[source].sort(key=lambda x: x['company'])
        
        # Save updated file
        with open(companies_file, 'w') as f:
            yaml.dump(current_data, f, default_flow_style=False, sort_keys=False,
                     allow_unicode=True, indent=2)
        
        # Also update master file
        master_file = backend_dir / "companies_master.yaml"
        with open(master_file, 'w') as f:
            yaml.dump(current_data, f, default_flow_style=False, sort_keys=False,
                     allow_unicode=True, indent=2)
        
        # Print summary
        total_companies = sum(len(companies) for companies in current_data.values())
        
        print(f"\n{'='*60}")
        print("EXPANSION SUMMARY")
        print(f"{'='*60}")
        print(f"Companies added: {len(valid_companies)}")
        print(f"Total companies: {total_companies}")
        print(f"Total sources: {len(current_data)}")
        print()
        
        for source, companies in current_data.items():
            print(f"{source.upper()}: {len(companies)} companies")
        
        print(f"\nNew companies added:")
        for company in valid_companies:
            print(f"  - {company['company']} ({company['source']})")
    
    else:
        print("No new companies to add (all were duplicates)")

if __name__ == "__main__":
    asyncio.run(main())
