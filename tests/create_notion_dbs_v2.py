#!/usr/bin/env python3
"""
Create Notion Databases v2
Creates all required databases in Notion workspace
"""

import asyncio
import aiohttp
import json
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionDatabaseCreator:
    def __init__(self):
        self.notion_token = Config.NOTION_TOKEN
        self.notion_headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.database_ids = {}
    
    async def get_workspace_pages(self):
        """Get workspace pages to use as parent"""
        try:
            async with aiohttp.ClientSession(headers=self.notion_headers) as session:
                # Try to get workspace pages
                url = "https://api.notion.com/v1/search"
                data = {
                    "query": "",
                    "filter": {
                        "value": "page",
                        "property": "object"
                    }
                }
                
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        pages = result.get('results', [])
                        if pages:
                            return pages[0]['id']  # Use first page as parent
                        else:
                            print("❌ No pages found in workspace")
                            return None
                    else:
                        error = await response.json()
                        print(f"❌ Failed to get workspace pages: {error}")
                        return None
        except Exception as e:
            print(f"❌ Error getting workspace pages: {e}")
            return None
    
    async def create_database(self, name, properties, parent_page_id):
        """Create a database in Notion"""
        print(f"📝 Creating database: {name}")
        
        # Create database schema
        schema = {
            "parent": {"page_id": parent_page_id},
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
        print("🏗️ Creating Notion Databases v2")
        print("=" * 50)
        
        # Get workspace page as parent
        parent_page_id = await self.get_workspace_pages()
        if not parent_page_id:
            print("❌ Could not find workspace page to use as parent")
            return False
        
        print(f"✅ Using workspace page as parent: {parent_page_id}")
        
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
        await self.create_database("People", people_props, parent_page_id)
        await self.create_database("Companies", companies_props, parent_page_id)
        await self.create_database("Interactions", interactions_props, parent_page_id)
        await self.create_database("Tasks", tasks_props, parent_page_id)
        
        return len(self.database_ids) > 0
    
    async def create_sample_data(self):
        """Create sample data for testing"""
        print("\n📝 Creating Sample Data")
        print("=" * 30)
        
        if not self.database_ids:
            print("❌ No databases created yet")
            return
        
        # Create Ethan person record
        ethan_properties = {
            "Name": {"title": [{"text": {"content": "Ethan Imboden"}}]},
            "Primary Email": {"email": "ethan@tuesday.vc"},
            "Role": {"select": {"name": "Investor"}},
            "Company": {"rich_text": [{"text": {"content": "Tuesday Capital"}}]},
            "Status": {"select": {"name": "Active"}},
            "Tier": {"select": {"name": "A"}}
        }
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            # Create Ethan person
            if "People" in self.database_ids:
                url = f"https://api.notion.com/v1/pages"
                data = {
                    "parent": {"database_id": self.database_ids["People"]},
                    "properties": ethan_properties
                }
                
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        print("✅ Created Ethan Imboden person record")
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create Ethan: {error}")
            
            # Create Tuesday Capital company
            company_properties = {
                "Name": {"title": [{"text": {"content": "Tuesday Capital"}}]},
                "Website": {"url": "https://tuesday.vc"},
                "Type": {"select": {"name": "Investor"}}
            }
            
            if "Companies" in self.database_ids:
                url = f"https://api.notion.com/v1/pages"
                data = {
                    "parent": {"database_id": self.database_ids["Companies"]},
                    "properties": company_properties
                }
                
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        print("✅ Created Tuesday Capital company record")
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create company: {error}")

async def main():
    """Main function"""
    print("🎯 Creating Notion Databases v2")
    print("=" * 60)
    
    creator = NotionDatabaseCreator()
    
    # Create databases
    success = await creator.create_all_databases()
    
    if success:
        print(f"\n🎉 Database creation complete!")
        print(f"Created {len(creator.database_ids)} databases:")
        for name, db_id in creator.database_ids.items():
            print(f"  - {name}: {db_id}")
        
        # Create sample data
        await creator.create_sample_data()
        
        print("\n🚀 Next Steps:")
        print("1. Check your Notion workspace")
        print("2. All databases and sample data are now created")
        print("3. Run: python3 store_data_with_ids.py")
        print("4. System will store all 20 emails")
    else:
        print("❌ Failed to create databases")

if __name__ == "__main__":
    asyncio.run(main())

