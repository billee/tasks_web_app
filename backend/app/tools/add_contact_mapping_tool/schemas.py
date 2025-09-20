from pydantic import BaseModel

class NameEmailMapping(BaseModel):
    name: str
    email_address: str

class MappingResponse(BaseModel):
    success: bool
    message: str

class ContactMapping(BaseModel):
    name: str
    email_address: str