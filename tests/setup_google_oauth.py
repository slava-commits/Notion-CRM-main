#!/usr/bin/env python3
"""
Google OAuth Setup Helper
Helps you get the refresh token for Gmail and Calendar access
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

def setup_google_oauth():
    """Set up Google OAuth and get refresh token"""
    
    print("🔧 Google OAuth Setup Helper")
    print("=" * 50)
    
    # Get client ID and secret from user
    client_id = input("Enter your Google Client ID: ").strip()
    client_secret = input("Enter your Google Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Secret are required")
        return None
    
    # Create credentials object
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Extract tokens
        refresh_token = creds.refresh_token
        access_token = creds.token
        
        print("\n✅ OAuth setup successful!")
        print(f"Refresh Token: {refresh_token}")
        print(f"Access Token: {access_token}")
        
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
            'client_id': client_id,
            'client_secret': client_secret,
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
    print("This script will help you set up Google OAuth for Gmail and Calendar access.")
    print("You'll need your Client ID and Client Secret from Google Cloud Console.")
    print()
    
    credentials = setup_google_oauth()
    
    if credentials:
        update_env_file(credentials)
        print("\n🎉 Setup complete! You can now run:")
        print("  python3 cli.py validate")
        print("  python3 cli.py init")
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")

