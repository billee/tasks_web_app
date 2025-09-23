#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tools.registry import tool_registry

def test_tool_registration():
    print("=== Testing Tool Registration ===")
    tools = tool_registry.get_tools()
    
    print(f"Total tools registered: {len(tools)}")
    
    for tool in tools:
        print(f"\nTool: {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"Parameters: {tool['parameters']}")
    
    # Check if Gmail tool is registered
    gmail_tool = None
    for tool in tools:
        if tool['name'] == 'read_gmail_inbox':
            gmail_tool = tool
            break
    
    if gmail_tool:
        print("\n✅ Gmail tool is properly registered!")
    else:
        print("\n❌ Gmail tool is NOT registered!")

if __name__ == "__main__":
    test_tool_registration()