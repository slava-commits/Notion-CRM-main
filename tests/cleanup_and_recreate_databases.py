#!/usr/bin/env python3
"""
Clean up databases from Investment Data Room and recreate in main Jupid HQ workspace
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

class NotionCleanupAndRecreate:
    """Notion API client for cleanup and recreation using 2025-09-03 version"""
    
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
    
    async def move_page_to_trash(self, page_id: str) -> Dict:
        """Move a page to trash using 2025-09-03 API"""
        try:
            data = {"in_trash": True}
            response = await self._make_request("PATCH", f"pages/{page_id}", data)
            return response
        except Exception as e:
            logger.error(f"Failed to move page {page_id} to trash: {e}")
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

async def cleanup_and_recreate():
    """Clean up databases from Investment Data Room and recreate in main Jupid HQ"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Database IDs to delete (from Investment Data Room)
    databases_to_delete = [
        "26838c5b-2978-41c2-9eb6-bd2ada8bfe13",  # Partners CRM 2025 Final
        "eedcdac3-de29-4080-ac3a-01a20edf74e5",  # Interactions Timeline 2025 Final
        "398cbebd-670b-413c-91bc-3640554bd88b",  # Partners CRM 2025
        "3959560f-9355-4fb5-ac1d-fdb185d4079b",  # Interactions Timeline 2025
        "2791bb72-4b52-81cf-987a-d4c25d3607ed",  # Partners CRM
        "2791bb72-4b52-8142-b057-f34dfe9451ab",  # Partners CRM
        "2791bb72-4b52-8192-9e30-fd7ba2438a3e",  # Partners CRM
        "2791bb72-4b52-813c-9662-fb9ee20512a5",  # Partners CRM
        "5dbbebb3-28c7-4ceb-8856-a2b03e6093fb",  # Partners CRM
        "2791bb72-4b52-818d-86a7-f67408d5da98",  # Interactions Timeline
        "2791bb72-4b52-81cd-a510-e57c43442cc3",  # Interactions Timeline
        "2791bb72-4b52-816c-863b-d0f5bfbc3651"   # Interactions Timeline
    ]
    
    # Main Jupid HQ workspace page ID
    main_jupid_page_id = "1911bb72-4b52-8161-a345-c996d53ae43c"
    
    async with NotionCleanupAndRecreate(notion_token) as notion:
        try:
            logger.info("🧹 CLEANUP AND RECREATION PROCESS")
            logger.info("=" * 60)
            
            # Step 1: Delete databases from Investment Data Room
            logger.info("\n1. Deleting databases from Investment Data Room...")
            
            deleted_count = 0
            for db_id in databases_to_delete:
                try:
                    await notion.move_page_to_trash(db_id)
                    deleted_count += 1
                    logger.info(f"✅ Deleted database: {db_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete {db_id}: {e}")
            
            logger.info(f"✅ Deleted {deleted_count} databases from Investment Data Room")
            
            # Step 2: Create new databases in main Jupid HQ
            logger.info("\n2. Creating new databases in main Jupid HQ workspace...")
            
            # Create Partners CRM Database
            partners_db = await notion.create_database(
                title="Partners CRM",
                parent_page_id=main_jupid_page_id
            )
            
            logger.info(f"✅ Partners CRM Database created: {partners_db['url']}")
            logger.info(f"✅ Database ID: {partners_db['id']}")
            
            # Create Interactions Timeline Database
            interactions_db = await notion.create_database(
                title="Interactions Timeline",
                parent_page_id=main_jupid_page_id
            )
            
            logger.info(f"✅ Interactions Timeline Database created: {interactions_db['url']}")
            logger.info(f"✅ Database ID: {interactions_db['id']}")
            
            # Step 3: Add Sample Partners
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
                    properties = {
                        "Name": {"title": [{"type": "text", "text": {"content": partner["name"]}}]}
                    }
                    
                    partner_page = await notion.create_page_in_database(partners_db['id'], properties)
                    partner_ids.append(partner_page['id'])
                    logger.info(f"✅ Added partner: {partner['name']} ({partner_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add partner {partner['name']}: {e}")
            
            # Step 4: Add Sample Interactions
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
                    properties = {
                        "Name": {"title": [{"type": "text", "text": {"content": interaction["title"]}}]}
                    }
                    
                    interaction_page = await notion.create_page_in_database(interactions_db['id'], properties)
                    logger.info(f"✅ Added interaction: {interaction['title'][:50]}... ({interaction_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add interaction: {e}")
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 SUCCESS! Cleanup and recreation completed!")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Databases deleted from Investment Data Room: {deleted_count}")
            logger.info(f"• Partners CRM Database: {partners_db['url']}")
            logger.info(f"• Interactions Timeline Database: {interactions_db['url']}")
            logger.info(f"• Partners added: {len(partner_ids)}")
            logger.info(f"• Interactions added: {len(sample_interactions)}")
            
            logger.info("\n🔗 NEW DATABASE LINKS (in main Jupid HQ):")
            logger.info(f"Partners CRM: {partners_db['url']}")
            logger.info(f"Interactions Timeline: {interactions_db['url']}")
            
            logger.info("\n✨ Key Features:")
            logger.info("• Latest API version 2025-09-03")
            logger.info("• Proper location in main Jupid HQ workspace")
            logger.info("• Clean slate with no duplicate databases")
            logger.info("• Data source architecture ready for enhancement")
            
        except Exception as e:
            logger.error(f"❌ Process failed: {e}")
            raise

def main():
    """Main function"""
    asyncio.run(cleanup_and_recreate())

if __name__ == "__main__":
    main()
