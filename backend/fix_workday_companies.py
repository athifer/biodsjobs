#!/usr/bin/env python3
"""
Move problematic Workday companies to comprehensive scraper and update URLs
"""

import yaml
from pathlib import Path

def fix_workday_companies():
    print("FIXING WORKDAY COMPANIES")
    print("=" * 60)
    
    # Load current companies
    companies_file = Path(__file__).parent / "companies.yaml"
    with open(companies_file, 'r') as f:
        companies_data = yaml.safe_load(f)
    
    # Companies that should be moved from workday to comprehensive
    # Based on our testing, these are JavaScript-heavy sites that don't work with our current workday scraper
    workday_to_comprehensive = {
        "Illumina": {
            "current_url": "https://illumina.wd1.myworkdayjobs.com/illumina-careers",
            "suggested_url": "https://illumina.wd1.myworkdayjobs.com/illumina-careers",
            "reason": "JavaScript-heavy Workday site, move to comprehensive scraper"
        },
        "Pfizer": {
            "current_url": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers", 
            "suggested_url": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers",
            "reason": "JavaScript-heavy Workday site, move to comprehensive scraper"
        },
        "Moderna": {
            "current_url": "https://modernatx.wd1.myworkdayjobs.com/M_tx",
            "suggested_url": "https://modernatx.wd1.myworkdayjobs.com/M_tx", 
            "reason": "JavaScript-heavy Workday site, move to comprehensive scraper"
        },
        "Gilead": {
            "current_url": "https://gilead.wd1.myworkdayjobs.com/gileadcareers",
            "suggested_url": "https://gilead.wd1.myworkdayjobs.com/gileadcareers",
            "reason": "JavaScript-heavy Workday site, move to comprehensive scraper"
        },
        "Bristol Myers Squibb": {
            "current_url": "https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS",
            "suggested_url": "https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS",
            "reason": "JavaScript-heavy Workday site, move to comprehensive scraper"  
        },
        "Vertex": {
            "current_url": "https://vrtx.wd501.myworkdayjobs.com/vertex_careers",
            "suggested_url": "https://vrtx.wd501.myworkdayjobs.com/vertex_careers",
            "reason": "JavaScript-heavy Workday site, move to comprehensive scraper"
        }
    }
    
    companies_moved = 0
    
    # Process each source
    for source_name, companies_list in companies_data.items():
        if source_name == "workday":
            # Find companies to move
            companies_to_remove = []
            for i, company in enumerate(companies_list):
                company_name = company.get("company")
                if company_name in workday_to_comprehensive:
                    info = workday_to_comprehensive[company_name]
                    print(f"\n📦 Moving {company_name} from workday to comprehensive")
                    print(f"   Reason: {info['reason']}")
                    print(f"   URL: {info['suggested_url']}")
                    
                    # Prepare for comprehensive scraper
                    new_company_entry = {
                        "company": company_name,
                        "token": company.get("token", company_name.lower().replace(" ", "")),
                        "careers_url": info['suggested_url']
                    }
                    
                    # Add to comprehensive section
                    if "comprehensive" not in companies_data:
                        companies_data["comprehensive"] = []
                    companies_data["comprehensive"].append(new_company_entry)
                    
                    # Mark for removal from workday
                    companies_to_remove.append(i)
                    companies_moved += 1
            
            # Remove from workday (in reverse order to maintain indices)
            for i in reversed(companies_to_remove):
                companies_list.pop(i)
    
    print(f"\n✅ Moved {companies_moved} companies from workday to comprehensive")
    
    # Save updated companies.yaml
    with open(companies_file, 'w') as f:
        yaml.dump(companies_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"💾 Updated {companies_file}")
    
    # Show final counts
    print(f"\n📊 Final company counts:")
    for source, companies_list in companies_data.items():
        print(f"   {source}: {len(companies_list)} companies")
    
    total = sum(len(companies_list) for companies_list in companies_data.values())
    print(f"   Total: {total} companies")

if __name__ == "__main__":
    fix_workday_companies()
