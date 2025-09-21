from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User, EmailHistory
from app.core.ai_client import ai_client
from app.tools.send_email_tool.email_client import email_client
from app.common.schemas import EmailHistoryResponse
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
        
        # Process with AI client (pass user_id and db)
        result = ai_client.chat_with_tools(
            openai_messages, 
            request.tool_type,
            user_id=current_user.id,
            db=db
        )
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