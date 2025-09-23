from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User
from .read_functions import read_gmail_inbox
from .schemas import GmailReadRequest

router = APIRouter()

@router.post("/read-inbox")
async def read_inbox_endpoint(
    request: GmailReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API endpoint to read Gmail inbox"""
    try:
        result = read_gmail_inbox(current_user.id, request.max_results)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inbox-status")
async def check_inbox_status(
    current_user: User = Depends(get_current_user)
):
    """Check if Gmail inbox is accessible"""
    try:
        gmail_client = GmailClient()
        is_configured = gmail_client.is_configured()
        
        return {
            "configured": is_configured,
            "message": "Gmail API is configured" if is_configured else "Gmail API not configured"
        }
        
    except Exception as e:
        return {
            "configured": False,
            "message": f"Error checking Gmail status: {str(e)}"
        }