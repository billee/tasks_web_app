import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .read_functions import read_gmail_inbox_tool

def register_gmail_tool():
    """Ensure the Gmail tool is properly registered"""
    # This function might be called by the main application
    # to ensure the tool is available
    return read_gmail_inbox_tool