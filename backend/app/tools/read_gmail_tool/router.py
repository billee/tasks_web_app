from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User
from .read_functions import read_gmail_inbox, archive_gmail_email
from .schemas import GmailReadRequest
from pydantic import BaseModel
from .gmail_client import GmailClient

router = APIRouter()

class ArchiveRequest(BaseModel):
    message_id: str

# Try to import reply functions, but handle if they don't exist yet
try:
    from .reply_functions import get_email_details, send_gmail_reply
    from .schemas import GmailReplyRequest
    REPLY_FUNCTIONS_AVAILABLE = True
except ImportError:
    print("Reply functions not available yet - skipping reply endpoints")
    REPLY_FUNCTIONS_AVAILABLE = False

@router.post("/read-inbox")
async def read_inbox_endpoint(
    request: GmailReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API endpoint to read Gmail inbox"""
    try:
        result = read_gmail_inbox(current_user.id, request.max_results, db)
        return result
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (like auth required)
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/archive-email")
async def archive_email_endpoint(
    request: ArchiveRequest,  # Change to use request body
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API endpoint to archive a Gmail email"""
    try:
        result = archive_gmail_email(current_user.id, request.message_id, db)
        return result
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (like auth required)
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inbox-status")
async def check_inbox_status(
    current_user: User = Depends(get_current_user)
):
    """Check if Gmail inbox is accessible"""
    try:
        from .gmail_client import GmailClient
        gmail_client = GmailClient()
        is_configured = gmail_client.is_configured()
        is_production = gmail_client.is_production
        
        return {
            "configured": is_configured,
            "environment": "production" if is_production else "local",
            "message": "Gmail API is configured" if is_configured else "Gmail API not configured"
        }
        
    except Exception as e:
        return {
            "configured": False,
            "message": f"Error checking Gmail status: {str(e)}"
        }

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working"""
    return {"message": "Gmail tool router is working!"}

@router.get("/oauth2callback")
async def gmail_oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle Gmail OAuth callback"""
    
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authorization failed: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code not provided"
        )
    
    try:
        gmail_client = GmailClient()
        
        # Complete the OAuth flow
        credentials = gmail_client.complete_oauth_flow(code, current_user.id)
        
        # Store the credentials in database
        gmail_client.store_oauth_token(current_user.id, credentials, db)
        
        return {
            "success": True,
            "message": "Gmail authentication successful! You can now read your inbox.",
            "redirect_url": "/chat"  # Frontend can redirect user back to chat
        }
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete Gmail authentication: {str(e)}"
        )

@router.get("/auth-status")
async def check_gmail_auth_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has valid Gmail authentication"""
    
    try:
        gmail_client = GmailClient()
        has_valid_token = gmail_client.has_valid_token(current_user.id, db)
        
        return {
            "authenticated": has_valid_token,
            "message": "Gmail authentication is active" if has_valid_token else "Gmail authentication required"
        }
        
    except Exception as e:
        return {
            "authenticated": False,
            "message": f"Error checking Gmail auth status: {str(e)}"
        }

@router.post("/auth-start")
async def start_gmail_auth(
    current_user: User = Depends(get_current_user)
):
    """Start Gmail OAuth flow"""
    
    try:
        gmail_client = GmailClient()
        auth_url = gmail_client.get_auth_url(current_user.id)
        
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Please visit the auth_url to authorize Gmail access"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Gmail authentication: {str(e)}"
        )

# Only add reply endpoints if the functions are available
if REPLY_FUNCTIONS_AVAILABLE:
    @router.get("/email-details/{message_id}")
    async def get_email_details_endpoint(
        message_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """API endpoint to get detailed email information"""
        try:
            result = get_email_details(current_user.id, message_id)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/send-reply")
    async def send_reply_endpoint(
        request: GmailReplyRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """API endpoint to send a reply to a Gmail email"""
        try:
            result = send_gmail_reply(current_user.id, request)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))