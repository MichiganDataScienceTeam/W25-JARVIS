from ollama import ChatResponse, chat
from functions import send_email, make_event, search_in_browser, handle_general_query
import logging
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_google_doc(title: str, text: str) -> str:
    """
    Create a Google Doc and insert text.
    Args:
        title (str): Title of the document.
        text (str): Text to insert into the document.
    Returns:
        str: The URL of the created document.
    """
    try:
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file'])
        docs_service = build('docs', 'v1', credentials=creds)
        doc = docs_service.documents().create(body={'title': title}).execute()
        document_id = doc['documentId']
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': text
                }
            }
        ]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        doc_url = f"https://docs.google.com/document/d/{document_id}/edit"
        print(f"Document created: {doc_url}")
        return doc_url
    except Exception as e:
        print(f"Error creating document: {str(e)}")
        return None

available_functions = {
    "search_in_browser": search_in_browser,
    "send_email": send_email,
    "make_event": make_event,
    "handle_general_query": handle_general_query,
    "create_google_doc": create_google_doc
}

# Hard-coded responses for each function
function_responses = {
    "search_in_browser": "I've searched for that information in your browser. You should see the results now.",
    "send_email": "I've sent your email successfully. The recipient should receive it shortly.",
    "make_event": "I've created that calendar event for you. It's been added to your calendar.",
    "create_google_doc": "I've created a Google Doc with the content you requested. You can access it now."
}

def handle_chat(message):
    messages = [{'role': 'user', 'content': message}]
    logger.info(f"Processing message: {message}")

    response: ChatResponse = chat(
        'llama3.2:latest',
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Create and send an email message",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "make_event",
                    "description": "Create a calendar event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of scheduled event"
                            },
                            "desc": {
                                "type": "string",
                                "description": "Description of scheduled event"
                            },
                            "start": {
                                "type": "string",
                                "description": "Start time in ISO format: YYYY-MM-DDTHH:MM:SS"
                            },
                            "end": {
                                "type": "string",
                                "description": "End time in ISO format: YYYY-MM-DDTHH:MM:SS"
                            },
                            "guests": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of email addresses for attendees"
                            }
                        },
                        "required": ["title", "desc", "start", "end", "guests"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_in_browser",
                    "description": "Search for information in web browser",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_google_doc",
                    "description": "Create a Google Doc and insert text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the document"
                            },
                            "text": {
                                "type": "string",
                                "description": "Text to insert into the document"
                            }
                        },
                        "required": ["title", "text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "handle_general_query",
                    "description": "Handle general conversation or questions not requiring specific tools",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string", 
                                "description": "The user's query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ],
    )
    
    if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
        logger.info(f"Model detected need for tool calls: {len(response.message.tool_calls)} tool(s)")
        
        for tool in response.message.tool_calls:
            function_name = tool.function.name
            function_to_call = available_functions.get(function_name)
            
            if function_to_call:
                args = tool.function.arguments
                logger.info(f"Executing function: {function_name} with args: {args}")
                
                try:
                    processed_args = {}
                    for key, value in args.items():
                        if key == "guests" and isinstance(value, str) and (value.startswith('[') or value.startswith('[')):
                            try:
                                processed_args[key] = json.loads(value)
                            except json.JSONDecodeError:
                                processed_args[key] = value
                        else:
                            processed_args[key] = value
                    
                    logger.info(f"Processed arguments: {processed_args}")
                    
                    output = function_to_call(**processed_args)
                    logger.info(f"Function executed successfully")
                    
                    if function_name != "handle_general_query" and function_name in function_responses:
                        return function_responses[function_name]
                    else:
                        messages.append({
                            'role': 'tool', 
                            'content': str(output), 
                            'name': function_name
                        })
                        
                        final_response = chat("jarvis:latest", messages=messages)
                        return final_response.message.content
                
                except Exception as e:
                    logger.error(f"Error executing function {function_name}: {str(e)}")
                    return f"I tried to {function_name} but encountered an error: {str(e)}"
            else:
                logger.warning(f"Function {function_name} not found in available functions")
    
    logger.info("No specific tool calls detected, using fallback function")
    try:
        output = handle_general_query(message)
        
        messages.append({
            'role': 'tool', 
            'content': str(output), 
            'name': 'handle_general_query'
        })
        
        final_response = chat("jarvis:latest", messages=messages)
        return final_response.message.content
    except Exception as e:
        logger.error(f"Error in fallback function: {str(e)}")
    
    return response.message.content