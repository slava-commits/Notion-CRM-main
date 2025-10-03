#!/usr/bin/env python3
"""
Store Data with Database IDs
Stores all collected data for ethan@tuesday.vc using existing database IDs
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

class DataStorer:
    def __init__(self):
        self.notion_token = Config.NOTION_TOKEN
        self.access_token = None
        self.notion_headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Database IDs - Updated with actual database IDs
        self.database_ids = {
            "People": "2771bb72-4b52-8156-821b-d2e1af65eb8d",
            "Companies": "2771bb72-4b52-8145-b204-f6190426ab01", 
            "Interactions": "2771bb72-4b52-8183-a579-c1c75decbedf",
            "Tasks": "2771bb72-4b52-819e-9f5b-ed853c2698ef"
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
    
    async def collect_gmail_data(self):
        """Collect all Gmail data for ethan@tuesday.vc"""
        print("📧 Collecting Gmail data...")
        
        gmail_headers = {"Authorization": f"Bearer {self.access_token}"}
        
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
                                    direction = 'Inbound' if 'ethan@tuesday.vc' in from_header.lower() else 'Outbound'
                                    
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
    
    async def create_page(self, database_name, properties):
        """Create a page in a database"""
        if database_name not in self.database_ids:
            print(f"❌ Database {database_name} not found")
            return None
        
        url = f"https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": self.database_ids[database_name]},
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
    
    async def store_all_data(self):
        """Store all collected data"""
        print("📝 Storing All Data in Notion")
        print("=" * 40)
        
        # Check if database IDs are set
        if "YOUR_PEOPLE_DATABASE_ID" in self.database_ids.values():
            print("❌ Please update database IDs in the script first!")
            print("\n📋 To get database IDs:")
            print("1. Create databases in Notion manually")
            print("2. Copy database ID from URL")
            print("3. Update this script with the IDs")
            print("4. Run again")
            return
        
        # Get access token
        await self.get_access_token()
        
        # Collect Gmail data
        email_data = await self.collect_gmail_data()
        
        # Create Ethan person record
        ethan_properties = {
            "Name": {"title": [{"text": {"content": "Ethan"}}]},
            "Primary Email": {"email": "ethan@tuesday.vc"},
            "Role": {"select": {"name": "Investor"}},
            "Company": {"rich_text": [{"text": {"content": "Tuesday VC"}}]},
            "Status": {"select": {"name": "Active"}},
            "Tier": {"select": {"name": "A"}}
        }
        
        ethan_page = await self.create_page("People", ethan_properties)
        if ethan_page:
            print("✅ Created Ethan person record")
        
        # Create Tuesday VC company record
        company_properties = {
            "Name": {"title": [{"text": {"content": "Tuesday VC"}}]},
            "Website": {"url": "https://tuesday.vc"},
            "Type": {"select": {"name": "Investor"}}
        }
        
        company_page = await self.create_page("Companies", company_properties)
        if company_page:
            print("✅ Created Tuesday VC company record")
        
        # Store all email interactions
        print(f"📧 Storing {len(email_data)} email interactions...")
        
        for i, email in enumerate(email_data):
            # Parse date
            try:
                from email.utils import parsedate_to_datetime
                parsed_date = parsedate_to_datetime(email['date'])
                date_str = parsed_date.strftime('%Y-%m-%d')
            except:
                date_str = "2025-01-01"  # fallback
            
            interaction_properties = {
                "Type": {"select": {"name": "Email Out" if email["direction"] == "Outbound" else "Email In"}},
                "Channel": {"select": {"name": "Gmail"}},
                "Subject/Title": {"title": [{"text": {"content": email["subject"]}}]},
                "Snippet/Link": {"url": f"https://gmail.com"},
                "Source Id": {"rich_text": [{"text": {"content": email["id"]}}]},
                "Date": {"date": {"start": date_str}},
                "Direction": {"select": {"name": email["direction"]}}
            }
            
            interaction_page = await self.create_page("Interactions", interaction_properties)
            if interaction_page:
                print(f"✅ Stored: {email['subject']} ({email['direction']})")
        
        # Create sample tasks
        print("📋 Creating sample tasks...")
        
        sample_tasks = [
            {
                "title": "Follow up on Jupid update",
                "status": "Todo",
                "priority": "High",
                "reason": "Waiting on reply"
            },
            {
                "title": "Schedule next meeting with Ethan",
                "status": "Todo",
                "priority": "Medium",
                "reason": "Next step"
            },
            {
                "title": "Send Jupid pitch deck",
                "status": "Todo",
                "priority": "High",
                "reason": "Next step"
            }
        ]
        
        for task in sample_tasks:
            task_properties = {
                "Title": {"title": [{"text": {"content": task["title"]}}]},
                "Status": {"select": {"name": task["status"]}},
                "Priority": {"select": {"name": task["priority"]}},
                "Reason": {"select": {"name": task["reason"]}}
            }
            
            task_page = await self.create_page("Tasks", task_properties)
            if task_page:
                print(f"✅ Created task: {task['title']}")
        
        print("\n🎉 Data storage complete!")
        print(f"📊 Stored:")
        print(f"   👤 1 person (Ethan)")
        print(f"   🏢 1 company (Tuesday VC)")
        print(f"   📧 {len(email_data)} email interactions")
        print(f"   📋 {len(sample_tasks)} tasks")

async def main():
    """Main function"""
    print("🎯 Storing All Data for ethan@tuesday.vc")
    print("=" * 60)
    
    storer = DataStorer()
    await storer.store_all_data()

if __name__ == "__main__":
    asyncio.run(main())
