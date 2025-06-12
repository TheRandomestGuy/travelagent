import os
import pickle
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    token_path = 'token.pickle'
    credentials_path = 'credentials.json'  # You must provide this file from Google Cloud Console

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def add_events_to_google_calendar(events: list):
    """
    Adds a list of events to the user's primary Google Calendar.
    Each event should be a dict with keys: summary, description, location, start, end (ISO format).
    """
    try:
        service = get_calendar_service()
        for event in events:
            event_body = {
                'summary': event.get('summary', 'Travel Event'),
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'start': {
                    'dateTime': event['start'],
                    'timeZone': 'UTC',  # Change if you want to use a specific timezone
                },
                'end': {
                    'dateTime': event['end'],
                    'timeZone': 'UTC',
                },
            }
            service.events().insert(calendarId='primary', body=event_body).execute()
        return f"Successfully added {len(events)} events to your Google Calendar."
    except Exception as e:
        return f"Failed to add events to Google Calendar: {e}"
