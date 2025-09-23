from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GmailEmail(BaseModel):
    id: str
    subject: str
    from_address: str
    date: str
    snippet: str
    thread_id: Optional[str] = None

class GmailReadRequest(BaseModel):
    max_results: Optional[int] = 10

class GmailReadResponse(BaseModel):
    success: bool
    message: str
    emails: List[GmailEmail]
    count: int