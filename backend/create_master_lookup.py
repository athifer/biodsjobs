#!/usr/bin/env python3
"""
Comprehensive Company Lookup Creator
Combines all companies from all YAML files including backup folder
Creates a master companies lookup with validated URLs
"""

import yaml
import asyncio
import httpx
from pathlib import Path
from collections import defaultdict
import re
from urllib.parse import urlparse

async def validate_url(url: str, semaphore: asyncio.Semaphore) -> bool:
    """Check if a URL is accessible (returns 200-399)"""
    async with semaphore:
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.head(url)
                return 200 <= response.status_code < 400
        except Exception:
            return False

def normalize_company_name(name: str) -> str:
    """Normalize company names for deduplication"""
    # Remove common suffixes and normalize case
    name = re.sub(r'\s+(Inc|LLC|Corp|Corporation|Ltd|Limited)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(YC|Research)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(Labs?|Therapeutics|Pharmaceuticals)\b', '', name, flags=re.IGNORECASE)
    return name.strip().lower().replace(':', '').replace('.', '')

def load_yaml_file(file_path: Path) -> dict:
    """Load a YAML file and return its content"""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f) or {}
            print(f"  Loaded {file_path.name}")
            return data
    except Exception as e:
        print(f"  Error loading {file_path}: {e}")
        return {}

def collect_all_companies():
    """Collect companies from all YAML files"""
    backend_dir = Path(__file__).parent
    backup_dir = backend_dir / "backup"
    
    all_companies = {}  # normalized_name -> {company_info, sources}
    
    # Find all YAML files in backend and backup directories
    yaml_files = []
    yaml_files.extend(backend_dir.glob("companies*.yaml"))
    if backup_dir.exists():
        yaml_files.extend(backup_dir.glob("companies*.yaml"))
    
    print(f"Found {len(yaml_files)} YAML files to process:")
    
    for file_path in yaml_files:
        print(f"\nProcessing {file_path.relative_to(backend_dir)}...")
        data = load_yaml_file(file_path)
        
        if not isinstance(data, dict):
            continue
            
        for source, companies in data.items():
            if not isinstance(companies, list):
                continue
                
            for company_entry in companies:
                if not isinstance(company_entry, dict):
                    continue
                    
                company_name = company_entry.get('company', '')
                if not company_name:
                    continue
                    
                normalized_name = normalize_company_name(company_name)
                careers_url = company_entry.get('careers_url', '')
                
                if normalized_name not in all_companies:
                    all_companies[normalized_name] = {
                        'name': company_name,  # Keep the first name encountered
                        'urls': set(),
                        'sources': set(),
                        'tokens': set(),
                        'hosts': set()
                    }
                
                # Collect all information for this company
                if careers_url:
                    all_companies[normalized_name]['urls'].add(careers_url)
                if source:
                    all_companies[normalized_name]['sources'].add(source)
                if company_entry.get('token'):
                    all_companies[normalized_name]['tokens'].add(company_entry['token'])
                if company_entry.get('host'):
                    all_companies[normalized_name]['hosts'].add(company_entry['host'])
                
                print(f"    Added: {company_name} ({source}) - {careers_url}")
    
    return all_companies

def get_best_url_for_company(company_info):
    """Select the best URL for a company from multiple options"""
    urls = list(company_info['urls'])
    if not urls:
        return None
    
    if len(urls) == 1:
        return urls[0]
    
    # Preference order for URL selection
    url_preferences = [
        'boards.greenhouse.io',
        'job-boards.greenhouse.io', 
        'jobs.lever.co',
        'myworkdayjobs.com',
        'careers.com',
        'jobs.com',
        'bamboohr.com',
        'workatastartup.com',
        'wellfound.com'
    ]
    
    # Sort URLs by preference
    for preference in url_preferences:
        for url in urls:
            if preference in url:
                return url
    
    # If no preference matches, return the first HTTPS URL
    for url in urls:
        if url.startswith('https://'):
            return url
            
    return urls[0]

def determine_best_source(company_info):
    """Determine the best source for a company"""
    sources = list(company_info['sources'])
    if not sources:
        return 'unknown'
    
    # Preference order for sources
    source_preferences = ['greenhouse', 'lever', 'workday', 'comprehensive', 'talentbrew', 'bamboo', 'ycombinator', 'angellist']
    
    for preference in source_preferences:
        if preference in sources:
            return preference
            
    return sources[0]

