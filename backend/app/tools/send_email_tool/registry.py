from app.tools.registry import Tool

def register_tools(registry):
    registry.register_tool(Tool(
        name="send_email",
        description="Send an email to a specified email address with AI-generated content",
        parameters={
            "to_email": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "content_request": {"type": "string", "description": "Description of email content"},
            "tone": {"type": "string", "description": "Email tone (professional, friendly, casual)", "default": "professional"}
        }
    ))