#!/usr/bin/env python3
"""
Test different Attio API versions and endpoints
"""

import asyncio
import aiohttp
import logging
import json
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_attio_api_versions():
    """Test different Attio API versions and endpoints"""
    
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        logger.error("Attio API key not found")
        return
    
    base_urls = [
        "https://api.attio.com/v1",
        "https://api.attio.com/v2", 
        "https://api.attio.com/v3",
        "https://api.attio.com"
    ]
    
    endpoints_to_test = [
        "records/search",
        "search",
        "people/search",
        "objects/people/search",
        "objects/people/records",
        "people/records",
        "records/people",
        "people",
        "objects/people"
    ]
    
    async with aiohttp.ClientSession() as session:
        for base_url in base_urls:
            logger.info(f"\n🔍 Testing API version: {base_url}")
            logger.info("=" * 50)
            
            for endpoint in endpoints_to_test:
                # Test GET
                try:
                    url = f"{base_url}/{endpoint}"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ GET {endpoint}: SUCCESS")
                            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                                logger.info(f"   Found {len(data['data'])} records!")
                                return data  # Return the first successful result
                        elif response.status == 404:
                            logger.info(f"❌ GET {endpoint}: Not found")
                        else:
                            error_text = await response.text()
                            logger.info(f"⚠️  GET {endpoint}: {response.status} - {error_text[:100]}...")
                            
                except Exception as e:
                    logger.info(f"❌ GET {endpoint}: Exception - {e}")
                
                # Test POST
                try:
                    url = f"{base_url}/{endpoint}"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Try different POST data structures
                    post_data_options = [
                        {"query": "ethan@tuesday.vc", "objects": ["people"]},
                        {"query": "ethan@tuesday.vc", "object_types": ["people"]},
                        {"filter": {"email_addresses": {"$eq": "ethan@tuesday.vc"}}},
                        {"data": {"query": "ethan@tuesday.vc", "objects": ["people"]}},
                        {}
                    ]
                    
                    for i, post_data in enumerate(post_data_options):
                        try:
                            async with session.post(url, headers=headers, json=post_data) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    logger.info(f"✅ POST {endpoint} (option {i+1}): SUCCESS")
                                    if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                                        logger.info(f"   Found {len(data['data'])} records!")
                                        return data  # Return the first successful result
                                elif response.status == 404:
                                    logger.info(f"❌ POST {endpoint} (option {i+1}): Not found")
                                else:
                                    error_text = await response.text()
                                    logger.info(f"⚠️  POST {endpoint} (option {i+1}): {response.status} - {error_text[:100]}...")
                                    
                        except Exception as e:
                            logger.info(f"❌ POST {endpoint} (option {i+1}): Exception - {e}")
                            
                except Exception as e:
                    logger.info(f"❌ POST {endpoint}: Exception - {e}")
    
    logger.info("\n❌ No working endpoints found")
    logger.info("This suggests:")
    logger.info("1. API version mismatch")
    logger.info("2. API structure has changed")
    logger.info("3. Workspace doesn't have search enabled")
    logger.info("4. API key doesn't have required permissions")

if __name__ == "__main__":
    asyncio.run(test_attio_api_versions())
