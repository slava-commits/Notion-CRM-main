#!/usr/bin/env python3
"""
Test various Attio API endpoints to find the correct one
"""

import asyncio
import aiohttp
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttioEndpointTester:
    """Test various Attio API endpoints"""
    
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
    
    async def test_endpoint(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Test a specific endpoint"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                response_text = await response.text()
                
                return {
                    "endpoint": f"{method} {endpoint}",
                    "status": response.status,
                    "success": response.status < 400,
                    "response": response_text[:500] if response_text else "Empty response"
                }
        except Exception as e:
            return {
                "endpoint": f"{method} {endpoint}",
                "status": "ERROR",
                "success": False,
                "response": str(e)
            }
    
    async def test_all_endpoints(self):
        """Test all possible endpoints"""
        
        endpoints_to_test = [
            # Search endpoints
            ("POST", "search", {"query": "ethan@tuesday.vc", "object_types": ["people"]}),
            ("POST", "records/search", {"query": "ethan@tuesday.vc", "objects": ["people"], "limit": 10}),
            ("POST", "v2/search", {"query": "ethan@tuesday.vc", "object_types": ["people"]}),
            ("GET", "search", None),
            
            # People endpoints
            ("GET", "people", None),
            ("GET", "people/records", None),
            ("POST", "people/records", {"filter": {}}),
            ("GET", "objects/people", None),
            ("POST", "objects/people/records", {"filter": {}}),
            ("GET", "objects/people/records", None),
            
            # Generic endpoints
            ("GET", "objects", None),
            ("GET", "records", None),
            ("POST", "records", {"filter": {}}),
            
            # Alternative versions
            ("GET", "v1/people", None),
            ("GET", "v1/objects/people", None),
            ("POST", "v1/search", {"query": "ethan@tuesday.vc"}),
        ]
        
        logger.info("🔍 Testing various Attio API endpoints...")
        logger.info("=" * 60)
        
        results = []
        for method, endpoint, data in endpoints_to_test:
            logger.info(f"Testing: {method} {endpoint}")
            result = await self.test_endpoint(method, endpoint, data)
            results.append(result)
            
            if result["success"]:
                logger.info(f"  ✅ SUCCESS: {result['status']}")
                logger.info(f"  Response: {result['response'][:200]}...")
            else:
                logger.info(f"  ❌ FAILED: {result['status']}")
                if "not found" in result["response"].lower():
                    logger.info(f"  Message: Endpoint not found")
                else:
                    logger.info(f"  Response: {result['response'][:200]}...")
            
            logger.info("")
        
        # Summary
        logger.info("📊 SUMMARY:")
        successful_endpoints = [r for r in results if r["success"]]
        if successful_endpoints:
            logger.info(f"✅ Found {len(successful_endpoints)} working endpoints:")
            for result in successful_endpoints:
                logger.info(f"  • {result['endpoint']}")
        else:
            logger.info("❌ No working endpoints found")
            logger.info("This might indicate:")
            logger.info("  • API key is invalid")
            logger.info("  • API version is incorrect")
            logger.info("  • Attio workspace is empty")
            logger.info("  • Different API structure than expected")

async def main():
    """Main function"""
    api_key = Config.ATTIO_API_KEY
    
    if not api_key:
        logger.error("Attio API key not found in config")
        return
    
    async with AttioEndpointTester(api_key) as tester:
        await tester.test_all_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
