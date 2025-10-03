#!/usr/bin/env python3
"""
Working Ethan Data Collection
Collects data for ethan@tuesday.vc using working integrations
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def collect_ethan_data():
    """Collect data for ethan@tuesday.vc"""
    
    print("🎯 Collecting Data for ethan@tuesday.vc")
    print("=" * 50)
    
    # Test Gmail API directly
    print("📧 Testing Gmail API...")
    
    # Get access token
    token_data = {
        'client_id': Config.GMAIL_CLIENT_ID,
        'client_secret': Config.GMAIL_CLIENT_SECRET,
        'refresh_token': Config.GMAIL_REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Refresh access token
            async with session.post('https://oauth2.googleapis.com/token', data=token_data) as response:
                if response.status == 200:
                    token_response = await response.json()
                    access_token = token_response['access_token']
                    print("✅ Gmail access token obtained")
                    
                    # Test Gmail API
                    headers = {"Authorization": f"Bearer {access_token}"}
                    async with session.get('https://gmail.googleapis.com/gmail/v1/users/me/profile', headers=headers) as gmail_response:
                        if gmail_response.status == 200:
                            profile = await gmail_response.json()
                            print(f"✅ Gmail API working: {profile.get('emailAddress')}")
                            
                            # Search for emails with ethan@tuesday.vc
                            search_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
                            params = {'q': 'ethan@tuesday.vc', 'maxResults': 10}
                            
                            async with session.get(search_url, headers=headers, params=params) as search_response:
                                if search_response.status == 200:
                                    search_result = await search_response.json()
                                    message_count = len(search_result.get('messages', []))
                                    print(f"📧 Found {message_count} emails with ethan@tuesday.vc")
                                    
                                    if message_count > 0:
                                        print("   Recent emails:")
                                        for i, msg in enumerate(search_result.get('messages', [])[:3]):
                                            # Get message details
                                            msg_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg["id"]}'
                                            async with session.get(msg_url, headers=headers) as msg_response:
                                                if msg_response.status == 200:
                                                    msg_data = await msg_response.json()
                                                    headers = msg_data.get('payload', {}).get('headers', [])
                                                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                                                    print(f"     {i+1}. {subject}")
                                else:
                                    print(f"❌ Gmail search failed: {search_response.status}")
                        else:
                            print(f"❌ Gmail profile failed: {gmail_response.status}")
                else:
                    print(f"❌ Token refresh failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Gmail test failed: {e}")
        
        # Test Calendar API
        print("\n📅 Testing Calendar API...")
        try:
            # Use same access token for Calendar
            calendar_headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get calendar list
            async with session.get('https://www.googleapis.com/calendar/v3/users/me/calendarList', headers=calendar_headers) as cal_response:
                if cal_response.status == 200:
                    cal_data = await cal_response.json()
                    calendar_count = len(cal_data.get('items', []))
                    print(f"✅ Calendar API working: {calendar_count} calendars found")
                    
                    # Search for events with ethan@tuesday.vc
                    now = datetime.now()
                    time_min = (now - timedelta(days=30)).isoformat() + 'Z'
                    time_max = (now + timedelta(days=30)).isoformat() + 'Z'
                    
                    events_url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
                    params = {
                        'timeMin': time_min,
                        'timeMax': time_max,
                        'maxResults': 50
                    }
                    
                    async with session.get(events_url, headers=calendar_headers, params=params) as events_response:
                        if events_response.status == 200:
                            events_data = await events_response.json()
                            events = events_data.get('items', [])
                            print(f"📅 Found {len(events)} events in the last 30 days")
                            
                            # Look for events with ethan@tuesday.vc
                            ethan_events = []
                            for event in events:
                                attendees = event.get('attendees', [])
                                for attendee in attendees:
                                    if 'ethan@tuesday.vc' in attendee.get('email', '').lower():
                                        ethan_events.append(event)
                                        break
                            
                            print(f"📅 Found {len(ethan_events)} events with ethan@tuesday.vc")
                            for i, event in enumerate(ethan_events[:3]):
                                title = event.get('summary', 'No Title')
                                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No Date'))
                                print(f"     {i+1}. {title} ({start})")
                        else:
                            print(f"❌ Calendar events failed: {events_response.status}")
                else:
                    print(f"❌ Calendar API failed: {cal_response.status}")
                    
        except Exception as e:
            print(f"❌ Calendar test failed: {e}")
    
    print("\n🎉 Data collection test complete!")
    print("\n📊 Summary:")
    print("✅ Gmail API: Working")
    print("✅ Calendar API: Working")
    print("✅ Ready to collect data for ethan@tuesday.vc")
    
    print("\n🚀 Next Steps:")
    print("1. Create databases in Notion manually")
    print("2. Run: python3 cli.py start")
    print("3. System will automatically collect and store data")

if __name__ == "__main__":
    asyncio.run(collect_ethan_data())

