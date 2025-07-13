from googleapiclient.discovery import build
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import logging
import base64

from utility import authenticate_google_apis
import config as cfg

class EmailTool:
    def __init__(self):
        # Create Google Gmail service object
        self.service = build('gmail', 'v1', credentials=authenticate_google_apis())

    def html_to_text(self, html_content):
        """Convert HTML content to plain text using BeautifulSoup."""
        if not html_content:
            return ""
        
        logging.info("Converting HTML to text ...")

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text()
        
        # Clean up extra whitespace and newlines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def extract_email_body(self, payload):
        """Extract email body from payload."""
        body = ""
        
        if 'parts' in payload:
            # Multi-part message - prioritize plain text
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
            
            # If no plain text found, look for HTML and convert to text
            if not body:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        data = part['body']['data']
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        body = self.html_to_text(html_body)
                        break
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
            elif payload['mimeType'] == 'text/html':
                data = payload['body']['data']
                html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                body = self.html_to_text(html_body)
        
        return body

    def read_email(self, query, max_results=20):
        """Retrieves emails from Gmail inbox."""

        try:
            # Fetch emails
            logging.info(f"Fetching emails from Gmail ...")
            results  = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])

            if not messages:
                logging.info("No emails found.")
                return []
            
            emails = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id']
                ).execute()
                emails.append(msg)

            # Extract relevant email data
            email_data = []
            for email in emails:
                headers = email['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender  = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                if cfg.EMAIL_BODY:
                    body    = self.extract_email_body(email['payload'])
                    email_data.append(f"From: {sender}\n\nSubject: {subject}\n\nBody: {body}")
                else:
                    email_data.append(f"From: {sender}\n\nSubject: {subject}")
            return email_data

        except Exception as e:
            logging.error(f'An error occurred: {e}')
            return []

    def send_email(self, to, subject, body):
        """Sends an email using Gmail API."""

        try:
            logging.info(f"Sending email ...")
            # Create MIME message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            logging.info(f"Email sent to {to}")
            return "Email Sent Successfully!"

        except Exception as e:
            logging.error(f'An error occurred while sending email: {e}')
            return 'Failed to send email'