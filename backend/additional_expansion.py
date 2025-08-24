#!/usr/bin/env python3
"""
Additional Public Biotech/Pharma Companies
Focus on well-known public companies with standard career pages
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

def get_additional_public_companies():
    """Return additional well-known public biotech/pharma companies"""
    return [
        # More Major Public Biotech
        {
            'company': 'Biohaven Pharmaceuticals',
            'token': 'biohaven',
            'careers_url': 'https://www.biohavenpharma.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Horizon Therapeutics',
            'token': 'horizon',
            'careers_url': 'https://www.horizontherapeutics.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Jazz Pharmaceuticals',
            'token': 'jazz',
            'careers_url': 'https://www.jazzpharmaceuticals.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Neurocrine Biosciences',
            'token': 'neurocrine',
            'careers_url': 'https://www.neurocrine.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Sarepta Therapeutics',
            'token': 'sarepta',
            'careers_url': 'https://www.sarepta.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'United Therapeutics',
            'token': 'unither',
            'careers_url': 'https://www.unither.com/careers.html',
            'source': 'comprehensive'
        },
        {
            'company': 'Halozyme Therapeutics',
            'token': 'halozyme',
            'careers_url': 'https://halozyme.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Retrophin',
            'token': 'retrophin',
            'careers_url': 'https://www.retrophin.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Zogenix',
            'token': 'zogenix',
            'careers_url': 'https://www.zogenix.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Intercept Pharmaceuticals',
            'token': 'intercept',
            'careers_url': 'https://www.interceptpharma.com/careers',
            'source': 'comprehensive'
        },
        
        # Genomics/Diagnostics
        {
            'company': 'NeoGenomics',
            'token': 'neogenomics',
            'careers_url': 'https://neogenomics.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Adaptive Biotechnologies',
            'token': 'adaptivebiotech',
            'careers_url': 'https://www.adaptivebiotech.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Personalis',
            'token': 'personalis',
            'careers_url': 'https://www.personalis.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Verisign',
            'token': 'verisign',
            'careers_url': 'https://www.verisign.com/en_US/company-information/careers/index.xhtml',
            'source': 'comprehensive'
        },
        
        # Medical Devices & Equipment
        {
            'company': 'Hologic',
            'token': 'hologic',
            'careers_url': 'https://www.hologic.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'IDEXX Laboratories',
            'token': 'idexx',
            'careers_url': 'https://www.idexx.com/en/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Waters Corporation',
            'token': 'waters',
            'careers_url': 'https://www.waters.com/waters/nav.htm?locale=en_US&cid=1000245',
            'source': 'comprehensive'
        },
        {
            'company': 'PerkinElmer',
            'token': 'perkinelmer',
            'careers_url': 'https://www.perkinelmer.com/corporate/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Bio-Rad Laboratories',
            'token': 'biorad',
            'careers_url': 'https://www.bio-rad.com/en-us/careers',
            'source': 'comprehensive'
        },
        
        # Smaller/Mid-cap Biotech
        {
            'company': 'Acadia Pharmaceuticals',
            'token': 'acadia',
            'careers_url': 'https://www.acadia-pharm.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Sage Therapeutics',
            'token': 'sage',
            'careers_url': 'https://www.sagerx.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Cassava Sciences',
            'token': 'cassava',
            'careers_url': 'https://www.cassavasciences.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Prothena Corporation',
            'token': 'prothena',
            'careers_url': 'https://www.prothena.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'MyoKardia',
            'token': 'myokardia',
            'careers_url': 'https://www.myokardia.com/careers/',
            'source': 'comprehensive'
        },
        
        # International Pharma/Biotech
        {
            'company': 'UCB',
            'token': 'ucb',
            'careers_url': 'https://www.ucb.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Galapagos',
            'token': 'galapagos',
            'careers_url': 'https://www.glpg.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Almirall',
            'token': 'almirall',
            'careers_url': 'https://www.almirall.com/careers/',
            'source': 'comprehensive'
        },
        
        # More Greenhouse Companies
        {
            'company': 'Lyell Immunopharma',
            'token': 'lyellimmuno',
            'careers_url': 'https://boards.greenhouse.io/lyellimmuno',
            'source': 'greenhouse'
        },
        {
            'company': 'A2 Biotherapeutics',
            'token': 'a2bio',
            'careers_url': 'https://boards.greenhouse.io/a2bio',
            'source': 'greenhouse'
        },
        {
            'company': 'Checkmate Pharmaceuticals',
            'token': 'checkmatepharma',
            'careers_url': 'https://boards.greenhouse.io/checkmatepharma',
            'source': 'greenhouse'
        },
        {
            'company': 'Laronde',
            'token': 'laronde',
            'careers_url': 'https://boards.greenhouse.io/laronde',
            'source': 'greenhouse'
        },
        {
            'company': 'Strand Therapeutics',
            'token': 'strandtx',
            'careers_url': 'https://boards.greenhouse.io/strandtx',
            'source': 'greenhouse'
        },
        
        # More Lever Companies
        {
            'company': 'Helix',
            'token': 'helix',
            'careers_url': 'https://jobs.lever.co/helix',
            'source': 'lever',
            'host': 'jobs.lever.co/helix'
        },
        {
            'company': 'Counsyl',
            'token': 'counsyl',
            'careers_url': 'https://jobs.lever.co/counsyl',
            'source': 'lever',
            'host': 'jobs.lever.co/counsyl'
        },
        
        # Contract Manufacturing
        {
            'company': 'Catalent',
            'token': 'catalent',
            'careers_url': 'https://www.catalent.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Lonza',
            'token': 'lonza',
            'careers_url': 'https://www.lonza.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'WuXi AppTec',
            'token': 'wuxiapptec',
            'careers_url': 'https://careers.wuxiapptec.com/',
            'source': 'comprehensive'
        }
    ]

async def main():
    """Add additional public biotech/pharma companies"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    
    print("ADDITIONAL PUBLIC BIOTECH/PHARMA COMPANIES")
    print("=" * 60)
    
    # Load current companies
    with open(companies_file, 'r') as f:
        current_data = yaml.safe_load(f)
    
    # Get current company names (normalized)
    current_companies = set()
    for source, companies in current_data.items():
        for company in companies:
            name = company.get('company', '').lower().strip().replace(' ', '').replace('.', '')
            current_companies.add(name)
    
    current_total = sum(len(companies) for companies in current_data.values())
    print(f"Current companies in database: {current_total}")
    
    # Get additional companies
    additional_companies = get_additional_public_companies()
    print(f"Additional companies to evaluate: {len(additional_companies)}")
    
    # Filter out duplicates
    new_companies = []
    for company in additional_companies:
        name = company['company'].lower().strip().replace(' ', '').replace('.', '')
        if name not in current_companies:
            new_companies.append(company)
        else:
            print(f"⏭️  Skipping duplicate: {company['company']}")
    
    print(f"\nValidating {len(new_companies)} new company URLs...")
    
    # Validate URLs
    semaphore = asyncio.Semaphore(3)
    valid_companies = []
    
    async def validate_with_semaphore(company):
        async with semaphore:
            is_valid = await validate_url(company['careers_url'])
            return company, is_valid
    
    tasks = [validate_with_semaphore(company) for company in new_companies]
    results = await asyncio.gather(*tasks)
    
    for company, is_valid in results:
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
    
    # Print summary
    total_companies = sum(len(companies) for companies in current_data.values())
    
    print(f"\n{'='*60}")
    print("ADDITIONAL EXPANSION SUMMARY")
    print(f"{'='*60}")
    print(f"New companies added: {len(valid_companies)}")
    print(f"Total companies: {total_companies}")
    print(f"Growth: {current_total} → {total_companies} ({total_companies - current_total} added)")
    print()
    
    for source, companies in current_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
    
    if valid_companies:
        print(f"\nNew valid companies added:")
        for company in valid_companies:
            print(f"  - {company['company']} ({company['source']})")

if __name__ == "__main__":
    asyncio.run(main())
