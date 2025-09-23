from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User, EmailHistory
from app.core.ai_client import ai_client
from app.tools.send_email_tool.email_client import email_client
from app.common.schemas import EmailHistoryResponse
from app.tools.read_gmail_tool.schemas import GmailEmail
from app.tools.read_gmail_tool.read_functions import read_gmail_inbox
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

# Pydantic models for chat functionality
class ChatMessage(BaseModel):
    text: str
    isUser: bool
    time: str

class EmailToolsRequest(BaseModel):
    messages: List[ChatMessage]
    tool_type: str = "email"

class EmailCompositionResponse(BaseModel):
    recipient: str
    subject: str
    body: str
    tone: str

class EmailToolsResponse(BaseModel):
    success: bool
    message: Optional[str] = ""
    tool_results: List[Dict[str, Any]] = []
    has_tool_calls: bool = False
    email_composition: Optional[EmailCompositionResponse] = None
    gmail_emails: Optional[List[GmailEmail]] = None

@router.post("/chat", response_model=EmailToolsResponse)
async def email_tools_chat(
    request: EmailToolsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process chat messages with email tools enabled
    """
    try:
        print(f"Email tools chat request received: {request}")
        
        # Check if user is explicitly asking to read Gmail
        user_message = request.messages[-1].text if request.messages and request.messages else ""
        should_read_gmail = any(phrase in user_message.lower() for phrase in [
            "read my inbox", "check my email", "read my email", 
            "check inbox", "show my emails", "read gmail", "view my inbox",
            "open my inbox", "get my emails", "fetch my emails"
        ])
        
        # If user explicitly asks to read Gmail and we're in email tools mode, call tool directly
        if should_read_gmail and request.tool_type == 'email':
            print("User requested Gmail reading, calling tool directly")
            gmail_result = read_gmail_inbox(current_user.id, 10)
            
            if gmail_result["success"]:
                return EmailToolsResponse(
                    success=True,
                    message=f"I found {gmail_result['count']} emails in your inbox. Here are your recent emails:",
                    tool_results=[],
                    has_tool_calls=False,
                    gmail_emails=gmail_result["emails"]
                )
            else:
                return EmailToolsResponse(
                    success=False,
                    message=gmail_result["message"],
                    tool_results=[],
                    has_tool_calls=False,
                    gmail_emails=None
                )
        
        # Convert messages to OpenAI format
        openai_messages = []
        
        for msg in request.messages:
            role = "user" if msg.isUser else "assistant"
            openai_messages.append({
                "role": role,
                "content": msg.text
            })
        
        print(f"Sending to AI client: {openai_messages}")
        
        # Process with AI client (pass user_id and db)
        result = ai_client.chat_with_tools(
            openai_messages, 
            request.tool_type,
            user_id=current_user.id,
            db=db
        )
        print(f"AI client result: {result}")
        
        # Check if the result contains Gmail emails from read_gmail_inbox tool
        gmail_emails = None
        if result.get("tool_results"):
            for tool_result in result["tool_results"]:
                if tool_result["tool_name"] == "read_gmail_inbox":
                    if tool_result["result"]["success"] and "emails" in tool_result["result"]:
                        gmail_emails = []
                        for email_data in tool_result["result"]["emails"]:
                            gmail_emails.append(GmailEmail(
                                id=email_data.get("id", ""),
                                subject=email_data.get("subject", ""),
                                from_address=email_data.get("from_address", email_data.get("from", "")),
                                date=email_data.get("date", ""),
                                snippet=email_data.get("snippet", ""),
                                thread_id=email_data.get("thread_id")
                            ))
                    break
        
        # Store email history only if email was actually sent (has details)
        if result.get("tool_results"):
            for tool_result in result["tool_results"]:
                if (tool_result["tool_name"] == "send_email" and 
                    tool_result["result"]["success"] and 
                    "details" in tool_result["result"]):
                    # Create email history record
                    email_history = EmailHistory(
                        user_id=current_user.id,
                        recipient=tool_result["result"]["details"]["recipient"],
                        subject=tool_result["result"]["details"]["subject"],
                        content_preview=tool_result["result"]["details"]["content_preview"],
                        email_id=tool_result["result"]["details"].get("email_id"),
                        status="sent"
                    )
                    db.add(email_history)
                    db.commit()
        
        # Return the response including gmail_emails if available
        response_data = {
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "tool_results": [],  # Empty array to hide technical details
            "has_tool_calls": result.get("has_tool_calls", False),
            "gmail_emails": gmail_emails
        }

        # Add email_composition to response if present
        if "email_composition" in result:
            response_data["email_composition"] = EmailCompositionResponse(**result["email_composition"])
        
        print(f"Returning response: {response_data}")
        return EmailToolsResponse(**response_data)
        
    except Exception as e:
        print(f"Error in email_tools_chat: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a more specific error response
        return EmailToolsResponse(
            success=False,
            message="I'm having trouble processing your email request. Please try again or contact support if the issue persists.",
            tool_results=[],
            has_tool_calls=False,
            gmail_emails=None
        )

# Existing endpoints (keep these if they exist in your original file)
@router.get("/history", response_model=List[EmailHistoryResponse])
async def get_email_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email history for current user"""
    history = db.query(EmailHistory).filter(
        EmailHistory.user_id == current_user.id
    ).order_by(EmailHistory.created_at.desc()).all()
    return history

@router.get("/admin/history", response_model=List[EmailHistoryResponse])
async def get_admin_email_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all email history (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    history = db.query(EmailHistory).order_by(EmailHistory.created_at.desc()).all()
    return history

# Add this endpoint to check registered tools
@router.get("/available-tools")
async def get_available_tools():
    """Get list of available tools for debugging"""
    from app.tools.registry import tool_registry
    tools = tool_registry.get_tools()
    return {"tools": tools}