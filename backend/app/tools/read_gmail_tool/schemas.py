from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GmailEmail(BaseModel):
    id: str
    subject: str
    from_address: str
    date: str
    snippet: str
    thread_id: Optional[str] = None
    body: str = ""  # Add body field for full email content

class GmailReadRequest(BaseModel):
    max_results: Optional[int] = 10

class GmailReadResponse(BaseModel):
    success: bool
    message: str
    emails: List[GmailEmail]
    count: int

class GmailReplyRequest(BaseModel):
    original_message_id: str
    reply_content: str
    subject: str
    to_address: str

class GmailReplyResponse(BaseModel):
    success: bool
    message: str
    message_id: Optional[str] = None
    thread_id: Optional[str] = None

class GmailEmailDetails(BaseModel):
    id: str
    subject: str
    from_address: str
    date: str
    snippet: str
    body: str
    thread_id: Optional[str] = None
    headers: Dict[str, str]