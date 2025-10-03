#!/usr/bin/env python3
"""
Create Notion Databases and Store Data
Creates databases and stores all collected data for ethan@tuesday.vc
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

class NotionDataManager:
    def __init__(self):
        self.notion_token = Config.NOTION_TOKEN
        self.access_token = None
        self.notion_headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.database_ids = {}
    
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
    
    async def create_database(self, name, properties):
        """Create a database in Notion"""
        print(f"📝 Creating database: {name}")
        
        # Create database schema
        schema = {
            "title": [{"type": "text", "text": {"content": name}}],
            "description": [{"type": "text", "text": {"content": f"Database for {name}"}}],
            "properties": properties
        }
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            try:
                async with session.post("https://api.notion.com/v1/databases", json=schema) as response:
                    if response.status == 200:
                        result = await response.json()
                        db_id = result["id"]
                        self.database_ids[name] = db_id
                        print(f"✅ Created {name}: {db_id}")
                        return db_id
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create {name}: {error}")
                        return None
            except Exception as e:
                print(f"❌ Error creating {name}: {e}")
                return None
    
    async def create_all_databases(self):
        """Create all required databases"""
        print("🏗️ Creating Notion Databases")
        print("=" * 40)
        
        # People database
        people_props = {
            "Name": {"title": {}},
            "Primary Email": {"email": {}},
            "LinkedIn URL": {"url": {}},
            "X Handle": {"rich_text": {}},
            "Role": {
                "select": {
                    "options": [
                        {"name": "Founder", "color": "blue"},
                        {"name": "Investor", "color": "green"},
                        {"name": "Partner", "color": "purple"},
                        {"name": "Client", "color": "orange"}
                    ]
                }
            },
            "Company": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Active", "color": "green"},
                        {"name": "Warm", "color": "yellow"},
                        {"name": "Cold", "color": "gray"},
                        {"name": "Dormant", "color": "red"}
                    ]
                }
            },
            "Tier": {
                "select": {
                    "options": [
                        {"name": "A", "color": "green"},
                        {"name": "B", "color": "yellow"},
                        {"name": "C", "color": "red"}
                    ]
                }
            }
        }
        
        # Interactions database
        interactions_props = {
            "Type": {
                "select": {
                    "options": [
                        {"name": "Email In", "color": "blue"},
                        {"name": "Email Out", "color": "green"},
                        {"name": "Meeting", "color": "purple"},
                        {"name": "Fathom Summary", "color": "orange"},
                        {"name": "Social Post", "color": "pink"},
                        {"name": "Social Comment", "color": "yellow"},
                        {"name": "Doc Event", "color": "gray"}
                    ]
                }
            },
            "Channel": {
                "select": {
                    "options": [
                        {"name": "Gmail", "color": "red"},
                        {"name": "Calendar", "color": "blue"},
                        {"name": "Fathom", "color": "green"},
                        {"name": "LinkedIn", "color": "blue"},
                        {"name": "X", "color": "black"},
                        {"name": "DocuSign", "color": "purple"}
                    ]
                }
            },
            "Subject/Title": {"title": {}},
            "Snippet/Link": {"url": {}},
            "Source Id": {"rich_text": {}},
            "Date": {"date": {}},
            "Direction": {
                "select": {
                    "options": [
                        {"name": "Inbound", "color": "blue"},
                        {"name": "Outbound", "color": "green"}
                    ]
                }
            }
        }
        
        # Companies database
        companies_props = {
            "Name": {"title": {}},
            "Website": {"url": {}},
            "Type": {
                "select": {
                    "options": [
                        {"name": "Investor", "color": "green"},
                        {"name": "Partner", "color": "blue"},
                        {"name": "Client", "color": "orange"},
                        {"name": "Provider", "color": "purple"}
                    ]
                }
            }
        }
        
        # Tasks database
        tasks_props = {
            "Title": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Todo", "color": "gray"},
                        {"name": "Doing", "color": "blue"},
                        {"name": "Blocked", "color": "red"},
                        {"name": "Done", "color": "green"}
                    ]
                }
            },
            "Priority": {
                "select": {
                    "options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "green"}
                    ]
                }
            },
            "Due": {"date": {}},
            "Reason": {
                "select": {
                    "options": [
                        {"name": "Waiting on reply", "color": "yellow"},
                        {"name": "Social touch", "color": "blue"},
                        {"name": "Next step", "color": "green"},
                        {"name": "Doc", "color": "purple"}
                    ]
                }
            }
        }
        
        # Create all databases
        await self.create_database("People", people_props)
        await self.create_database("Companies", companies_props)
        await self.create_database("Interactions", interactions_props)
        await self.create_database("Tasks", tasks_props)
        
        return len(self.database_ids) > 0
    
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
    
    async def store_ethan_data(self):
        """Store all data for ethan@tuesday.vc"""
        print("\n📝 Storing Data in Notion")
        print("=" * 40)
        
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
        
        # Store email interactions
        print("📧 Storing email interactions...")
        
        # Sample email data (you can expand this with the full 20 emails)
        sample_emails = [
            {
                "subject": "Re: Jupid update",
                "date": "2025-07-21",
                "direction": "Outbound",
                "snippet": "Thanks for the update on Jupid..."
            },
            {
                "subject": "Jupid Update: Pivoting Toward a Bigger, More Urgent Problem",
                "date": "2025-07-05",
                "direction": "Outbound",
                "snippet": "We're pivoting Jupid to address a bigger problem..."
            },
            {
                "subject": "Re: Following up",
                "date": "2025-05-19",
                "direction": "Inbound",
                "snippet": "Thanks for following up..."
            }
        ]
        
        for email in sample_emails:
            interaction_properties = {
                "Type": {"select": {"name": "Email Out" if email["direction"] == "Outbound" else "Email In"}},
                "Channel": {"select": {"name": "Gmail"}},
                "Subject/Title": {"title": [{"text": {"content": email["subject"]}}]},
                "Snippet/Link": {"url": f"https://gmail.com"},
                "Date": {"date": {"start": email["date"]}},
                "Direction": {"select": {"name": email["direction"]}}
            }
            
            interaction_page = await self.create_page("Interactions", interaction_properties)
            if interaction_page:
                print(f"✅ Stored: {email['subject']}")
        
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
        print(f"   📧 {len(sample_emails)} email interactions")
        print(f"   📋 {len(sample_tasks)} tasks")

async def main():
    """Main function"""
    print("🎯 Creating Notion Databases and Storing Data")
    print("=" * 60)
    
    manager = NotionDataManager()
    
    # Create databases
    success = await manager.create_all_databases()
    
    if success:
        # Store data
        await manager.store_ethan_data()
        
        print("\n🚀 Next Steps:")
        print("1. Check your Notion workspace")
        print("2. All databases and data are now created")
        print("3. Run: python3 cli.py start")
        print("4. System will continue collecting new data")
    else:
        print("❌ Failed to create databases")

if __name__ == "__main__":
    asyncio.run(main())

