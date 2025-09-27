# In backend/app/tools/read_gmail_tool/oauth_callback.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.auth import get_current_user
from .gmail_client import GmailClient

router = APIRouter()

@router.get("/oauth2callback")
async def oauth_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth 2.0 callback from Google"""
    try:
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
        
        if not state:
            raise HTTPException(
                status_code=400, 
                detail="State parameter missing"
            )
        
        user_id = state
        print(f"Processing OAuth callback for user {user_id}")
        
        # Complete the OAuth flow
        client = GmailClient()
        credentials = client.complete_oauth_flow(code, user_id)
        
        # Store the token in database
        client.store_oauth_token(user_id, credentials, db)
        
        # Return a success page that will close the window
        html_content = """
        <html>
            <head>
                <title>Authentication Successful</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .success-box { 
                        background: rgba(255,255,255,0.1); 
                        padding: 30px; 
                        border-radius: 10px; 
                        backdrop-filter: blur(10px);
                    }
                </style>
            </head>
            <body>
                <div class="success-box">
                    <h1>✅ Authentication Successful!</h1>
                    <p>You can now close this window and return to the application.</p>
                    <button onclick="window.close();" style="padding: 10px 20px; background: white; color: #667eea; border: none; border-radius: 5px; cursor: pointer;">
                        Close Window
                    </button>
                </div>
                <script>
                    // Notify the parent window
                    window.opener.postMessage({type: 'OAUTH_SUCCESS', service: 'gmail'}, '*');
                    // Auto-close after 3 seconds
                    setTimeout(() => window.close(), 3000);
                </script>
            </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        
        error_html = f"""
        <html>
            <head><title>Authentication Failed</title></head>
            <body>
                <h1>❌ Authentication Failed</h1>
                <p>Error: {str(e)}</p>
                <button onclick="window.close();">Close</button>
                <script>
                    window.opener.postMessage({{type: 'OAUTH_ERROR', error: '{str(e)}'}}, '*');
                </script>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)