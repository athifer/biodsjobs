#!/usr/bin/env python3
"""
Update companies with better career page URLs
"""

import yaml
from pathlib import Path

def update_company_urls():
    print("UPDATING COMPANY URLS WITH BETTER ALTERNATIVES")
    print("=" * 60)
    
    # Better URLs found from research
    url_updates = {
        "Pfizer": "https://www.pfizer.com/careers",
        "Moderna": "https://www.modernatx.com/careers", 
        "Gilead": "https://www.gilead.com/careers",
        "Bristol Myers Squibb": "https://www.bms.com/careers",
        "Vertex": "https://www.vrtx.com/careers"
        # Note: Keeping Illumina's Workday URL as it was the only working one
    }
    
    # Load current companies
    companies_file = Path(__file__).parent / "companies.yaml"
    with open(companies_file, 'r') as f:
        companies_data = yaml.safe_load(f)
    
    updated_count = 0
    
    # Update URLs in comprehensive section
    if "comprehensive" in companies_data:
        for company in companies_data["comprehensive"]:
            company_name = company.get("company")
            if company_name in url_updates:
                old_url = company.get("careers_url")
                new_url = url_updates[company_name]
                company["careers_url"] = new_url
                print(f"✅ Updated {company_name}:")
                print(f"   Old: {old_url}")
                print(f"   New: {new_url}")
                updated_count += 1
    
    print(f"\n📊 Updated {updated_count} company URLs")
    
    # Save updated companies.yaml
    with open(companies_file, 'w') as f:
        yaml.dump(companies_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"💾 Saved to {companies_file}")

if __name__ == "__main__":
    update_company_urls()
