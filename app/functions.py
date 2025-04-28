import base64
import datetime
import os.path
import webbrowser
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send", 
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar"]


# Create credentials.json file
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

creds = get_credentials()
print("Authentication successful! Token has been saved to token.json")

def send_email(to, subject, body):
    """Create and send an email message
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    
    Returns:
        Sent message object, including message id
    """
    try:
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["Subject"] = subject

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        
        # Send the message
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        
        print(f'Message sent successfully! Message Id: {send_message["id"]}')
        return send_message
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    
def make_event(title, desc, start, end, guests):
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat() # + "Z"  # 'Z' indicates UTC time

    f"""Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    The current date is: {now}.

    Args:
        title: Title of schedueled event
        desc: Description of schedueled event
        start: Start time for the event
        end: End time for the event
        guests: List of emails for attendees
    
    Returns:
        None
    """

    try:
        service = build("calendar", "v3", credentials=creds)

        attendees = [{'email': email} for email in guests]
        event = {
            'summary': f'{title}',
            # 'location': '800 Howard St., San Francisco, CA 94103',
            'description': f'{desc}',
            'start': {
                'dateTime': f'{start}',
                'timeZone': 'America/Detroit',
            },
            'end': {
                'dateTime': f'{end}',
                'timeZone': 'America/Detroit',
            },
            'attendees': attendees
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print(f"An error occurred: {error}")

def search_in_browser(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url, new=2)  # Opens the URL in default browser