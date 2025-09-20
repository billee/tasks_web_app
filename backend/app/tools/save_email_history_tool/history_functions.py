from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_admin
from app.models import User, EmailHistory
from app.schemas import EmailHistoryResponse
from typing import List

router = APIRouter()

@router.get("/admin/history", response_model=List[EmailHistoryResponse])
async def get_email_history(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    email_history = db.query(EmailHistory).join(User).order_by(EmailHistory.created_at.desc()).all()
    
    response = []
    for email in email_history:
        response.append(EmailHistoryResponse(
            id=email.id,
            recipient=email.recipient,
            subject=email.subject,
            content_preview=email.content_preview,
            email_id=email.email_id,
            status=email.status,
            created_at=email.created_at,
            user_email=email.user.email
        ))
    
    return response

@router.get("/email-content/{email_id}")
async def get_email_content(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email_history = db.query(EmailHistory).filter(
        EmailHistory.id == email_id,
        EmailHistory.user_id == current_user.id
    ).first()
    
    if not email_history:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {
        "success": True,
        "email_content": email_history.full_content_html
    }