#!/usr/bin/env python3
"""
Test Attio Integration - Using Object ID
Use the people object ID to get actual records
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

class AttioIntegrationWithObjectID:
    """Attio CRM API integration - Using object ID to get records"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.attio.com/v2"
        self.session = None
        self.people_object_id = "82febeeb-fef5-42f0-a91a-6a8956783666"  # From the debug output
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Attio API"""
        url = f"{self.base_url}/{endpoint}"
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
    
    async def get_people_records(self) -> List[Dict]:
        """Get people records using the object ID"""
        try:
            # Try different endpoints with the object ID
            endpoints_to_try = [
                f"objects/{self.people_object_id}/records",
                f"objects/{self.people_object_id}",
                f"records/{self.people_object_id}",
                f"objects/people/{self.people_object_id}/records",
                f"objects/people/{self.people_object_id}",
            ]
            
            for endpoint in endpoints_to_try:
                logger.info(f"Trying endpoint: GET {endpoint}")
                
                try:
                    response = await self._make_request("GET", endpoint)
                    
                    if 'data' in response and isinstance(response['data'], list):
                        logger.info(f"✅ SUCCESS! Found {len(response['data'])} records")
                        return response['data']
                    else:
                        logger.info(f"❌ No records found in response")
                        logger.info(f"Response keys: {list(response.keys())}")
                        
                except Exception as e:
                    logger.info(f"❌ Failed: {e}")
            
            # Try POST with the object ID
            logger.info("Trying POST approaches...")
            
            post_endpoints = [
                (f"objects/{self.people_object_id}/records", {"filter": {}}),
                (f"objects/{self.people_object_id}/records", {"data": {"filter": {}}}),
                (f"records/search", {"query": "", "objects": [self.people_object_id]}),
                (f"search", {"query": "", "object_types": ["people"]}),
            ]
            
            for endpoint, data in post_endpoints:
                logger.info(f"Trying: POST {endpoint}")
                
                try:
                    response = await self._make_request("POST", endpoint, data)
                    
                    if 'data' in response and isinstance(response['data'], list):
                        logger.info(f"✅ SUCCESS! Found {len(response['data'])} records")
                        return response['data']
                    else:
                        logger.info(f"❌ No records found in response")
                        
                except Exception as e:
                    logger.info(f"❌ Failed: {e}")
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get people records: {e}")
            return []
    
    async def get_all_people(self) -> List[Dict]:
        """Get all people from Attio"""
        try:
            records = await self.get_people_records()
            
            people = []
            for person in records:
                person_data = await self._parse_person(person)
                if person_data:
                    people.append(person_data)
            
            return people
            
        except Exception as e:
            logger.error(f"Failed to get all people: {e}")
            return []
    
    async def search_person_by_email(self, email: str) -> Optional[Dict]:
        """Search for a person by email"""
        try:
            all_people = await self.get_all_people()
            
            # Look for exact email match
            for person in all_people:
                if email.lower() in [e.lower() for e in person.get('all_emails', [])]:
                    return person
                elif email.lower() == person.get('primary_email', '').lower():
                    return person
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to search person by email {email}: {e}")
            return None
    
    async def _parse_person(self, person: Dict) -> Optional[Dict]:
        """Parse Attio person into standardized format"""
        try:
            person_id = person.get('id', {}).get('value', '') if isinstance(person.get('id'), dict) else str(person.get('id', ''))
            attributes = person.get('attributes', {})
            
            # Extract basic information
            name = attributes.get('name', {}).get('value', '') if isinstance(attributes.get('name'), dict) else str(attributes.get('name', ''))
            
            # Handle email addresses
            email_data = attributes.get('email_addresses', {})
            if isinstance(email_data, dict):
                email = email_data.get('value', [])
            else:
                email = [email_data] if email_data else []
            primary_email = email[0] if email else ''
            
            # Extract company information
            company = attributes.get('company', {}).get('value', '') if isinstance(attributes.get('company'), dict) else str(attributes.get('company', ''))
            job_title = attributes.get('job_title', {}).get('value', '') if isinstance(attributes.get('job_title'), dict) else str(attributes.get('job_title', ''))
            
            # Extract contact information
            phone_data = attributes.get('phone_numbers', {})
            if isinstance(phone_data, dict):
                phone = phone_data.get('value', [])
            else:
                phone = [phone_data] if phone_data else []
            primary_phone = phone[0] if phone else ''
            
            # Extract social media
            linkedin_url = attributes.get('linkedin_url', {}).get('value', '') if isinstance(attributes.get('linkedin_url'), dict) else str(attributes.get('linkedin_url', ''))
            twitter_handle = attributes.get('twitter_handle', {}).get('value', '') if isinstance(attributes.get('twitter_handle'), dict) else str(attributes.get('twitter_handle', ''))
            
            # Extract additional fields
            created_at = attributes.get('created_at', {}).get('value', '') if isinstance(attributes.get('created_at'), dict) else str(attributes.get('created_at', ''))
            updated_at = attributes.get('updated_at', {}).get('value', '') if isinstance(attributes.get('updated_at'), dict) else str(attributes.get('updated_at', ''))
            
            # Extract custom fields
            custom_fields = {}
            for key, value in attributes.items():
                if key not in ['name', 'email_addresses', 'company', 'job_title', 
                              'phone_numbers', 'linkedin_url', 'twitter_handle', 
                              'created_at', 'updated_at']:
                    if isinstance(value, dict):
                        custom_fields[key] = value.get('value', '')
                    else:
                        custom_fields[key] = str(value) if value is not None else ''
            
            return {
                'attio_id': person_id,
                'name': name,
                'primary_email': primary_email,
                'all_emails': email,
                'company': company,
                'job_title': job_title,
                'primary_phone': primary_phone,
                'linkedin_url': linkedin_url,
                'twitter_handle': twitter_handle,
                'created_at': created_at,
                'updated_at': updated_at,
                'custom_fields': custom_fields,
                'source': 'attio',
                'raw_data': person  # Include raw data for debugging
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Attio person: {e}")
            logger.error(f"Person data: {person}")
            return None

async def test_attio_with_object_id():
    """Test Attio integration using object ID"""
    
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
        logger.info("🚀 Testing Attio Integration (Using Object ID)")
        logger.info("=" * 60)
        
        async with AttioIntegrationWithObjectID(attio_api_key) as attio:
            # Step 1: Get all people
            logger.info("\n1. Getting all people from Attio...")
            
            all_people = await attio.get_all_people()
            logger.info(f"✅ Retrieved {len(all_people)} people from Attio")
            
            if all_people:
                logger.info("People found:")
                for i, person in enumerate(all_people):
                    name = person.get('name', 'Unknown')
                    email = person.get('primary_email', 'No email')
                    logger.info(f"  {i+1}. {name} - {email}")
            
            # Step 2: Search for Ethan specifically
            logger.info("\n2. Searching for ethan@tuesday.vc...")
            
            ethan_data = await attio.search_person_by_email("ethan@tuesday.vc")
            
            if not ethan_data:
                logger.info("Ethan not found with exact email. Checking all people for Ethan...")
                
                # Look for Ethan in all people
                for person in all_people:
                    name = person.get('name', '').lower()
                    emails = person.get('all_emails', [])
                    email_str = ' '.join(emails).lower()
                    
                    if 'ethan' in name or 'ethan' in email_str or 'tuesday' in email_str:
                        logger.info(f"✅ Found potential Ethan: {person.get('name')} - {person.get('primary_email')}")
                        ethan_data = person
                        break
                
                if not ethan_data:
                    logger.error("❌ ethan@tuesday.vc not found in Attio")
                    logger.info("Available people:")
                    for person in all_people:
                        logger.info(f"  • {person.get('name')} - {person.get('primary_email')} - {person.get('all_emails')}")
                    return
            else:
                logger.info(f"✅ Found Ethan: {ethan_data.get('name', 'Unknown')}")
            
            # Step 3: Display all attributes
            logger.info("\n3. Ethan's Attio attributes:")
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
            
            # Step 4: Add to Notion Partners CRM
            logger.info("\n4. Adding Ethan to Notion Partners CRM...")
            
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
                    logger.info(f"• Attio Data: ✅ Real data retrieved")
                    logger.info(f"• Person: ✅ {ethan_data.get('name', 'Unknown')}")
                    logger.info(f"• Attributes Retrieved: ✅ {len(ethan_data)} fields")
                    logger.info(f"• Custom Fields: ✅ {len(ethan_data.get('custom_fields', {}))} additional fields")
                    logger.info(f"• Notion Integration: ✅ Page created")
                    logger.info(f"• Notion Page URL: {ethan_page['url']}")
                    
                    logger.info("\n✨ Key Features Demonstrated:")
                    logger.info("• Real Attio API integration with object ID")
                    logger.info("• Complete attribute extraction from real data")
                    logger.info("• Notion database integration")
                    logger.info("• Data transformation and mapping")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add Ethan to Notion: {e}")
                    return
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(test_attio_with_object_id())

if __name__ == "__main__":
    main()