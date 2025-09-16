# backend/app/ai_client.py
from openai import OpenAI
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
        print(f"OpenAI API Key: {self.openai_api_key[:10]}...")  # Print first 10 chars
        # Don't raise error if API key is not set, just log a warning
        if not self.openai_api_key:
            print("WARNING: OPENAI_API_KEY environment variable not set. AI functionality will be disabled.")
            self.enabled = False
            return
        else:
            print("OpenAI API Key found and loaded successfully")   
            
        self.enabled = True
        self.client = OpenAI(api_key=self.openai_api_key)
        # openai.api_key = self.openai_api_key
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
            
            response = self.client.chat.completions.create(
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
            
            # Return composition data instead of sending immediately
            return {
                "success": True,
                "pending_approval": True,
                "email_composition": {
                    "recipient": to_email,
                    "subject": subject,
                    "body": email_content,
                    "tone": tone
                }
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
                "message": "AI service is not configured. Please set OPENAI_API_KEY environment variable."
            }
        
        try:
            # Select tools based on tool_type
            tools = []
            if tool_type == "email":
                tools = self.email_tools
            
            # Make the initial API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful business assistant. Use the available tools when appropriate to help users with their tasks."}
                ] + messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                max_tokens=1000,
                temperature=0.7
            )
            
            message = response.choices[0].message
            tool_results = []
            
            # Check if the AI wants to use tools
            if message.tool_calls:
                # Process each tool call
                for tool_call in message.tool_calls:
                    tool_result = self.process_tool_call(tool_call)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "tool_name": tool_call.function.name,
                        "result": tool_result
                    })
                


                    pending_email_compositions = []

                    # Check if we have email compositions pending approval
                    for tool_result in tool_results:
                        if (tool_result["tool_name"] == "send_email" and 
                            tool_result["result"].get("pending_approval") and 
                            tool_result["result"].get("email_composition")):
                            pending_email_compositions.append(tool_result)

                    if pending_email_compositions:
                        # Return the first email composition for approval
                        email_composition = pending_email_compositions[0]["result"]["email_composition"]
                        response_data = {
                            "success": True,
                            "message": "I've composed an email for your review:",
                            "email_composition": email_composition,
                            "has_tool_calls": True
                        }
                        
                        # Include tool_results only if needed for debugging
                        if os.getenv("DEBUG", "False").lower() == "true":
                            response_data["tool_results"] = tool_results
                        else:
                            response_data["tool_results"] = []
                        
                        return response_data
                




                # Create tool messages for the conversation
                tool_messages = []
                for i, tool_call in enumerate(message.tool_calls):
                    tool_messages.append({
                        "role": "tool",
                        "content": json.dumps(tool_results[i]["result"]),
                        "tool_call_id": tool_call.id
                    })
                
                # Get final response from AI after tool execution
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful business assistant. Provide a friendly summary of the completed actions."}
                    ] + messages + [
                        {"role": "assistant", "content": message.content, "tool_calls": message.tool_calls}
                    ] + tool_messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                message_content = final_response.choices[0].message.content
            else:
                # No tool calls, just return the regular response
                message_content = message.content
            
            # If we have tool results, format a friendly response
            if tool_results:
                friendly_responses = []
                for tool_result in tool_results:
                    if tool_result["tool_name"] == "send_email":
                        result = tool_result["result"]
                        if result["success"] and not result.get("pending_approval"):
                            friendly_responses.append(
                                f"✅ I've sent an email to {result['details']['recipient']} "
                                f"with subject '{result['details']['subject']}'. "
                                f"The email has been successfully delivered!"
                            )
                        elif result["success"] and result.get("pending_approval"):
                            # This case is handled above, but keeping for completeness
                            pass
                        else:
                            friendly_responses.append(
                                f"❌ Sorry, I couldn't send the email. Error: {result['message']}"
                            )
                
                # Use the friendly response instead of the technical one
                if friendly_responses:
                    message_content = "\n".join(friendly_responses)
            
            return {
                "success": True,
                "message": message_content,
                "tool_results": tool_results,
                "has_tool_calls": len(tool_results) > 0
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error in AI chat: {str(e)}"
            }
    
    def regular_chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Regular chat without tools (for backward compatibility)
        """
        # Check if AI client is enabled
        if not self.enabled:
            return "AI service is not configured. Please set OPENAI_API_KEY environment variable."
            
        try:
            response = self.client.chat.completions.create(
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