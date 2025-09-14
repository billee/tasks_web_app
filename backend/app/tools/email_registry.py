# backend/app/tools/email_registry.py
from typing import Dict, Any, List
from pydantic import BaseModel

class EmailTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class EmailToolRegistry:
    def __init__(self):
        self.tools: Dict[str, EmailTool] = {}
        
    def register_tool(self, tool: EmailTool):
        self.tools[tool.name] = tool
        
    def get_tools(self) -> List[Dict[str, Any]]:
        return [tool.dict() for tool in self.tools.values()]

# Create global registry instance
email_tool_registry = EmailToolRegistry()

# Register email sending tool
email_tool_registry.register_tool(EmailTool(
    name="send_email",
    description="Send an email to a specified email address with AI-generated content",
    parameters={
        "to_email": {"type": "string", "description": "Recipient email address"},
        "subject": {"type": "string", "description": "Email subject"},
        "content_request": {"type": "string", "description": "Description of email content"},
        "tone": {"type": "string", "description": "Email tone (professional, friendly, casual)", "default": "professional"}
    }
))