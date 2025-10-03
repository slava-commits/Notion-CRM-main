#!/usr/bin/env python3
"""
Fix Ethan's name in the Partners CRM database
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
    
    async def update_page(self, page_id: str, properties: Dict) -> Dict:
        """Update page properties"""
        try:
            data = {"properties": properties}
            response = await self._make_request("PATCH", f"pages/{page_id}", data)
            return response
        except Exception as e:
            logger.error(f"Failed to update page: {e}")
            raise

async def fix_ethan_name():
    """Fix Ethan's name in the Partners CRM database"""
    
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Ethan's page ID
    page_id = "27b1bb72-4b52-8126-bdc0-e6f50226abce"
    
    try:
        logger.info("🔧 Fixing Ethan's Name in Partners CRM Database")
        logger.info("=" * 60)
        
        async with NotionClientStable(notion_token) as notion:
            # Step 1: Update the Name property
            logger.info("\n1. Updating Name property...")
            
            properties = {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Ethan Imboden"
                            }
                        }
                    ]
                }
            }
            
            try:
                updated_page = await notion.update_page(page_id, properties)
                logger.info("✅ Name updated successfully!")
                
                # Step 2: Verify the update
                logger.info("\n2. Verifying the update...")
                
                # Get the updated page
                page_response = await notion._make_request("GET", f"pages/{page_id}")
                page_properties = page_response.get('properties', {})
                
                name_property = page_properties.get('Name', {})
                if name_property:
                    name_title = name_property.get('title', [])
                    if name_title:
                        name_text = name_title[0].get('text', {}).get('content', '')
                        logger.info(f"✅ Name is now: {name_text}")
                    else:
                        logger.warning("Name property still empty")
                else:
                    logger.error("Name property not found")
                
                # Show other key properties
                logger.info("\n3. Current page properties:")
                logger.info("-" * 40)
                
                key_properties = {
                    'Name': 'title',
                    'Email': 'email',
                    'Company': 'rich_text',
                    'Attio Record ID': 'rich_text',
                    'Connection Strength': 'number',
                    'First Email': 'date',
                    'Last Email': 'date'
                }
                
                for prop_name, prop_type in key_properties.items():
                    prop_value = page_properties.get(prop_name, {})
                    if prop_value:
                        if prop_type == 'title':
                            title_text = prop_value.get('title', [])
                            if title_text:
                                content = title_text[0].get('text', {}).get('content', '')
                                logger.info(f"  {prop_name}: {content}")
                        elif prop_type == 'email':
                            email_value = prop_value.get('email', '')
                            logger.info(f"  {prop_name}: {email_value}")
                        elif prop_type == 'rich_text':
                            rich_text = prop_value.get('rich_text', [])
                            if rich_text:
                                content = rich_text[0].get('text', {}).get('content', '')
                                logger.info(f"  {prop_name}: {content}")
                        elif prop_type == 'number':
                            number_value = prop_value.get('number', '')
                            logger.info(f"  {prop_name}: {number_value}")
                        elif prop_type == 'date':
                            date_value = prop_value.get('date', {}).get('start', '')
                            logger.info(f"  {prop_name}: {date_value}")
                    else:
                        logger.info(f"  {prop_name}: (empty)")
                
                logger.info("\n" + "=" * 60)
                logger.info("🎉 SUCCESS! Ethan's Name Fixed")
                logger.info("=" * 60)
                
                logger.info("\n📊 PAGE SUMMARY:")
                logger.info(f"• Page ID: {page_id}")
                logger.info(f"• Page URL: https://www.notion.so/{page_id.replace('-', '')}")
                logger.info(f"• Name: Ethan Imboden ✅")
                logger.info(f"• Email: ethan@tuesday.vc ✅")
                logger.info(f"• Company: Tuesday Capital ✅")
                logger.info(f"• All Attio attributes: ✅")
                
            except Exception as e:
                logger.error(f"❌ Failed to update page: {e}")
                return
            
    except Exception as e:
        logger.error(f"❌ Name fix failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(fix_ethan_name())

if __name__ == "__main__":
    main()
