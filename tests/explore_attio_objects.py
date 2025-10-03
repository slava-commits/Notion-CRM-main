#!/usr/bin/env python3
"""
Explore Attio objects to understand the API structure
"""

import asyncio
import aiohttp
import logging
import json
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttioExplorer:
    """Explore Attio API structure"""
    
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
    
    async def explore_objects(self):
        """Explore available objects"""
        try:
            url = f"{self.base_url}/objects"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info("🔍 Exploring Attio objects...")
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Available objects:")
                    
                    for obj in data.get('data', []):
                        obj_id = obj.get('id', {})
                        api_slug = obj.get('api_slug', 'Unknown')
                        singular = obj.get('singular_noun', 'Unknown')
                        plural = obj.get('plural_noun', 'Unknown')
                        
                        logger.info(f"  • {api_slug} ({singular}/{plural})")
                        logger.info(f"    ID: {obj_id}")
                        
                        # Check if this looks like people
                        if 'people' in api_slug.lower() or 'person' in singular.lower():
                            logger.info(f"    ✅ This looks like the people object!")
                            
                            # Try to get records for this object
                            await self.try_get_records(api_slug, obj_id)
                
        except Exception as e:
            logger.error(f"Failed to explore objects: {e}")
    
    async def try_get_records(self, api_slug: str, obj_id: dict):
        """Try to get records for a specific object"""
        try:
            # Try different approaches to get records
            approaches = [
                f"objects/{api_slug}/records",
                f"objects/{api_slug}",
                f"records/{api_slug}",
                f"{api_slug}/records",
                f"{api_slug}"
            ]
            
            for approach in approaches:
                logger.info(f"  Trying: GET {approach}")
                
                url = f"{self.base_url}/{approach}"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                try:
                    async with self.session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"    ✅ SUCCESS! Found {len(data.get('data', []))} records")
                            
                            # Show first record structure
                            records = data.get('data', [])
                            if records:
                                logger.info(f"    First record structure:")
                                logger.info(f"    {json.dumps(records[0], indent=4)[:500]}...")
                            
                            return data
                        else:
                            error_text = await response.text()
                            logger.info(f"    ❌ Failed: {response.status} - {error_text[:100]}...")
                            
                except Exception as e:
                    logger.info(f"    ❌ Exception: {e}")
            
            # Try POST with different data structures
            logger.info(f"  Trying POST approaches...")
            
            post_approaches = [
                (f"objects/{api_slug}/records", {"filter": {}}),
                (f"objects/{api_slug}/records", {"data": {"filter": {}}}),
                (f"records/search", {"query": "", "objects": [api_slug]}),
                (f"search", {"query": "", "object_types": [api_slug]}),
            ]
            
            for endpoint, data in post_approaches:
                logger.info(f"  Trying: POST {endpoint}")
                
                url = f"{self.base_url}/{endpoint}"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                try:
                    async with self.session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            logger.info(f"    ✅ SUCCESS! Found {len(response_data.get('data', []))} records")
                            
                            # Show first record structure
                            records = response_data.get('data', [])
                            if records:
                                logger.info(f"    First record structure:")
                                logger.info(f"    {json.dumps(records[0], indent=4)[:500]}...")
                            
                            return response_data
                        else:
                            error_text = await response.text()
                            logger.info(f"    ❌ Failed: {response.status} - {error_text[:100]}...")
                            
                except Exception as e:
                    logger.info(f"    ❌ Exception: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to get records for {api_slug}: {e}")

async def main():
    """Main function"""
    api_key = Config.ATTIO_API_KEY
    
    if not api_key:
        logger.error("Attio API key not found in config")
        return
    
    async with AttioExplorer(api_key) as explorer:
        await explorer.explore_objects()

if __name__ == "__main__":
    asyncio.run(main())
