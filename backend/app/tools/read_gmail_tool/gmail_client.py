# In backend/app/tools/read_gmail_tool/gmail_client.py

import os
import base64
from pathlib import Path
from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailClient:
    def __init__(self):
        # Add modify scope for archiving
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'  # Add this for archiving
        ]
        self.service = None
        
        # Get the correct path - tokens should be in the same directory as credentials.json
        self.root_dir = Path(__file__).parent.parent.parent  # This goes up to app directory
        self.credentials_path = self.root_dir / "core" / "credentials.json"
        self.tokens_dir = self.root_dir / "core" / "tokens"  # Tokens in core/tokens/
        
    def is_configured(self):
        """Check if Gmail API is configured"""
        return os.path.exists(self.credentials_path)
        

    def authenticate(self, user_id):
        """Authenticate with Gmail API for a specific user"""
        # Check if credentials file exists
        if not self.is_configured():
            print(f"Credentials file not found at: {self.credentials_path}")
            raise HTTPException(
                status_code=501, 
                detail="Gmail credentials not configured. Please set up OAuth credentials."
            )
            
        creds = None
        # Store tokens in core/tokens directory
        token_path = self.tokens_dir / f"{user_id}_token.json"
        
        # Create tokens directory if it doesn't exist
        os.makedirs(self.tokens_dir, exist_ok=True)
        
        print(f"Looking for token at: {token_path}")
        print(f"Token directory exists: {os.path.exists(self.tokens_dir)}")
        
        if os.path.exists(token_path):
            try:
                print("Found existing token file, loading...")
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                print("Token loaded successfully")
                
                # Check if token has the required scopes
                if creds and creds.valid:
                    token_scopes = creds.scopes if creds.scopes else []
                    required_scopes = set(self.SCOPES)
                    current_scopes = set(token_scopes)
                    
                    if not required_scopes.issubset(current_scopes):
                        print(f"Token missing required scopes. Required: {required_scopes}, Current: {current_scopes}")
                        print("Deleting token to force re-authentication with new scopes...")
                        os.remove(token_path)
                        creds = None
                        
            except Exception as e:
                print(f"Error loading token: {e}")
                # Remove invalid token file
                if os.path.exists(token_path):
                    os.remove(token_path)
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Refreshing expired token...")
                    creds.refresh(Request())
                    print("Token refreshed successfully")
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    # Remove invalid token file and force re-authentication
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    creds = None
            
            if not creds:
                try:
                    print(f"Starting new authentication flow...")
                    print(f"Using credentials file at: {self.credentials_path}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), self.SCOPES)
                    # Use a fixed port and make sure it matches Google Cloud Console
                    creds = flow.run_local_server(port=8080, prompt='consent')
                    print("Authentication successful")
                except Exception as e:
                    print(f"Authentication error: {e}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to authenticate with Gmail: {str(e)}"
                    )
            
            # Save the credentials for the next run (only if we have valid creds)
            if creds:
                print(f"Saving token to: {token_path}")
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                print("Token saved successfully")
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to obtain valid credentials after authentication attempt"
                )
        
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service



    def get_inbox_emails(self, max_results=10):
        """Get emails from inbox"""
        if not self.service:
            raise Exception("Gmail service not initialized. Call authenticate() first.")
            
        try:
            print(f"Fetching {max_results} emails from inbox...")
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            print(f"Found {len(messages)} messages")
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                
                headers = msg.get('payload', {}).get('headers', [])
                email_data = {
                    'id': msg['id'],
                    'snippet': msg.get('snippet', ''),
                    'subject': '',
                    'from': '',
                    'date': '',
                    'threadId': msg.get('threadId')  # Add threadId for archiving
                }
                
                for header in headers:
                    if header['name'] == 'Subject':
                        email_data['subject'] = header['value']
                    elif header['name'] == 'From':
                        email_data['from'] = header['value']
                    elif header['name'] == 'Date':
                        email_data['date'] = header['value']
                
                emails.append(email_data)
            
            print(f"Processed {len(emails)} emails")
            return emails
            
        except HttpError as error:
            print(f'Gmail API error occurred: {error}')
            return []

    def archive_email(self, message_id):
        """Archive an email by removing the INBOX label"""
        if not self.service:
            raise Exception("Gmail service not initialized. Call authenticate() first.")
            
        try:
            # Remove the 'INBOX' label to archive the email
            # This moves it to "All Mail" but removes it from inbox
            body = {
                'removeLabelIds': ['INBOX']
            }
            
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            print(f"Email {message_id} archived successfully")
            return {
                "success": True,
                "message": "Email archived successfully",
                "archived_email": result
            }
            
        except HttpError as error:
            print(f'Gmail API error occurred while archiving: {error}')
            return {
                "success": False,
                "message": f"Failed to archive email: {str(error)}"
            }

    def get_email_body(self, message_id):
        """Get the full body content of an email"""
        if not self.service:
            raise Exception("Gmail service not initialized. Call authenticate() first.")
            
        try:
            # Get the full message with body content
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return self._extract_email_body(message.get('payload', {}))
            
        except HttpError as error:
            print(f'Error getting email body: {error}')
            return "Unable to retrieve email content"

    def _extract_email_body(self, payload):
        """Extract the email body from the message payload"""
        body = ""
        
        # Check if the payload has parts (multipart message)
        if 'parts' in payload:
            for part in payload['parts']:
                # Look for text/plain part first
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                # Fallback to text/html if plain text not found
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        # Remove HTML tags for plain text display
                        import re
                        body = re.sub('<[^<]+?>', '', body)
        else:
            # Simple message without parts
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body if body else "No content available"