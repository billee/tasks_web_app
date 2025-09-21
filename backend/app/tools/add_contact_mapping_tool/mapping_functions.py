from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User, EmailNameMap
from pydantic import BaseModel

router = APIRouter()

def add_name_email_mapping(name: str, email_address: str, user_id: int, db: Session):
    existing = db.query(EmailNameMap).filter(
        EmailNameMap.user_id == user_id,
        EmailNameMap.name.ilike(name)
    ).first()
    
    if existing:
        existing.email_address = email_address
    else:
        new_mapping = EmailNameMap(
            user_id=user_id,
            name=name,
            email_address=email_address
        )
        db.add(new_mapping)
    
    db.commit()

class NameEmailMapping(BaseModel):
    name: str
    email_address: str

@router.post("/name-mappings")
async def add_email_name_mapping(
    mapping: NameEmailMapping,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        add_name_email_mapping(
            name=mapping.name,
            email_address=mapping.email_address,
            user_id=current_user.id,
            db=db
        )
        return {"success": True, "message": "Mapping added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/name-mappings")
async def get_all_name_mappings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mappings = db.query(EmailNameMap).filter(
        EmailNameMap.user_id == current_user.id
    ).all()
    
    return [{"name": m.name, "email_address": m.email_address} for m in mappings]