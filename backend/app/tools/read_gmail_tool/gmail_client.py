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
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
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
            except Exception as e:
                print(f"Error loading token: {e}")
                # Remove invalid token file
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
                    creds = None
            else:
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
            
            # Save the credentials for the next run
            print(f"Saving token to: {token_path}")
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            print("Token saved successfully")
        
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
                    'date': ''
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