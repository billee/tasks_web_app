import base64
import os
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, Any

class GmailReplyClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.service = None
        
    def _get_credentials(self) -> Credentials:
        """Get Gmail credentials for the user"""
        # TODO: Implement credential retrieval from database
        # This should fetch stored OAuth tokens for the user
        from app.common.database import get_db
        from app.common.models import User
        from sqlalchemy.orm import Session
        
        db: Session = next(get_db())
        user = db.query(User).filter(User.id == self.user_id).first()
        
        if not user or not user.gmail_credentials:
            raise Exception("Gmail credentials not found for user")
            
        # Assuming credentials are stored as a JSON string
        import json
        creds_dict = json.loads(user.gmail_credentials)
        creds = Credentials.from_authorized_user_info(creds_dict)
        return creds
    
    def _build_service(self):
        """Build Gmail service instance"""
        creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
    
    def send_reply(self, thread_id: str, to_email: str, subject: str, body: str, 
                  references: str = None) -> Dict[str, Any]:
        """Send a reply to a Gmail thread"""
        if not self.service:
            self._build_service()
            
        try:
            # Create the email message
            message = MIMEText(body, 'html' if '<' in body else 'plain')
            message['To'] = to_email
            message['Subject'] = subject
            message['In-Reply-To'] = references
            message['References'] = references
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send the message as a reply to the thread
            sent_message = self.service.users().messages().send(
                userId='me',
                body={
                    'raw': raw_message,
                    'threadId': thread_id
                }
            ).execute()
            
            return {
                "success": True,
                "message_id": sent_message['id'],
                "thread_id": thread_id,
                "details": {
                    "recipient": to_email,
                    "subject": subject,
                    "content_preview": body[:100] + "..." if len(body) > 100 else body
                }
            }
            
        except HttpError as error:
            return {
                "success": False,
                "error": str(error),
                "message": f"Failed to send reply: {error}"
            }
    
    def create_reply_draft(self, thread_id: str, to_email: str, subject: str, 
                          body: str) -> Dict[str, Any]:
        """Create a draft reply"""
        if not self.service:
            self._build_service()
            
        try:
            message = MIMEText(body, 'html' if '<' in body else 'plain')
            message['To'] = to_email
            message['Subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={
                    'message': {
                        'raw': raw_message,
                        'threadId': thread_id
                    }
                }
            ).execute()
            
            return {
                "success": True,
                "draft_id": draft['id'],
                "thread_id": thread_id
            }
            
        except HttpError as error:
            return {
                "success": False,
                "error": str(error),
                "message": f"Failed to create draft: {error}"
            }