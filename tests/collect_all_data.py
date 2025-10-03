#!/usr/bin/env python3
"""
Collect All Data for ethan@tuesday.vc
Comprehensive data collection and storage in Notion
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.notion_token = Config.NOTION_TOKEN
        self.access_token = None
        self.notion_headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def get_access_token(self):
        """Get Google access token"""
        token_data = {
            'client_id': Config.GMAIL_CLIENT_ID,
            'client_secret': Config.GMAIL_CLIENT_SECRET,
            'refresh_token': Config.GMAIL_REFRESH_TOKEN,
            'grant_type': 'refresh_token'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post('https://oauth2.googleapis.com/token', data=token_data) as response:
                if response.status == 200:
                    token_response = await response.json()
                    self.access_token = token_response['access_token']
                    return True
                else:
                    print(f"❌ Token refresh failed: {response.status}")
                    return False
    
    async def get_gmail_headers(self):
        """Get Gmail API headers"""
        if not self.access_token:
            await self.get_access_token()
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def get_calendar_headers(self):
        """Get Calendar API headers"""
        if not self.access_token:
            await self.get_access_token()
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def collect_gmail_data(self):
        """Collect all Gmail data for ethan@tuesday.vc"""
        print("📧 Collecting Gmail data...")
        
        gmail_headers = await self.get_gmail_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                # Search for emails with ethan@tuesday.vc
                search_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
                params = {'q': 'ethan@tuesday.vc', 'maxResults': 50}
                
                async with session.get(search_url, headers=gmail_headers, params=params) as response:
                    if response.status == 200:
                        search_result = await response.json()
                        messages = search_result.get('messages', [])
                        print(f"✅ Found {len(messages)} emails with ethan@tuesday.vc")
                        
                        email_data = []
                        for msg in messages:
                            # Get full message details
                            msg_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg["id"]}'
                            async with session.get(msg_url, headers=gmail_headers) as msg_response:
                                if msg_response.status == 200:
                                    msg_data = await msg_response.json()
                                    
                                    # Extract email details
                                    headers = msg_data.get('payload', {}).get('headers', [])
                                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                                    from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
                                    to_header = next((h['value'] for h in headers if h['name'] == 'To'), '')
                                    date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                                    
                                    # Determine direction
                                    direction = 'inbound' if 'ethan@tuesday.vc' in from_header.lower() else 'outbound'
                                    
                                    email_data.append({
                                        'id': msg['id'],
                                        'subject': subject,
                                        'from': from_header,
                                        'to': to_header,
                                        'date': date_header,
                                        'direction': direction,
                                        'snippet': msg_data.get('snippet', ''),
                                        'thread_id': msg_data.get('threadId', '')
                                    })
                        
                        return email_data
                    else:
                        print(f"❌ Gmail search failed: {response.status}")
                        return []
                        
            except Exception as e:
                print(f"❌ Gmail collection failed: {e}")
                return []
    
    async def collect_calendar_data(self):
        """Collect all Calendar data for ethan@tuesday.vc"""
        print("📅 Collecting Calendar data...")
        
        calendar_headers = await self.get_calendar_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                # Get events from the last 90 days
                now = datetime.now()
                time_min = (now - timedelta(days=90)).isoformat() + 'Z'
                time_max = (now + timedelta(days=30)).isoformat() + 'Z'
                
                events_url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
                params = {
                    'timeMin': time_min,
                    'timeMax': time_max,
                    'maxResults': 100
                }
                
                async with session.get(events_url, headers=calendar_headers, params=params) as response:
                    if response.status == 200:
                        events_data = await response.json()
                        events = events_data.get('items', [])
                        print(f"✅ Found {len(events)} events in the last 90 days")
                        
                        # Filter for events with ethan@tuesday.vc
                        ethan_events = []
                        for event in events:
                            attendees = event.get('attendees', [])
                            for attendee in attendees:
                                if 'ethan@tuesday.vc' in attendee.get('email', '').lower():
                                    ethan_events.append({
                                        'id': event.get('id', ''),
                                        'title': event.get('summary', 'No Title'),
                                        'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', '')),
                                        'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
                                        'description': event.get('description', ''),
                                        'attendees': [a.get('email', '') for a in attendees],
                                        'location': event.get('location', ''),
                                        'status': event.get('status', '')
                                    })
                                    break
                        
                        print(f"✅ Found {len(ethan_events)} events with ethan@tuesday.vc")
                        return ethan_events
                    else:
                        print(f"❌ Calendar events failed: {response.status}")
                        return []
                        
            except Exception as e:
                print(f"❌ Calendar collection failed: {e}")
                return []
    
    async def create_notion_page(self, database_id, properties):
        """Create a page in Notion database"""
        url = f"https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.json()
                    print(f"❌ Failed to create page: {error}")
                    return None
    
    async def store_data_in_notion(self, email_data, calendar_data):
        """Store collected data in Notion"""
        print("📝 Storing data in Notion...")
        
        # First, let's find the database IDs
        # For now, we'll create pages in a simple way
        # You'll need to replace these with your actual database IDs
        
        print("📊 Data Summary:")
        print(f"   📧 Emails: {len(email_data)}")
        print(f"   📅 Events: {len(calendar_data)}")
        
        # Store email data
        for email in email_data:
            print(f"   📧 {email['subject']} ({email['direction']}) - {email['date']}")
        
        # Store calendar data
        for event in calendar_data:
            print(f"   📅 {event['title']} - {event['start']}")
        
        print("\n✅ Data collection complete!")
        print("\n📋 Next Steps:")
        print("1. Create databases in Notion manually")
        print("2. Get database IDs from Notion")
        print("3. Update this script with database IDs")
        print("4. Run again to store data in Notion")

async def main():
    """Main data collection function"""
    print("🎯 Collecting All Data for ethan@tuesday.vc")
    print("=" * 60)
    
    collector = DataCollector()
    
    # Collect Gmail data
    email_data = await collector.collect_gmail_data()
    
    # Collect Calendar data
    calendar_data = await collector.collect_calendar_data()
    
    # Store in Notion
    await collector.store_data_in_notion(email_data, calendar_data)
    
    print("\n🎉 Data Collection Complete!")
    print(f"📊 Total Data Collected:")
    print(f"   📧 {len(email_data)} emails")
    print(f"   📅 {len(calendar_data)} calendar events")
    print(f"   👤 1 person: ethan@tuesday.vc")

if __name__ == "__main__":
    asyncio.run(main())

