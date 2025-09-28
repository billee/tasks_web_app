from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel 

from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User
from .gmail_client import GmailClient
from .read_functions import read_gmail_inbox, archive_gmail_email, get_email_details


class ArchiveRequest(BaseModel):
    message_id: str


router = APIRouter()

@router.post("/read-inbox")
async def read_inbox_endpoint(
    max_results: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Read emails from Gmail inbox"""
    try:
        # This will handle both local and production authentication
        client = GmailClient()
        service = client.authenticate(current_user.id, db)
        
        emails = client.get_inbox_emails(max_results)
        
        # Format emails for frontend
        formatted_emails = []
        for email in emails:
            formatted_emails.append({
                'id': email['id'],
                'threadId': email.get('threadId'),
                'from_address': email['from'],
                'subject': email['subject'],
                'snippet': email['snippet'],
                'date': email['date']
            })
        
        return {
            "success": True,
            "message": f"Found {len(formatted_emails)} emails in your inbox.",
            "gmail_emails": formatted_emails
        }
        
    except HTTPException as e:
        # If authentication requires OAuth, return the auth URL
        if e.status_code == 401 and hasattr(e, 'detail') and isinstance(e.detail, dict) and 'auth_url' in e.detail:
            return {
                "success": False,
                "message": "Gmail authentication required. Click the button below to authorize access to your Gmail account.",
                "tool_results": [
                    {
                        "type": "oauth_required",
                        "service": "gmail",
                        "auth_url": e.detail['auth_url'],
                        "button_text": "Authorize Gmail Access"
                    }
                ]
            }
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read inbox: {str(e)}")

@router.post("/archive-email")
async def archive_email_endpoint(
    request: ArchiveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a Gmail email"""
    try:
        client = GmailClient()
        service = client.authenticate(current_user.id, db)
        
        result = client.archive_email(message_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive email: {str(e)}")

@router.get("/email-details/{message_id}")
async def get_email_details_endpoint(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed content of a specific email"""
    try:
        client = GmailClient()
        service = client.authenticate(current_user.id, db)
        
        email_body = client.get_email_body(message_id)
        return {
            "success": True,
            "email_body": email_body
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email details: {str(e)}")