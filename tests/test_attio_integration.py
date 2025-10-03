#!/usr/bin/env python3
"""
Test Attio Integration
Retrieve all attributes for ethan@tuesday.vc and put into Notion
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from integrations.attio_integration import AttioIntegration
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

async def test_attio_integration():
    """Test Attio integration by retrieving Ethan's data and adding to Notion"""
    
    # Get API keys from config
    attio_api_key = Config.ATTIO_API_KEY
    notion_token = Config.NOTION_TOKEN
    
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Partners CRM Database ID (from our previous creation)
    partners_db_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    try:
        logger.info("🚀 Testing Attio Integration")
        logger.info("=" * 60)
        
        # Step 1: Test Attio connection
        logger.info("\n1. Testing Attio connection...")
        
        async with AttioIntegration(attio_api_key) as attio:
            connection_test = await attio.test_connection()
            if not connection_test:
                logger.error("❌ Attio connection test failed")
                return
            
            logger.info("✅ Attio connection successful")
            
            # Step 2: Search for Ethan by email
            logger.info("\n2. Searching for ethan@tuesday.vc in Attio...")
            
            ethan_data = await attio.search_person_by_email("ethan@tuesday.vc")
            
            if not ethan_data:
                logger.warning("⚠️ No data found for ethan@tuesday.vc in Attio")
                logger.info("Trying alternative search methods...")
                
                # Try getting all people and filtering
                all_people = await attio.get_people(limit=100)
                ethan_matches = []
                
                for person in all_people:
                    emails = person.get('all_emails', [])
                    primary_email = person.get('primary_email', '')
                    
                    if ('ethan@tuesday.vc' in [e.lower() for e in emails] or 
                        'ethan@tuesday.vc' in primary_email.lower()):
                        ethan_matches.append(person)
                
                if ethan_matches:
                    ethan_data = ethan_matches[0]
                    logger.info(f"✅ Found Ethan using alternative search: {ethan_data.get('name', 'Unknown')}")
                else:
                    logger.error("❌ Ethan not found in Attio")
                    return
            else:
                logger.info(f"✅ Found Ethan: {ethan_data[0].get('name', 'Unknown')}")
                ethan_data = ethan_data[0]
            
            # Step 3: Display all attributes
            logger.info("\n3. Ethan's Attio attributes:")
            logger.info("-" * 40)
            
            for key, value in ethan_data.items():
                if isinstance(value, dict):
                    logger.info(f"  {key}: {value}")
                elif isinstance(value, list):
                    logger.info(f"  {key}: {', '.join(map(str, value))}")
                else:
                    logger.info(f"  {key}: {value}")
            
            # Step 4: Add to Notion Partners CRM
            logger.info("\n4. Adding Ethan to Notion Partners CRM...")
            
            async with NotionClient2025(notion_token) as notion:
                # Prepare properties for Notion
                properties = {
                    "Name": {"title": [{"type": "text", "text": {"content": ethan_data.get('name', 'Ethan Imboden')}}]}
                }
                
                # Add additional properties if they exist
                if ethan_data.get('primary_email'):
                    properties["Email"] = {"email": ethan_data['primary_email']}
                
                if ethan_data.get('company'):
                    properties["Company"] = {"rich_text": [{"type": "text", "text": {"content": ethan_data['company']}}]}
                
                if ethan_data.get('job_title'):
                    properties["Job Title"] = {"rich_text": [{"type": "text", "text": {"content": ethan_data['job_title']}}]}
                
                if ethan_data.get('primary_phone'):
                    properties["Phone"] = {"phone_number": ethan_data['primary_phone']}
                
                if ethan_data.get('linkedin_url'):
                    properties["LinkedIn"] = {"url": ethan_data['linkedin_url']}
                
                if ethan_data.get('twitter_handle'):
                    properties["Twitter/X"] = {"url": f"https://twitter.com/{ethan_data['twitter_handle']}"}
                
                # Add custom fields as notes
                custom_fields = ethan_data.get('custom_fields', {})
                if custom_fields:
                    notes_content = "Attio Custom Fields:\n"
                    for key, value in custom_fields.items():
                        notes_content += f"• {key}: {value}\n"
                    properties["Notes"] = {"rich_text": [{"type": "text", "text": {"content": notes_content}}]}
                
                # Add source information
                source_info = f"Source: Attio\nAttio ID: {ethan_data.get('attio_id', 'N/A')}\nLast Updated: {ethan_data.get('updated_at', 'N/A')}"
                if 'Notes' in properties:
                    properties["Notes"]["rich_text"][0]["text"]["content"] += f"\n\n{source_info}"
                else:
                    properties["Notes"] = {"rich_text": [{"type": "text", "text": {"content": source_info}}]}
                
                # Create the page in Notion
                try:
                    ethan_page = await notion.create_page_in_database(partners_db_id, properties)
                    logger.info(f"✅ Ethan added to Notion: {ethan_page['url']}")
                    logger.info(f"✅ Page ID: {ethan_page['id']}")
                    
                    logger.info("\n" + "=" * 60)
                    logger.info("🎉 SUCCESS! Attio Integration Test Completed")
                    logger.info("\n📊 SUMMARY:")
                    logger.info(f"• Attio Connection: ✅ Working")
                    logger.info(f"• Ethan Found: ✅ {ethan_data.get('name', 'Unknown')}")
                    logger.info(f"• Attributes Retrieved: ✅ {len(ethan_data)} fields")
                    logger.info(f"• Notion Integration: ✅ Page created")
                    logger.info(f"• Notion Page URL: {ethan_page['url']}")
                    
                    logger.info("\n✨ Key Features Demonstrated:")
                    logger.info("• Attio API connection and authentication")
                    logger.info("• Person search by email address")
                    logger.info("• Complete attribute extraction")
                    logger.info("• Notion database integration")
                    logger.info("• Data transformation and mapping")
                    logger.info("• Error handling and logging")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add Ethan to Notion: {e}")
                    return
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(test_attio_integration())

if __name__ == "__main__":
    main()
