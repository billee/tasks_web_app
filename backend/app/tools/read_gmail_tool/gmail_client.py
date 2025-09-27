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
from sqlalchemy.orm import Session
from datetime import datetime

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
                "redirect_uris": [
                    os.getenv('GOOGLE_OAUTH_REDIRECT_URI_PROD', 'https://tasks-web-app-h343.onrender.com/email-tools/oauth2callback') if self.is_production 
                    else os.getenv('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:8000/email-tools/oauth2callback')
                ]
            }
        }

    def authenticate(self, user_id, db: Session = None):
        """Authenticate with Gmail API - uses different methods for local vs production"""
        if not self.is_configured():
            error_msg = ("Gmail API not configured. "
                        if self.is_production 
                        else "Gmail credentials not configured. Please set up OAuth credentials.")
            raise HTTPException(status_code=501, detail=error_msg)
        
        if self.is_production:
            return self._authenticate_production(user_id, db)
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

    def _authenticate_production(self, user_id, db: Session = None):
        """Production authentication using database-stored tokens"""
        try:
            print("Starting production authentication...")
            
            if not db:
                raise HTTPException(
                    status_code=500,
                    detail="Database session required for production authentication"
                )
            
            # Try to get existing token from database
            creds = self.get_oauth_token_from_db(user_id, db)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        print("Refreshing expired token...")
                        creds.refresh(Request())
                        # Update token in database
                        self.store_oauth_token(user_id, creds, db)
                        print("Token refreshed successfully")
                    except Exception as e:
                        print(f"Error refreshing token: {e}")
                        creds = None
                
                if not creds:
                    # No valid token, need to start OAuth flow
                    auth_url = self.get_auth_url(user_id)
                    raise HTTPException(
                        status_code=401,
                        detail={
                            "message": "Gmail authentication required",
                            "auth_url": auth_url,
                            "instructions": "Please visit the auth_url to authenticate Gmail access"
                        }
                    )
            
            self.service = build('gmail', 'v1', credentials=creds)
            return self.service
            
        except HTTPException:
            raise
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
    
    def get_auth_url(self, user_id):
        """Generate OAuth authorization URL for production"""
        try:
            client_config = self.get_production_client_config()
            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri=client_config['web']['redirect_uris'][0]
            )
            
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=str(user_id)  # Include user_id in state for callback
            )
            
            return auth_url
            
        except Exception as e:
            raise Exception(f"Failed to generate auth URL: {str(e)}")
    
    def complete_oauth_flow(self, authorization_code, user_id):
        """Complete OAuth flow with authorization code"""
        try:
            client_config = self.get_production_client_config()
            flow = Flow.from_client_config(
                client_config,
                scopes=self.SCOPES,
                redirect_uri=client_config['web']['redirect_uris'][0]
            )
            
            # Exchange authorization code for credentials
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            return credentials
            
        except Exception as e:
            raise Exception(f"Failed to complete OAuth flow: {str(e)}")
    
    def store_oauth_token(self, user_id, credentials, db: Session):
        """Store OAuth token in database"""
        try:
            from app.common.models import OAuthToken
            
            # Convert credentials to JSON
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            # Check if token already exists
            existing_token = db.query(OAuthToken).filter(
                OAuthToken.user_id == user_id,
                OAuthToken.service == 'gmail'
            ).first()
            
            if existing_token:
                # Update existing token
                existing_token.token_data = token_data
                existing_token.updated_at = datetime.utcnow()
            else:
                # Create new token
                oauth_token = OAuthToken(
                    user_id=user_id,
                    service='gmail',
                    token_data=token_data
                )
                db.add(oauth_token)
            
            db.commit()
            print(f"OAuth token stored for user {user_id}")
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to store OAuth token: {str(e)}")
    
    def get_oauth_token_from_db(self, user_id, db: Session):
        """Retrieve OAuth token from database"""
        try:
            from app.common.models import OAuthToken
            
            oauth_token = db.query(OAuthToken).filter(
                OAuthToken.user_id == user_id,
                OAuthToken.service == 'gmail'
            ).first()
            
            if not oauth_token:
                return None
            
            token_data = oauth_token.token_data
            
            # Reconstruct credentials from stored data
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Set expiry if available
            if token_data.get('expiry'):
                from datetime import datetime
                credentials.expiry = datetime.fromisoformat(token_data['expiry'])
            
            return credentials
            
        except Exception as e:
            print(f"Error retrieving OAuth token: {e}")
            return None
    
    def has_valid_token(self, user_id, db: Session):
        """Check if user has a valid OAuth token"""
        try:
            credentials = self.get_oauth_token_from_db(user_id, db)
            return credentials and credentials.valid
        except Exception:
            return False