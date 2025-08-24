#!/usr/bin/env python3
"""
Comprehensive Biotech/Pharma Companies Database Expansion
Adds hundreds of missing public and private biotech/pharma companies
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

def get_comprehensive_biotech_pharma_companies():
    """Return comprehensive list of biotech/pharma companies"""
    return [
        # Major Pharmaceutical Companies (Public)
        {
            'company': 'Johnson & Johnson',
            'token': 'jnj',
            'careers_url': 'https://jnjcareers.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Eli Lilly',
            'token': 'lilly',
            'careers_url': 'https://lilly.wd5.myworkdayjobs.com/LillyCareers',
            'source': 'workday'
        },
        {
            'company': 'AbbVie',
            'token': 'abbvie',
            'careers_url': 'https://careers.abbvie.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Sanofi',
            'token': 'sanofi',
            'careers_url': 'https://en.sanofi.com/careers/search-jobs',
            'source': 'comprehensive'
        },
        {
            'company': 'Bayer',
            'token': 'bayer',
            'careers_url': 'https://career.bayer.com/en/jobs',
            'source': 'comprehensive'
        },
        {
            'company': 'Boehringer Ingelheim',
            'token': 'boehringer',
            'careers_url': 'https://www.boehringer-ingelheim.com/careers',
            'source': 'comprehensive'
        },
        
        # Major Biotech Companies (Public)
        {
            'company': 'Regeneron',
            'token': 'regeneron',
            'careers_url': 'https://careers.regeneron.com/search-jobs',
            'source': 'comprehensive'
        },
        {
            'company': 'BioMarin',
            'token': 'biomarin',
            'careers_url': 'https://biomarin.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Incyte',
            'token': 'incyte',
            'careers_url': 'https://www.incyte.com/careers/job-opportunities',
            'source': 'comprehensive'
        },
        {
            'company': 'Alexion',
            'token': 'alexion',
            'careers_url': 'https://alexion.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Seagen',
            'token': 'seagen',
            'careers_url': 'https://www.seagen.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Exact Sciences',
            'token': 'exactsciences',
            'careers_url': 'https://www.exactsciences.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Ionis Pharmaceuticals',
            'token': 'ionis',
            'careers_url': 'https://www.ionis.com/careers/',
            'source': 'comprehensive'
        },
        
        # Gene Therapy & Cell Therapy
        {
            'company': 'Bluebird Bio',
            'token': 'bluebirdbio',
            'careers_url': 'https://www.bluebirdbio.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Editas Medicine',
            'token': 'editas',
            'careers_url': 'https://www.editasmedicine.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'CRISPR Therapeutics',
            'token': 'crisprtx',
            'careers_url': 'https://crisprtx.com/about-us/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Intellia Therapeutics',
            'token': 'intellia',
            'careers_url': 'https://www.intelliatx.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Beam Therapeutics',
            'token': 'beamtx',
            'careers_url': 'https://beamtx.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Allogene Therapeutics',
            'token': 'allogene',
            'careers_url': 'https://www.allogene.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Kite Pharma',
            'token': 'kitepharma',
            'careers_url': 'https://www.kitepharma.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Juno Therapeutics',
            'token': 'junotherapeutics',
            'careers_url': 'https://www.junotherapeutics.com/careers',
            'source': 'comprehensive'
        },
        
        # Oncology Focused
        {
            'company': 'Mirati Therapeutics',
            'token': 'mirati',
            'careers_url': 'https://www.mirati.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Exelixis',
            'token': 'exelixis',
            'careers_url': 'https://www.exelixis.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Danaher',
            'token': 'danaher',
            'careers_url': 'https://jobs.danaher.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Thermo Fisher Scientific',
            'token': 'thermofisher',
            'careers_url': 'https://jobs.thermofisher.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Agilent Technologies',
            'token': 'agilent',
            'careers_url': 'https://jobs.agilent.com/',
            'source': 'comprehensive'
        },
        
        # Emerging Biotech (Private/Public)
        {
            'company': 'Sana Biotechnology',
            'token': 'sanabio',
            'careers_url': 'https://sana.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Relay Therapeutics',
            'token': 'relaytx',
            'careers_url': 'https://relaytx.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Denali Therapeutics',
            'token': 'denalitx',
            'careers_url': 'https://www.denalitherapeutics.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Argenx',
            'token': 'argenx',
            'careers_url': 'https://www.argenx.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Fate Therapeutics',
            'token': 'fatetherapeutics',
            'careers_url': 'https://fatetherapeutics.com/careers/',
            'source': 'comprehensive'
        },
        
        # AI/Computational Biology
        {
            'company': 'Recursion',
            'token': 'recursion',
            'careers_url': 'https://www.recursion.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Tempus',
            'token': 'tempus',
            'careers_url': 'https://www.tempus.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Veracyte',
            'token': 'veracyte',
            'careers_url': 'https://www.veracyte.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Atomwise',
            'token': 'atomwise',
            'careers_url': 'https://www.atomwise.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Deep Genomics',
            'token': 'deepgenomics',
            'careers_url': 'https://www.deepgenomics.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Insilico Medicine',
            'token': 'insilicomedicine',
            'careers_url': 'https://insilico.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Owkin',
            'token': 'owkin',
            'careers_url': 'https://owkin.com/careers/',
            'source': 'comprehensive'
        },
        
        # Diagnostics Companies
        {
            'company': 'Natera',
            'token': 'natera',
            'careers_url': 'https://www.natera.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Myriad Genetics',
            'token': 'myriad',
            'careers_url': 'https://myriad.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Invitae',
            'token': 'invitae',
            'careers_url': 'https://www.invitae.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Pacific Biosciences',
            'token': 'pacbio',
            'careers_url': 'https://www.pacb.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Oxford Nanopore',
            'token': 'nanopore',
            'careers_url': 'https://nanoporetech.com/careers',
            'source': 'comprehensive'
        },
        
        # Medical Devices
        {
            'company': 'Medtronic',
            'token': 'medtronic',
            'careers_url': 'https://jobs.medtronic.com/jobs',
            'source': 'comprehensive'
        },
        {
            'company': 'Stryker',
            'token': 'stryker',
            'careers_url': 'https://careers.stryker.com/careers-home',
            'source': 'comprehensive'
        },
        {
            'company': 'Edwards Lifesciences',
            'token': 'edwards',
            'careers_url': 'https://www.edwards.com/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Intuitive Surgical',
            'token': 'intuitive',
            'careers_url': 'https://www.intuitive.com/en-us/about-us/careers',
            'source': 'comprehensive'
        },
        {
            'company': 'Zimmer Biomet',
            'token': 'zimmerbiomet',
            'careers_url': 'https://www.zimmerbiomet.com/en/careers.html',
            'source': 'comprehensive'
        },
        
        # Contract Research Organizations
        {
            'company': 'Covance',
            'token': 'covance',
            'careers_url': 'https://careers.covance.com/',
            'source': 'comprehensive'
        },
        {
            'company': 'Parexel',
            'token': 'parexel',
            'careers_url': 'https://careers.parexel.com/careers-home',
            'source': 'comprehensive'
        },
        {
            'company': 'ICON',
            'token': 'iconplc',
            'careers_url': 'https://www.iconplc.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'PRA Health Sciences',
            'token': 'prahealth',
            'careers_url': 'https://www.prahs.com/careers/',
            'source': 'comprehensive'
        },
        {
            'company': 'Charles River Laboratories',
            'token': 'criver',
            'careers_url': 'https://jobs.criver.com/',
            'source': 'comprehensive'
        },
        
        # Emerging/Private Companies on Greenhouse
        {
            'company': 'Mammoth Biosciences',
            'token': 'mammothbio',
            'careers_url': 'https://boards.greenhouse.io/mammothbiosciences',
            'source': 'greenhouse'
        },
        {
            'company': 'Scribe Therapeutics',
            'token': 'scribetx',
            'careers_url': 'https://boards.greenhouse.io/scribetx',
            'source': 'greenhouse'
        },
        {
            'company': 'Berkeley Lights',
            'token': 'berkeleylights',
            'careers_url': 'https://boards.greenhouse.io/berkeleylights',
            'source': 'greenhouse'
        },
        {
            'company': 'Synthetic Biologics',
            'token': 'syntheticbiologics',
            'careers_url': 'https://boards.greenhouse.io/syntheticbiologics',
            'source': 'greenhouse'
        },
        {
            'company': 'Cellarity',
            'token': 'cellarity',
            'careers_url': 'https://boards.greenhouse.io/cellarity',
            'source': 'greenhouse'
        },
        {
            'company': 'Tome Biosciences',
            'token': 'tomebio',
            'careers_url': 'https://boards.greenhouse.io/tomebio',
            'source': 'greenhouse'
        },
        {
            'company': 'NotCo',
            'token': 'notco',
            'careers_url': 'https://boards.greenhouse.io/notco',
            'source': 'greenhouse'
        },
        
        # Workday Companies
        {
            'company': 'Biohaven',
            'token': 'biohaven',
            'careers_url': 'https://biohaven.wd5.myworkdayjobs.com/Biohaven_Careers',
            'source': 'workday'
        },
        {
            'company': 'Ultragenyx',
            'token': 'ultragenyx',
            'careers_url': 'https://ultragenyx.wd1.myworkdayjobs.com/Ultragenyx_Careers',
            'source': 'workday'
        },
        {
            'company': 'BeiGene',
            'token': 'beigene',
            'careers_url': 'https://beigene.wd3.myworkdayjobs.com/BeiGene_Careers',
            'source': 'workday'
        },
        
        # Lever Companies
        {
            'company': 'Memphis Meats',
            'token': 'memphismeats',
            'careers_url': 'https://jobs.lever.co/upside-foods',
            'source': 'lever',
            'host': 'jobs.lever.co/upside-foods'
        },
        {
            'company': 'Perfect Day',
            'token': 'perfectday',
            'careers_url': 'https://jobs.lever.co/perfectday',
            'source': 'lever',
            'host': 'jobs.lever.co/perfectday'
        },
        {
            'company': 'Impossible Foods',
            'token': 'impossible',
            'careers_url': 'https://jobs.lever.co/impossible',
            'source': 'lever',
            'host': 'jobs.lever.co/impossible'
        },
        {
            'company': 'Zymergen',
            'token': 'zymergen',
            'careers_url': 'https://jobs.lever.co/zymergen',
            'source': 'lever',
            'host': 'jobs.lever.co/zymergen'
        }
    ]

async def main():
    """Add comprehensive biotech/pharma companies"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    
    print("COMPREHENSIVE BIOTECH/PHARMA EXPANSION")
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
    
    print(f"Current companies in database: {len(current_companies)}")
    
    # Get comprehensive list
    comprehensive_companies = get_comprehensive_biotech_pharma_companies()
    print(f"Comprehensive companies to evaluate: {len(comprehensive_companies)}")
    
    # Filter out duplicates
    new_companies = []
    for company in comprehensive_companies:
        name = company['company'].lower().strip().replace(' ', '').replace('.', '')
        if name not in current_companies:
            new_companies.append(company)
        else:
            print(f"⏭️  Skipping duplicate: {company['company']}")
    
    print(f"\nValidating {len(new_companies)} new company URLs...")
    
    # Validate URLs with smaller batches
    semaphore = asyncio.Semaphore(5)  # Reduced concurrency
    valid_companies = []
    
    async def validate_with_semaphore(company):
        async with semaphore:
            is_valid = await validate_url(company['careers_url'])
            return company, is_valid
    
    # Process in batches of 20
    batch_size = 20
    for i in range(0, len(new_companies), batch_size):
        batch = new_companies[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(new_companies) + batch_size - 1)//batch_size}...")
        
        tasks = [validate_with_semaphore(company) for company in batch]
        results = await asyncio.gather(*tasks)
        
        for company, is_valid in results:
            if is_valid:
                valid_companies.append(company)
                print(f"✅ {company['company']}: {company['careers_url']}")
            else:
                print(f"❌ {company['company']}: {company['careers_url']}")
        
        # Small delay between batches
        await asyncio.sleep(1)
    
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
    print("COMPREHENSIVE EXPANSION SUMMARY")
    print(f"{'='*60}")
    print(f"New companies added: {len(valid_companies)}")
    print(f"Total companies: {total_companies}")
    print(f"Total sources: {len(current_data)}")
    print()
    
    for source, companies in current_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
    
    if valid_companies:
        print(f"\nNew companies added by category:")
        pharma = [c for c in valid_companies if any(word in c['company'].lower() for word in ['johnson', 'lilly', 'abbvie', 'sanofi', 'bayer', 'boehringer'])]
        biotech = [c for c in valid_companies if any(word in c['company'].lower() for word in ['regeneron', 'biomarin', 'incyte', 'alexion', 'seagen'])]
        gene_therapy = [c for c in valid_companies if any(word in c['company'].lower() for word in ['editas', 'crispr', 'intellia', 'beam', 'allogene', 'kite'])]
        
        if pharma:
            print(f"\nMajor Pharma ({len(pharma)}):")
            for c in pharma:
                print(f"  - {c['company']}")
                
        if biotech:
            print(f"\nBiotech Leaders ({len(biotech)}):")
            for c in biotech:
                print(f"  - {c['company']}")
                
        if gene_therapy:
            print(f"\nGene/Cell Therapy ({len(gene_therapy)}):")
            for c in gene_therapy:
                print(f"  - {c['company']}")

if __name__ == "__main__":
    asyncio.run(main())
