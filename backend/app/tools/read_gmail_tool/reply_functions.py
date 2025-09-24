from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.common.models import User
from .gmail_client import GmailClient
from .schemas import GmailReplyRequest, GmailEmailDetails
from typing import Dict, Any

def get_email_details(user_id: int, message_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific email"""
    try:
        gmail_client = GmailClient()
        
        if not gmail_client.is_configured():
            return {
                "success": False,
                "message": "Gmail API not configured."
            }
        
        service = gmail_client.authenticate(user_id)
        result = gmail_client.get_email_details(message_id)
        
        if result["success"]:
            # Extract basic info from headers
            headers = result["headers"]
            email_details = GmailEmailDetails(
                id=message_id,
                subject=headers.get('Subject', ''),
                from_address=headers.get('From', ''),
                date=headers.get('Date', ''),
                snippet=result["message"].get('snippet', ''),
                body=result["body"],
                thread_id=result.get('thread_id'),
                headers=headers
            )
            
            return {
                "success": True,
                "message": "Email details retrieved successfully",
                "email_details": email_details.dict()
            }
        else:
            return result
            
    except Exception as e:
        print(f"Error getting email details: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to get email details: {str(e)}"
        }

def send_gmail_reply(user_id: int, reply_request: GmailReplyRequest) -> Dict[str, Any]:
    """Send a reply to a Gmail email"""
    try:
        gmail_client = GmailClient()
        
        if not gmail_client.is_configured():
            return {
                "success": False,
                "message": "Gmail API not configured."
            }
        
        service = gmail_client.authenticate(user_id)
        result = gmail_client.send_reply(
            reply_request.original_message_id,
            reply_request.reply_content,
            reply_request.subject,
            reply_request.to_address
        )
        
        return result
        
    except Exception as e:
        print(f"Error sending Gmail reply: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to send reply: {str(e)}"
        }