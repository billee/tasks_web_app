from typing import Dict, Any, List
from pydantic import BaseModel

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool
        
    def get_tools(self) -> List[Dict[str, Any]]:
        return [tool.dict() for tool in self.tools.values()]

# Create global registry instance
tool_registry = ToolRegistry()

# Manually register all tools to avoid circular imports
tool_registry.register_tool(Tool(
    name="send_email",
    description="Send an email to a specified email address with AI-generated content",
    parameters={
        "to_email": {"type": "string", "description": "Recipient email address"},
        "subject": {"type": "string", "description": "Email subject"},
        "content_request": {"type": "string", "description": "Description of email content"},
        "tone": {"type": "string", "description": "Email tone (professional, friendly, casual)", "default": "professional"}
    }
))

tool_registry.register_tool(Tool(
    name="lookup_contact",
    description="Look up an email address by contact name",
    parameters={
        "name": {"type": "string", "description": "Contact name to look up"}
    }
))

tool_registry.register_tool(Tool(
    name="save_email_history",
    description="Save a record of a sent email to the history database",
    parameters={
        "recipient": {"type": "string", "description": "Email recipient"},
        "subject": {"type": "string", "description": "Email subject"},
        "content_preview": {"type": "string", "description": "Preview of email content"},
        "email_id": {"type": "string", "description": "Unique identifier for the email", "optional": True}
    }
))

tool_registry.register_tool(Tool(
    name="add_contact_mapping",
    description="Add or update a name-to-email mapping for a contact",
    parameters={
        "name": {"type": "string", "description": "Contact name"},
        "email_address": {"type": "string", "description": "Email address for the contact"}
    }
))


tool_registry.register_tool(Tool(
    name="read_gmail_inbox",
    description="Read the user's Gmail inbox to check for new emails, view recent messages, or monitor incoming mail. Use this when the user asks to read their inbox, check emails, or see recent messages.",
    parameters={
        "max_results": {
            "type": "integer", 
            "description": "Maximum number of emails to return (default: 10, max: 50)",
            "default": 10,
            "optional": True
        }
    }
))

tool_registry.register_tool(Tool(
    name="reply_gmail",
    description="Reply to a Gmail email thread. Use this when the user wants to reply to an email in their Gmail inbox.",
    parameters={
        "thread_id": {"type": "string", "description": "The Gmail thread ID of the email to reply to"},
        "to_email": {"type": "string", "description": "The email address to reply to"},
        "subject": {"type": "string", "description": "The subject of the reply, typically starting with 'Re: '"},
        "body": {"type": "string", "description": "The body content of the reply"},
        "references": {
            "type": "string", 
            "description": "References header for proper email threading",
            "optional": True
        }
    }
))