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
            },
            {
                "type": "function",
                "function": {
                    "name": "lookup_email_by_name",
                    "description": "Look up an email address by a person's name from the user's personal contact database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the person to look up"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_name_email_mapping",
                    "description": "Add a new name-to-email mapping to the user's personal contact database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the person"
                            },
                            "email_address": {
                                "type": "string",
                                "description": "The email address to associate with this name"
                            }
                        },
                        "required": ["name", "email_address"]
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
    
    def lookup_email_by_name_tool(self, name: str, user_id: int, db) -> Dict[str, Any]:
        """
        Tool function to look up email by name
        """
        from app.email_tools import lookup_email_by_name
        email_address = lookup_email_by_name(name, user_id, db)
        
        if email_address:
            return {
                "success": True,
                "email_address": email_address,
                "message": f"Found email address for {name}: {email_address}"
            }
        else:
            # Instead of just returning an error, return a special flag to indicate we need the user's input
            return {
                "success": False,
                "needs_email_input": True,
                "name": name,
                "message": f"I couldn't find an email address for {name} in your contacts. Could you please provide their email address?"
            }
    
    def add_name_email_mapping_tool(self, name: str, email_address: str, user_id: int, db) -> Dict[str, Any]:
        """
        Tool function to add a name-email mapping
        """
        from app.email_tools import add_name_email_mapping
        
        try:
            add_name_email_mapping(name, email_address, user_id, db)
            return {
                "success": True,
                "message": f"Added mapping: {name} -> {email_address}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error adding mapping: {str(e)}"
            }
    
    def process_tool_call(self, tool_call, user_id: int = None, db = None) -> Dict[str, Any]:
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
        elif function_name == "lookup_email_by_name":
            if not user_id or not db:
                return {
                    "success": False,
                    "message": "User context required for name lookup"
                }
            return self.lookup_email_by_name_tool(
                name=arguments.get("name"),
                user_id=user_id,
                db=db
            )
        elif function_name == "add_name_email_mapping":
            if not user_id or not db:
                return {
                    "success": False,
                    "message": "User context required for adding mappings"
                }
            return self.add_name_email_mapping_tool(
                name=arguments.get("name"),
                email_address=arguments.get("email_address"),
                user_id=user_id,
                db=db
            )
        else:
            return {
                "success": False,
                "message": f"Unknown tool: {function_name}"
            }
    






    # ... (previous code remains the same until the chat_with_tools method)

    def chat_with_tools(self, messages: List[Dict[str, str]], tool_type: str = "email", 
                    user_id: int = None, db = None) -> Dict[str, Any]:
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
            
            # Check if this is a response to a missing email request
            pending_name = None
            if len(messages) >= 2:
                last_ai_message = next((msg for msg in reversed(messages) if msg["role"] == "assistant"), None)
                last_user_message = messages[-1] if messages[-1]["role"] == "user" else None
                
                if (last_ai_message and 
                    "I couldn't find an email address for" in last_ai_message.get("content", "") and
                    "in your contacts" in last_ai_message.get("content", "")):
                    # Extract the name from the AI message
                    import re
                    match = re.search(r"for (.+?) in your contacts", last_ai_message.get("content", ""))
                    if match:
                        pending_name = match.group(1)
                        
                        # Check if the user provided an email address
                        if last_user_message and self.is_valid_email(last_user_message.get("content", "")):
                            # This is an email address response to a missing name
                            email_address = last_user_message["content"]
                            
                            # Add the name-email mapping
                            from app.email_tools import add_name_email_mapping
                            add_name_email_mapping(pending_name, email_address, user_id, db)
                            
                            # Extract email details from the original request
                            original_request = next((msg for msg in messages if msg["role"] == "user" and "email to" in msg.get("content", "").lower()), None)
                            if original_request:
                                original_text = original_request["content"].lower()
                                
                                # Extract subject
                                subject = "Meeting"  # Default
                                if "subject is" in original_text:
                                    subject_start = original_text.find("subject is") + len("subject is")
                                    subject_end = original_text.find(" and", subject_start)
                                    if subject_end == -1:
                                        subject_end = len(original_text)
                                    subject = original_text[subject_start:subject_end].strip()
                                
                                # Extract content
                                content = "Web design"  # Default
                                if "content is" in original_text:
                                    content_start = original_text.find("content is") + len("content is")
                                    content = original_text[content_start:].strip()
                                
                                # Generate email content
                                email_content = self.generate_email_content(content, "professional")
                                
                                # Return email composition
                                email_composition = {
                                    "recipient": email_address,
                                    "subject": subject,
                                    "body": email_content,
                                    "tone": "professional"
                                }
                                
                                return {
                                    "success": True,
                                    "message": f"Added {pending_name} to your contacts and prepared an email:",
                                    "email_composition": email_composition,
                                    "has_tool_calls": True
                                }
            
            # Make the initial API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful business assistant. Use the available tools when appropriate to help users with their tasks. When a name lookup fails, ask the user for the email address. When a user provides an email address for a missing name, add it to their contacts and proceed with email composition."}
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
                    tool_result = self.process_tool_call(tool_call, user_id, db)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "tool_name": tool_call.function.name,
                        "result": tool_result
                    })
                
                # Check if we have a successful email lookup that should trigger email composition
                successful_lookups = []
                for tool_result in tool_results:
                    if (tool_result["tool_name"] == "lookup_email_by_name" and 
                        tool_result["result"]["success"]):
                        successful_lookups.append(tool_result)
                
                # If we have a successful lookup, proceed to email composition
                if successful_lookups:
                    # Extract the original user message to get subject and content
                    user_message = next((msg for msg in messages if msg["role"] == "user"), None)
                    if user_message:
                        # Parse the user message to extract subject and content
                        user_text = user_message["content"].lower()
                        
                        # Extract subject
                        subject = "Meeting"  # Default
                        if "subject is" in user_text:
                            subject_start = user_text.find("subject is") + len("subject is")
                            subject_end = user_text.find(" and", subject_start)
                            if subject_end == -1:
                                subject_end = len(user_text)
                            subject = user_text[subject_start:subject_end].strip()
                        
                        # Extract content
                        content = "Web design"  # Default
                        if "content is" in user_text:
                            content_start = user_text.find("content is") + len("content is")
                            content = user_text[content_start:].strip()
                        
                        # Create email composition from the first successful lookup
                        lookup_result = successful_lookups[0]["result"]
                        
                        # Generate proper email content using AI
                        email_content = self.generate_email_content(content, "professional")
                        
                        email_composition = {
                            "recipient": lookup_result["email_address"],
                            "subject": subject,
                            "body": email_content,
                            "tone": "professional"
                        }
                        
                        response_data = {
                            "success": True,
                            "message": f"Found email address for {successful_lookups[0]['result'].get('name', 'the contact')}. I've prepared an email for your review:",
                            "email_composition": email_composition,
                            "has_tool_calls": True
                        }
                        
                        return response_data
                
                # Check if we have email compositions pending approval
                pending_email_compositions = []
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
                
                # Check if we need to ask the user for an email address
                needs_email_input = False
                missing_name = None
                for tool_result in tool_results:
                    if (tool_result["tool_name"] == "lookup_email_by_name" and 
                        tool_result["result"].get("needs_email_input")):
                        needs_email_input = True
                        missing_name = tool_result["result"].get("name")
                        break
                
                if needs_email_input:
                    # Return a message asking for the email address
                    response_data = {
                        "success": True,
                        "message": f"I couldn't find an email address for {missing_name} in your contacts. Could you please provide their email address?",
                        "has_tool_calls": True,
                        "needs_email_input": True,
                        "missing_name": missing_name
                    }
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
                    elif tool_result["tool_name"] == "lookup_email_by_name":
                        result = tool_result["result"]
                        if result["success"]:
                            # Don't show the success message here - we want to proceed to email composition
                            pass
                        else:
                            # Don't show error message for lookup failures - we want the AI to handle this
                            pass
                    elif tool_result["tool_name"] == "add_name_email_mapping":
                        result = tool_result["result"]
                        if result["success"]:
                            friendly_responses.append(
                                f"✅ {result['message']}"
                            )
                        else:
                            friendly_responses.append(
                                f"❌ {result['message']}"
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

    def is_valid_email(self, email):
        """Simple email validation function"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None






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