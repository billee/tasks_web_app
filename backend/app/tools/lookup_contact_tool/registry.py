from app.tools.registry import Tool

def register_tools(registry):
    registry.register_tool(Tool(
        name="lookup_contact",
        description="Look up an email address by contact name",
        parameters={
            "name": {"type": "string", "description": "Contact name to look up"}
        }
    ))