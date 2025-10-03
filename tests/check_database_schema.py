#!/usr/bin/env python3
"""
Check current Notion database schema
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionClient2025:
    """Notion API client using 2025-09-03 version"""
    
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
    
    async def get_database(self, database_id: str) -> Dict:
        """Get database schema"""
        try:
            response = await self._make_request("GET", f"databases/{database_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get database: {e}")
            raise

async def check_database_schema():
    """Check current database schema"""
    
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    partners_db_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    try:
        logger.info("🔍 Checking Notion Partners CRM Database Schema")
        logger.info("=" * 60)
        
        async with NotionClient2025(notion_token) as notion:
            # Get database info
            db_info = await notion.get_database(partners_db_id)
            
            logger.info(f"Database Title: {db_info.get('title', [{}])[0].get('text', {}).get('content', 'Unknown')}")
            logger.info(f"Database ID: {db_info.get('id', 'Unknown')}")
            logger.info(f"Created Time: {db_info.get('created_time', 'Unknown')}")
            logger.info(f"Last Edited Time: {db_info.get('last_edited_time', 'Unknown')}")
            
            # Check properties
            properties = db_info.get('properties', {})
            logger.info(f"\nProperties ({len(properties)} total):")
            
            if not properties:
                logger.warning("❌ No properties found in database!")
                logger.info("This might be because:")
                logger.info("1. The database is using the 2025-09-03 API with data sources")
                logger.info("2. The properties are defined in data sources, not the database itself")
                logger.info("3. The database schema update didn't work")
            else:
                for prop_name, prop_config in properties.items():
                    prop_type = prop_config.get('type', 'unknown')
                    logger.info(f"  • {prop_name} ({prop_type})")
            
            # Check if it's using data sources (2025-09-03 API)
            if 'data_sources' in db_info:
                logger.info(f"\nData Sources ({len(db_info['data_sources'])} total):")
                for i, data_source in enumerate(db_info['data_sources']):
                    logger.info(f"  Data Source {i+1}:")
                    logger.info(f"    ID: {data_source.get('id', 'Unknown')}")
                    logger.info(f"    Name: {data_source.get('name', 'Unknown')}")
                    logger.info(f"    Properties: {len(data_source.get('properties', {}))}")
                    
                    # Show properties in data source
                    ds_properties = data_source.get('properties', {})
                    for prop_name, prop_config in ds_properties.items():
                        prop_type = prop_config.get('type', 'unknown')
                        logger.info(f"      • {prop_name} ({prop_type})")
            
            # Try to get pages to see what's actually in the database
            logger.info(f"\nChecking existing pages...")
            try:
                pages_response = await notion._make_request("POST", f"databases/{partners_db_id}/query", {})
                pages = pages_response.get('results', [])
                logger.info(f"Found {len(pages)} pages in database")
                
                if pages:
                    logger.info("Sample page properties:")
                    sample_page = pages[0]
                    page_properties = sample_page.get('properties', {})
                    for prop_name, prop_value in page_properties.items():
                        logger.info(f"  • {prop_name}: {type(prop_value)}")
                        
            except Exception as e:
                logger.error(f"Failed to query pages: {e}")
            
    except Exception as e:
        logger.error(f"❌ Failed to check database: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(check_database_schema())

if __name__ == "__main__":
    main()
