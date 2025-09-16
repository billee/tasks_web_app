# backend/app/email_tools.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.admin import require_admin
from sqlalchemy.orm import Session
from app.models import EmailHistory
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.ai_client import ai_client
from .tools.email_registry import email_tool_registry
from app.schemas import EmailHistoryResponse 


router = APIRouter(prefix="/email-tools", tags=["email-tools"])

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
    message: Optional[str] = ""  # Make message optional with default empty string
    tool_results: List[Dict[str, Any]] = []
    has_tool_calls: bool = False
    email_composition: Optional[EmailCompositionResponse] = None  # Add this field




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
        
        # Convert messages to OpenAI format
        openai_messages = []
        
        for msg in request.messages:
            role = "user" if msg.isUser else "assistant"
            openai_messages.append({
                "role": role,
                "content": msg.text
            })
        
        print(f"Sending to AI client: {openai_messages}")
        
        # Process with AI client
        result = ai_client.chat_with_tools(openai_messages, request.tool_type)
        print(f"AI client result: {result}")
        
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
        
        # Return the response as-is (including email_composition if present)
        response_data = {
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "tool_results": [],  # Empty array to hide technical details
            "has_tool_calls": result.get("has_tool_calls", False)
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
            has_tool_calls=False
        )




@router.get("/tools/available")
async def get_available_tools(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available email tools
    """
    return {
        "tools": email_tool_registry.get_tools()
    }


@router.get("/admin/history", response_model=List[EmailHistoryResponse])
async def get_email_history(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all email history (admin only)
    """
    email_history = db.query(EmailHistory).join(User).order_by(EmailHistory.created_at.desc()).all()
    
    # Convert to response format with user email
    response = []
    for email in email_history:
        response.append(EmailHistoryResponse(
            id=email.id,
            recipient=email.recipient,
            subject=email.subject,
            content_preview=email.content_preview,
            email_id=email.email_id,
            status=email.status,
            created_at=email.created_at,
            user_email=email.user.email  # Add user email
        ))
    
    return response

# Add request models
class EmailComposition(BaseModel):
    recipient: str
    subject: str
    body: str
    composition_id: Optional[str] = None

# Add new endpoints
@router.post("/approve-and-send")
async def approve_and_send_email(
    email_data: EmailComposition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Format as HTML and send
        html_content = email_client.format_email_html(email_data.body)
        result = email_client.send_email(
            to_email=email_data.recipient,
            subject=email_data.subject,
            html_content=html_content
        )
        
        if result["success"]:
            # Store in history
            email_history = EmailHistory(
                user_id=current_user.id,
                recipient=email_data.recipient,
                subject=email_data.subject,
                content_preview=email_data.body[:100] + "..." if len(email_data.body) > 100 else email_data.body,
                email_id=result.get("email_id"),
                status="sent"
            )
            db.add(email_history)
            db.commit()
            
            return {"success": True, "message": "Email sent successfully"}
        else:
            return {"success": False, "message": result["message"]}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-draft")
async def save_email_draft(
    email_data: EmailComposition,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Implementation for saving draft
    pass

@router.delete("/cancel-composition/{composition_id}")
async def cancel_email_composition(
    composition_id: str,
    current_user: User = Depends(get_current_user)
):
    # Implementation for canceling composition
    return {"success": True, "message": "Composition canceled"}