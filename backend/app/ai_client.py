# backend/app/ai_client.py
import openai
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

from app.email_client import email_client

# Load environment variables from root directory
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

class AIClient:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        # Don't raise error if API key is not set, just log a warning
        if not self.openai_api_key:
            print("WARNING: OPENAI_API_KEY environment variable not set. AI functionality will be disabled.")
            self.enabled = False
            return
            
        self.enabled = True
        openai.api_key = self.openai_api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Email tools definition
        self.email_tools = [
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email to a specified email address with AI-generated content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_email": {
                                "type": "string",
                                "description": "The recipient's email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "The email subject line"
                            },
                            "content_request": {
                                "type": "string",
                                "description": "Description of what the email content should be about"
                            },
                            "tone": {
                                "type": "string",
                                "description": "The tone of the email (professional, friendly, casual, formal, etc.)",
                                "default": "professional"
                            }
                        },
                        "required": ["to_email", "subject", "content_request"]
                    }
                }
            }
        ]
    
    def generate_email_content(self, content_request: str, tone: str = "professional") -> str:
        """
        Generate email content based on the request and tone
        """
        # Check if AI client is enabled
        if not self.enabled:
            return "AI service is not configured. Please set OPENAI_API_KEY environment variable."
            
        try:
            prompt = f"""
            Write a {tone} email based on this request: {content_request}
            
            Guidelines:
            - Keep it concise and clear
            - Use appropriate {tone} tone
            - Include a proper greeting and closing
            - Make it engaging and actionable if needed
            - Do not include subject line (that's handled separately)
            
            Write only the email body content:
            """
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional email writer. Generate clear, well-structured email content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating email content: {str(e)}"
    
    def send_email_tool(self, to_email: str, subject: str, content_request: str, tone: str = "professional") -> Dict[str, Any]:
        """
        Tool function to send an email with AI-generated content
        """
        # Check if AI client is enabled
        if not self.enabled:
            return {
                "success": False,
                "message": "AI service is not configured. Please set OPENAI_API_KEY environment variable."
            }
            
        try:
            # Validate email address
            if not email_client.validate_email_address(to_email):
                return {
                    "success": False,
                    "message": f"Invalid email address: {to_email}"
                }
            
            # Generate email content
            email_content = self.generate_email_content(content_request, tone)
            
            # Format as HTML
            html_content = email_client.format_email_html(email_content)
            
            # Send the email
            result = email_client.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Email sent successfully to {to_email}",
                    "details": {
                        "recipient": to_email,
                        "subject": subject,
                        "content_preview": email_content[:100] + "..." if len(email_content) > 100 else email_content,
                        "email_id": result.get("email_id")
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to send email: {result['message']}",
                    "error": result.get("error")
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error in email tool: {str(e)}"
            }
    
    def process_tool_call(self, tool_call) -> Dict[str, Any]:
        """
        Process a tool call from OpenAI
        """
        # Check if AI client is enabled
        if not self.enabled:
            return {
                "success": False,
                "message": "AI service is not configured. Please set OPENAI_API_KEY environment variable."
            }
            
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        if function_name == "send_email":
            return self.send_email_tool(
                to_email=arguments.get("to_email"),
                subject=arguments.get("subject"),
                content_request=arguments.get("content_request"),
                tone=arguments.get("tone", "professional")
            )
        else:
            return {
                "success": False,
                "message": f"Unknown tool: {function_name}"
            }
    
    def chat_with_tools(self, messages: List[Dict[str, str]], tool_type: str = "email") -> Dict[str, Any]:
        """
        Chat with the AI using tools based on the selected tool type
        """
        # Check if AI client is enabled
        if not self.enabled:
            return {
                "success": False,
                "message": "AI service is not configured. Please set OPENAI_API_KEY environment variable.",
                "tool_results": [],
                "has_tool_calls": False
            }
            
        try:
            # Select tools based on tool_type
            tools = self.email_tools if tool_type == "email" else []
            
            # Make the API call
            if tools:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=1000,
                    temperature=0.7
                )
            else:
                # No tools, regular chat
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
            
            message = response.choices[0].message
            tool_results = []
            
            # Process tool calls if any
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_result = self.process_tool_call(tool_call)
                    tool_results.append({
                        "tool_name": tool_call.function.name,
                        "result": tool_result
                    })
            
            return {
                "success": True,
                "message": message.content,
                "tool_results": tool_results,
                "has_tool_calls": len(tool_results) > 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error in AI processing: {str(e)}",
                "tool_results": [],
                "has_tool_calls": False
            }
    
    def regular_chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Regular chat without tools (for backward compatibility)
        """
        # Check if AI client is enabled
        if not self.enabled:
            return "AI service is not configured. Please set OPENAI_API_KEY environment variable."
            
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize global AI client instance
# This will not raise an error even if OPENAI_API_KEY is not set
ai_client = AIClient()