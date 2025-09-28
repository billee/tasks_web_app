import base64
import os
import json
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, Any
from google.auth.transport.requests import Request

class GmailReplyClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.service = None
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.send'
        ]
        
        # Get the correct path - match the read tool's path calculation
        self.root_dir = Path(__file__).parent.parent.parent  # This goes up to app directory
        self.credentials_path = self.root_dir / "core" / "credentials.json"
        self.tokens_dir = self.root_dir / "core" / "tokens"  # Tokens in core/tokens/
        
    def _get_credentials(self) -> Credentials:
        """Get Gmail credentials for the user - supports both local and production"""
        # Environment detection
        is_production = os.getenv('RENDER') or os.getenv('ENVIRONMENT') == 'production'
        
        if is_production:
            # Production: Use database tokens
            return self._get_production_credentials()
        else:
            # Local: Use file-based tokens
            return self._get_local_credentials()
    
    def _get_local_credentials(self) -> Credentials:
        """Get credentials from local token file"""
        # Check if credentials file exists
        if not os.path.exists(self.credentials_path):
            raise Exception("Gmail credentials not configured. Please set up OAuth credentials.")
            
        creds = None
        # Store tokens in core/tokens directory
        token_path = self.tokens_dir / f"{self.user_id}_token.json"
        
        # Create tokens directory if it doesn't exist
        os.makedirs(self.tokens_dir, exist_ok=True)
        
        print(f"Looking for token at: {token_path}")
        print(f"Token directory exists: {os.path.exists(self.tokens_dir)}")
        
        if os.path.exists(token_path):
            try:
                print("Found existing token file, loading...")
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                print("Token loaded successfully")
                
                # Check if the token has the required scopes for sending
                if creds and creds.valid:
                    token_scopes = creds.scopes if creds.scopes else []
                    print(f"Token scopes: {token_scopes}")
                    
                    # Check if we have sufficient permissions
                    if not any('gmail.modify' in scope for scope in token_scopes):
                        raise Exception("Token does not have gmail.modify scope required for sending replies")
                        
            except Exception as e:
                print(f"Error loading token: {e}")
                raise Exception(f"Failed to load Gmail token: {str(e)}")
        else:
            raise Exception(f"Gmail token not found for user {self.user_id}. Please authenticate first.")
        
        return creds

    def _get_production_credentials(self) -> Credentials:
        """Get credentials from database for production"""
        try:
            from app.common.database import get_db
            from app.tools.read_gmail_tool.gmail_client import GmailClient
            
            # Get database session
            db = next(get_db())
            
            # Use the existing GmailClient to get tokens from database
            gmail_client = GmailClient()
            credentials = gmail_client.get_oauth_token_from_db(self.user_id, db)
            
            if not credentials:
                raise Exception(f"No Gmail token found for user {self.user_id}. Please authenticate first.")
            
            if not credentials.valid:
                if credentials.expired and credentials.refresh_token:
                    try:
                        credentials.refresh(Request())
                        # Update the refreshed token in database
                        gmail_client.store_oauth_token(self.user_id, credentials, db)
                        print("Token refreshed successfully")
                    except Exception as e:
                        print(f"Error refreshing token: {e}")
                        raise Exception("Token expired and could not be refreshed. Please re-authenticate.")
                else:
                    raise Exception("Invalid credentials. Please re-authenticate.")
            
            return credentials
            
        except Exception as e:
            raise Exception(f"Failed to get production credentials: {str(e)}")
    
    def _build_service(self):
        """Build Gmail service instance"""
        creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=creds)
    
    def _format_email_body(self, body: str) -> str:
        """Format the email body with proper HTML formatting"""
        # Convert plain text to HTML with proper formatting
        html_body = body.replace('\n', '<br>')
        
        # Add basic HTML structure and styling
        formatted_body = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333;">
            {html_body}
        </div>
        """
        return formatted_body
    
    def send_reply(self, thread_id: str, to_email: str, subject: str, body: str, 
                  references: str = None) -> Dict[str, Any]:
        """Send a reply to a Gmail thread using existing permissions"""
        if not self.service:
            self._build_service()
            
        try:
            # Format the body with HTML
            formatted_body = self._format_email_body(body)
            
            # Create a multipart message (both HTML and plain text)
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            if references:
                message['In-Reply-To'] = references
                message['References'] = references
            
            # Add both HTML and plain text versions
            message.attach(MIMEText(formatted_body, 'html'))
            message.attach(MIMEText(body, 'plain'))
            
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
            error_msg = str(error)
            if 'insufficient' in error_msg.lower() or 'permission' in error_msg.lower():
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "Insufficient permissions to send replies. Please re-authenticate with Gmail."
                }
            else:
                return {
                    "success": False,
                    "error": error_msg,
                    "message": f"Failed to send reply: {error}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to send reply: {e}"
            }
    
    def create_reply_draft(self, thread_id: str, to_email: str, subject: str, 
                          body: str) -> Dict[str, Any]:
        """Create a draft reply"""
        if not self.service:
            self._build_service()
            
        try:
            # Format the body with HTML
            formatted_body = self._format_email_body(body)
            
            # Create a multipart message for draft
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add both HTML and plain text versions
            message.attach(MIMEText(formatted_body, 'html'))
            message.attach(MIMEText(body, 'plain'))
            
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

    def has_valid_token(self) -> bool:
        """Check if user has a valid OAuth token"""
        try:
            creds = self._get_credentials()
            return creds and creds.valid
        except Exception:
            return False