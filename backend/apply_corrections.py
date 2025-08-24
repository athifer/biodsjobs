#!/usr/bin/env python3
"""
Apply researched URL corrections to companies.yaml
"""

import yaml
from pathlib import Path

def main():
    """Apply researched URL corrections"""
    backend_dir = Path(__file__).parent
    companies_file = backend_dir / "companies.yaml"
    researched_file = backend_dir / "researched_urls.yaml"
    
    print("APPLYING RESEARCHED URL CORRECTIONS")
    print("=" * 60)
    
    # Load current companies
    with open(companies_file, 'r') as f:
        current_data = yaml.safe_load(f)
    
    # Load researched URLs
    with open(researched_file, 'r') as f:
        researched_urls = yaml.safe_load(f)
    
    corrections_made = []
    moves_made = []
    
    # Function to find and remove company from any source
    def find_and_remove_company(company_name):
        for source in current_data:
            for i, company in enumerate(current_data[source]):
                if company['company'] == company_name:
                    removed_company = current_data[source].pop(i)
                    return source, removed_company
        return None, None
    
    # Function to add company to source
    def add_company_to_source(company_data, source):
        if source not in current_data:
            current_data[source] = []
        current_data[source].append(company_data)
    
    # Apply corrections
    for company_name, url_info in researched_urls.items():
        new_url = url_info['url']
        target_source = url_info['source']
        
        print(f"\\n🔧 Correcting {company_name}:")
        print(f"   New URL: {new_url}")
        print(f"   Target source: {target_source}")
        
        # Find and remove the company from its current location
        old_source, company_data = find_and_remove_company(company_name)
        
        if company_data:
            print(f"   Found in: {old_source}")
            
            # Update the URL
            company_data['careers_url'] = new_url
            
            # Create token if it doesn't exist
            if 'token' not in company_data:
                company_data['token'] = company_name.lower().replace(' ', '').replace('.', '')
            
            # Add host field for lever companies
            if target_source == 'lever' and 'lever.co' in new_url:
                company_data['host'] = new_url.replace('https://', '').replace('http://', '')
            
            # Add to target source
            add_company_to_source(company_data, target_source)
            
            if old_source == target_source:
                corrections_made.append(f"{company_name}: URL updated")
            else:
                moves_made.append(f"{company_name}: {old_source} → {target_source}")
                
            print(f"   ✅ Applied correction")
        else:
            print(f"   ⚠️  Company not found in database")
    
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
    print("URL CORRECTIONS SUMMARY")
    print(f"{'='*60}")
    print(f"Total companies: {total_companies}")
    print(f"URL corrections: {len(corrections_made)}")
    print(f"Source moves: {len(moves_made)}")
    print()
    
    for source, companies in current_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
    
    if corrections_made:
        print(f"\\n✅ URL corrections:")
        for correction in corrections_made:
            print(f"  • {correction}")
    
    if moves_made:
        print(f"\\n🔄 Source moves:")
        for move in moves_made:
            print(f"  • {move}")

if __name__ == "__main__":
    main()
