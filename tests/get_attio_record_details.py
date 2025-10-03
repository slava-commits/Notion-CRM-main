#!/usr/bin/env python3
"""
Get all attributes for a specific Attio record ID
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttioRecordDetails:
    """Get detailed information for a specific Attio record"""
    
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
    
    async def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Get complete record details by record ID"""
        try:
            # Try different endpoints to get the record
            endpoints_to_try = [
                f"{self.base_url}/records/people/{record_id}",
                f"{self.base_url}/objects/people/records/{record_id}",
                f"{self.base_url}/records/{record_id}",
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = await self._make_request("GET", endpoint)
                    
                    if 'data' in response or 'id' in response:
                        logger.info(f"✅ Success with endpoint: {endpoint}")
                        return response
                    else:
                        logger.info(f"❌ No data found with endpoint: {endpoint}")
                        
                except Exception as e:
                    logger.info(f"❌ Failed with endpoint {endpoint}: {e}")
                    continue
            
            # If direct GET doesn't work, try using the PUT method we know works
            logger.info("Trying PUT method with email lookup...")
            url = f"{self.base_url}/objects/people/records?matching_attribute=email_addresses"
            data = {
                "data": {
                    "values": {
                        "email_addresses": ["ethan@tuesday.vc"]
                    }
                }
            }
            
            response = await self._make_request("PUT", url, data)
            if 'data' in response and response['data']:
                logger.info("✅ Success with PUT method")
                return response
            
            return None
                
        except Exception as e:
            logger.error(f"Failed to get record by ID {record_id}: {e}")
            return None
    
    def format_attribute_value(self, value: Any, attribute_type: str = None) -> str:
        """Format attribute value for display"""
        if value is None:
            return "None"
        
        if isinstance(value, list):
            if len(value) == 0:
                return "[]"
            
            # Handle different list item types
            formatted_items = []
            for item in value:
                if isinstance(item, dict):
                    if 'value' in item:
                        formatted_items.append(str(item['value']))
                    elif 'title' in item:
                        formatted_items.append(str(item['title']))
                    elif 'email_address' in item:
                        formatted_items.append(str(item['email_address']))
                    elif 'full_name' in item:
                        formatted_items.append(str(item['full_name']))
                    else:
                        # Show key-value pairs for complex objects
                        key_vals = []
                        for k, v in item.items():
                            if k not in ['active_from', 'active_until', 'created_by_actor', 'attribute_type']:
                                key_vals.append(f"{k}: {v}")
                        if key_vals:
                            formatted_items.append("{" + ", ".join(key_vals) + "}")
                        else:
                            formatted_items.append("{}")
                else:
                    formatted_items.append(str(item))
            
            return "[" + ", ".join(formatted_items) + "]"
        
        return str(value)
    
    def display_record_details(self, record_data: Dict):
        """Display all record details in a formatted way"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 COMPLETE ATTIO RECORD DETAILS")
        logger.info("=" * 80)
        
        # Basic record info
        if 'data' in record_data:
            data = record_data['data']
        else:
            data = record_data
        
        # Record ID and basic info
        if 'id' in data:
            record_id_info = data['id']
            logger.info(f"🆔 Record ID: {record_id_info.get('record_id', 'Unknown')}")
            logger.info(f"🏢 Workspace ID: {record_id_info.get('workspace_id', 'Unknown')}")
            logger.info(f"📦 Object ID: {record_id_info.get('object_id', 'Unknown')}")
        
        if 'web_url' in data:
            logger.info(f"🌐 Web URL: {data['web_url']}")
        
        if 'created_at' in data:
            logger.info(f"📅 Created At: {data['created_at']}")
        
        # Values section
        if 'values' in data:
            values = data['values']
            logger.info(f"\n📊 ATTRIBUTES ({len(values)} total):")
            logger.info("-" * 80)
            
            # Sort attributes for better display
            sorted_attributes = sorted(values.items())
            
            for attr_name, attr_value in sorted_attributes:
                if attr_value and len(attr_value) > 0:
                    # Get attribute type if available
                    attr_type = None
                    if isinstance(attr_value, list) and len(attr_value) > 0:
                        if isinstance(attr_value[0], dict) and 'attribute_type' in attr_value[0]:
                            attr_type = attr_value[0]['attribute_type']
                    
                    # Format the value
                    formatted_value = self.format_attribute_value(attr_value, attr_type)
                    
                    # Display with type info
                    type_info = f" ({attr_type})" if attr_type else ""
                    logger.info(f"  {attr_name}{type_info}:")
                    
                    # For complex values, show more detail
                    if isinstance(attr_value, list) and len(attr_value) > 0 and isinstance(attr_value[0], dict):
                        for i, item in enumerate(attr_value):
                            if isinstance(item, dict):
                                logger.info(f"    [{i+1}] {self.format_attribute_value(item)}")
                    else:
                        logger.info(f"    {formatted_value}")
                    
                    logger.info("")  # Empty line for readability
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📈 SUMMARY")
        logger.info("=" * 80)
        
        if 'values' in data:
            values = data['values']
            non_empty_attrs = {k: v for k, v in values.items() if v and len(v) > 0}
            
            logger.info(f"• Total Attributes: {len(values)}")
            logger.info(f"• Non-Empty Attributes: {len(non_empty_attrs)}")
            logger.info(f"• Empty Attributes: {len(values) - len(non_empty_attrs)}")
            
            # Key attributes summary
            key_attrs = ['name', 'email_addresses', 'company', 'job_title', 'phone_numbers', 
                        'linkedin', 'twitter', 'first_email_interaction', 'last_email_interaction',
                        'first_calendar_interaction', 'last_calendar_interaction', 
                        'strongest_connection_strength_legacy', 'created_at']
            
            logger.info(f"\n🔑 Key Attributes Status:")
            for attr in key_attrs:
                if attr in values:
                    has_value = values[attr] and len(values[attr]) > 0
                    status = "✅" if has_value else "❌"
                    logger.info(f"  {status} {attr}")

async def get_attio_record_details():
    """Get and display all attributes for the specific record ID"""
    
    # Get API key from config
    attio_api_key = Config.ATTIO_API_KEY
    
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    record_id = "972bb59b-a767-4ac6-8031-020392cb2111"
    
    try:
        logger.info(f"🔍 Getting all attributes for Record ID: {record_id}")
        logger.info("=" * 60)
        
        async with AttioRecordDetails(attio_api_key) as attio:
            # Get the record details
            record_data = await attio.get_record_by_id(record_id)
            
            if not record_data:
                logger.error(f"❌ Could not retrieve record with ID: {record_id}")
                return
            
            # Display all details
            attio.display_record_details(record_data)
            
            # Also save to file for reference
            with open(f"attio_record_{record_id}.json", "w") as f:
                json.dump(record_data, f, indent=2, default=str)
            
            logger.info(f"\n💾 Full record data saved to: attio_record_{record_id}.json")
            
    except Exception as e:
        logger.error(f"❌ Failed to get record details: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(get_attio_record_details())

if __name__ == "__main__":
    main()
