import httpx
from datetime import datetime
from typing import List, Dict

async def fetch_company_jobs(company: str) -> List[Dict]:
    """Fetch jobs from Greenhouse for a given company board token.
    Public JSON endpoint: https://boards-api.greenhouse.io/v1/boards/{company}/jobs
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "title": j.get("title", ""),
            "company": company,
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url"),
            "source": "greenhouse",
            "posted_at": datetime.fromisoformat(j.get("updated_at" , "1970-01-01T00:00:00Z").replace("Z","+00:00")),
            "description": j.get("content") or "",
        })
    return jobs
