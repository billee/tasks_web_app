from pydantic import BaseModel, Field
from typing import Optional

class ReplyRequest(BaseModel):
    thread_id: str = Field(..., description="Gmail thread ID to reply to")
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Reply subject")
    body: str = Field(..., description="Reply body content")
    references: Optional[str] = Field(None, description="References header for threading")

class ReplyDraftRequest(BaseModel):
    thread_id: str = Field(..., description="Gmail thread ID")
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Draft subject")
    body: str = Field(..., description="Draft body content")

class ReplyResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    draft_id: Optional[str] = None
    details: Optional[dict] = None
    error: Optional[str] = None