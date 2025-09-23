# Map tool names to their actual functions
from app.tools.read_gmail_tool.read_functions import read_gmail_inbox_tool
from app.tools.send_email_tool.send_functions import send_email_tool
from app.tools.lookup_contact_tool.lookup_functions import lookup_contact_tool
from app.tools.add_contact_mapping_tool.mapping_functions import add_contact_mapping_tool
from app.tools.save_email_history_tool.history_functions import save_email_history_tool

TOOL_MAPPINGS = {
    "read_gmail_inbox": read_gmail_inbox_tool,
    "send_email": send_email_tool,
    "lookup_contact": lookup_contact_tool,
    "add_contact_mapping": add_contact_mapping_tool,
    "save_email_history": save_email_history_tool
}

def get_tool_function(tool_name):
    return TOOL_MAPPINGS.get(tool_name)