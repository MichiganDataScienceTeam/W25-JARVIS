from ollama import ChatResponse, chat
import googlemaps
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

# Define the scopes needed for Google Docs and Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

#this thing you need to do to create the credentials.json file
def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Run the authentication flow
creds = get_credentials()
print("Authentication successful! Token has been saved to token.json")




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

        # Create the Docs API service
        docs_service = build('docs', 'v1', credentials=creds)

        # Create the document
        doc = docs_service.documents().create(body={'title': title}).execute()
        document_id = doc['documentId']

        # Insert text
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


# Replace with your actual API Key
GOOGLE_MAP_API_KEY = "YOUR_GOOGLE_MAP_API_KEY" #TODO: Replace with your actual Google Maps API key

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)

def get_walking_distance(origin, destination):
    """
    Calculate the walking distance and duration between two locations using Google Maps API.
    
    :param origin: Starting location (address or "latitude,longitude")
    :param destination: Destination location (address or "latitude,longitude")
    :return: A dictionary with distance and duration
    """
    try:
        result = gmaps.distance_matrix(
            origins=origin,
            destinations=destination,
            mode="walking"  # Set the mode to walking
        )

        # Extract distance and duration
        if result["status"] == "OK":
            elements = result["rows"][0]["elements"][0]
            if elements["status"] == "OK":
                distance = elements["distance"]["text"]  # e.g., "2.3 km"
                duration = elements["duration"]["text"]  # e.g., "28 mins"
                return {"distance": distance, "duration": duration}
            else:
                return {"error": f"Could not calculate distance: {elements['status']}"}
        else:
            return {"error": f"API Error: {result['status']}"}

    except Exception as e:
        return {"error": str(e)}

def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The sum of the two numbers
    """
    return int(a) + int(b)

def subtract_two_numbers(a: int, b: int) -> int:
    """
    Subtract two numbers

    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The difference of the two numbers
    """
    return int(a) - int(b)

def search_in_browser(query):
    import webbrowser
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url, new=2)

available_functions = {
    "add_two_numbers": add_two_numbers,
    "subtract_two_numbers": subtract_two_numbers,
    "search_in_browser": search_in_browser,
    "get_walking_distance": get_walking_distance,
    "create_google_doc": create_google_doc
}

def handle_chat(messages):
    response: ChatResponse = chat(
        "llama3.2:latest",
        messages=messages,
        tools=[add_two_numbers, subtract_two_numbers, search_in_browser],
    )
    
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            function_to_call = available_functions.get(tool.function.name)
            if function_to_call:
                output = function_to_call(**tool.function.arguments)
                messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})
                final_response = chat("llama3.2:latest", messages=messages)
                return final_response.message.content
