#!/usr/bin/env python3
"""
Test the ingestor for specific companies to see actual job counts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestor import load_companies
from scrapers import workday as workday_scraper
from scrapers import comprehensive as comprehensive_scraper

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
            if company.get("company") == company_name:
                found_company = company
                break
        
        if not found_company:
            print(f"   ❌ Company not found in database")
            continue
            
        source = found_company.get("source")
        company_token = found_company.get("token", company_name)
        careers_url = found_company.get("careers_url", "N/A")
        
        print(f"   Source: {source}")
        print(f"   URL: {careers_url}")
        print(f"   Token: {company_token}")
        
        try:
            # Try to scrape jobs based on source
            jobs = []
            if source == "workday":
                jobs = await workday_scraper.fetch_company_jobs(company_token)
            elif source == "comprehensive":
                jobs = await comprehensive_scraper.fetch_company_jobs(company_token)
            else:
                print(f"   ⚠️  Source '{source}' not tested in this script")
                continue
                
            print(f"   ✅ Found {len(jobs)} jobs")
            
            if jobs:
                print(f"   Sample job titles:")
                for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                    print(f"     {i+1}. {job.get('title', 'No title')}")
                if len(jobs) > 3:
                    print(f"     ... and {len(jobs) - 3} more jobs")
            else:
                print(f"   ⚠️  No jobs found - this might be the issue!")
                
        except Exception as e:
            print(f"   ❌ Error scraping: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_specific_companies())
