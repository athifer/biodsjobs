#!/usr/bin/env python3
"""
Final cleanup and consolidation of companies configuration
Creates a single companies.yaml file with only valid, working companies
"""

import yaml
import os
from pathlib import Path

def main():
    backend_dir = Path(__file__).parent
    
    # The current companies_all.yaml already contains the validated companies
    # Let's verify it has all the companies that are currently working
    
    current_file = backend_dir / "companies_all.yaml"
    
    with open(current_file, 'r') as f:
        companies_data = yaml.safe_load(f)
    
    # Add Johnson & Johnson since it's actually working
    jnj_found = False
    for source, companies in companies_data.items():
        for company in companies:
            if 'johnson' in company.get('company', '').lower():
                jnj_found = True
                break
        if jnj_found:
            break
    
    if not jnj_found:
        # Add J&J to workday section since it's working
        if 'workday' not in companies_data:
            companies_data['workday'] = []
        
        companies_data['workday'].append({
            'company': 'Johnson & Johnson',
            'token': 'jnj',
            'careers_url': 'https://jobs.jnj.com/'
        })
        
        print("Added Johnson & Johnson to workday section")
    
    # Sort companies within each source
    for source in companies_data:
        companies_data[source].sort(key=lambda x: x.get('company', ''))
    
    # Save the final clean configuration
    final_file = backend_dir / "companies.yaml"
    with open(final_file, 'w') as f:
        yaml.dump(companies_data, f, default_flow_style=False, sort_keys=False, 
                 allow_unicode=True, indent=2)
    
    # Also update companies_all.yaml to include J&J
    with open(current_file, 'w') as f:
        yaml.dump(companies_data, f, default_flow_style=False, sort_keys=False, 
                 allow_unicode=True, indent=2)
    
    # Count companies and sources
    total_companies = sum(len(companies) for companies in companies_data.values())
    
    print(f"\n{'='*50}")
    print("FINAL COMPANIES CONFIGURATION")
    print(f"{'='*50}")
    print(f"File: companies.yaml")
    print(f"Total companies: {total_companies}")
    print(f"Total sources: {len(companies_data)}")
    print()
    
    for source, companies in companies_data.items():
        print(f"{source}: {len(companies)} companies")
        for company in companies[:3]:
            print(f"  - {company.get('company', 'Unknown')}")
        if len(companies) > 3:
            print(f"  ... and {len(companies) - 3} more")
        print()

if __name__ == "__main__":
    main()
