import httpx
from datetime import datetime
from typing import List, Dict

async def fetch_company_jobs(company: str) -> List[Dict]:
    """Fetch jobs from Lever for a given company handle.
    Public JSON endpoint: https://api.lever.co/v0/postings/{company}?mode=json
    """
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    jobs = []
    for j in data:
        jobs.append({
            "title": j.get("text") or j.get("title") or "",
            "company": company,
            "location": (j.get("categories", {}) or {}).get("location", ""),
            "url": j.get("hostedUrl") or j.get("applyUrl") or j.get("url"),
            "source": "lever",
            "posted_at": datetime.fromtimestamp(j.get("createdAt", 0)/1000.0) if j.get("createdAt") else datetime.utcnow(),
            "description": j.get("descriptionPlain") or j.get("description") or "",
        })
    return jobs
