#!/usr/bin/env python3
"""
Consolidate companies_*.yaml files and validate URLs
"""

import yaml
import asyncio
import httpx
from pathlib import Path
from collections import defaultdict
import re

async def validate_url(url: str, semaphore: asyncio.Semaphore) -> bool:
    """Check if a URL is accessible (returns 200-299 or 300-399)"""
    async with semaphore:
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                response = await client.head(url)
                return 200 <= response.status_code < 400
        except Exception as e:
            print(f"Error checking {url}: {e}")
            return False

def load_yaml_file(file_path: Path) -> dict:
    """Load a YAML file and return its content"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def normalize_company_name(name: str) -> str:
    """Normalize company names for deduplication"""
    # Remove common suffixes and normalize case
    name = re.sub(r'\s+(Inc|LLC|Corp|Corporation|Ltd|Limited)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(YC|Research)\b', '', name, flags=re.IGNORECASE)
    return name.strip().lower()

def merge_companies_data(files: list) -> dict:
    """Merge multiple YAML files, removing duplicates by company name"""
    merged = defaultdict(list)
    seen_companies = set()
    
    for file_path in files:
        data = load_yaml_file(file_path)
        print(f"Loading {file_path.name}...")
        
        for source, companies in data.items():
            if not isinstance(companies, list):
                continue
                
            for company_entry in companies:
                if not isinstance(company_entry, dict):
                    continue
                    
                company_name = company_entry.get('company', '')
                normalized_name = normalize_company_name(company_name)
                
                # Create a unique key based on company name and source
                unique_key = f"{normalized_name}_{source}"
                
                if unique_key not in seen_companies:
                    seen_companies.add(unique_key)
                    merged[source].append(company_entry)
                    print(f"  Added: {company_name} ({source})")
                else:
                    print(f"  Skipped duplicate: {company_name} ({source})")
    
    return dict(merged)

async def validate_companies_urls(companies_data: dict) -> dict:
    """Validate URLs for all companies and filter out invalid ones"""
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    valid_companies = defaultdict(list)
    
    validation_tasks = []
    company_mappings = []
    
    print("\nValidating URLs...")
    
    for source, companies in companies_data.items():
        for company_entry in companies:
            careers_url = company_entry.get('careers_url', '')
            if careers_url and careers_url.startswith('http'):
                task = validate_url(careers_url, semaphore)
                validation_tasks.append(task)
                company_mappings.append((source, company_entry, careers_url))
    
    # Run all validations concurrently
    results = await asyncio.gather(*validation_tasks)
    
    # Filter based on results
    for (source, company_entry, url), is_valid in zip(company_mappings, results):
        company_name = company_entry.get('company', 'Unknown')
        if is_valid:
            valid_companies[source].append(company_entry)
            print(f"✅ {company_name}: {url}")
        else:
            print(f"❌ {company_name}: {url}")
    
    return dict(valid_companies)

def save_consolidated_file(companies_data: dict, output_path: Path):
    """Save the consolidated and validated companies data"""
    
    # Sort companies within each source by company name
    for source in companies_data:
        companies_data[source].sort(key=lambda x: x.get('company', ''))
    
    # Sort sources by number of companies (descending)
    sorted_data = dict(sorted(companies_data.items(), 
                             key=lambda x: len(x[1]), reverse=True))
    
    with open(output_path, 'w') as f:
        yaml.dump(sorted_data, f, default_flow_style=False, sort_keys=False, 
                 allow_unicode=True, indent=2)
    
    print(f"\nConsolidated file saved to: {output_path}")

def print_summary(companies_data: dict):
    """Print a summary of the consolidation"""
    total_companies = sum(len(companies) for companies in companies_data.values())
    
    print(f"\n{'='*50}")
    print("CONSOLIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total companies: {total_companies}")
    print(f"Total sources: {len(companies_data)}")
    print()
    
    for source, companies in companies_data.items():
        print(f"{source}: {len(companies)} companies")
        for company in companies[:3]:  # Show first 3 companies
            print(f"  - {company.get('company', 'Unknown')}")
        if len(companies) > 3:
            print(f"  ... and {len(companies) - 3} more")
        print()

async def main():
    """Main consolidation function"""
    backend_dir = Path(__file__).parent
    
    # Find all companies_*.yaml files
    yaml_files = [
        backend_dir / "companies_all.yaml",
        backend_dir / "companies_all_backup.yaml", 
        backend_dir / "companies_all_new.yaml"
    ]
    
    existing_files = [f for f in yaml_files if f.exists()]
    print(f"Found {len(existing_files)} YAML files to consolidate:")
    for f in existing_files:
        print(f"  - {f.name}")
    
    # Merge all files
    merged_data = merge_companies_data(existing_files)
    print(f"\nMerged {len(merged_data)} sources")
    
    # Validate URLs
    valid_data = await validate_companies_urls(merged_data)
    
    # Save consolidated file
    output_path = backend_dir / "companies_consolidated.yaml"
    save_consolidated_file(valid_data, output_path)
    
    # Print summary
    print_summary(valid_data)

if __name__ == "__main__":
    asyncio.run(main())
