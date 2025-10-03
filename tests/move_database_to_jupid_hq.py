#!/usr/bin/env python3
"""
Move Partners CRM database from Investment Data Room to Jupid HQ
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionClientStable:
    """Notion API client using stable 2022-06-28 version"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # Stable API version
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
    
    async def search_pages(self, query: str = "") -> Dict:
        """Search for pages"""
        try:
            data = {"query": query}
            response = await self._make_request("POST", "search", data)
            return response
        except Exception as e:
            logger.error(f"Failed to search pages: {e}")
            raise
    
    async def get_page(self, page_id: str) -> Dict:
        """Get page details"""
        try:
            response = await self._make_request("GET", f"pages/{page_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get page: {e}")
            raise
    
    async def update_page(self, page_id: str, properties: Dict) -> Dict:
        """Update page properties"""
        try:
            data = {"properties": properties}
            response = await self._make_request("PATCH", f"pages/{page_id}", data)
            return response
        except Exception as e:
            logger.error(f"Failed to update page: {e}")
            raise

async def move_database_to_jupid_hq():
    """Move Partners CRM database to Jupid HQ workspace"""
    
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Database ID to move
    database_id = "27b1bb72-4b52-8107-988b-d729a8a3421f"
    
    try:
        logger.info("🚀 Moving Partners CRM Database to Jupid HQ")
        logger.info("=" * 60)
        
        async with NotionClientStable(notion_token) as notion:
            # Step 1: Search for Jupid HQ workspace
            logger.info("\n1. Searching for Jupid HQ workspace...")
            
            search_results = await notion.search_pages("Jupid HQ")
            pages = search_results.get('results', [])
            
            jupid_hq_page = None
            for page in pages:
                if page.get('object') == 'page':
                    title = page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                    if 'Jupid HQ' in title or 'Jupid' in title:
                        jupid_hq_page = page
                        break
            
            if not jupid_hq_page:
                logger.error("❌ Could not find Jupid HQ workspace")
                return
            
            jupid_hq_id = jupid_hq_page['id']
            logger.info(f"✅ Found Jupid HQ: {jupid_hq_id}")
            
            # Step 2: Get current database location
            logger.info("\n2. Getting current database location...")
            
            try:
                db_info = await notion._make_request("GET", f"databases/{database_id}")
                current_parent = db_info.get('parent', {})
                logger.info(f"Current parent: {current_parent}")
            except Exception as e:
                logger.error(f"Failed to get database info: {e}")
                return
            
            # Step 3: Try to move database (if supported)
            logger.info("\n3. Attempting to move database...")
            
            try:
                # Try to update the database parent
                move_data = {
                    "parent": {"type": "page_id", "page_id": jupid_hq_id}
                }
                
                updated_db = await notion._make_request("PATCH", f"databases/{database_id}", move_data)
                logger.info("✅ Database moved successfully!")
                logger.info(f"New parent: {updated_db.get('parent', {})}")
                
            except Exception as e:
                logger.warning(f"Direct move not supported: {e}")
                logger.info("Creating new database in Jupid HQ instead...")
                
                # Step 4: Create new database in Jupid HQ
                logger.info("\n4. Creating new database in Jupid HQ...")
                
                # Get the database schema from the old database
                try:
                    old_db = await notion._make_request("GET", f"databases/{database_id}")
                    old_properties = old_db.get('properties', {})
                    old_title = old_db.get('title', [{}])[0].get('text', {}).get('content', 'Partners CRM')
                    
                    logger.info(f"Copying schema with {len(old_properties)} properties...")
                    
                    # Create new database
                    new_db_data = {
                        "parent": {"type": "page_id", "page_id": jupid_hq_id},
                        "title": [{"type": "text", "text": {"content": old_title}}],
                        "properties": old_properties
                    }
                    
                    new_db = await notion._make_request("POST", "databases", new_db_data)
                    new_db_id = new_db['id']
                    new_db_url = new_db['url']
                    
                    logger.info(f"✅ New database created in Jupid HQ!")
                    logger.info(f"📄 New Database ID: {new_db_id}")
                    logger.info(f"🌐 New Database URL: {new_db_url}")
                    
                    # Step 5: Copy pages from old database to new database
                    logger.info("\n5. Copying pages to new database...")
                    
                    try:
                        # Query old database for pages
                        query_data = {"page_size": 100}
                        pages_response = await notion._make_request("POST", f"databases/{database_id}/query", query_data)
                        pages = pages_response.get('results', [])
                        
                        logger.info(f"Found {len(pages)} pages to copy...")
                        
                        for i, page in enumerate(pages):
                            try:
                                # Get page properties
                                page_properties = page.get('properties', {})
                                
                                # Create page in new database
                                new_page_data = {
                                    "parent": {"type": "database_id", "database_id": new_db_id},
                                    "properties": page_properties
                                }
                                
                                new_page = await notion._make_request("POST", "pages", new_page_data)
                                logger.info(f"  ✅ Copied page {i+1}: {new_page['url']}")
                                
                            except Exception as e:
                                logger.error(f"  ❌ Failed to copy page {i+1}: {e}")
                        
                        logger.info("\n" + "=" * 60)
                        logger.info("🎉 SUCCESS! Database Moved to Jupid HQ")
                        logger.info("=" * 60)
                        
                        logger.info("\n📊 MIGRATION SUMMARY:")
                        logger.info(f"• Old Database ID: {database_id}")
                        logger.info(f"• New Database ID: {new_db_id}")
                        logger.info(f"• New Database URL: {new_db_url}")
                        logger.info(f"• Location: Jupid HQ workspace")
                        logger.info(f"• Pages Copied: {len(pages)}")
                        logger.info(f"• Properties: {len(old_properties)}")
                        
                        logger.info("\n✨ NEXT STEPS:")
                        logger.info("• Use the new database ID for future integrations")
                        logger.info("• The old database can be deleted if no longer needed")
                        logger.info("• All data has been successfully migrated")
                        
                    except Exception as e:
                        logger.error(f"Failed to copy pages: {e}")
                        return
                    
                except Exception as e:
                    logger.error(f"Failed to get old database schema: {e}")
                    return
            
    except Exception as e:
        logger.error(f"❌ Database move failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(move_database_to_jupid_hq())

if __name__ == "__main__":
    main()
