#!/usr/bin/env python3
"""
Main Integration System
Streamlined production-ready integration system
"""

import asyncio
import logging
from typing import List
from attio_to_notion_integration import AttioToNotionIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationSystem:
    """Main integration system"""
    
    def __init__(self):
        self.integration = AttioToNotionIntegration()
    
    async def sync_contacts(self, emails: List[str]) -> Dict:
        """Sync multiple contacts from Attio to Notion"""
        logger.info(f"🚀 Starting sync for {len(emails)} contacts")
        
        results = {
            "total": len(emails),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for email in emails:
            try:
                result = await self.integration.sync_contact(email)
                results["details"].append({
                    "email": email,
                    "success": result["success"],
                    "action": result.get("action", "unknown"),
                    "page_id": result.get("page_id"),
                    "error": result.get("error")
                })
                
                if result["success"]:
                    results["successful"] += 1
                    logger.info(f"✅ {email}: {result['action']} page {result['page_id']}")
                else:
                    results["failed"] += 1
                    logger.error(f"❌ {email}: {result['error']}")
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "email": email,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"❌ {email}: {e}")
        
        # Summary
        logger.info(f"📊 Sync complete: {results['successful']}/{results['total']} successful")
        return results
    
    async def sync_all_contacts(self) -> Dict:
        """Sync all contacts from a predefined list"""
        # Default contact list - can be modified
        default_contacts = [
            "ethan@tuesday.vc",
            "nitin@unshackledvc.com",
            "ryan@k50ventures.com",
            "mykyta.fediushyn@flyerone.vc",
            "wayne@banktechventures.com",
            "denis@concentric.vc"
        ]
        
        return await self.sync_contacts(default_contacts)

async def main():
    """Main function"""
    system = IntegrationSystem()
    
    # Example: Sync specific contacts
    contacts = ["nitin@unshackledvc.com", "ethan@tuesday.vc"]
    results = await system.sync_contacts(contacts)
    
    # Print summary
    print(f"\n📊 SYNC SUMMARY:")
    print(f"  Total: {results['total']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Success Rate: {(results['successful']/results['total'])*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
