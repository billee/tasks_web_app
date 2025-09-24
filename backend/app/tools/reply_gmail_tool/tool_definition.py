from pydantic import BaseModel, Field

class ReplyGmailTool(BaseModel):
    thread_id: str = Field(..., description="The Gmail thread ID of the email to reply to")
    to_email: str = Field(..., description="The email address to reply to")
    subject: str = Field(..., description="The subject of the reply, typically starting with 'Re: '")
    body: str = Field(..., description="The body content of the reply")
    references: str = Field(None, description="References header for proper email threading")

    class Config:
        schema_extra = {
            "name": "reply_gmail",
            "description": "Reply to a Gmail email thread. Use this when the user wants to reply to an email in their Gmail inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "The Gmail thread ID of the email to reply to"
                    },
                    "to_email": {
                        "type": "string",
                        "description": "The email address to reply to"
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the reply, typically starting with 'Re: '"
                    },
                    "body": {
                        "type": "string",
                        "description": "The body content of the reply"
                    },
                    "references": {
                        "type": "string",
                        "description": "References header for proper email threading"
                    }
                },
                "required": ["thread_id", "to_email", "subject", "body"]
            }
        }