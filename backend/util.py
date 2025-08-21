from typing import List, Dict
import re
from .settings import settings

KEYWORDS = [k.strip().lower() for k in settings.KEYWORDS.split(',') if k.strip()]

def score_job(job: Dict) -> float:
    """Very simple relevance scoring based on keyword matches in title + description."""
    text = f"{job.get('title','')}\n{job.get('description','')}".lower()
    score = 0
    for kw in KEYWORDS:
        if re.search(r"\\b" + re.escape(kw) + r"\\b", text):
            score += 1
    # Weight title hits slightly more
    title = (job.get('title') or '').lower()
    score += sum(1 for kw in KEYWORDS if kw in title)
    return float(score)
