from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    name: Optional[str] = None  # Add name field to UserCreate as well

class UserResponse(UserBase):
    id: int
    name: Optional[str] = None  # Add this line - this was missing!
    is_active: bool
    is_admin: bool
    created_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True  # This replaces the deprecated 'orm_mode'

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class EmailHistoryResponse(BaseModel):
    id: int
    recipient: str
    subject: str
    content_preview: str
    email_id: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True