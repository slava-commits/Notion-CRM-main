#!/usr/bin/env python3
"""
Sync Contacts CLI
Streamlined command-line interface for syncing contacts from Attio to Notion
"""

import asyncio
import argparse
import logging
from typing import List
from attio_to_notion_integration import AttioToNotionIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def sync_single_contact(email: str) -> bool:
    """Sync a single contact"""
    integration = AttioToNotionIntegration()
    result = await integration.sync_contact(email)
    
    if result["success"]:
        logger.info(f"✅ {email}: {result['action']} page {result['page_id']}")
        return True
    else:
        logger.error(f"❌ {email}: {result['error']}")
        return False

async def sync_multiple_contacts(emails: List[str]) -> None:
    """Sync multiple contacts"""
    logger.info(f"🚀 Syncing {len(emails)} contacts...")
    
    integration = AttioToNotionIntegration()
    success_count = 0
    
    for email in emails:
        result = await integration.sync_contact(email)
        if result["success"]:
            logger.info(f"✅ {email}: {result['action']} page {result['page_id']}")
            success_count += 1
        else:
            logger.error(f"❌ {email}: {result['error']}")
    
    logger.info(f"📊 Completed: {success_count}/{len(emails)} contacts synced successfully")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Sync contacts from Attio to Notion")
    parser.add_argument("emails", nargs="+", help="Email addresses to sync")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run sync
    asyncio.run(sync_multiple_contacts(args.emails))

if __name__ == "__main__":
    main()
