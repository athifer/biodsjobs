#!/usr/bin/env python3
"""
Debug the comprehensive scraper for Illumina specifically
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers import comprehensive as comprehensive_scraper

async def debug_comprehensive_scraper():
    print("DEBUGGING COMPREHENSIVE SCRAPER FOR ILLUMINA")
    print("=" * 60)
    
    # Test Illumina specifically
    company_token = "illumina"
    
    try:
        jobs = await comprehensive_scraper.fetch_company_jobs(company_token)
        print(f"Jobs returned: {len(jobs)}")
        
        for i, job in enumerate(jobs):
            print(f"{i+1}. {job.get('title', 'No title')}")
            print(f"   Company: {job.get('company', 'No company')}")
            print(f"   URL: {job.get('url', 'No URL')}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_comprehensive_scraper())
