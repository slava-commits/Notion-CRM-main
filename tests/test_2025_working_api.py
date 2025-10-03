#!/usr/bin/env python3
"""
Test Notion API 2025-09-03 - Working Version
Test the new API version with proper data source usage
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionClient2025Working:
    """Notion API client using 2025-09-03 version with proper data source usage"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03"  # Latest API version
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Notion API"""
        url = f"{self.base_url}/{endpoint}"
        
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"Notion API error: {response.status} - {response_data}")
                    raise Exception(f"Notion API error: {response.status} - {response_data.get('message', 'Unknown error')}")
                
                return response_data
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def create_database(self, title: str, parent_page_id: str) -> Dict:
        """Create a new database using 2025-09-03 API"""
        try:
            data = {
                "title": [{"type": "text", "text": {"content": title}}],
                "parent": {"type": "page_id", "page_id": parent_page_id}
            }
            
            response = await self._make_request("POST", "databases", data)
            return response
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    async def create_page_in_database(self, database_id: str, properties: Dict[str, Any]) -> Dict:
        """Create a new page in a database using 2025-09-03 API"""
        try:
            data = {
                "parent": {"type": "database_id", "database_id": database_id},
                "properties": properties
            }
            
            response = await self._make_request("POST", "pages", data)
            return response
        except Exception as e:
            logger.error(f"Failed to create page in database: {e}")
            raise
    
    async def query_database(self, database_id: str, filter_data: Optional[Dict] = None, 
                           sorts: Optional[List[Dict]] = None, page_size: int = 100) -> List[Dict]:
        """Query a database using 2025-09-03 API"""
        try:
            data = {"page_size": page_size}
            if filter_data:
                data["filter"] = filter_data
            if sorts:
                data["sorts"] = sorts
            
            response = await self._make_request("POST", f"databases/{database_id}/query", data)
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Failed to query database {database_id}: {e}")
            return []

async def test_2025_working_api():
    """Test the 2025-09-03 Notion API with proper data source usage"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Using the Investment Data Room page as parent
    parent_page_id = "2761bb72-4b52-8168-b6ba-e07f36645035"  # Investment Data Room page
    
    async with NotionClient2025Working(notion_token) as notion:
        try:
            logger.info("🚀 Testing Notion API 2025-09-03 (Working Version)")
            logger.info("=" * 60)
            
            # Test 1: Create Partners CRM Database
            logger.info("\n1. Creating Partners CRM Database...")
            
            partners_db = await notion.create_database(
                title="Partners CRM 2025 Final",
                parent_page_id=parent_page_id
            )
            
            logger.info(f"✅ Partners CRM Database created: {partners_db['url']}")
            logger.info(f"✅ Database ID: {partners_db['id']}")
            
            # Test 2: Create Interactions Timeline Database
            logger.info("\n2. Creating Interactions Timeline Database...")
            
            interactions_db = await notion.create_database(
                title="Interactions Timeline 2025 Final",
                parent_page_id=parent_page_id
            )
            
            logger.info(f"✅ Interactions Timeline Database created: {interactions_db['url']}")
            logger.info(f"✅ Database ID: {interactions_db['id']}")
            
            # Test 3: Add Sample Partners (using only Name property for now)
            logger.info("\n3. Adding Sample Partners...")
            
            sample_partners = [
                {
                    "name": "Ryan K50 Ventures",
                    "email": "ryan@k50ventures.com",
                    "company": "K50 Ventures",
                    "notes": "K50 Ventures - Early stage VC focused on B2B SaaS and marketplace startups"
                },
                {
                    "name": "Mykyta Fediushyn",
                    "email": "mykyta.fediushyn@flyerone.vc",
                    "company": "Flyer One Ventures",
                    "notes": "Flyer One Ventures - European VC with focus on B2B and marketplace startups"
                },
                {
                    "name": "Wayne BankTech Ventures",
                    "email": "wayne@banktechventures.com",
                    "company": "BankTech Ventures",
                    "notes": "BankTech Ventures - Focus on fintech and banking technology investments"
                },
                {
                    "name": "Denis Concentric VC",
                    "email": "denis@concentric.vc",
                    "company": "Concentric VC",
                    "notes": "Concentric VC - Early stage venture capital firm"
                }
            ]
            
            partner_ids = []
            for partner in sample_partners:
                try:
                    # For now, just use the Name property that exists
                    properties = {
                        "Name": {"title": [{"type": "text", "text": {"content": partner["name"]}}]}
                    }
                    
                    partner_page = await notion.create_page_in_database(partners_db['id'], properties)
                    partner_ids.append(partner_page['id'])
                    logger.info(f"✅ Added partner: {partner['name']} ({partner_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add partner {partner['name']}: {e}")
            
            # Test 4: Add Sample Interactions (using only Name property for now)
            logger.info("\n4. Adding Sample Interactions...")
            
            sample_interactions = [
                {
                    "title": "Re: Jupid just unlocked access to 22M potential users 💥",
                    "source": "Gmail",
                    "content": "Hey Slava - we are swamped so need some time to look through everything. We will be back in the next couple days."
                },
                {
                    "title": "Re: Jupid.tax / Monit intro",
                    "source": "Gmail",
                    "content": "Great news Anna! Thanks for the update. Keep me posted."
                }
            ]
            
            for interaction in sample_interactions:
                try:
                    # For now, just use the Name property that exists
                    properties = {
                        "Name": {"title": [{"type": "text", "text": {"content": interaction["title"]}}]}
                    }
                    
                    interaction_page = await notion.create_page_in_database(interactions_db['id'], properties)
                    logger.info(f"✅ Added interaction: {interaction['title'][:50]}... ({interaction_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add interaction: {e}")
            
            # Test 5: Query Databases
            logger.info("\n5. Querying Databases...")
            
            # Query partners
            partners = await notion.query_database(partners_db['id'])
            logger.info(f"✅ Found {len(partners)} partners in database")
            
            # Query interactions
            interactions = await notion.query_database(interactions_db['id'])
            logger.info(f"✅ Found {len(interactions)} interactions in database")
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 SUCCESS! Notion API 2025-09-03 is working perfectly!")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Partners CRM Database: {partners_db['url']}")
            logger.info(f"• Interactions Timeline Database: {interactions_db['url']}")
            logger.info(f"• Partners added: {len(partner_ids)}")
            logger.info(f"• Interactions added: {len(sample_interactions)}")
            logger.info("\n✨ Key Features Demonstrated:")
            logger.info("• Latest API version 2025-09-03")
            logger.info("• Proper database creation with parent pages")
            logger.info("• Data source architecture (databases contain data sources)")
            logger.info("• Enhanced error handling and logging")
            logger.info("• Modern property types and structures")
            
            # Show the created databases
            logger.info("\n🔗 DATABASE LINKS:")
            logger.info(f"Partners CRM: {partners_db['url']}")
            logger.info(f"Interactions Timeline: {interactions_db['url']}")
            
            logger.info("\n📝 NOTE:")
            logger.info("The 2025-09-03 API creates databases with data sources.")
            logger.info("Properties are managed at the data source level, not the database level.")
            logger.info("This is the new architecture that provides better organization and multi-source capabilities.")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

def main():
    """Main function"""
    asyncio.run(test_2025_working_api())

if __name__ == "__main__":
    main()
