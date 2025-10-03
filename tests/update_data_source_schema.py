#!/usr/bin/env python3
"""
Update Notion data source schema with all Attio attributes
Using 2025-09-03 API with data sources
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
    """Notion API client using 2025-09-03 version with data sources"""
    
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
        """Get database with data sources"""
        try:
            response = await self._make_request("GET", f"databases/{database_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get database: {e}")
            raise
    
    async def update_data_source(self, data_source_id: str, properties: Dict) -> Dict:
        """Update data source properties"""
        try:
            data = {"properties": properties}
            response = await self._make_request("PATCH", f"data-sources/{data_source_id}", data)
            return response
        except Exception as e:
            logger.error(f"Failed to update data source: {e}")
            raise

def create_attio_data_source_properties() -> Dict[str, Any]:
    """Create comprehensive property schema for data source"""
    
    properties = {
        # Basic Information
        "Name": {
            "type": "title",
            "title": {}
        },
        "Email": {
            "type": "email",
            "email": {}
        },
        "Company": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Job Title": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Phone": {
            "type": "phone_number",
            "phone_number": {}
        },
        
        # Social Media & Web
        "LinkedIn": {
            "type": "url",
            "url": {}
        },
        "Twitter/X": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Website": {
            "type": "url",
            "url": {}
        },
        "Avatar URL": {
            "type": "url",
            "url": {}
        },
        
        # Location & Description
        "Location": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Description": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Comments": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Summary": {
            "type": "rich_text",
            "rich_text": {}
        },
        
        # Interaction History
        "First Email": {
            "type": "date",
            "date": {}
        },
        "Last Email": {
            "type": "date",
            "date": {}
        },
        "First Meeting": {
            "type": "date",
            "date": {}
        },
        "Last Meeting": {
            "type": "date",
            "date": {}
        },
        "First Interaction": {
            "type": "date",
            "date": {}
        },
        "Last Interaction": {
            "type": "date",
            "date": {}
        },
        
        # Connection Analysis
        "Connection Strength": {
            "type": "number",
            "number": {
                "format": "number"
            }
        },
        "Relationship Quality": {
            "type": "select",
            "select": {
                "options": [
                    {"name": "Excellent", "color": "green"},
                    {"name": "Good", "color": "blue"},
                    {"name": "Fair", "color": "yellow"},
                    {"name": "Poor", "color": "red"},
                    {"name": "Unknown", "color": "gray"}
                ]
            }
        },
        
        # System Information
        "Created At": {
            "type": "date",
            "date": {}
        },
        "Attio Record ID": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Attio Web URL": {
            "type": "url",
            "url": {}
        },
        
        # Custom Fields
        "Custom Fields": {
            "type": "rich_text",
            "rich_text": {}
        }
    }
    
    return properties

async def update_data_source_schema():
    """Update data source with all Attio attributes"""
    
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    partners_db_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    try:
        logger.info("🚀 Updating Notion Data Source Schema")
        logger.info("=" * 60)
        
        async with NotionClient2025(notion_token) as notion:
            # Step 1: Get database and data source info
            logger.info("\n1. Getting database and data source info...")
            
            db_info = await notion.get_database(partners_db_id)
            data_sources = db_info.get('data_sources', [])
            
            if not data_sources:
                logger.error("❌ No data sources found in database")
                return
            
            data_source = data_sources[0]
            data_source_id = data_source['id']
            data_source_name = data_source['name']
            
            logger.info(f"Data Source ID: {data_source_id}")
            logger.info(f"Data Source Name: {data_source_name}")
            logger.info(f"Current Properties: {len(data_source.get('properties', {}))}")
            
            # Step 2: Create comprehensive property schema
            logger.info("\n2. Creating comprehensive property schema...")
            
            new_properties = create_attio_data_source_properties()
            logger.info(f"Created schema with {len(new_properties)} properties")
            
            # Step 3: Update data source with new properties
            logger.info("\n3. Updating data source with new properties...")
            
            try:
                updated_ds = await notion.update_data_source(data_source_id, new_properties)
                logger.info("✅ Data source schema updated successfully!")
                
                # Step 4: Display updated schema
                logger.info("\n4. Updated data source schema:")
                logger.info("-" * 40)
                
                updated_properties = updated_ds.get('properties', {})
                for prop_name, prop_config in updated_properties.items():
                    prop_type = prop_config.get('type', 'unknown')
                    logger.info(f"  • {prop_name} ({prop_type})")
                
                logger.info("\n" + "=" * 60)
                logger.info("🎉 SUCCESS! Data Source Schema Updated")
                logger.info("=" * 60)
                
                logger.info("\n📊 SCHEMA SUMMARY:")
                logger.info(f"• Total Properties: {len(updated_properties)}")
                logger.info(f"• Data Source: {data_source_name}")
                logger.info(f"• Database: Partners CRM")
                
                logger.info("\n✨ READY FOR ATTIO INTEGRATION!")
                logger.info("The data source now supports all Attio attributes")
                
            except Exception as e:
                logger.error(f"❌ Failed to update data source schema: {e}")
                return
            
    except Exception as e:
        logger.error(f"❌ Schema update failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(update_data_source_schema())

if __name__ == "__main__":
    main()
