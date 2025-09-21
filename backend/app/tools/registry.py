from typing import Dict, Any, List
from pydantic import BaseModel
from importlib import import_module

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
    
    def load_all_tools(self):
        """Dynamically load tools from all tool directories"""
        tool_modules = [
            "app.tools.send_email_tool.registry",
            "app.tools.lookup_contact_tool.registry",
            "app.tools.save_email_history_tool.registry",
            "app.tools.add_contact_mapping_tool.registry"
        ]
        
        for module_path in tool_modules:
            try:
                module = import_module(module_path)
                if hasattr(module, 'register_tools'):
                    module.register_tools(self)
            except ImportError as e:
                print(f"Could not import tool module {module_path}: {e}")

# Create global registry instance
tool_registry = ToolRegistry()
tool_registry.load_all_tools()