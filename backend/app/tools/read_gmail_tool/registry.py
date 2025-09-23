from app.tools.registry import tool_registry, Tool

# Register Gmail reading tool
tool_registry.register_tool(Tool(
    name="read_gmail_inbox",
    description="Read the user's Gmail inbox and return the latest emails",
    parameters={
        "max_results": {
            "type": "integer", 
            "description": "Maximum number of emails to return (default: 10, max: 50)",
            "default": 10,
            "optional": True
        }
    }
))