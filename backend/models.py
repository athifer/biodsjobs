from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union

class JobIn(BaseModel):
    title: str
    company: str
    location: str = ""
    url: str
    source: str
    posted_at: Optional[datetime] = None
    description: str = ""
    score: float = 0.0

class JobOut(JobIn):
    id: int
    posted_at: datetime
    score: Optional[Union[float, None]] = None  # Allow None for when no search query
