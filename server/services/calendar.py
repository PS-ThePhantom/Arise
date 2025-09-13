from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

def get_calendar_service():
    SERVICE_ACCOUNT_FILE = 'config/key.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build('calendar', 'v3', credentials=credentials)
    
    return service

def format_events(events):
    formatted_events = {}

    for event in events:
        #get the start and end time of the event in string format
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        #turn the string to datetime object
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Get the day of the month for each datetime object
        start_day = start_dt.day
        end_day = end_dt.day

        # Store the event in the dictionary
        # If the start and end day are the same, store it under that day
        # If they are different, store it under all days it spans
        formatted_events.setdefault(start_day, []).append((start_dt, end_dt))
        if start_day != end_day:
            for day in range(start_day + 1, end_day + 1):
                formatted_events.setdefault(day, []).append((start_dt, end_dt))

    return formatted_events

def get_events(time_min, time_max, calendar_id):
    calendar = get_calendar_service()

    events_result = calendar.events().list(
        calendarId=calendar_id,
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    #get and format the events
    events = events_result.get('items', [])
    events = format_events(events)
    
    return events