from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, EmailNameMap
from pydantic import BaseModel

router = APIRouter()

def lookup_email_by_name(name: str, user_id: int, db: Session) -> Optional[str]:
    mapping = db.query(EmailNameMap).filter(
        EmailNameMap.user_id == user_id,
        EmailNameMap.name.ilike(name)
    ).first()
    
    return mapping.email_address if mapping else None

class EmailLookupRequest(BaseModel):
    name: str

@router.get("/name-mappings/{name}")
async def get_email_by_name(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email_address = lookup_email_by_name(name, current_user.id, db)
    if email_address:
        return {"success": True, "email_address": email_address}
    else:
        return {"success": False, "message": "No mapping found for this name"}