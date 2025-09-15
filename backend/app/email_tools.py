# backend/app/email_tools.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.ai_client import ai_client
from .tools.email_registry import email_tool_registry


router = APIRouter(prefix="/email-tools", tags=["email-tools"])

class ChatMessage(BaseModel):
    text: str
    isUser: bool
    time: str

class EmailToolsRequest(BaseModel):
    messages: List[ChatMessage]
    tool_type: str = "email"

class EmailToolsResponse(BaseModel):
    success: bool
    message: Optional[str] = ""  # Make message optional with default empty string
    tool_results: List[Dict[str, Any]] = []
    has_tool_calls: bool = False

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

        return EmailToolsResponse(**result)
        
    except Exception as e:
        print(f"Error in email_tools_chat: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

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