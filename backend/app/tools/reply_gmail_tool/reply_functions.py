from typing import Dict, Any
from .gmail_reply_client import GmailReplyClient

def send_gmail_reply(user_id: str, thread_id: str, to_email: str, subject: str, 
                    body: str, references: str = None) -> Dict[str, Any]:
    """
    Send a reply to a Gmail thread
    
    Args:
        user_id: The user ID
        thread_id: Gmail thread ID to reply to
        to_email: Recipient email address
        subject: Email subject (should start with 'Re: ')
        body: Reply body content
        references: References header for threading
    
    Returns:
        Dictionary with success status and response data
    """
    client = GmailReplyClient(user_id)
    return client.send_reply(thread_id, to_email, subject, body, references)

def create_gmail_reply_draft(user_id: str, thread_id: str, to_email: str, 
                           subject: str, body: str) -> Dict[str, Any]:
    """
    Create a draft reply in Gmail
    
    Args:
        user_id: The user ID
        thread_id: Gmail thread ID
        to_email: Recipient email address
        subject: Email subject
        body: Draft body content
    
    Returns:
        Dictionary with success status and draft info
    """
    client = GmailReplyClient(user_id)
    return client.create_reply_draft(thread_id, to_email, subject, body)

def format_reply_body(original_content: str, reply_content: str, 
                     include_original: bool = True) -> str:
    """
    Format a reply body with proper quoting
    
    Args:
        original_content: Original email content to quote
        reply_content: New reply content
        include_original: Whether to include original message
    
    Returns:
        Formatted reply body
    """
    if not include_original:
        return reply_content
    
    # Simple formatting for quoted content
    quoted_original = "\n\n--- Original Message ---\n"
    quoted_original += "\n".join(f"> {line}" for line in original_content.split('\n'))
    
    return reply_content + quoted_original

def prepare_reply_subject(original_subject: str) -> str:
    """
    Prepare a reply subject with proper 'Re: ' prefix
    
    Args:
        original_subject: Original email subject
    
    Returns:
        Formatted reply subject
    """
    if original_subject.startswith('Re: '):
        return original_subject
    elif original_subject.startswith('Fwd: '):
        return original_subject.replace('Fwd: ', 'Re: ')
    else:
        return f"Re: {original_subject}"