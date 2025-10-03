#!/usr/bin/env python3
"""
Create a complete Partners CRM database with all Attio attributes
Using stable 2022-06-28 API for better compatibility
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
    
    async def create_database(self, parent_page_id: str, title: str, properties: Dict) -> Dict:
        """Create a new database"""
        try:
            data = {
                "parent": {"type": "page_id", "page_id": parent_page_id},
                "title": [{"type": "text", "text": {"content": title}}],
                "properties": properties
            }
            
            response = await self._make_request("POST", "databases", data)
            return response
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    async def create_page_in_database(self, database_id: str, properties: Dict[str, Any]) -> Dict:
        """Create a new page in a database"""
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

def create_comprehensive_properties_schema() -> Dict[str, Any]:
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

async def create_complete_partners_database():
    """Create a complete Partners CRM database with all Attio attributes"""
    
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Jupid HQ page ID (from previous work)
    parent_page_id = "2761bb72-4b52-8168-b6ba-e07f36645035"
    
    try:
        logger.info("🚀 Creating Complete Partners CRM Database")
        logger.info("=" * 60)
        
        async with NotionClientStable(notion_token) as notion:
            # Step 1: Create comprehensive property schema
            logger.info("\n1. Creating comprehensive property schema...")
            
            properties = create_comprehensive_properties_schema()
            logger.info(f"Created schema with {len(properties)} properties")
            
            # Step 2: Create database
            logger.info("\n2. Creating Partners CRM database...")
            
            try:
                database = await notion.create_database(
                    parent_page_id=parent_page_id,
                    title="Partners CRM - Complete",
                    properties=properties
                )
                
                database_id = database['id']
                database_url = database['url']
                
                logger.info(f"✅ Database created successfully!")
                logger.info(f"📄 Database ID: {database_id}")
                logger.info(f"🌐 Database URL: {database_url}")
                
                # Step 3: Display created properties
                logger.info("\n3. Created database properties:")
                logger.info("-" * 40)
                
                created_properties = database.get('properties', {})
                for prop_name, prop_config in created_properties.items():
                    prop_type = prop_config.get('type', 'unknown')
                    logger.info(f"  • {prop_name} ({prop_type})")
                
                logger.info("\n" + "=" * 60)
                logger.info("🎉 SUCCESS! Complete Partners CRM Database Created")
                logger.info("=" * 60)
                
                logger.info("\n📊 DATABASE SUMMARY:")
                logger.info(f"• Database Name: Partners CRM - Complete")
                logger.info(f"• Total Properties: {len(created_properties)}")
                logger.info(f"• Database ID: {database_id}")
                logger.info(f"• Database URL: {database_url}")
                
                logger.info("\n✨ PROPERTY CATEGORIES:")
                logger.info("• Basic Info: Name, Email, Company, Job Title, Phone")
                logger.info("• Social Media: LinkedIn, Twitter/X, Website, Avatar")
                logger.info("• Location & Description: Location, Description, Comments, Summary")
                logger.info("• Interaction History: First/Last Email, First/Last Meeting")
                logger.info("• Connection Analysis: Connection Strength, Relationship Quality")
                logger.info("• System Info: Created At, Attio Record ID, Attio Web URL")
                logger.info("• Custom Fields: Custom Fields, Additional Attio Fields")
                logger.info("• Fathom Integration: FathomCalls, Next Actions")
                logger.info("• Future Planning: Next Calendar/Interaction")
                logger.info("• Associated Records: Associated Deals, Associated Users")
                
                logger.info("\n🔗 READY FOR ATTIO INTEGRATION!")
                logger.info("This database now supports all possible Attio attributes")
                
                return database_id
                
            except Exception as e:
                logger.error(f"❌ Failed to create database: {e}")
                return None
            
    except Exception as e:
        logger.error(f"❌ Database creation failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(create_complete_partners_database())

if __name__ == "__main__":
    main()
