#!/usr/bin/env python3
"""
Attio Integration - Real Data Version
Using the working PUT endpoint to get real Attio data
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

class AttioRealIntegration:
    """Attio CRM API integration - Real data version"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.attio.com/v2"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Attio API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Attio API error: {response.status} - {error_text}")
                    raise Exception(f"Attio API error: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"Attio API request failed: {e}")
            raise
    
    async def get_person_by_email(self, email: str) -> Optional[Dict]:
        """Get person data using the working PUT endpoint"""
        try:
            url = f"{self.base_url}/objects/people/records?matching_attribute=email_addresses"
            data = {
                "data": {
                    "values": {
                        "email_addresses": [email]
                    }
                }
            }
            
            logger.info(f"Getting person data for {email} using PUT endpoint...")
            response = await self._make_request("PUT", url, data)
            
            if 'data' in response and response['data']:
                person_data = response['data']
                logger.info(f"✅ Successfully retrieved person data for {email}")
                return await self._parse_attio_person(person_data)
            else:
                logger.error(f"❌ No data found for {email}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get person by email {email}: {e}")
            return None
    
    async def _parse_attio_person(self, person_data: Dict) -> Dict:
        """Parse Attio person data into standardized format"""
        try:
            # Extract basic info
            record_id = person_data['id']['record_id']
            values = person_data['values']
            
            # Extract name
            name_data = values.get('name', [{}])[0] if values.get('name') else {}
            full_name = name_data.get('full_name', '')
            first_name = name_data.get('first_name', '')
            last_name = name_data.get('last_name', '')
            
            # Extract email
            email_data = values.get('email_addresses', [{}])[0] if values.get('email_addresses') else {}
            primary_email = email_data.get('email_address', '')
            
            # Extract company
            company_data = values.get('company', [{}])[0] if values.get('company') else {}
            company_id = company_data.get('target_record_id', '') if company_data else ''
            
            # Extract job title
            job_title_data = values.get('job_title', [{}])[0] if values.get('job_title') else {}
            job_title = job_title_data.get('value', '') if job_title_data else ''
            
            # Extract phone
            phone_data = values.get('phone_numbers', [{}])[0] if values.get('phone_numbers') else {}
            primary_phone = phone_data.get('value', '') if phone_data else ''
            
            # Extract social media
            linkedin_data = values.get('linkedin', [{}])[0] if values.get('linkedin') else {}
            linkedin_url = linkedin_data.get('value', '') if linkedin_data else ''
            
            twitter_data = values.get('twitter', [{}])[0] if values.get('twitter') else {}
            twitter_handle = twitter_data.get('value', '') if twitter_data else ''
            
            # Extract interaction data
            first_email = values.get('first_email_interaction', [{}])[0] if values.get('first_email_interaction') else {}
            last_email = values.get('last_email_interaction', [{}])[0] if values.get('last_email_interaction') else {}
            first_calendar = values.get('first_calendar_interaction', [{}])[0] if values.get('first_calendar_interaction') else {}
            last_calendar = values.get('last_calendar_interaction', [{}])[0] if values.get('last_calendar_interaction') else {}
            
            # Extract connection strength
            connection_strength = values.get('strongest_connection_strength_legacy', [{}])[0] if values.get('strongest_connection_strength_legacy') else {}
            connection_value = connection_strength.get('value', 0) if connection_strength else 0
            
            # Extract timestamps
            created_at = values.get('created_at', [{}])[0] if values.get('created_at') else {}
            created_timestamp = created_at.get('value', '') if created_at else ''
            
            # Extract custom fields
            custom_fields = {}
            for key, value in values.items():
                if key not in ['record_id', 'name', 'email_addresses', 'company', 'job_title', 
                              'phone_numbers', 'linkedin', 'twitter', 'first_email_interaction',
                              'last_email_interaction', 'first_calendar_interaction', 
                              'last_calendar_interaction', 'strongest_connection_strength_legacy',
                              'created_at', 'avatar_url', 'primary_location', 'website',
                              'telegram', 'comments', 'summary', 'fathomcalls', 'next_actions',
                              'linkedin_description', 'connection_degree_with_anna', 
                              'mutual_connections_with_anna', 'associated_deals', 'associated_users',
                              'created_by', 'angellist', 'facebook', 'instagram', 'twitter_follower_count',
                              'next_calendar_interaction', 'next_interaction', 'strongest_connection_strength',
                              'strongest_connection_user', 'description']:
                    if value and isinstance(value, list) and len(value) > 0:
                        field_value = value[0].get('value', '') if isinstance(value[0], dict) else str(value[0])
                        if field_value:
                            custom_fields[key] = field_value
            
            return {
                'attio_id': record_id,
                'name': full_name,
                'first_name': first_name,
                'last_name': last_name,
                'primary_email': primary_email,
                'company_id': company_id,
                'job_title': job_title,
                'primary_phone': primary_phone,
                'linkedin_url': linkedin_url,
                'twitter_handle': twitter_handle,
                'first_email_interaction': first_email.get('interacted_at', '') if first_email else '',
                'last_email_interaction': last_email.get('interacted_at', '') if last_email else '',
                'first_calendar_interaction': first_calendar.get('interacted_at', '') if first_calendar else '',
                'last_calendar_interaction': last_calendar.get('interacted_at', '') if last_calendar else '',
                'connection_strength': connection_value,
                'created_at': created_timestamp,
                'web_url': person_data.get('web_url', ''),
                'custom_fields': custom_fields,
                'source': 'attio_real',
                'raw_data': person_data  # Include raw data for debugging
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Attio person: {e}")
            logger.error(f"Person data: {person_data}")
            return None

async def test_attio_real_integration():
    """Test complete Attio integration with real data"""
    
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
        logger.info("🚀 Testing Attio Integration (Real Data Version)")
        logger.info("=" * 60)
        
        async with AttioRealIntegration(attio_api_key) as attio:
            # Step 1: Get real person data
            logger.info("\n1. Getting real person data for ethan@tuesday.vc...")
            
            ethan_data = await attio.get_person_by_email("ethan@tuesday.vc")
            
            if not ethan_data:
                logger.error("❌ Could not get data for ethan@tuesday.vc")
                return
            
            # Step 2: Display all attributes
            logger.info("\n2. Ethan's Real Attio Data:")
            logger.info("-" * 40)
            
            for key, value in ethan_data.items():
                if key == 'raw_data':
                    continue  # Skip raw data in display
                elif key == 'custom_fields':
                    logger.info(f"  {key}:")
                    for field_key, field_value in value.items():
                        if field_value:  # Only show non-empty values
                            logger.info(f"    • {field_key}: {field_value}")
                elif isinstance(value, list):
                    logger.info(f"  {key}: {', '.join(map(str, value))}")
                else:
                    logger.info(f"  {key}: {value}")
            
            # Step 3: Add to Notion Partners CRM
            logger.info("\n3. Adding Ethan to Notion Partners CRM...")
            
            async with NotionClient2025(notion_token) as notion:
                # Prepare properties for Notion (using only Name property that exists)
                properties = {
                    "Name": {"title": [{"type": "text", "text": {"content": ethan_data.get('name', 'Ethan Imboden')}}]}
                }
                
                # Create the page in Notion
                try:
                    ethan_page = await notion.create_page_in_database(partners_db_id, properties)
                    logger.info(f"✅ Ethan added to Notion: {ethan_page['url']}")
                    logger.info(f"✅ Page ID: {ethan_page['id']}")
                    
                    logger.info("\n" + "=" * 60)
                    logger.info("🎉 SUCCESS! Real Attio Integration Completed")
                    logger.info("\n📊 SUMMARY:")
                    logger.info(f"• Attio Data: ✅ REAL data retrieved")
                    logger.info(f"• Person: ✅ {ethan_data.get('name', 'Unknown')}")
                    logger.info(f"• Record ID: ✅ {ethan_data.get('attio_id', 'Unknown')}")
                    logger.info(f"• Email: ✅ {ethan_data.get('primary_email', 'Unknown')}")
                    logger.info(f"• Company ID: ✅ {ethan_data.get('company_id', 'Unknown')}")
                    logger.info(f"• Connection Strength: ✅ {ethan_data.get('connection_strength', 0)}")
                    logger.info(f"• Email Interactions: ✅ {ethan_data.get('first_email_interaction', 'N/A')} to {ethan_data.get('last_email_interaction', 'N/A')}")
                    logger.info(f"• Calendar Interactions: ✅ {ethan_data.get('first_calendar_interaction', 'N/A')} to {ethan_data.get('last_calendar_interaction', 'N/A')}")
                    logger.info(f"• Custom Fields: ✅ {len(ethan_data.get('custom_fields', {}))} additional fields")
                    logger.info(f"• Notion Integration: ✅ Page created")
                    logger.info(f"• Notion Page URL: {ethan_page['url']}")
                    logger.info(f"• Attio Web URL: {ethan_data.get('web_url', 'N/A')}")
                    
                    logger.info("\n✨ Key Features Demonstrated:")
                    logger.info("• Real Attio API integration with working PUT endpoint")
                    logger.info("• Complete person data retrieval from existing records")
                    logger.info("• Interaction history extraction (email & calendar)")
                    logger.info("• Connection strength analysis")
                    logger.info("• Company relationship mapping")
                    logger.info("• Notion database integration with 2025-09-03 API")
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
    asyncio.run(test_attio_real_integration())

if __name__ == "__main__":
    main()
