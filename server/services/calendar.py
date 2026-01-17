from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os, traceback
from .db.crud import error_log
from .meeting import create_meeting


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

    try:
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

        return {"error": None, "events": events}
    
    except Exception as e:
        error_log(f"Failed to fetch events from calendar: {str(e)}", traceback.format_exc())
        return {"error": "An error occured, please try again later", "events": None}

def get_normal_events(time_min, time_max):
    return get_events(time_min, time_max, os.getenv("CALENDAR_ID"))

def get_holiday_events(time_min, time_max):
    return get_events(time_min, time_max, os.getenv("CALENDAR_HOLIDAYS_ID"))

def create_event(event_details):
    calendar = get_calendar_service()
    booking_minutes = int(os.getenv("BOOKING_MINUTES", "30"))
    end_datetime = event_details['datetime'] + timedelta(minutes=booking_minutes)

    info = create_meeting(event_details['datetime'])
    if info["error"]:
        return info

    # create event description
    description = ""
    description += f"Meeting Link: {info['meeting_link']}\n\n"
    description += f"Email: {event_details['email']}\n"
    description += f"Phone: {event_details['phone']}\n"
    description += f"Service: {event_details['service']}\n"
    description += f"Consultation Type: {event_details['type']}\n"

    if event_details['company']:
        description += f"Company: {event_details['company']}\n"
    if event_details['company_age']:
        description += f"Company Age: {event_details['company_age']}\n"
    if event_details['business_revenue']:
        description += f"Business Revenue: {event_details['business_revenue']}\n"
    if event_details['additional_info']:
        description += f"\nAdditional Info:\n{event_details['additional_info']}\n"

    #create the calendar event
    event ={
        'summary': f"Consultation with {event_details['first_name']} {event_details['last_name']}",
        'description': description,
        'start': {
            'dateTime': event_details['datetime'].isoformat(),
            'timeZone': os.getenv("TIMEZONE", "Africa/Johannesburg"),
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': os.getenv("TIMEZONE", "Africa/Johannesburg"),
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60 * 24},
                {'method': 'email', 'minutes': 60},
                {'method': 'popup', 'minutes': 10},
                {'method': 'popup', 'minutes': 0},
            ],
        },
    }

    try: 
        created_event = calendar.events().insert(calendarId=os.getenv("CALENDAR_ID"), body=event).execute()
        return {"error": None, "meeting_link": info['meeting_link']}
    
    except Exception as e:
        error_log(f"Failed to create calendar event: {str(e)}", traceback.format_exc())
        return {"error": "An error occurred, please try again later", "meeting_link": None}