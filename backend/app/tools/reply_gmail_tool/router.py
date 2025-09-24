from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.common.database import get_db
from app.common.auth import get_current_user
from app.common.models import User
from .reply_functions import send_gmail_reply, create_gmail_reply_draft, format_reply_body, prepare_reply_subject
from .schemas import ReplyRequest, ReplyDraftRequest, ReplyResponse

router = APIRouter()

@router.post("/send-reply", response_model=ReplyResponse)
async def send_gmail_reply_endpoint(
    request: ReplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a reply to a Gmail thread"""
    try:
        result = send_gmail_reply(
            user_id=current_user.id,
            thread_id=request.thread_id,
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            references=request.references
        )
        
        return ReplyResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {str(e)}")

@router.post("/create-draft", response_model=ReplyResponse)
async def create_gmail_reply_draft_endpoint(
    request: ReplyDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a draft reply in Gmail"""
    try:
        result = create_gmail_reply_draft(
            user_id=current_user.id,
            thread_id=request.thread_id,
            to_email=request.to_email,
            subject=request.subject,
            body=request.body
        )
        
        return ReplyResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create draft: {str(e)}")

@router.post("/format-reply")
async def format_reply_body_endpoint(
    original_content: str,
    reply_content: str,
    include_original: bool = True
):
    """Format a reply body with proper quoting"""
    formatted_body = format_reply_body(original_content, reply_content, include_original)
    return {"formatted_body": formatted_body}

@router.get("/prepare-subject/{original_subject}")
async def prepare_reply_subject_endpoint(original_subject: str):
    """Prepare a proper reply subject"""
    prepared_subject = prepare_reply_subject(original_subject)
    return {"prepared_subject": prepared_subject}