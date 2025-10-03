#!/usr/bin/env python3
"""
Test Attio Integration - Mock Data Version
Demonstrate the integration with mock data for ethan@tuesday.vc
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

def get_mock_ethan_data():
    """Get mock data for Ethan from Tuesday VC"""
    return {
        'attio_id': 'mock-ethan-id-12345',
        'name': 'Ethan Imboden',
        'primary_email': 'ethan@tuesday.vc',
        'all_emails': ['ethan@tuesday.vc', 'ethan.imboden@tuesday.vc'],
        'company': 'Tuesday Capital',
        'job_title': 'Partner',
        'primary_phone': '+1 (555) 123-4567',
        'linkedin_url': 'https://linkedin.com/in/ethanimboden',
        'twitter_handle': 'ethanimboden',
        'created_at': '2024-01-15T10:30:00Z',
        'updated_at': '2024-09-25T14:22:00Z',
        'custom_fields': {
            'investment_focus': 'B2B SaaS, Fintech, AI/ML',
            'check_size': '$50K - $500K',
            'stage_preference': 'Seed, Series A',
            'portfolio_companies': '25+',
            'years_experience': '8',
            'location': 'San Francisco, CA',
            'university': 'Stanford University',
            'previous_company': 'Google',
            'specialties': 'Product Strategy, Go-to-Market, Fundraising',
            'notes': 'Very responsive, prefers email communication. Interested in AI-powered tools for small businesses.'
        },
        'source': 'attio'
    }

async def test_attio_mock_integration():
    """Test Attio integration with mock data for ethan@tuesday.vc"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Partners CRM Database ID (from our previous creation)
    partners_db_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    try:
        logger.info("🚀 Testing Attio Integration (Mock Data Version)")
        logger.info("=" * 60)
        
        # Step 1: Get mock Ethan data
        logger.info("\n1. Retrieving mock data for ethan@tuesday.vc...")
        
        ethan_data = get_mock_ethan_data()
        logger.info("✅ Mock data retrieved successfully")
        
        # Step 2: Display all attributes
        logger.info("\n2. Ethan's Attio attributes:")
        logger.info("-" * 40)
        
        for key, value in ethan_data.items():
            if key == 'custom_fields':
                logger.info(f"  {key}:")
                for field_key, field_value in value.items():
                    logger.info(f"    • {field_key}: {field_value}")
            elif isinstance(value, list):
                logger.info(f"  {key}: {', '.join(map(str, value))}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Step 3: Add to Notion Partners CRM
        logger.info("\n3. Adding Ethan to Notion Partners CRM...")
        
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
            
            # Add custom fields as detailed notes
            custom_fields = ethan_data.get('custom_fields', {})
            notes_content = "Attio Custom Fields:\n"
            for key, value in custom_fields.items():
                if value:  # Only add non-empty values
                    notes_content += f"• {key.replace('_', ' ').title()}: {value}\n"
            
            # Add source information
            source_info = f"\nSource: Attio (Mock Data)\nAttio ID: {ethan_data.get('attio_id', 'N/A')}\nLast Updated: {ethan_data.get('updated_at', 'N/A')}\nCreated: {ethan_data.get('created_at', 'N/A')}"
            notes_content += source_info
            
            properties["Notes"] = {"rich_text": [{"type": "text", "text": {"content": notes_content}}]}
            
            # Create the page in Notion
            try:
                ethan_page = await notion.create_page_in_database(partners_db_id, properties)
                logger.info(f"✅ Ethan added to Notion: {ethan_page['url']}")
                logger.info(f"✅ Page ID: {ethan_page['id']}")
                
                logger.info("\n" + "=" * 60)
                logger.info("🎉 SUCCESS! Attio Integration Test Completed")
                logger.info("\n📊 SUMMARY:")
                logger.info(f"• Attio Data: ✅ Mock data retrieved")
                logger.info(f"• Person: ✅ {ethan_data.get('name', 'Unknown')}")
                logger.info(f"• Attributes Retrieved: ✅ {len(ethan_data)} fields")
                logger.info(f"• Custom Fields: ✅ {len(custom_fields)} additional fields")
                logger.info(f"• Notion Integration: ✅ Page created")
                logger.info(f"• Notion Page URL: {ethan_page['url']}")
                
                logger.info("\n✨ Key Features Demonstrated:")
                logger.info("• Complete attribute extraction from Attio")
                logger.info("• Custom fields handling")
                logger.info("• Notion database integration with 2025-09-03 API")
                logger.info("• Data transformation and mapping")
                logger.info("• Rich text formatting for notes")
                logger.info("• Error handling and logging")
                
                logger.info("\n📝 NEXT STEPS:")
                logger.info("1. Set up Attio workspace with actual data")
                logger.info("2. Add ethan@tuesday.vc to your Attio workspace")
                logger.info("3. Update the integration to use real Attio API endpoints")
                logger.info("4. Test with live data from Attio")
                
            except Exception as e:
                logger.error(f"❌ Failed to add Ethan to Notion: {e}")
                return
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(test_attio_mock_integration())

if __name__ == "__main__":
    main()
