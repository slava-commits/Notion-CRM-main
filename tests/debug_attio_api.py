#!/usr/bin/env python3
"""
Debug Attio API Response
Examine the raw API response to understand the data structure
"""

import asyncio
import aiohttp
import logging
import json
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_attio_api():
    """Debug Attio API response structure"""
    
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
            logger.info("🔍 Debugging Attio API Response")
            logger.info("=" * 50)
            
            # Test 1: Basic people endpoint
            logger.info("\n1. Testing basic people endpoint...")
            url = f"{base_url}/objects/people?limit=5"
            
            async with session.get(url, headers=headers) as response:
                logger.info(f"Status Code: {response.status}")
                logger.info(f"Headers: {dict(response.headers)}")
                
                response_text = await response.text()
                logger.info(f"Raw Response Length: {len(response_text)}")
                
                if response.status == 200:
                    try:
                        response_json = await response.json()
                        logger.info("✅ JSON Response Structure:")
                        logger.info(f"Top-level keys: {list(response_json.keys())}")
                        
                        if 'data' in response_json:
                            data = response_json['data']
                            logger.info(f"Data type: {type(data)}")
                            logger.info(f"Data length: {len(data) if isinstance(data, list) else 'N/A'}")
                            
                            if isinstance(data, list) and len(data) > 0:
                                logger.info("First person structure:")
                                logger.info(json.dumps(data[0], indent=2))
                            else:
                                logger.info("No people in data array")
                        else:
                            logger.info("No 'data' key in response")
                            logger.info(f"Response structure: {json.dumps(response_json, indent=2)}")
                            
                    except Exception as e:
                        logger.error(f"Failed to parse JSON: {e}")
                        logger.info(f"Raw response: {response_text[:500]}...")
                else:
                    logger.error(f"API Error: {response.status}")
                    logger.info(f"Error response: {response_text}")
            
            # Test 2: Try different endpoints
            logger.info("\n2. Testing different endpoints...")
            
            endpoints_to_test = [
                "objects/people",
                "objects/people?limit=10",
                "objects/people?page_size=10",
                "people",
                "contacts"
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    url = f"{base_url}/{endpoint}"
                    logger.info(f"\nTesting: {endpoint}")
                    
                    async with session.get(url, headers=headers) as response:
                        logger.info(f"  Status: {response.status}")
                        if response.status == 200:
                            response_json = await response.json()
                            logger.info(f"  Keys: {list(response_json.keys())}")
                            if 'data' in response_json:
                                data = response_json['data']
                                logger.info(f"  Data length: {len(data) if isinstance(data, list) else 'N/A'}")
                        else:
                            error_text = await response.text()
                            logger.info(f"  Error: {error_text[:200]}...")
                            
                except Exception as e:
                    logger.error(f"  Exception: {e}")
            
            # Test 3: Check API documentation endpoint
            logger.info("\n3. Testing API info endpoint...")
            try:
                url = f"{base_url}/"
                async with session.get(url, headers=headers) as response:
                    logger.info(f"Root endpoint status: {response.status}")
                    if response.status == 200:
                        response_json = await response.json()
                        logger.info(f"API info: {json.dumps(response_json, indent=2)}")
            except Exception as e:
                logger.error(f"Root endpoint error: {e}")
            
        except Exception as e:
            logger.error(f"Debug failed: {e}")

def main():
    """Main function"""
    asyncio.run(debug_attio_api())

if __name__ == "__main__":
    main()
