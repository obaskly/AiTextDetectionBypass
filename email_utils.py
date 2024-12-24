import os
import re
import base64
import random
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# File to persist generated variations
VARIATIONS_FILE = 'generated_variations.json'

def authenticate_gmail():
    creds = None
    # The token.json file stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # This was causing the error
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def calculate_email_variations(email):
    username, domain = email.split("@")
    
    positions = len(username) - 1
    
    total_variations = 2 ** positions
    return total_variations

def email_exists_in_file(email):
    if not os.path.exists(VARIATIONS_FILE):
        return False
    try:
        with open(VARIATIONS_FILE, 'r') as f:
            variations = json.load(f)
            return email in variations
    except (json.JSONDecodeError, ValueError):
        # If the file is empty or corrupted, return False
        return False

def save_email_to_file(email):
    if os.path.exists(VARIATIONS_FILE):
        try:
            with open(VARIATIONS_FILE, 'r') as f:
                variations = json.load(f)
        except (json.JSONDecodeError, ValueError):
            # If the file is empty or corrupted, start with an empty list
            variations = []
    else:
        variations = []
    
    variations.append(email)
    with open(VARIATIONS_FILE, 'w') as f:
        json.dump(variations, f, indent=4)

def generate_gmail_variation(base_email, max_attempts=20):
    local_part, domain = base_email.split('@')
    
    if len(local_part) <= 2:
        return base_email  # Not enough characters to add dots
    
    for _ in range(max_attempts):
        local_part_variants = list(local_part)
        max_dots = len(local_part) - 2
        num_dots = random.randint(1, max_dots) if max_dots > 0 else 0
        dot_positions = sorted(random.sample(range(1, len(local_part) - 1), num_dots))

        for i, pos in enumerate(dot_positions):
            local_part_variants.insert(pos + i, '.')

        new_email = ''.join(local_part_variants).strip('.') + '@' + domain

        # Check if the email already exists in the file
        if not email_exists_in_file(new_email):
            save_email_to_file(new_email)
            return new_email
    
    raise ValueError("Unable to generate a unique Gmail variation after multiple attempts.")

def extract_verify_link(text):
    pattern = r'https://undetectable\.ai/api/auth/callback/sendgrid\?[^"]+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def get_gmail_service(creds):
    return build('gmail', 'v1', credentials=creds)

def search_for_confirmation_email(service, query='subject:Sign in to Undetectable AI'):
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No confirmation email found.")
            return None
        
        # Get the first (most recent) message
        message = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
        return message
    except Exception as e:
        print(f"Error retrieving confirmation email: {e}")
        return None

def get_message_body(message):
    if 'parts' in message['payload']:
        # Iterate through all parts of the email
        for part in message['payload']['parts']:
            # Check if the part is HTML
            if part['mimeType'] == 'text/html':
                msg_data = part['body'].get('data', '')
                decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
                print(f"Extracted HTML part: {decoded_data[:500]}") 
                return decoded_data
            # Fallback to plain text if no HTML part found
            elif part['mimeType'] == 'text/plain':
                msg_data = part['body'].get('data', '')
                decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
                print(f"Extracted plain text part: {decoded_data[:500]}")  
                return decoded_data
    else:
        # Handle case where the message does not have parts (e.g., it's a single text/plain or text/html email)
        msg_data = message['payload']['body'].get('data', '')
        decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
        print(f"Extracted single body message: {decoded_data[:500]}")  
        return decoded_data
    return ''
