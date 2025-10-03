#!/usr/bin/env python3
"""
Debug Attio API Response Structure
Examine the actual response from GET objects/people
"""

import asyncio
import aiohttp
import logging
import json
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_attio_response():
    """Debug the actual Attio API response structure"""
    
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        logger.error("Attio API key not found")
        return
    
    base_url = "https://api.attio.com/v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Test GET objects/people
        logger.info("🔍 Testing GET objects/people...")
        
        try:
            async with session.get(f"{base_url}/objects/people", headers=headers) as response:
                logger.info(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info("Response structure:")
                    logger.info(json.dumps(data, indent=2))
                    
                    # Check if it's object metadata or actual records
                    if 'data' in data:
                        data_array = data['data']
                        logger.info(f"Data type: {type(data_array)}")
                        logger.info(f"Data length: {len(data_array) if isinstance(data_array, list) else 'N/A'}")
                        
                        if isinstance(data_array, list) and len(data_array) > 0:
                            logger.info("First item in data array:")
                            logger.info(json.dumps(data_array[0], indent=2))
                            
                            # Check if it looks like object metadata
                            first_item = data_array[0]
                            if isinstance(first_item, str):
                                logger.info("❌ Data contains strings (object type metadata)")
                            elif isinstance(first_item, dict):
                                if 'id' in first_item and 'api_slug' in first_item:
                                    logger.info("❌ Data contains object type metadata, not person records")
                                elif 'attributes' in first_item:
                                    logger.info("✅ Data contains person records with attributes")
                                else:
                                    logger.info("❓ Data structure unclear")
                                    logger.info(f"Keys in first item: {list(first_item.keys())}")
                        else:
                            logger.info("❌ Data is not a list or is empty")
                    else:
                        logger.info("❌ No 'data' field in response")
                
                else:
                    error_text = await response.text()
                    logger.error(f"Error: {error_text}")
        
        except Exception as e:
            logger.error(f"Exception: {e}")
        
        # Test GET objects to see the difference
        logger.info("\n🔍 Testing GET objects for comparison...")
        
        try:
            async with session.get(f"{base_url}/objects", headers=headers) as response:
                logger.info(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info("Objects response structure:")
                    logger.info(json.dumps(data, indent=2))
                    
                    # Find the people object
                    if 'data' in data and isinstance(data['data'], list):
                        for obj in data['data']:
                            if obj.get('api_slug') == 'people':
                                logger.info("Found people object:")
                                logger.info(json.dumps(obj, indent=2))
                                break
                
                else:
                    error_text = await response.text()
                    logger.error(f"Error: {error_text}")
        
        except Exception as e:
            logger.error(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_attio_response())
