from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
import pickle
import re
import os

import config as cfg

# Scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',            # Gmail Read-only access 
    'https://www.googleapis.com/auth/gmail.send',                # Gmail Send mail access
    'https://www.googleapis.com/auth/calendar',                  # Google Calendar Read and write access
]

def authenticate_google_apis():
    """
    Authenticates the user with Google APIs using OAuth 2.0.
    """
    
    try:
        creds = None
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            logging.info("Loading existing credentials from token.pickle")
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            logging.info("No valid credentials found, requesting new credentials.")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logging.info("Credentials refreshed successfully.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cfg.CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                logging.info("New credentials obtained successfully.")
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                logging.info("Credentials saved to token.pickle")
        
        return creds
    except Exception as e:
        logging.error(f"Authentication failed: {str(e)}")
        raise

def validate_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.
    
    Args:
        email (str): The email address to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None