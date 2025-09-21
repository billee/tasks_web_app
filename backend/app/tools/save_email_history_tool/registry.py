from app.tools.registry import Tool

def register_tools(registry):
    registry.register_tool(Tool(
        name="save_email_history",
        description="Save a record of a sent email to the history database",
        parameters={
            "recipient": {"type": "string", "description": "Email recipient"},
            "subject": {"type": "string", "description": "Email subject"},
            "content_preview": {"type": "string", "description": "Preview of email content"},
            "email_id": {"type": "string", "description": "Unique identifier for the email", "optional": True}
        }
    ))