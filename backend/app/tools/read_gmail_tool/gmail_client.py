# In backend/app/tools/read_gmail_tool/gmail_client.py

import os
import base64
import json
from pathlib import Path
from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailClient:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.service = None
        
        # Environment detection
        self.is_production = os.getenv('RENDER', False) or os.getenv('ENVIRONMENT') == 'production'
        
        # Local file paths (preserve existing logic)
        self.root_dir = Path(__file__).parent.parent.parent
        self.credentials_path = self.root_dir / "core" / "credentials.json"
        self.tokens_dir = self.root_dir / "core" / "tokens"
        
    def is_configured(self):
        """Check if Gmail API is configured for current environment"""
        if self.is_production:
            # Production: Check environment variables
            client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
            print(f"Production Gmail config check - Client ID: {'Found' if client_id else 'Missing'}, Client Secret: {'Found' if client_secret else 'Missing'}")
            return all([client_id, client_secret])
        else:
            # Local: Check credentials file
            local_configured = os.path.exists(self.credentials_path)
            print(f"Local Gmail config check - Credentials file: {'Found' if local_configured else 'Missing'}")
            return local_configured
    
    def get_production_client_config(self):
        """Get OAuth client config from environment variables for production"""
        return {
            "web": {
                "client_id": os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:8080/oauth2callback')]
            }
        }

    def authenticate(self, user_id):
        """Authenticate with Gmail API - uses different methods for local vs production"""
        if not self.is_configured():
            error_msg = ("Gmail API not configured. "
                        if self.is_production 
                        else "Gmail credentials not configured. Please set up OAuth credentials.")
            raise HTTPException(status_code=501, detail=error_msg)
        
        if self.is_production:
            return self._authenticate_production(user_id)
        else:
            return self._authenticate_local(user_id)

    def _authenticate_local(self, user_id):
        """Original local authentication method - PRESERVED EXACTLY"""
        creds = None
        token_path = self.tokens_dir / f"{user_id}_token.json"
        
        # Create tokens directory if it doesn't exist
        os.makedirs(self.tokens_dir, exist_ok=True)
        
        print(f"Local auth: Looking for token at: {token_path}")
        
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
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    creds = None
            
            if not creds:
                try:
                    print(f"Starting new authentication flow...")
                    print(f"Using credentials file at: {self.credentials_path}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), self.SCOPES)
                    creds = flow.run_local_server(port=8080, prompt='consent')
                    print("Authentication successful")
                except Exception as e:
                    print(f"Authentication error: {e}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to authenticate with Gmail: {str(e)}"
                    )
            
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

    def _authenticate_production(self, user_id):
        """Production authentication using environment variables"""
        try:
            print("Starting production authentication...")
            
            # Get client config from environment variables
            client_config = self.get_production_client_config()
            print(f"Production client config created for client_id: {client_config['web']['client_id'][:20]}...")
            
            # For production, we need to implement a proper OAuth flow
            # For now, we'll use a simplified approach that requires manual setup
            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri=client_config['web']['redirect_uris'][0]
            )
            
            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # In production, we need to handle the OAuth flow properly
            # For now, we'll return an error with instructions
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Gmail authentication required for production",
                    "auth_url": auth_url,
                    "instructions": "Please visit the auth_url to authenticate and then use the provided code with the /oauth2callback endpoint"
                }
            )
            
        except Exception as e:
            print(f"Production authentication error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Production Gmail authentication failed: {str(e)}"
            )

    # KEEP ALL EXISTING METHODS EXACTLY AS THEY ARE
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
                    'threadId': msg.get('threadId')
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
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        import re
                        body = re.sub('<[^<]+?>', '', body)
        else:
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body if body else "No content available"