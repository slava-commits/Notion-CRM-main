#!/usr/bin/env python3
"""
Google OAuth Setup from JSON File
Uses the client_secret.json file to set up OAuth
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes needed for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def setup_oauth_from_json():
    """Set up Google OAuth using client_secret.json file"""
    
    print("🔧 Google OAuth Setup from JSON File")
    print("=" * 50)
    
    # Check if JSON file exists
    if not os.path.exists('client_secret.json'):
        print("❌ client_secret.json file not found!")
        print("Please make sure the file is in the current directory.")
        return None
    
    try:
        # Load the JSON file
        with open('client_secret.json', 'r') as f:
            client_config = json.load(f)
        
        print("✅ Loaded client_secret.json")
        
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Extract tokens
        refresh_token = creds.refresh_token
        access_token = creds.token
        
        print("\n✅ OAuth setup successful!")
        print(f"Refresh Token: {refresh_token}")
        
        # Test the credentials
        print("\n🧪 Testing credentials...")
        
        # Test Gmail
        try:
            gmail_service = build('gmail', 'v1', credentials=creds)
            profile = gmail_service.users().getProfile(userId='me').execute()
            print(f"✅ Gmail access: {profile.get('emailAddress')}")
        except Exception as e:
            print(f"❌ Gmail test failed: {e}")
        
        # Test Calendar
        try:
            calendar_service = build('calendar', 'v3', credentials=creds)
            calendar_list = calendar_service.calendarList().list().execute()
            print(f"✅ Calendar access: {len(calendar_list.get('items', []))} calendars found")
        except Exception as e:
            print(f"❌ Calendar test failed: {e}")
        
        return {
            'client_id': client_config['installed']['client_id'],
            'client_secret': client_config['installed']['client_secret'],
            'refresh_token': refresh_token
        }
        
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        return None

def update_env_file(credentials):
    """Update .env file with Google credentials"""
    if not credentials:
        return False
    
    env_content = f"""NOTION_TOKEN=ntn_g743979707482i8bPwprIryDWBLKAl1vxn9v2aksrFggXe
ATTIO_API_KEY=35ed3b321b2194994fb89c47aa16878a14a969f5d2fb2ea732d0fb10d7d75560

# Google OAuth Credentials
GMAIL_CLIENT_ID={credentials['client_id']}
GMAIL_CLIENT_SECRET={credentials['client_secret']}
GMAIL_REFRESH_TOKEN={credentials['refresh_token']}
CALENDAR_CLIENT_ID={credentials['client_id']}
CALENDAR_CLIENT_SECRET={credentials['client_secret']}
CALENDAR_REFRESH_TOKEN={credentials['refresh_token']}

# Optional - add these as you get them
FATHOM_API_KEY=
LINKEDIN_API_KEY=
X_API_KEY=
LEANER_API_KEY=
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Updated .env file with Google credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

if __name__ == "__main__":
    print("This script will set up Google OAuth using your client_secret.json file.")
    print("It will open a browser window for you to authorize access.")
    print()
    
    credentials = setup_oauth_from_json()
    
    if credentials:
        update_env_file(credentials)
        print("\n🎉 Setup complete! You can now run:")
        print("  python3 cli.py validate")
        print("  python3 cli.py init")
        print("  python3 cli.py start")
    else:
        print("\n❌ Setup failed. Please check your JSON file and try again.")

