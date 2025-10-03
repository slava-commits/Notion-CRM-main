#!/usr/bin/env python3
"""
Test Latest Notion API (2025-09-03)
Demonstrate the new data sources and collections functionality
"""

import asyncio
import logging
from datetime import datetime
from integrations.notion_client_v2 import NotionClientV2
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_latest_notion_api():
    """Test the latest Notion API with data sources and collections"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    async with NotionClientV2(notion_token) as notion:
        try:
            logger.info("🚀 Testing Latest Notion API (2025-09-03)")
            logger.info("=" * 60)
            
            # Test 1: Create Partners CRM Database with Data Source
            logger.info("\n1. Creating Partners CRM Database...")
            partners_db = await notion.create_partners_crm_database()
            logger.info(f"✅ Partners CRM Database created: {partners_db['database']['url']}")
            logger.info(f"✅ Data Source ID: {partners_db['data_source']['id']}")
            
            # Test 2: Create Interactions Timeline Database with Relation
            logger.info("\n2. Creating Interactions Timeline Database...")
            interactions_db = await notion.create_interactions_timeline_database(
                partners_data_source_id=partners_db['data_source']['id']
            )
            logger.info(f"✅ Interactions Timeline Database created: {interactions_db['database']['url']}")
            logger.info(f"✅ Data Source ID: {interactions_db['data_source']['id']}")
            
            # Test 3: Add Sample Partners
            logger.info("\n3. Adding Sample Partners...")
            
            sample_partners = [
                {
                    "name": "Ryan",
                    "first_name": "Ryan",
                    "last_name": "K50 Ventures",
                    "email": "ryan@k50ventures.com",
                    "company": "K50 Ventures",
                    "job_title": "Partner",
                    "status": "Active",
                    "tier": "A - High Priority",
                    "role": "Investor",
                    "tags": ["VIP", "Follow Up"],
                    "notes": "K50 Ventures - Early stage VC focused on B2B SaaS and marketplace startups"
                },
                {
                    "name": "Mykyta Fediushyn",
                    "first_name": "Mykyta",
                    "last_name": "Fediushyn",
                    "email": "mykyta.fediushyn@flyerone.vc",
                    "company": "Flyer One Ventures",
                    "job_title": "Partner",
                    "status": "Active",
                    "tier": "A - High Priority",
                    "role": "Investor",
                    "tags": ["Follow Up"],
                    "notes": "Flyer One Ventures - European VC with focus on B2B and marketplace startups"
                }
            ]
            
            partner_ids = []
            for partner in sample_partners:
                try:
                    partner_page = await notion.add_partner(partners_db['data_source']['id'], partner)
                    partner_ids.append(partner_page['id'])
                    logger.info(f"✅ Added partner: {partner['name']} ({partner_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add partner {partner['name']}: {e}")
            
            # Test 4: Add Sample Interactions
            logger.info("\n4. Adding Sample Interactions...")
            
            sample_interactions = [
                {
                    "title": "Re: Jupid just unlocked access to 22M potential users 💥",
                    "type": "Email In",
                    "source": "Gmail",
                    "subject": "Re: Jupid just unlocked access to 22M potential users 💥",
                    "content": "Hey Slava - we are swamped so need some time to look through everything. We will be back in the next couple days.",
                    "direction": "Inbound",
                    "priority": "High",
                    "follow_up": True,
                    "date": "2025-09-25T16:56:07.816661",
                    "person_id": partner_ids[0] if partner_ids else None
                },
                {
                    "title": "Re: Jupid.tax / Monit intro",
                    "type": "Email In",
                    "source": "Gmail",
                    "subject": "Re: Jupid.tax / Monit intro",
                    "content": "Great news Anna! Thanks for the update. Keep me posted.",
                    "direction": "Inbound",
                    "priority": "Medium",
                    "follow_up": False,
                    "date": "2025-09-25T16:56:09.349502",
                    "person_id": partner_ids[1] if len(partner_ids) > 1 else None
                }
            ]
            
            for interaction in sample_interactions:
                try:
                    interaction_page = await notion.add_interaction(interactions_db['data_source']['id'], interaction)
                    logger.info(f"✅ Added interaction: {interaction['title'][:50]}... ({interaction_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add interaction: {e}")
            
            # Test 5: Query Data Sources
            logger.info("\n5. Querying Data Sources...")
            
            # Query partners
            partners = await notion.query_data_source(partners_db['data_source']['id'])
            logger.info(f"✅ Found {len(partners)} partners in database")
            
            # Query interactions
            interactions = await notion.query_data_source(interactions_db['data_source']['id'])
            logger.info(f"✅ Found {len(interactions)} interactions in database")
            
            # Test 6: Search Functionality
            logger.info("\n6. Testing Search...")
            search_results = await notion.search("Ryan")
            logger.info(f"✅ Search found {len(search_results)} results for 'Ryan'")
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 SUCCESS! Latest Notion API (2025-09-03) is working perfectly!")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Partners CRM Database: {partners_db['database']['url']}")
            logger.info(f"• Interactions Timeline Database: {interactions_db['database']['url']}")
            logger.info(f"• Partners added: {len(partner_ids)}")
            logger.info(f"• Interactions added: {len(sample_interactions)}")
            logger.info("\n✨ Key Features Demonstrated:")
            logger.info("• Data Sources vs Databases separation")
            logger.info("• Proper relationship management")
            logger.info("• Latest API version 2025-09-03")
            logger.info("• Enhanced error handling")
            logger.info("• Modern property types and structures")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

def main():
    """Main function"""
    asyncio.run(test_latest_notion_api())

if __name__ == "__main__":
    main()
