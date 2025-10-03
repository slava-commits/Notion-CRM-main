#!/usr/bin/env python3
"""
Check Ethan's page in the Partners CRM database
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
    
    async def query_database(self, database_id: str) -> Dict:
        """Query database for pages"""
        try:
            data = {"page_size": 100}
            response = await self._make_request("POST", f"databases/{database_id}/query", data)
            return response
        except Exception as e:
            logger.error(f"Failed to query database: {e}")
            raise
    
    async def get_page(self, page_id: str) -> Dict:
        """Get page details"""
        try:
            response = await self._make_request("GET", f"pages/{page_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get page: {e}")
            raise

async def check_ethan_page():
    """Check Ethan's page in the Partners CRM database"""
    
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # New database ID in Jupid HQ
    database_id = "27b1bb72-4b52-81be-9982-c2fa850ba44e"
    
    try:
        logger.info("🔍 Checking Ethan's Page in Partners CRM Database")
        logger.info("=" * 60)
        
        async with NotionClientStable(notion_token) as notion:
            # Step 1: Query database for pages
            logger.info("\n1. Querying database for pages...")
            
            query_response = await notion.query_database(database_id)
            pages = query_response.get('results', [])
            
            logger.info(f"Found {len(pages)} pages in database")
            
            if not pages:
                logger.error("❌ No pages found in database")
                return
            
            # Step 2: Check each page
            for i, page in enumerate(pages):
                logger.info(f"\n2. Checking page {i+1}...")
                
                page_id = page['id']
                page_url = page['url']
                properties = page.get('properties', {})
                
                logger.info(f"Page ID: {page_id}")
                logger.info(f"Page URL: {page_url}")
                
                # Check Name property
                name_property = properties.get('Name', {})
                if name_property:
                    name_title = name_property.get('title', [])
                    if name_title:
                        name_text = name_title[0].get('text', {}).get('content', '')
                        logger.info(f"Name: {name_text}")
                    else:
                        logger.warning("Name property exists but is empty")
                else:
                    logger.warning("❌ Name property not found")
                
                # Check Email property
                email_property = properties.get('Email', {})
                if email_property:
                    email_value = email_property.get('email', '')
                    logger.info(f"Email: {email_value}")
                else:
                    logger.warning("Email property not found")
                
                # Check other key properties
                key_properties = ['Company', 'Attio Record ID', 'Connection Strength', 'First Email', 'Last Email']
                for prop_name in key_properties:
                    prop_value = properties.get(prop_name, {})
                    if prop_value:
                        if prop_name == 'Connection Strength':
                            strength = prop_value.get('number', '')
                            logger.info(f"{prop_name}: {strength}")
                        elif prop_name in ['First Email', 'Last Email']:
                            date_value = prop_value.get('date', {}).get('start', '')
                            logger.info(f"{prop_name}: {date_value}")
                        else:
                            # Rich text or other types
                            if 'rich_text' in prop_value:
                                rich_text = prop_value['rich_text']
                                if rich_text:
                                    text_content = rich_text[0].get('text', {}).get('content', '')
                                    logger.info(f"{prop_name}: {text_content}")
                            elif 'url' in prop_value:
                                url_value = prop_value.get('url', '')
                                logger.info(f"{prop_name}: {url_value}")
                            else:
                                logger.info(f"{prop_name}: {prop_value}")
                    else:
                        logger.info(f"{prop_name}: (empty)")
                
                # Show all properties
                logger.info(f"\nAll properties ({len(properties)} total):")
                for prop_name, prop_value in properties.items():
                    logger.info(f"  • {prop_name}: {type(prop_value)}")
                
                break  # Only check first page for now
            
    except Exception as e:
        logger.error(f"❌ Failed to check page: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(check_ethan_page())

if __name__ == "__main__":
    main()
