#!/usr/bin/env python3
"""
Debug Attio API Response
Examine the raw response structure from Attio API
"""

import asyncio
import aiohttp
import logging
import json
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttioDebugger:
    """Debug Attio API responses"""
    
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
    
    async def debug_people_endpoint(self):
        """Debug the people endpoint response"""
        try:
            url = f"{self.base_url}/objects/people?limit=5"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Making request to: {url}")
            
            async with self.session.get(url, headers=headers) as response:
                logger.info(f"Response status: {response.status}")
                
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Error response: {error_text}")
                    return
                
                response_data = await response.json()
                logger.info("Raw response structure:")
                logger.info(json.dumps(response_data, indent=2))
                
                # Check if it's object type metadata or actual records
                if 'data' in response_data:
                    data = response_data['data']
                    logger.info(f"Data type: {type(data)}")
                    logger.info(f"Data length: {len(data) if isinstance(data, list) else 'N/A'}")
                    
                    if data and len(data) > 0:
                        logger.info("First item in data:")
                        logger.info(json.dumps(data[0], indent=2))
                        
                        # Check if it looks like object type metadata
                        first_item = data[0]
                        if isinstance(first_item, str):
                            logger.info("❌ Data contains strings (object type metadata)")
                        elif isinstance(first_item, dict):
                            if 'id' in first_item and 'api_slug' in first_item:
                                logger.info("❌ Data contains object type metadata, not person records")
                            elif 'attributes' in first_item:
                                logger.info("✅ Data contains person records with attributes")
                            else:
                                logger.info("❓ Data structure unclear")
                
        except Exception as e:
            logger.error(f"Debug failed: {e}")
    
    async def debug_search_endpoint(self):
        """Debug the search endpoint"""
        try:
            url = f"{self.base_url}/search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            search_data = {
                "query": "ethan@tuesday.vc",
                "object_types": ["people"]
            }
            
            logger.info(f"Making search request to: {url}")
            logger.info(f"Search data: {json.dumps(search_data, indent=2)}")
            
            async with self.session.post(url, headers=headers, json=search_data) as response:
                logger.info(f"Search response status: {response.status}")
                
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Search error response: {error_text}")
                    return
                
                response_data = await response.json()
                logger.info("Search response structure:")
                logger.info(json.dumps(response_data, indent=2))
                
        except Exception as e:
            logger.error(f"Search debug failed: {e}")
    
    async def debug_alternative_endpoints(self):
        """Debug alternative endpoints"""
        endpoints_to_try = [
            "objects/people/records",
            "people",
            "contacts",
            "persons",
            "objects/people/list",
            "objects/people/search"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{self.base_url}/{endpoint}"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                logger.info(f"\nTrying endpoint: {endpoint}")
                
                async with self.session.get(url, headers=headers) as response:
                    logger.info(f"  Status: {response.status}")
                    
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"  ✅ Success! Response keys: {list(response_data.keys())}")
                        
                        if 'data' in response_data:
                            data = response_data['data']
                            if isinstance(data, list) and len(data) > 0:
                                first_item = data[0]
                                if isinstance(first_item, dict) and 'attributes' in first_item:
                                    logger.info(f"  ✅ Contains person records! Found {len(data)} records")
                                else:
                                    logger.info(f"  ❌ Contains metadata, not person records")
                            else:
                                logger.info(f"  ❌ Empty data")
                        else:
                            logger.info(f"  ❌ No data field")
                    else:
                        error_text = await response.text()
                        logger.info(f"  ❌ Error: {error_text[:200]}...")
                        
            except Exception as e:
                logger.info(f"  ❌ Exception: {e}")

async def main():
    """Main debug function"""
    attio_api_key = Config.ATTIO_API_KEY
    
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    async with AttioDebugger(attio_api_key) as debugger:
        logger.info("🔍 Debugging Attio API Response Structure")
        logger.info("=" * 60)
        
        # Debug people endpoint
        logger.info("\n1. Debugging people endpoint...")
        await debugger.debug_people_endpoint()
        
        # Debug search endpoint
        logger.info("\n2. Debugging search endpoint...")
        await debugger.debug_search_endpoint()
        
        # Debug alternative endpoints
        logger.info("\n3. Debugging alternative endpoints...")
        await debugger.debug_alternative_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
