from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, EmailHistory
from app.email_client import email_client
from pydantic import BaseModel

router = APIRouter()

class EmailComposition(BaseModel):
    recipient: str
    subject: str
    body: str
    composition_id: Optional[str] = None

@router.post("/approve-and-send")
async def approve_and_send_email(
    email_data: EmailComposition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        html_content = email_client.format_email_html(email_data.body)
        result = email_client.send_email(
            to_email=email_data.recipient,
            subject=email_data.subject,
            html_content=html_content
        )
        
        if result["success"]:
            email_history = EmailHistory(
                user_id=current_user.id,
                recipient=email_data.recipient,
                subject=email_data.subject,
                content_preview=email_data.body[:100] + "..." if len(email_data.body) > 100 else email_data.body,
                full_content_html=html_content,
                email_id=result.get("email_id"),
                status="sent"
            )
            db.add(email_history)
            db.commit()
            
            return {
                "success": True, 
                "message": "Email sent successfully",
                "email_id": email_history.id
            }
        else:
            return {"success": False, "message": result["message"]}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-draft")
async def save_email_draft(
    email_data: EmailComposition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Implementation for saving draft
    pass

@router.delete("/cancel-composition/{composition_id}")
async def cancel_email_composition(
    composition_id: str,
    current_user: User = Depends(get_current_user)
):
    return {"success": True, "message": "Composition canceled"}