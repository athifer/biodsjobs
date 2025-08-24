"""
Advanced scraping utilities for handling complex job sites.
Includes support for JavaScript-heavy sites, API detection, and dynamic content loading.
"""

import asyncio
import httpx
import json
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class AdvancedScraper:
    """Enhanced scraper with multiple strategies for different site types."""
    
    def __init__(self):
        self.biotech_keywords = [
            'scientist', 'research', 'data', 'computational', 'bioinformatics', 
            'clinical', 'genomics', 'biostatistics', 'biologist', 'engineer',
            'analyst', 'director', 'manager', 'associate', 'principal', 'lead',
            'machine learning', 'ai', 'software', 'informatics', 'statistics',
            'bioinformatics', 'computational biology', 'drug discovery',
            'clinical trial', 'regulatory affairs', 'quality assurance'
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }

    async def detect_site_type(self, url: str, client: httpx.AsyncClient) -> str:
        """Detect what type of job site we're dealing with."""
        try:
            response = await client.get(url, headers=self.headers)
            content = response.text.lower()
            
            # Check for known platforms
            if 'workday' in content or 'myworkdayjobs.com' in url:
                return 'workday'
            elif 'greenhouse.io' in content or 'greenhouse.io' in url:
                return 'greenhouse' 
            elif 'lever.co' in content or 'lever.co' in url:
                return 'lever'
            elif 'bamboohr.com' in content or 'bamboohr.com' in url:
                return 'bamboo'
            elif 'icims.com' in content:
                return 'icims'
            elif 'taleo' in content:
                return 'taleo'
            elif len(content) < 15000 and 'json' in content:
                return 'spa'  # Single Page Application
            else:
                return 'standard'
                
        except Exception:
            return 'unknown'

    async def try_workday_apis(self, base_url: str, client: httpx.AsyncClient) -> List[Dict]:
        """Try multiple Workday API patterns."""
        jobs = []
        
        # Extract base domain for API calls
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common Workday API endpoints
        api_patterns = [
            f"{base_url}/fs/searchPaginated/jobs",
            f"{base_url}/searchPaginated/jobs",
            f"{base_domain}/wday/cxs/jobs/api/search",
            f"{base_url}/jobs",
            f"{base_url}/api/jobs",
        ]
        
        for api_url in api_patterns:
            try:
                # Try POST with pagination
                payload = {
                    "appliedFacets": {},
                    "limit": 50,
                    "offset": 0,
                    "searchText": ""
                }
                
                response = await client.post(
                    api_url, 
                    json=payload,
                    headers={**self.headers, 'Content-Type': 'application/json', 'Accept': 'application/json'}
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        jobs_data = self._extract_jobs_from_api_response(data)
                        if jobs_data:
                            print(f"✅ Found {len(jobs_data)} jobs via API: {api_url}")
                            return jobs_data
                    except json.JSONDecodeError:
                        continue
                        
                # Try GET request
                response = await client.get(api_url, headers={**self.headers, 'Accept': 'application/json'})
                if response.status_code == 200:
                    try:
                        data = response.json()
                        jobs_data = self._extract_jobs_from_api_response(data)
                        if jobs_data:
                            print(f"✅ Found {len(jobs_data)} jobs via GET API: {api_url}")
                            return jobs_data
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                continue
                
        return []

    def _extract_jobs_from_api_response(self, data: Dict) -> List[Dict]:
        """Extract job data from various API response formats."""
        jobs = []
        
        # Try different response structures
        jobs_data = None
        if isinstance(data, dict):
            for key in ['jobPostings', 'jobs', 'searchResults', 'body', 'data', 'total', 'results']:
                if key in data:
                    potential_jobs = data[key]
                    if isinstance(potential_jobs, list) and len(potential_jobs) > 0:
                        jobs_data = potential_jobs
                        break
                    elif isinstance(potential_jobs, dict) and 'jobs' in potential_jobs:
                        jobs_data = potential_jobs['jobs']
                        break
        
        if not jobs_data:
            return []
            
        for job_item in jobs_data[:30]:  # Limit processing
            try:
                title = (job_item.get('title') or job_item.get('jobTitle') or 
                        job_item.get('name') or job_item.get('positionTitle', ''))
                
                if not title:
                    continue
                    
                # Filter for biotech relevance
                if any(keyword.lower() in title.lower() for keyword in self.biotech_keywords):
                    location = (job_item.get('location') or job_item.get('primaryLocation') or 
                              job_item.get('locationsText') or 'Not specified')
                    
                    job_url = (job_item.get('url') or job_item.get('jobUrl') or 
                              job_item.get('externalUrl') or job_item.get('applyUrl', ''))
                    
                    jobs.append({
                        'title': title[:200],
                        'location': location,
                        'url': job_url,
                        'raw_data': job_item
                    })
                    
            except Exception:
                continue
                
        return jobs

    async def try_icims_api(self, base_url: str, client: httpx.AsyncClient) -> List[Dict]:
        """Try to find iCIMS API endpoints."""
        try:
            # Common iCIMS patterns
            parsed = urlparse(base_url)
            company_subdomain = parsed.netloc.split('.')[0]
            
            api_urls = [
                f"https://{company_subdomain}.icims.com/jobs/search",
                f"https://{company_subdomain}-atriumworks.icims.com/jobs/search",
                f"{base_url}/search",
                f"{base_url}/api/jobs"
            ]
            
            for api_url in api_urls:
                try:
                    response = await client.get(api_url, headers=self.headers)
                    if response.status_code == 200 and 'json' in response.headers.get('content-type', ''):
                        data = response.json()
                        jobs = self._extract_jobs_from_api_response(data)
                        if jobs:
                            print(f"✅ Found {len(jobs)} jobs via iCIMS API: {api_url}")
                            return jobs
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        return []

    async def enhanced_html_scraping(self, url: str, client: httpx.AsyncClient) -> List[Dict]:
        """Enhanced HTML scraping with multiple strategies."""
        try:
            response = await client.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            # Strategy 1: Look for structured job data in JSON-LD
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                        jobs.append(self._parse_json_ld_job(data))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'JobPosting':
                                jobs.append(self._parse_json_ld_job(item))
                except json.JSONDecodeError:
                    continue
            
            if jobs:
                return jobs
            
            # Strategy 2: Advanced CSS selector patterns
            job_selectors = [
                '[data-testid*="job"], [data-test*="job"]',
                '.job-listing, .job-item, .job-card, .position',
                '[class*="job"], [class*="position"], [class*="role"]',
                'li[data-automation-id], div[data-automation-id]',
                '.careers-position, .career-opportunity'
            ]
            
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:20]:
                        job = self._extract_job_from_element(element, url)
                        if job:
                            jobs.append(job)
                    if jobs:
                        break
            
            # Strategy 3: Look for jobs based on biotech keywords in text
            if not jobs:
                jobs = self._find_jobs_by_keywords(soup, url)
            
            return jobs
            
        except Exception as e:
            print(f"Error in enhanced HTML scraping: {e}")
            return []

    def _parse_json_ld_job(self, data: Dict) -> Dict:
        """Parse job data from JSON-LD structured data."""
        title = data.get('title', '')
        location = ''
        if 'jobLocation' in data:
            loc_data = data['jobLocation']
            if isinstance(loc_data, dict):
                location = loc_data.get('address', {}).get('addressLocality', '')
            elif isinstance(loc_data, str):
                location = loc_data
        
        return {
            'title': title,
            'location': location or 'Not specified',
            'url': data.get('url', ''),
            'description': data.get('description', '')[:300]
        }

    def _extract_job_from_element(self, element, base_url: str) -> Optional[Dict]:
        """Extract job information from a DOM element."""
        try:
            # Try to find title
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.job-title', '[data-testid*="title"]', 'a']
            title = ''
            title_link = ''
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title_elem.name == 'a' and title_elem.get('href'):
                        title_link = title_elem.get('href')
                    elif not title_link:
                        link_elem = title_elem.find('a', href=True)
                        if link_elem:
                            title_link = link_elem.get('href')
                    if title and len(title) > 5:
                        break
            
            if not title or len(title) < 5:
                return None
                
            # Check biotech relevance
            if not any(keyword.lower() in title.lower() for keyword in self.biotech_keywords):
                return None
            
            # Try to find location
            location_selectors = ['.location', '.job-location', '[data-testid*="location"]']
            location = 'Not specified'
            for selector in location_selectors:
                loc_elem = element.select_one(selector)
                if loc_elem:
                    location = loc_elem.get_text(strip=True)
                    break
            
            # Build full URL
            if title_link:
                if title_link.startswith('http'):
                    url = title_link
                else:
                    url = urljoin(base_url, title_link)
            else:
                url = base_url
            
            return {
                'title': title[:200],
                'location': location,
                'url': url,
                'description': f"Position at company - {title[:100]}"
            }
            
        except Exception:
            return None

    def _find_jobs_by_keywords(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Find jobs by searching for biotech keywords in the page."""
        jobs = []
        
        # Find all text elements containing biotech keywords
        for keyword in self.biotech_keywords[:10]:  # Use first 10 keywords to avoid too many matches
            elements = soup.find_all(string=re.compile(rf'\b{re.escape(keyword)}\b', re.I))
            
            for text_node in elements[:5]:  # Limit to avoid spam
                parent = text_node.parent
                if parent and parent.name in ['h1', 'h2', 'h3', 'h4', 'a', 'span', 'div']:
                    text = parent.get_text(strip=True)
                    if 20 <= len(text) <= 150:  # Reasonable title length
                        # Look for a link in parent or nearby elements
                        link_elem = parent if parent.name == 'a' else parent.find('a', href=True)
                        link_url = base_url
                        if link_elem and link_elem.get('href'):
                            href = link_elem.get('href')
                            link_url = href if href.startswith('http') else urljoin(base_url, href)
                        
                        jobs.append({
                            'title': text,
                            'location': 'Not specified',
                            'url': link_url,
                            'description': f"Position - {text[:100]}"
                        })
                        
                        if len(jobs) >= 10:
                            break
            
            if len(jobs) >= 10:
                break
        
        return jobs

    async def scrape_company_advanced(self, company_name: str, url: str) -> List[Dict[str, Any]]:
        """Main method to scrape a company using advanced techniques."""
        jobs = []
        
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                print(f"🔍 Analyzing {company_name} at {url}")
                
                # Detect site type
                site_type = await self.detect_site_type(url, client)
                print(f"📊 Site type detected: {site_type}")
                
                # Try appropriate scraping strategy
                if site_type == 'workday':
                    jobs = await self.try_workday_apis(url, client)
                elif site_type == 'icims':
                    jobs = await self.try_icims_api(url, client)
                
                # If API methods failed, try enhanced HTML scraping
                if not jobs:
                    print(f"🌐 Trying enhanced HTML scraping for {company_name}")
                    jobs = await self.enhanced_html_scraping(url, client)
                
                # Format jobs with company info
                formatted_jobs = []
                for job in jobs[:15]:  # Limit to 15 jobs per company
                    formatted_jobs.append({
                        "title": job.get('title', ''),
                        "company": company_name,
                        "location": job.get('location', 'Not specified'),
                        "url": job.get('url', url),
                        "source": "advanced",
                        "posted_at": datetime.utcnow(),
                        "description": job.get('description', f"Position at {company_name}")
                    })
                
                print(f"✅ Found {len(formatted_jobs)} jobs for {company_name}")
                return formatted_jobs
                
        except Exception as e:
            print(f"❌ Error scraping {company_name}: {e}")
            return []
