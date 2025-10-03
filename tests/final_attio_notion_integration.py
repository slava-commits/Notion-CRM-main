#!/usr/bin/env python3
"""
Final Complete Attio to Notion Integration
Add all possible Attio attributes to the complete Partners CRM database
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

def create_complete_notion_properties_from_attio(attio_data: Dict) -> Dict[str, Any]:
    """Convert Attio data to complete Notion properties format"""
    properties = {}
    
    if 'values' not in attio_data:
        return properties
    
    values = attio_data['values']
    
    # Helper function to extract value from Attio attribute
    def extract_value(attr_data, key='value'):
        if not attr_data or len(attr_data) == 0:
            return None
        item = attr_data[0]
        if isinstance(item, dict):
            return item.get(key)
        return str(item) if item else None
    
    # Helper function to extract multiple values
    def extract_values(attr_data, key='value'):
        if not attr_data or len(attr_data) == 0:
            return []
        return [item.get(key) for item in attr_data if isinstance(item, dict) and item.get(key)]
    
    # Basic information
    if 'name' in values:
        name_data = extract_value(values['name'])
        if name_data:
            properties['Name'] = {"title": [{"type": "text", "text": {"content": name_data}}]}
    
    # Email addresses
    if 'email_addresses' in values:
        email_data = extract_value(values['email_addresses'], 'email_address')
        if email_data:
            properties['Email'] = {"email": email_data}
    
    # Company (as text for now, could be enhanced with relation)
    if 'company' in values:
        company_data = extract_value(values['company'], 'target_record_id')
        if company_data:
            properties['Company'] = {"rich_text": [{"type": "text", "text": {"content": f"Company ID: {company_data}"}}]}
    
    # Job title
    if 'job_title' in values:
        job_title = extract_value(values['job_title'])
        if job_title:
            properties['Job Title'] = {"rich_text": [{"type": "text", "text": {"content": job_title}}]}
    
    # Phone numbers
    if 'phone_numbers' in values:
        phone_data = extract_value(values['phone_numbers'])
        if phone_data:
            properties['Phone'] = {"phone_number": phone_data}
    
    # LinkedIn
    if 'linkedin' in values:
        linkedin_data = extract_value(values['linkedin'])
        if linkedin_data:
            properties['LinkedIn'] = {"url": linkedin_data}
    
    # Twitter
    if 'twitter' in values:
        twitter_data = extract_value(values['twitter'])
        if twitter_data:
            properties['Twitter/X'] = {"rich_text": [{"type": "text", "text": {"content": twitter_data}}]}
    
    # Website
    if 'website' in values:
        website_data = extract_value(values['website'])
        if website_data:
            properties['Website'] = {"url": website_data}
    
    # Avatar URL
    if 'avatar_url' in values:
        avatar_data = extract_value(values['avatar_url'])
        if avatar_data:
            properties['Avatar URL'] = {"url": avatar_data}
    
    # Primary location
    if 'primary_location' in values:
        location_data = extract_value(values['primary_location'])
        if location_data:
            properties['Location'] = {"rich_text": [{"type": "text", "text": {"content": location_data}}]}
    
    # Description
    if 'description' in values:
        desc_data = extract_value(values['description'])
        if desc_data:
            properties['Description'] = {"rich_text": [{"type": "text", "text": {"content": desc_data}}]}
    
    # Comments
    if 'comments' in values:
        comments_data = extract_value(values['comments'])
        if comments_data:
            properties['Comments'] = {"rich_text": [{"type": "text", "text": {"content": comments_data}}]}
    
    # Summary
    if 'summary' in values:
        summary_data = extract_value(values['summary'])
        if summary_data:
            properties['Summary'] = {"rich_text": [{"type": "text", "text": {"content": summary_data}}]}
    
    # Interaction data
    if 'first_email_interaction' in values:
        first_email = extract_value(values['first_email_interaction'], 'interacted_at')
        if first_email:
            properties['First Email'] = {"date": {"start": first_email.split('T')[0]}}
    
    if 'last_email_interaction' in values:
        last_email = extract_value(values['last_email_interaction'], 'interacted_at')
        if last_email:
            properties['Last Email'] = {"date": {"start": last_email.split('T')[0]}}
    
    if 'first_calendar_interaction' in values:
        first_calendar = extract_value(values['first_calendar_interaction'], 'interacted_at')
        if first_calendar:
            properties['First Meeting'] = {"date": {"start": first_calendar.split('T')[0]}}
    
    if 'last_calendar_interaction' in values:
        last_calendar = extract_value(values['last_calendar_interaction'], 'interacted_at')
        if last_calendar:
            properties['Last Meeting'] = {"date": {"start": last_calendar.split('T')[0]}}
    
    if 'first_interaction' in values:
        first_interaction = extract_value(values['first_interaction'], 'interacted_at')
        if first_interaction:
            properties['First Interaction'] = {"date": {"start": first_interaction.split('T')[0]}}
    
    if 'last_interaction' in values:
        last_interaction = extract_value(values['last_interaction'], 'interacted_at')
        if last_interaction:
            properties['Last Interaction'] = {"date": {"start": last_interaction.split('T')[0]}}
    
    # Connection strength
    if 'strongest_connection_strength_legacy' in values:
        strength = extract_value(values['strongest_connection_strength_legacy'])
        if strength:
            properties['Connection Strength'] = {"number": float(strength)}
    
    # Connection strength (select)
    if 'strongest_connection_strength' in values:
        strength_select = extract_value(values['strongest_connection_strength'], 'title')
        if strength_select:
            properties['Relationship Quality'] = {"select": {"name": strength_select}}
    
    # Created at
    if 'created_at' in values:
        created_at = extract_value(values['created_at'])
        if created_at:
            properties['Created At'] = {"date": {"start": created_at.split('T')[0]}}
    
    # Attio specific fields
    properties['Attio Record ID'] = {"rich_text": [{"type": "text", "text": {"content": attio_data.get('id', {}).get('record_id', '')}}]}
    properties['Attio Web URL'] = {"url": attio_data.get('web_url', '')}
    
    # Additional Attio fields
    additional_fields = {
        'angellist': 'Angellist',
        'facebook': 'Facebook',
        'instagram': 'Instagram',
        'telegram': 'Telegram',
        'twitter_follower_count': 'Twitter Follower Count',
        'fathomcalls': 'FathomCalls',
        'next_actions': 'Next Actions',
        'linkedin_description': 'LinkedIn Description',
        'connection_degree_with_anna': 'Connection Degree with Anna',
        'mutual_connections_with_anna': 'Mutual Connections with Anna',
        'next_calendar_interaction': 'Next Calendar Interaction',
        'next_interaction': 'Next Interaction',
        'associated_deals': 'Associated Deals',
        'associated_users': 'Associated Users'
    }
    
    for attio_field, notion_field in additional_fields.items():
        if attio_field in values:
            field_value = extract_value(values[attio_field])
            if field_value:
                if notion_field in ['Angellist', 'Facebook', 'Instagram']:
                    properties[notion_field] = {"url": field_value}
                elif notion_field in ['Twitter Follower Count', 'Connection Degree with Anna', 'Mutual Connections with Anna']:
                    try:
                        properties[notion_field] = {"number": float(field_value)}
                    except (ValueError, TypeError):
                        properties[notion_field] = {"rich_text": [{"type": "text", "text": {"content": str(field_value)}}]}
                elif notion_field in ['Next Calendar Interaction', 'Next Interaction']:
                    properties[notion_field] = {"date": {"start": field_value.split('T')[0]}}
                else:
                    properties[notion_field] = {"rich_text": [{"type": "text", "text": {"content": str(field_value)}}]}
    
    # Custom fields (any remaining fields)
    custom_fields = {}
    for key, value in values.items():
        if key not in ['record_id', 'name', 'email_addresses', 'company', 'job_title', 
                      'phone_numbers', 'linkedin', 'twitter', 'website', 'avatar_url',
                      'primary_location', 'description', 'comments', 'summary',
                      'first_email_interaction', 'last_email_interaction', 
                      'first_calendar_interaction', 'last_calendar_interaction',
                      'first_interaction', 'last_interaction',
                      'strongest_connection_strength_legacy', 'strongest_connection_strength',
                      'created_at', 'created_by', 'angellist', 'facebook', 'instagram',
                      'twitter_follower_count', 'next_calendar_interaction', 'next_interaction',
                      'strongest_connection_user', 'associated_deals', 'associated_users',
                      'fathomcalls', 'next_actions', 'linkedin_description',
                      'connection_degree_with_anna', 'mutual_connections_with_anna',
                      'telegram']:
            if value and len(value) > 0:
                field_value = extract_value(value)
                if field_value:
                    custom_fields[key] = field_value
    
    if custom_fields:
        custom_text = "\n".join([f"{k}: {v}" for k, v in custom_fields.items()])
        properties['Custom Fields'] = {"rich_text": [{"type": "text", "text": {"content": custom_text}}]}
    
    return properties

async def final_attio_notion_integration():
    """Final complete Attio to Notion integration"""
    
    # Get API keys from config
    attio_api_key = Config.ATTIO_API_KEY
    notion_token = Config.NOTION_TOKEN
    
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Complete Partners CRM Database ID (from previous creation)
    partners_db_id = "27b1bb72-4b52-8107-988b-d729a8a3421f"
    
    try:
        logger.info("🚀 Final Complete Attio to Notion Integration")
        logger.info("=" * 60)
        
        # Step 1: Get Attio data
        async with AttioRealIntegration(attio_api_key) as attio:
            logger.info("\n1. Getting Attio data for ethan@tuesday.vc...")
            
            attio_data = await attio.get_person_by_email("ethan@tuesday.vc")
            
            if not attio_data:
                logger.error("❌ Could not get Attio data for ethan@tuesday.vc")
                return
            
            logger.info("✅ Attio data retrieved successfully")
        
        # Step 2: Convert Attio data to Notion properties
        logger.info("\n2. Converting Attio data to Notion properties...")
        
        notion_properties = create_complete_notion_properties_from_attio(attio_data)
        
        logger.info(f"Converted {len(notion_properties)} properties:")
        for prop_name in sorted(notion_properties.keys()):
            logger.info(f"  • {prop_name}")
        
        # Step 3: Create page with all properties
        logger.info("\n3. Creating Notion page with all Attio attributes...")
        
        async with NotionClientStable(notion_token) as notion:
            try:
                ethan_page = await notion.create_page_in_database(partners_db_id, notion_properties)
                logger.info(f"✅ Page created successfully!")
                logger.info(f"📄 Page URL: {ethan_page['url']}")
                logger.info(f"🆔 Page ID: {ethan_page['id']}")
                
                # Step 4: Summary
                logger.info("\n" + "=" * 60)
                logger.info("🎉 SUCCESS! Complete Attio to Notion Integration")
                logger.info("=" * 60)
                
                logger.info("\n📊 INTEGRATION SUMMARY:")
                logger.info(f"• Attio Data Source: ✅ Real data from Attio workspace")
                logger.info(f"• Person: ✅ {notion_properties.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Unknown')}")
                logger.info(f"• Properties Mapped: ✅ {len(notion_properties)}")
                logger.info(f"• Notion Database: ✅ Partners CRM - Complete")
                logger.info(f"• Notion Page: ✅ Created successfully")
                logger.info(f"• Page URL: {ethan_page['url']}")
                
                logger.info("\n✨ ATTRIBUTES INCLUDED:")
                for prop_name in sorted(notion_properties.keys()):
                    logger.info(f"  • {prop_name}")
                
                logger.info("\n🔗 INTEGRATION FEATURES:")
                logger.info("• Complete Attio data mapping")
                logger.info("• Interaction history tracking")
                logger.info("• Connection strength analysis")
                logger.info("• Custom fields preservation")
                logger.info("• URL and date formatting")
                logger.info("• Rich text and structured data")
                logger.info("• All 39 database properties supported")
                
            except Exception as e:
                logger.error(f"❌ Failed to create Notion page: {e}")
                return
            
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(final_attio_notion_integration())

if __name__ == "__main__":
    main()
