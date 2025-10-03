#!/usr/bin/env python3
"""
Streamlined Attio to Notion Integration
Production-ready code with only essential functionality
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttioToNotionIntegration:
    """Streamlined Attio to Notion integration"""
    
    def __init__(self):
        self.notion_token = Config.NOTION_TOKEN
        self.attio_api_key = Config.ATTIO_API_KEY
        self.partners_db_id = "27b1bb72-4b52-81be-9982-c2fa850ba44e"  # Partners CRM in Jupid HQ
        
        # Field mappings
        self.field_mappings = {
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
            'created_at': 'Created At',
            'record_id': 'Attio Record ID'
        }
    
    async def sync_contact(self, email: str) -> Dict:
        """Sync a single contact from Attio to Notion"""
        try:
            # Get Attio data
            attio_data = await self._get_attio_data(email)
            if not attio_data:
                return {"success": False, "error": "No Attio data found"}
            
            # Map to Notion format
            notion_data = self._map_to_notion_format(attio_data)
            
            # Create/Update Notion page
            result = await self._create_notion_page(email, notion_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Sync failed for {email}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_attio_data(self, email: str) -> Optional[Dict]:
        """Get Attio data for email"""
        headers = {
            "Authorization": f"Bearer {self.attio_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            url = "https://api.attio.com/v2/objects/people/records?matching_attribute=email_addresses"
            data = {"data": {"values": {"email_addresses": [email]}}}
            
            async with session.put(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data')
                return None
    
    def _extract_attio_value(self, attr_data) -> Any:
        """Extract value from Attio attribute"""
        if not attr_data or len(attr_data) == 0:
            return None
        
        item = attr_data[0]
        if isinstance(item, dict):
            # Try different keys based on attribute type
            for key in ['value', 'email_address', 'full_name', 'interacted_at', 'title', 'target_record_id']:
                if key in item:
                    return item[key]
            # Return first non-metadata value
            for k, v in item.items():
                if k not in ['active_from', 'active_until', 'created_by_actor', 'attribute_type']:
                    return v
        return str(item) if item else None
    
    def _map_to_notion_format(self, attio_data: Dict) -> Dict:
        """Map Attio data to Notion format"""
        attio_values = attio_data.get('values', {})
        notion_properties = {}
        
        for attio_field, notion_field in self.field_mappings.items():
            if attio_field in attio_values:
                value = self._extract_attio_value(attio_values[attio_field])
                if value:
                    notion_properties[notion_field] = self._format_notion_property(notion_field, value)
        
        # Add Attio Web URL
        record_id = self._extract_attio_value(attio_values.get('record_id', []))
        if record_id:
            notion_properties['Attio Web URL'] = {"url": f"https://app.attio.com/jupid/person/{record_id}"}
        
        return notion_properties
    
    def _format_notion_property(self, field_name: str, value: Any) -> Dict:
        """Format value for Notion property based on field type"""
        if field_name == 'Name':
            return {"title": [{"type": "text", "text": {"content": str(value)}}]}
        elif field_name == 'Email':
            return {"email": str(value)}
        elif field_name == 'Phone':
            return {"phone_number": str(value)}
        elif field_name in ['Website', 'LinkedIn', 'Avatar URL']:
            return {"url": str(value)}
        elif field_name == 'Twitter/X':
            return {"rich_text": [{"type": "text", "text": {"content": str(value)}}]}
        elif field_name == 'Connection Strength':
            return {"number": float(value) if value else 0}
        elif field_name in ['First Email', 'Last Email', 'First Meeting', 'Last Meeting', 
                           'First Interaction', 'Last Interaction', 'Created At']:
            if isinstance(value, str) and 'T' in value:
                date_str = value.split('T')[0]
                return {"date": {"start": date_str}}
            return {"date": {"start": str(value)}}
        elif field_name == 'Relationship Quality':
            if isinstance(value, dict) and 'title' in value:
                return {"select": {"name": value['title']}}
            return {"select": {"name": str(value)}}
        else:
            return {"rich_text": [{"type": "text", "text": {"content": str(value)}}]}
    
    async def _create_notion_page(self, email: str, notion_data: Dict) -> Dict:
        """Create or update Notion page"""
        headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        async with aiohttp.ClientSession() as session:
            # Check if page exists
            query_data = {"filter": {"property": "Email", "email": {"equals": email}}}
            
            async with session.post(
                f"https://api.notion.com/v1/databases/{self.partners_db_id}/query",
                headers=headers,
                json=query_data
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": "Database query failed"}
                
                result = await response.json()
                existing_pages = result.get('results', [])
                
                if existing_pages:
                    # Update existing page
                    page_id = existing_pages[0]['id']
                    update_data = {"properties": notion_data}
                    
                    async with session.patch(
                        f"https://api.notion.com/v1/pages/{page_id}",
                        headers=headers,
                        json=update_data
                    ) as update_response:
                        if update_response.status == 200:
                            return {"success": True, "action": "updated", "page_id": page_id}
                        else:
                            error = await update_response.text()
                            return {"success": False, "error": f"Update failed: {error}"}
                else:
                    # Create new page
                    create_data = {
                        "parent": {"database_id": self.partners_db_id},
                        "properties": notion_data
                    }
                    
                    async with session.post(
                        "https://api.notion.com/v1/pages",
                        headers=headers,
                        json=create_data
                    ) as create_response:
                        if create_response.status == 200:
                            result = await create_response.json()
                            return {"success": True, "action": "created", "page_id": result['id']}
                        else:
                            error = await create_response.text()
                            return {"success": False, "error": f"Creation failed: {error}"}

async def main():
    """Main function for testing"""
    integration = AttioToNotionIntegration()
    
    # Test with Nitin
    result = await integration.sync_contact("nitin@unshackledvc.com")
    
    if result["success"]:
        logger.info(f"✅ Success: {result['action']} page {result['page_id']}")
    else:
        logger.error(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
