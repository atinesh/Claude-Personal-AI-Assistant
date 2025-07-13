from datetime import datetime, timedelta
from fastmcp import FastMCP
import requests
import pickle
import uuid
import json
import os

from tools.email import EmailTool
from tools.calendar import CalendarTool
from utility import validate_email

import logging
logging.basicConfig(level=logging.INFO)

mcp = FastMCP("Personal AI Assistant")

@mcp.tool
def get_local_datetime() -> dict:
    """
    Tool returns current local date, time, and timezone.
    
    Returns:
        local_date_time (dict): Dictionary containing local date, time, and timezone.
    """
    logging.info(f"Get local datetime called.")

    now = datetime.now().astimezone()

    local_date_time = {
        'date': now.date(),
        'time': now.time(),
        'timezone': now.tzname()
    }

    return local_date_time

@mcp.tool
def read_email(query: str, max_results: int) -> str:
    """
    Tool retrieves emails using Gmail API.

    Args:
        query (str): Search query to filter emails (e.g. "is:read", "is:unread", "after:04/16/2024", "before:04/18/2024", "from:amy@example.com", "to:john@example.com", "from:amy OR from:david", "label:important", "category:social", "has:attachment", etc.). 
        max_results (int): Maximum number of emails to retrieve.
    
    Returns:
        email_data (str): String containing list of emails, each containing sender, subject and email body.
    """
    logging.info(f"Read email tool called.")

    try:
        
        # Initialize EmailTool to access Gmail API
        email_tool = EmailTool()
        email_data = email_tool.read_email(query, max_results)

        # Join emails into a single string
        email_data = "\n##################\n".join(email_data)
        return email_data

    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return ""

@mcp.tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    Tool composes and sends an email via Gmail API.

    Args:
        to (str): Recipient's email address.
        subject (str): Subject line of the email.
        body (str): Content of the email message.

    Returns:
        response (str): Confirmation or status message after sending.
    """
    logging.info(f"Send email tool called.")

    try:

        if not validate_email(to):
            logging.error(f"Invalid email address provided: {to}")
            return "Invalid email address provided."
        logging.info(f"Email address validated: {to}")
        
        # Initialize EmailTool to access Gmail API
        email_tool = EmailTool()
        response = email_tool.send_email(to, subject, body)
        return response

    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return ""

@mcp.tool
def read_calendar(query: str, time_min: str, time_max: str) -> str:
    """
    Tool Retrieves calendar events using Google Calendar API.

    Args:
        query (str): Free text search to filter calendar events.
        time_min (str): Start date and time must be an RFC3339 format with mandatory time zone offset (e.g. 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z).
        time_max (str): End date and time must be an RFC3339 format with mandatory time zone offset (e.g. 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z).
    
    Returns:
        calendar_data (str): String containing list of calendar events, each containing sender and subject.
    """
    logging.info(f"Read calendar tool called.")

    try:
        
        # Initialize CalendarTool to access Google Calendar
        calendar_tool = CalendarTool()
        event_data = calendar_tool.read_calendar_events(query, time_min, time_max)

        # Join calendar events into a single string
        event_data = "\n".join(event_data)

        return event_data

    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return "Failed to retrieve calendar events"

@mcp.tool
def update_calendar(summary: str, description: str, start_date: str, end_date: str, meeting_link: bool, attendees: list) -> str:
    """
    Tool create calendar events using Google Calendar API.

    Args:
        summary (str): Title of the calendar event.
        description (str): Description of the calendar event.
        start_date (str): Start date and time of the event in RFC3339 format with mandatory time zone offset (e.g., 2024-04-16T10:00:00Z).
        end_date (str): End date and time of the event in RFC3339 format with mandatory time zone offset (e.g., 2024-04-16T11:00:00Z).
        meeting_link (bool): If True, creates a Google Meet link for the event.
        attendees (list): List of email addresses to invite to the event. If meeting_link is True, this should be a list of valid email addresses.
    
    Returns:
        calendar_data (str): Confirmation or status message after creating event.
    """
    logging.info(f"Update calendar tool called.")

    try:

        # Create event details
        event_details = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_date, 'timeZone': 'UTC'},
            'end': {'dateTime': end_date, 'timeZone': 'UTC'}
        }

        if meeting_link:
            event_details['conferenceData'] = {
                'createRequest': {
                    'requestId': str(uuid.uuid4()), # Unique random string
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }

            for attendee in attendees:
                if not validate_email(attendee):
                    logging.error(f"Invalid email address provided: {attendee}")
                    return "Invalid email address provided."
            event_details['attendees'] = attendees
        
        # Initialize CalendarTool to access Google Calendar
        calendar_tool = CalendarTool()
        event_data = calendar_tool.create_calendar_event(event_details, meeting_link)

        if meeting_link:
            return f"Event created: {event_data['htmlLink']}, Meeting Link: {event_data['hangoutLink']}"
        else:
            return f"Event created: {event_data['htmlLink']}"

    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return "Failed to create event"

if __name__ == "__main__":
    mcp.run()