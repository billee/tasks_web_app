from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.models import User
from .gmail_client import GmailClient
from .schemas import GmailReadResponse, GmailEmail
from typing import Dict, Any

def read_gmail_inbox(user_id: int, max_results: int = 10) -> Dict[str, Any]:
    """Read Gmail inbox for a specific user"""
    try:
        gmail_client = GmailClient()
        
        # Check if Gmail is configured
        if not gmail_client.is_configured():
            return {
                "success": False,
                "message": "Gmail API not configured. Please set up OAuth credentials.",
                "emails": []
            }
        
        # Authenticate and get service
        service = gmail_client.authenticate(user_id)
        
        # Get inbox emails
        emails_data = gmail_client.get_inbox_emails(max_results)
        
        # Format emails for response
        formatted_emails = []
        for email in emails_data:
            formatted_emails.append(GmailEmail(
                id=email['id'],
                subject=email['subject'],
                from_address=email['from'],
                date=email['date'],
                snippet=email['snippet'],
                thread_id=email.get('threadId')
            ))
        
        return {
            "success": True,
            "message": f"Retrieved {len(formatted_emails)} emails from inbox",
            "emails": formatted_emails,
            "count": len(formatted_emails)
        }
        
    except Exception as e:
        print(f"Error reading Gmail inbox: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to read Gmail inbox: {str(e)}",
            "emails": []
        }

def archive_gmail_email(user_id: int, message_id: str) -> Dict[str, Any]:
    """Archive a Gmail email for a specific user"""
    try:
        gmail_client = GmailClient()
        
        # Check if Gmail is configured
        if not gmail_client.is_configured():
            return {
                "success": False,
                "message": "Gmail API not configured. Please set up OAuth credentials."
            }
        
        # Authenticate and get service
        service = gmail_client.authenticate(user_id)
        
        # Archive the email
        result = gmail_client.archive_email(message_id)
        
        return result
        
    except Exception as e:
        print(f"Error archiving Gmail email: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to archive email: {str(e)}"
        }

def read_gmail_inbox_tool(max_results: int = 10, user_id: int = None, db: Session = None) -> Dict[str, Any]:
    """Tool function to be called by AI client"""
    return read_gmail_inbox(user_id, max_results)