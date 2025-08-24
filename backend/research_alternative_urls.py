#!/usr/bin/env python3
"""
Research alternative career page URLs for the problematic companies
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def research_alternative_urls():
    print("RESEARCHING ALTERNATIVE CAREER URLS")
    print("=" * 60)
    
    companies_to_research = {
        "Illumina": [
            "https://illumina.wd1.myworkdayjobs.com/illumina-careers",
            "https://www.illumina.com/careers.html",
            "https://careers.illumina.com",
            "https://www.illumina.com/company/careers/job-opportunities.html"
        ],
        "Pfizer": [
            "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers",
            "https://www.pfizer.com/careers",
            "https://careers.pfizer.com",
            "https://www.pfizer.com/about/careers/career-opportunities"
        ],
        "Moderna": [
            "https://modernatx.wd1.myworkdayjobs.com/M_tx",
            "https://www.modernatx.com/careers",
            "https://careers.modernatx.com",
            "https://www.modernatx.com/en-US/careers"
        ],
        "Gilead": [
            "https://gilead.wd1.myworkdayjobs.com/gileadcareers",
            "https://www.gilead.com/careers",
            "https://careers.gilead.com",
            "https://www.gilead.com/about/company/careers"
        ],
        "Bristol Myers Squibb": [
            "https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS",
            "https://www.bms.com/careers",
            "https://careers.bms.com",
            "https://www.bms.com/about-us/careers.html"
        ],
        "Vertex": [
            "https://vrtx.wd501.myworkdayjobs.com/vertex_careers",
            "https://www.vrtx.com/careers",
            "https://careers.vrtx.com",
            "https://www.verteximaging.com/careers"
        ]
    }
    
    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    ) as client:
        
        for company, urls in companies_to_research.items():
            print(f"\n🔍 {company}")
            
            best_url = None
            best_score = 0
            
            for url in urls:
                try:
                    print(f"  Testing: {url}")
                    response = await client.get(url)
                    status = response.status_code
                    content_length = len(response.text)
                    
                    print(f"    Status: {status}, Length: {content_length}")
                    
                    if status == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Score the page based on job-related content
                        score = 0
                        
                        # Check for job-related keywords
                        job_keywords = ['job', 'career', 'position', 'opportunity', 'opening']
                        for keyword in job_keywords:
                            elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
                            score += min(len(elements), 10)  # Cap at 10 per keyword
                        
                        # Look for job links
                        job_links = soup.find_all('a', href=True)
                        job_related_links = [link for link in job_links if 
                                           any(pattern in link.get('href', '').lower() for pattern in 
                                               ['/job', 'position', 'career', 'opportunity'])]
                        score += min(len(job_related_links), 20)
                        
                        # Look for biotech-related job titles
                        biotech_keywords = ['scientist', 'research', 'data', 'engineer', 'analyst', 'director']
                        for keyword in biotech_keywords:
                            elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
                            score += min(len(elements), 5)
                        
                        # Check if it has substantial content (not just a redirect page)
                        if content_length > 10000:
                            score += 10
                        
                        print(f"    Score: {score}")
                        
                        if score > best_score:
                            best_score = score
                            best_url = url
                            
                        # Show some job content if found
                        job_elements = soup.find_all(string=lambda text: text and 
                                                    any(word in text.lower() for word in ['scientist', 'engineer', 'data']) and
                                                    len(text.strip()) > 20)
                        if job_elements:
                            print(f"    Sample job content: {job_elements[0][:100]}...")
                            
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            if best_url:
                print(f"  🎯 Best URL for {company}: {best_url} (score: {best_score})")
            else:
                print(f"  ❌ No working URLs found for {company}")

if __name__ == "__main__":
    asyncio.run(research_alternative_urls())
