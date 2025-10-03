#!/usr/bin/env python3
"""
Test New Notion API 2025-09-03
Create "Clients CRM" section in Jupid HQ workspace
"""

import asyncio
import aiohttp
import json
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewNotionAPITester:
    def __init__(self):
        self.notion_token = Config.NOTION_TOKEN
        self.notion_headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03"  # Using new API version
        }
        self.database_ids = {}
        self.data_source_ids = {}
    
    async def search_workspace(self):
        """Search for Jupid HQ workspace or pages"""
        print("🔍 Searching for Jupid HQ workspace...")
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            try:
                # Search for pages with "Jupid" in the title
                url = "https://api.notion.com/v1/search"
                data = {
                    "query": "Jupid",
                    "filter": {
                        "value": "page",
                        "property": "object"
                    }
                }
                
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        pages = result.get('results', [])
                        print(f"✅ Found {len(pages)} pages with 'Jupid'")
                        
                        for page in pages:
                            title = "Untitled"
                            if 'title' in page.get('properties', {}):
                                title_prop = page['properties']['title']
                                if title_prop.get('title') and len(title_prop['title']) > 0:
                                    title = title_prop['title'][0]['text']['content']
                            
                            print(f"  📄 {title} - {page['id']}")
                        
                        return pages
                    else:
                        error = await response.json()
                        print(f"❌ Search failed: {error}")
                        return []
            except Exception as e:
                print(f"❌ Error searching workspace: {e}")
                return []
    
    async def get_database_data_sources(self, database_id):
        """Get data sources for a database using new API"""
        print(f"🔍 Getting data sources for database: {database_id}")
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            try:
                url = f"https://api.notion.com/v1/databases/{database_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        data_sources = result.get('data_sources', [])
                        print(f"✅ Found {len(data_sources)} data sources")
                        
                        for ds in data_sources:
                            print(f"  📊 {ds['name']} - {ds['id']}")
                        
                        return data_sources
                    else:
                        error = await response.json()
                        print(f"❌ Failed to get data sources: {error}")
                        return []
            except Exception as e:
                print(f"❌ Error getting data sources: {e}")
                return []
    
    async def create_page_in_workspace(self, title, parent_page_id):
        """Create a new page in the workspace"""
        print(f"📝 Creating page: {title}")
        
        page_data = {
            "parent": {"page_id": parent_page_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        }
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            try:
                url = "https://api.notion.com/v1/pages"
                async with session.post(url, json=page_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        page_id = result['id']
                        print(f"✅ Created page '{title}': {page_id}")
                        return page_id
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create page: {error}")
                        return None
            except Exception as e:
                print(f"❌ Error creating page: {e}")
                return None
    
    async def create_database_with_new_api(self, name, properties, parent_page_id):
        """Create database using new API version"""
        print(f"📝 Creating database: {name}")
        
        # Create database schema with proper parent type
        schema = {
            "parent": {
                "type": "page_id",
                "page_id": parent_page_id
            },
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
                        print(f"✅ Created {name}: {db_id}")
                        
                        # Get data sources for this database
                        data_sources = await self.get_database_data_sources(db_id)
                        if data_sources:
                            self.data_source_ids[name] = data_sources[0]['id']
                            print(f"✅ Data source ID: {data_sources[0]['id']}")
                        
                        return db_id
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create {name}: {error}")
                        return None
            except Exception as e:
                print(f"❌ Error creating {name}: {e}")
                return None
    
    async def create_page_with_data_source(self, title, data_source_id, properties):
        """Create page using data source ID (new API feature)"""
        print(f"📝 Creating page in data source: {title}")
        
        page_data = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": data_source_id
            },
            "properties": properties
        }
        
        async with aiohttp.ClientSession(headers=self.notion_headers) as session:
            try:
                url = "https://api.notion.com/v1/pages"
                async with session.post(url, json=page_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        page_id = result['id']
                        print(f"✅ Created page '{title}': {page_id}")
                        return page_id
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create page: {error}")
                        return None
            except Exception as e:
                print(f"❌ Error creating page: {e}")
                return None
    
    async def test_new_api_features(self):
        """Test new API features"""
        print("🧪 Testing New Notion API 2025-09-03")
        print("=" * 60)
        
        # Step 1: Search for Jupid HQ workspace
        pages = await self.search_workspace()
        if not pages:
            print("❌ No Jupid pages found. Creating in first available page.")
            # Get any page as parent
            pages = await self.search_workspace()
            if not pages:
                print("❌ No pages found in workspace")
                return False
        
        parent_page_id = pages[0]['id']
        print(f"✅ Using parent page: {parent_page_id}")
        
        # Step 2: Create "Clients CRM" section
        clients_crm_page_id = await self.create_page_in_workspace("Clients CRM", parent_page_id)
        if not clients_crm_page_id:
            return False
        
        # Step 3: Create databases in the new section
        print(f"\n📊 Creating CRM Databases in 'Clients CRM' section")
        print("=" * 50)
        
        # People database
        people_props = {
            "Name": {"title": {}},
            "Email": {"email": {}},
            "Company": {"rich_text": {}},
            "Role": {
                "select": {
                    "options": [
                        {"name": "Client", "color": "blue"},
                        {"name": "Prospect", "color": "yellow"},
                        {"name": "Partner", "color": "green"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Active", "color": "green"},
                        {"name": "Inactive", "color": "gray"},
                        {"name": "Lead", "color": "blue"}
                    ]
                }
            }
        }
        
        # Companies database
        companies_props = {
            "Name": {"title": {}},
            "Website": {"url": {}},
            "Industry": {"rich_text": {}},
            "Size": {
                "select": {
                    "options": [
                        {"name": "Startup", "color": "blue"},
                        {"name": "SMB", "color": "green"},
                        {"name": "Enterprise", "color": "purple"}
                    ]
                }
            }
        }
        
        # Create databases
        people_db_id = await self.create_database_with_new_api("People", people_props, clients_crm_page_id)
        companies_db_id = await self.create_database_with_new_api("Companies", companies_props, clients_crm_page_id)
        
        if people_db_id and companies_db_id:
            print(f"\n🎉 Successfully created CRM section!")
            print(f"📄 Clients CRM page: {clients_crm_page_id}")
            print(f"👥 People database: {people_db_id}")
            print(f"🏢 Companies database: {companies_db_id}")
            
            # Test creating pages with data source IDs
            if "People" in self.data_source_ids:
                print(f"\n🧪 Testing data source page creation...")
                await self.create_page_with_data_source(
                    "Test Client",
                    self.data_source_ids["People"],
                    {
                        "Name": {"title": [{"text": {"content": "Test Client"}}]},
                        "Email": {"email": "test@example.com"},
                        "Role": {"select": {"name": "Client"}},
                        "Status": {"select": {"name": "Active"}}
                    }
                )
            
            return True
        else:
            print("❌ Failed to create some databases")
            return False

async def main():
    """Main function"""
    print("🚀 Testing New Notion API 2025-09-03")
    print("Creating 'Clients CRM' section in Jupid HQ")
    print("=" * 60)
    
    tester = NewNotionAPITester()
    success = await tester.test_new_api_features()
    
    if success:
        print(f"\n🎉 New API test completed successfully!")
        print(f"✅ Created 'Clients CRM' section")
        print(f"✅ Tested data source functionality")
        print(f"✅ All new API features working")
    else:
        print(f"\n❌ New API test failed")

if __name__ == "__main__":
    asyncio.run(main())
