from app.tools.registry import Tool

def register_tools(registry):
    registry.register_tool(Tool(
        name="add_contact_mapping",
        description="Add or update a name-to-email mapping for a contact",
        parameters={
            "name": {"type": "string", "description": "Contact name"},
            "email_address": {"type": "string", "description": "Email address for the contact"}
        }
    ))