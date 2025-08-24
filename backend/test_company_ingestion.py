#!/usr/bin/env python3
"""
Test the ingestor for specific companies to see actual job counts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestor import load_companies, scrape_jobs_for_company
from models import Company

async def test_specific_companies():
    print("TESTING SPECIFIC COMPANY INGESTION")
    print("=" * 60)
    
    companies_to_test = [
        "Illumina",
        "Exact Sciences", 
        "Amgen",
        "Pfizer",
        "Moderna"
    ]
    
    # Load all companies
    all_companies = load_companies()
    
    for company_name in companies_to_test:
        print(f"\n🔍 Testing {company_name}:")
        
        # Find the company
        found_company = None
        for company in all_companies:
            if company.company == company_name:
                found_company = company
                break
        
        if not found_company:
            print(f"   ❌ Company not found in database")
            continue
            
        print(f"   Source: {found_company.source}")
        print(f"   URL: {found_company.careers_url}")
        print(f"   Token: {found_company.token}")
        
        try:
            # Try to scrape jobs
            jobs = await scrape_jobs_for_company(found_company)
            print(f"   ✅ Found {len(jobs)} jobs")
            
            if jobs:
                print(f"   Sample job titles:")
                for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                    print(f"     {i+1}. {job.title}")
                if len(jobs) > 3:
                    print(f"     ... and {len(jobs) - 3} more jobs")
            else:
                print(f"   ⚠️  No jobs found - this might be the issue!")
                
        except Exception as e:
            print(f"   ❌ Error scraping: {e}")

if __name__ == "__main__":
    asyncio.run(test_specific_companies())
