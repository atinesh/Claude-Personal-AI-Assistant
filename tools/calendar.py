from utility import authenticate_google_apis
from googleapiclient.discovery import build
import logging

class CalendarTool:
    def __init__(self):
        # Create Google Calendar service object
        self.service = build('calendar', 'v3', credentials=authenticate_google_apis())

    def read_calendar_events(self, query, time_min=None, time_max=None):
        """Retrieves calendar events"""
        try:
            # Fetch calendar events
            logging.info(f"\nFetching calendar events from Google Calendar ...")
            events_result = self.service.events().list(
                calendarId='primary',
                orderBy='startTime',
                q=query,
                singleEvents=True,
                timeMin=time_min,
                timeMax=time_max
            ).execute()

            events = events_result.get('items', [])

            # Extract event data
            event_data = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                event_data.append(f"{start}: {summary}")

            return event_data
        except Exception as e:
            logging.error(f'An error occurred: {e}')
            return []

    def create_calendar_event(self, event_details, meeting_link):
        """Creates a new calendar event"""

        try:
            logging.info(f"Creating calendar event ...")

            if meeting_link:
                event = self.service.events().insert(
                    calendarId='primary',
                    body=event_details,
                    conferenceDataVersion=1,
                ).execute()

            else:
                event = self.service.events().insert(
                    calendarId='primary',
                    body=event_details
                ).execute()
            return event
        except Exception as e:
            logging.error(f'An error occurred: {e}')
            return 'Failed to create event'