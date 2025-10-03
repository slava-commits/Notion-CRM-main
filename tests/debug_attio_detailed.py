#!/usr/bin/env python3
"""
Debug Attio API Response - Detailed
Examine the exact structure of the Attio API response
"""

import asyncio
import aiohttp
import logging
import json
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_attio_detailed():
    """Debug Attio API response structure in detail"""
    
    attio_api_key = Config.ATTIO_API_KEY
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    base_url = "https://api.attio.com/v2"
    headers = {
        "Authorization": f"Bearer {attio_api_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("🔍 Detailed Attio API Debug")
            logger.info("=" * 50)
            
            # Test people endpoint
            url = f"{base_url}/objects/people?limit=5"
            
            async with session.get(url, headers=headers) as response:
                logger.info(f"Status Code: {response.status}")
                
                if response.status == 200:
                    response_json = await response.json()
                    logger.info("Full Response Structure:")
                    logger.info(json.dumps(response_json, indent=2))
                    
                    # Check if data is a dict with specific structure
                    data = response_json.get('data', {})
                    logger.info(f"\nData type: {type(data)}")
                    logger.info(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                    
                    # Check for pagination or different structure
                    if isinstance(data, dict):
                        if 'results' in data:
                            logger.info(f"Results found: {len(data['results'])}")
                            if data['results']:
                                logger.info("First result:")
                                logger.info(json.dumps(data['results'][0], indent=2))
                        elif 'items' in data:
                            logger.info(f"Items found: {len(data['items'])}")
                            if data['items']:
                                logger.info("First item:")
                                logger.info(json.dumps(data['items'][0], indent=2))
                        elif 'people' in data:
                            logger.info(f"People found: {len(data['people'])}")
                            if data['people']:
                                logger.info("First person:")
                                logger.info(json.dumps(data['people'][0], indent=2))
                        else:
                            logger.info("No standard array keys found in data")
                            logger.info("Data content:")
                            logger.info(json.dumps(data, indent=2))
                    
                else:
                    error_text = await response.text()
                    logger.error(f"API Error: {response.status}")
                    logger.error(f"Error response: {error_text}")
            
        except Exception as e:
            logger.error(f"Debug failed: {e}")

def main():
    """Main function"""
    asyncio.run(debug_attio_detailed())

if __name__ == "__main__":
    main()
