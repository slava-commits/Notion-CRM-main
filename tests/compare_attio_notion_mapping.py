#!/usr/bin/env python3
"""
Compare Attio data structure with Notion data structure
Verify proper mapping between the two systems
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
                return person_data
            else:
                logger.error(f"❌ No data found for {email}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get person by email {email}: {e}")
            return None

def extract_attio_value(attr_data, key='value'):
    """Extract value from Attio attribute"""
    if not attr_data or len(attr_data) == 0:
        return None
    item = attr_data[0]
    if isinstance(item, dict):
        return item.get(key)
    return str(item) if item else None

def extract_notion_value(prop_data, prop_type):
    """Extract value from Notion property based on type"""
    if not prop_data:
        return None
    
    if prop_type == 'title':
        title_text = prop_data.get('title', [])
        if title_text:
            return title_text[0].get('text', {}).get('content', '')
    elif prop_type == 'email':
        return prop_data.get('email', '')
    elif prop_type == 'rich_text':
        rich_text = prop_data.get('rich_text', [])
        if rich_text:
            return rich_text[0].get('text', {}).get('content', '')
    elif prop_type == 'url':
        return prop_data.get('url', '')
    elif prop_type == 'phone_number':
        return prop_data.get('phone_number', '')
    elif prop_type == 'number':
        return prop_data.get('number', '')
    elif prop_type == 'date':
        return prop_data.get('date', {}).get('start', '')
    elif prop_type == 'select':
        return prop_data.get('select', {}).get('name', '')
    
    return None

async def compare_attio_notion_mapping():
    """Compare Attio data structure with Notion data structure"""
    
    # Get API keys from config
    attio_api_key = Config.ATTIO_API_KEY
    notion_token = Config.NOTION_TOKEN
    
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Database ID in Jupid HQ
    database_id = "27b1bb72-4b52-81be-9982-c2fa850ba44e"
    
    try:
        logger.info("🔍 Comparing Attio vs Notion Data Structure")
        logger.info("=" * 80)
        
        # Step 1: Get Attio data
        logger.info("\n1. Getting Attio data...")
        
        async with AttioRealIntegration(attio_api_key) as attio:
            attio_data = await attio.get_person_by_email("ethan@tuesday.vc")
            
            if not attio_data:
                logger.error("❌ Could not get Attio data")
                return
        
        # Step 2: Get Notion data
        logger.info("\n2. Getting Notion data...")
        
        async with NotionClientStable(notion_token) as notion:
            query_response = await notion.query_database(database_id)
            pages = query_response.get('results', [])
            
            if not pages:
                logger.error("❌ No pages found in Notion database")
                return
            
            notion_page = pages[0]  # Get first page
            notion_properties = notion_page.get('properties', {})
        
        # Step 3: Analyze Attio data structure
        logger.info("\n3. Analyzing Attio data structure...")
        logger.info("-" * 50)
        
        attio_values = attio_data.get('values', {})
        attio_analysis = {}
        
        for attr_name, attr_data in attio_values.items():
            if attr_data and len(attr_data) > 0:
                # Get attribute type
                attr_type = attr_data[0].get('attribute_type', 'unknown')
                
                # Extract value
                value = extract_attio_value(attr_data)
                
                attio_analysis[attr_name] = {
                    'type': attr_type,
                    'value': value,
                    'raw_data': attr_data[0] if attr_data else None
                }
        
        logger.info(f"Attio attributes with data: {len(attio_analysis)}")
        for attr_name, attr_info in attio_analysis.items():
            logger.info(f"  • {attr_name} ({attr_info['type']}): {attr_info['value']}")
        
        # Step 4: Analyze Notion data structure
        logger.info("\n4. Analyzing Notion data structure...")
        logger.info("-" * 50)
        
        notion_analysis = {}
        
        for prop_name, prop_data in notion_properties.items():
            # Determine property type
            prop_type = None
            if 'title' in prop_data:
                prop_type = 'title'
            elif 'email' in prop_data:
                prop_type = 'email'
            elif 'rich_text' in prop_data:
                prop_type = 'rich_text'
            elif 'url' in prop_data:
                prop_type = 'url'
            elif 'phone_number' in prop_data:
                prop_type = 'phone_number'
            elif 'number' in prop_data:
                prop_type = 'number'
            elif 'date' in prop_data:
                prop_type = 'date'
            elif 'select' in prop_data:
                prop_type = 'select'
            
            # Extract value
            value = extract_notion_value(prop_data, prop_type) if prop_type else None
            
            notion_analysis[prop_name] = {
                'type': prop_type or 'unknown',
                'value': value,
                'has_data': value is not None and value != ''
            }
        
        logger.info(f"Notion properties: {len(notion_analysis)}")
        for prop_name, prop_info in notion_analysis.items():
            status = "✅" if prop_info['has_data'] else "❌"
            logger.info(f"  {status} {prop_name} ({prop_info['type']}): {prop_info['value']}")
        
        # Step 5: Compare mappings
        logger.info("\n5. Comparing data mappings...")
        logger.info("-" * 50)
        
        # Define expected mappings
        expected_mappings = {
            'name': 'Name',
            'email_addresses': 'Email',
            'company': 'Company',
            'job_title': 'Job Title',
            'phone_numbers': 'Phone',
            'linkedin': 'LinkedIn',
            'twitter': 'Twitter/X',
            'website': 'Website',
            'avatar_url': 'Avatar URL',
            'primary_location': 'Location',
            'description': 'Description',
            'comments': 'Comments',
            'summary': 'Summary',
            'first_email_interaction': 'First Email',
            'last_email_interaction': 'Last Email',
            'first_calendar_interaction': 'First Meeting',
            'last_calendar_interaction': 'Last Meeting',
            'first_interaction': 'First Interaction',
            'last_interaction': 'Last Interaction',
            'strongest_connection_strength_legacy': 'Connection Strength',
            'strongest_connection_strength': 'Relationship Quality',
            'created_at': 'Created At'
        }
        
        mapping_analysis = []
        
        for attio_field, notion_field in expected_mappings.items():
            attio_info = attio_analysis.get(attio_field, {})
            notion_info = notion_analysis.get(notion_field, {})
            
            attio_has_data = attio_info.get('value') is not None
            notion_has_data = notion_info.get('has_data', False)
            
            status = "✅" if (attio_has_data and notion_has_data) else "❌"
            
            mapping_analysis.append({
                'attio_field': attio_field,
                'notion_field': notion_field,
                'attio_value': attio_info.get('value'),
                'notion_value': notion_info.get('value'),
                'attio_type': attio_info.get('type'),
                'notion_type': notion_info.get('type'),
                'status': status,
                'mapped': attio_has_data and notion_has_data
            })
        
        # Display mapping results
        logger.info("\n📊 MAPPING ANALYSIS:")
        logger.info("=" * 80)
        
        mapped_count = 0
        for mapping in mapping_analysis:
            status = mapping['status']
            attio_field = mapping['attio_field']
            notion_field = mapping['notion_field']
            attio_value = mapping['attio_value']
            notion_value = mapping['notion_value']
            attio_type = mapping['attio_type']
            notion_type = mapping['notion_type']
            
            if mapping['mapped']:
                mapped_count += 1
            
            logger.info(f"{status} {attio_field} → {notion_field}")
            logger.info(f"    Attio: {attio_value} ({attio_type})")
            logger.info(f"    Notion: {notion_value} ({notion_type})")
            logger.info("")
        
        # Step 6: Summary
        logger.info("\n" + "=" * 80)
        logger.info("📈 MAPPING SUMMARY")
        logger.info("=" * 80)
        
        total_mappings = len(mapping_analysis)
        logger.info(f"• Total expected mappings: {total_mappings}")
        logger.info(f"• Successfully mapped: {mapped_count}")
        logger.info(f"• Mapping success rate: {(mapped_count/total_mappings)*100:.1f}%")
        
        # Identify issues
        issues = []
        for mapping in mapping_analysis:
            if not mapping['mapped']:
                attio_field = mapping['attio_field']
                notion_field = mapping['notion_field']
                attio_has_data = mapping['attio_value'] is not None
                notion_has_data = mapping['notion_value'] is not None
                
                if not attio_has_data:
                    issues.append(f"❌ {attio_field} has no data in Attio")
                elif not notion_has_data:
                    issues.append(f"❌ {notion_field} not populated in Notion")
        
        if issues:
            logger.info(f"\n🔍 ISSUES FOUND:")
            for issue in issues:
                logger.info(f"  {issue}")
        else:
            logger.info(f"\n✅ NO ISSUES FOUND - All mappings working correctly!")
        
        # Additional Attio fields not in standard mapping
        logger.info(f"\n📋 ADDITIONAL ATTIO FIELDS:")
        additional_fields = []
        for attr_name in attio_analysis.keys():
            if attr_name not in expected_mappings:
                additional_fields.append(attr_name)
        
        if additional_fields:
            for field in additional_fields:
                logger.info(f"  • {field} ({attio_analysis[field]['type']})")
        else:
            logger.info("  None")
        
        logger.info(f"\n🎉 DATA STRUCTURE COMPARISON COMPLETE!")
        
    except Exception as e:
        logger.error(f"❌ Comparison failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(compare_attio_notion_mapping())

if __name__ == "__main__":
    main()