def get_best_token(company_info, source, url):
    """Get the best token for a company"""
    tokens = list(company_info['tokens'])
    hosts = list(company_info['hosts'])
    
    # For lever, extract from host if available
    if source == 'lever' and hosts:
        for host in hosts:
            if '/' in host:
                return host.split('/')[-1]
    
    # For other sources, use existing tokens
    if tokens:
        # Prefer shorter, simpler tokens
        tokens.sort(key=len)
        return tokens[0]
    
    # Generate token from company name as fallback
    name = company_info['name'].lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    return name[:20]  # Limit length

async def validate_all_urls(all_companies):
    """Validate URLs for all companies"""
    semaphore = asyncio.Semaphore(10)
    
    print(f"\nValidating URLs for {len(all_companies)} companies...")
    
    validation_tasks = []
    company_mapping = []
    
    for normalized_name, company_info in all_companies.items():
        best_url = get_best_url_for_company(company_info)
        if best_url:
            task = validate_url(best_url, semaphore)
            validation_tasks.append(task)
            company_mapping.append((normalized_name, best_url))
    
    if not validation_tasks:
        return {}
    
    results = await asyncio.gather(*validation_tasks)
    
    valid_companies = {}
    invalid_count = 0
    
    for (normalized_name, url), is_valid in zip(company_mapping, results):
        company_info = all_companies[normalized_name]
        
        if is_valid:
            valid_companies[normalized_name] = company_info
            print(f"✅ {company_info['name']}: {url}")
        else:
            invalid_count += 1
            print(f"❌ {company_info['name']}: {url}")
    
    print(f"\nValidation complete: {len(valid_companies)} valid, {invalid_count} invalid")
    return valid_companies

def create_master_companies_file(valid_companies):
    """Create the master companies YAML file"""
    backend_dir = Path(__file__).parent
    
    # Organize companies by source
    companies_by_source = defaultdict(list)
    
    for normalized_name, company_info in valid_companies.items():
        best_source = determine_best_source(company_info)
        best_url = get_best_url_for_company(company_info)
        best_token = get_best_token(company_info, best_source, best_url)
        
        company_entry = {
            'company': company_info['name'],
            'token': best_token,
            'careers_url': best_url
        }
        
        # Add host field for lever
        if best_source == 'lever' and 'jobs.lever.co' in best_url:
            host = best_url.replace('https://', '').replace('http://', '')
            company_entry['host'] = host
        
        companies_by_source[best_source].append(company_entry)
    
    # Sort companies within each source
    for source in companies_by_source:
        companies_by_source[source].sort(key=lambda x: x['company'])
    
    # Sort sources by number of companies
    sorted_companies = dict(sorted(companies_by_source.items(), 
                                 key=lambda x: len(x[1]), reverse=True))
    
    # Save master file
    output_file = backend_dir / "companies_master.yaml"
    with open(output_file, 'w') as f:
        yaml.dump(sorted_companies, f, default_flow_style=False, sort_keys=False,
                 allow_unicode=True, indent=2)
    
    return output_file, sorted_companies

def print_summary(companies_data, output_file):
    """Print comprehensive summary"""
    total_companies = sum(len(companies) for companies in companies_data.values())
    
    print(f"\n{'='*70}")
    print("MASTER COMPANIES LOOKUP - SUMMARY")
    print(f"{'='*70}")
    print(f"Output file: {output_file.name}")
    print(f"Total companies: {total_companies}")
    print(f"Total sources: {len(companies_data)}")
    print()
    
    for source, companies in companies_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
        for company in companies[:5]:  # Show first 5
            print(f"  - {company['company']}")
        if len(companies) > 5:
            print(f"  ... and {len(companies) - 5} more")
        print()
    
    # Additional statistics
    all_urls = []
    all_domains = set()
    
    for companies in companies_data.values():
        for company in companies:
            url = company.get('careers_url', '')
            if url:
                all_urls.append(url)
                domain = urlparse(url).netloc
                all_domains.add(domain)
    
    print(f"Unique domains: {len(all_domains)}")
    print(f"Total career URLs: {len(all_urls)}")
    
    print(f"\nTop domains:")
    domain_counts = defaultdict(int)
    for url in all_urls:
        domain = urlparse(url).netloc
        domain_counts[domain] += 1
    
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {domain}: {count} companies")

async def main():
    """Main function"""
    print("Creating Master Companies Lookup...")
    print("=" * 50)
    
    # Collect all companies
    all_companies = collect_all_companies()
    print(f"\nCollected {len(all_companies)} unique companies")
    
    # Validate URLs
    valid_companies = await validate_all_urls(all_companies)
    
    # Create master file
    output_file, companies_data = create_master_companies_file(valid_companies)
    
    # Print summary
    print_summary(companies_data, output_file)

if __name__ == "__main__":
    asyncio.run(main())
