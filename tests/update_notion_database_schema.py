#!/usr/bin/env python3
"""
Update Notion Partners CRM database schema with all Attio attributes
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
    
    async def update_database_properties(self, database_id: str, properties: Dict) -> Dict:
        """Update database properties"""
        try:
            data = {"properties": properties}
            response = await self._make_request("PATCH", f"databases/{database_id}", data)
            return response
        except Exception as e:
            logger.error(f"Failed to update database properties: {e}")
            raise

def create_attio_properties_schema() -> Dict[str, Any]:
    """Create comprehensive property schema for all Attio attributes"""
    
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
        },
        
        # Additional Attio Fields
        "Angellist": {
            "type": "url",
            "url": {}
        },
        "Facebook": {
            "type": "url",
            "url": {}
        },
        "Instagram": {
            "type": "url",
            "url": {}
        },
        "Telegram": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Twitter Follower Count": {
            "type": "number",
            "number": {
                "format": "number"
            }
        },
        
        # Fathom Integration
        "FathomCalls": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Next Actions": {
            "type": "rich_text",
            "rich_text": {}
        },
        "LinkedIn Description": {
            "type": "rich_text",
            "rich_text": {}
        },
        
        # Connection Analysis
        "Connection Degree with Anna": {
            "type": "number",
            "number": {
                "format": "number"
            }
        },
        "Mutual Connections with Anna": {
            "type": "number",
            "number": {
                "format": "number"
            }
        },
        
        # Future Interactions
        "Next Calendar Interaction": {
            "type": "date",
            "date": {}
        },
        "Next Interaction": {
            "type": "date",
            "date": {}
        },
        
        # Associated Records
        "Associated Deals": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Associated Users": {
            "type": "rich_text",
            "rich_text": {}
        }
    }
    
    return properties

async def update_notion_database_schema():
    """Update Notion Partners CRM database with all Attio attributes"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Partners CRM Database ID
    partners_db_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    try:
        logger.info("🚀 Updating Notion Partners CRM Database Schema")
        logger.info("=" * 60)
        
        async with NotionClient2025(notion_token) as notion:
            # Step 1: Get current database schema
            logger.info("\n1. Getting current database schema...")
            
            try:
                db_info = await notion.get_database(partners_db_id)
                current_properties = db_info.get('properties', {})
                logger.info(f"Current properties: {list(current_properties.keys())}")
            except Exception as e:
                logger.error(f"Failed to get current schema: {e}")
                return
            
            # Step 2: Create comprehensive property schema
            logger.info("\n2. Creating comprehensive property schema...")
            
            new_properties = create_attio_properties_schema()
            logger.info(f"Created schema with {len(new_properties)} properties")
            
            # Step 3: Update database with new properties
            logger.info("\n3. Updating database with new properties...")
            
            try:
                updated_db = await notion.update_database_properties(partners_db_id, new_properties)
                logger.info("✅ Database schema updated successfully!")
                
                # Step 4: Display updated schema
                logger.info("\n4. Updated database schema:")
                logger.info("-" * 40)
                
                updated_properties = updated_db.get('properties', {})
                for prop_name, prop_config in updated_properties.items():
                    prop_type = prop_config.get('type', 'unknown')
                    logger.info(f"  • {prop_name} ({prop_type})")
                
                logger.info("\n" + "=" * 60)
                logger.info("🎉 SUCCESS! Database Schema Updated")
                logger.info("=" * 60)
                
                logger.info("\n📊 SCHEMA SUMMARY:")
                logger.info(f"• Total Properties: {len(updated_properties)}")
                logger.info(f"• Basic Info: Name, Email, Company, Job Title, Phone")
                logger.info(f"• Social Media: LinkedIn, Twitter/X, Website, Avatar")
                logger.info(f"• Location & Description: Location, Description, Comments, Summary")
                logger.info(f"• Interaction History: First/Last Email, First/Last Meeting")
                logger.info(f"• Connection Analysis: Connection Strength, Relationship Quality")
                logger.info(f"• System Info: Created At, Attio Record ID, Attio Web URL")
                logger.info(f"• Custom Fields: Custom Fields, Additional Attio Fields")
                logger.info(f"• Fathom Integration: FathomCalls, Next Actions")
                logger.info(f"• Future Planning: Next Calendar/Interaction")
                logger.info(f"• Associated Records: Associated Deals, Associated Users")
                
                logger.info("\n✨ READY FOR ATTIO INTEGRATION!")
                logger.info("The database now supports all Attio attributes")
                
            except Exception as e:
                logger.error(f"❌ Failed to update database schema: {e}")
                return
            
    except Exception as e:
        logger.error(f"❌ Schema update failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(update_notion_database_schema())

if __name__ == "__main__":
    main()
