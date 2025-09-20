from pydantic import BaseModel
from typing import Optional

class EmailComposition(BaseModel):
    recipient: str
    subject: str
    body: str
    composition_id: Optional[str] = None

class SendEmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[int] = None