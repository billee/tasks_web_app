from pydantic import BaseModel
from datetime import datetime

class EmailContentResponse(BaseModel):
    success: bool
    email_content: str