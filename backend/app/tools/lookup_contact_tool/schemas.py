from pydantic import BaseModel

class EmailLookupRequest(BaseModel):
    name: str

class EmailLookupResponse(BaseModel):
    success: bool
    email_address: Optional[str] = None
    message: Optional[str] = None