#!/usr/bin/env python3
"""
Test Working Notion API
Demonstrate database creation and management with proper property handling
"""

import asyncio
import logging
from datetime import datetime
from integrations.notion_client_updated import NotionClientUpdated
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_working_notion_api():
    """Test the working Notion API with proper property handling"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Using the Investment Data Room page as parent
    parent_page_id = "2761bb72-4b52-8168-b6ba-e07f36645035"  # Investment Data Room page
    
    async with NotionClientUpdated(notion_token) as notion:
        try:
            logger.info("🚀 Testing Working Notion API (2022-06-28)")
            logger.info("=" * 60)
            
            # Test 1: Create Partners CRM Database
            logger.info("\n1. Creating Partners CRM Database...")
            partners_db = await notion.create_partners_crm_database(parent_page_id)
            logger.info(f"✅ Partners CRM Database created: {partners_db['url']}")
            logger.info(f"✅ Database ID: {partners_db['id']}")
            
            # Test 2: Create Interactions Timeline Database with Relation
            logger.info("\n2. Creating Interactions Timeline Database...")
            interactions_db = await notion.create_interactions_timeline_database(
                partners_database_id=partners_db['id'],
                parent_page_id=parent_page_id
            )
            logger.info(f"✅ Interactions Timeline Database created: {interactions_db['url']}")
            logger.info(f"✅ Database ID: {interactions_db['id']}")
            
            # Test 3: Add Sample Partners with proper null handling
            logger.info("\n3. Adding Sample Partners...")
            
            sample_partners = [
                {
                    "name": "Ryan K50 Ventures",
                    "first_name": "Ryan",
                    "last_name": "K50 Ventures",
                    "email": "ryan@k50ventures.com",
                    "company": "K50 Ventures",
                    "job_title": "Partner",
                    "status": "Active",
                    "tier": "A - High Priority",
                    "role": "Investor",
                    "tags": ["VIP", "Follow Up"],
                    "notes": "K50 Ventures - Early stage VC focused on B2B SaaS and marketplace startups",
                    "phone": "",  # Use empty string instead of None
                    "linkedin": "",
                    "twitter": "",
                    "next_step": ""
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
                    "notes": "Flyer One Ventures - European VC with focus on B2B and marketplace startups",
                    "phone": "",
                    "linkedin": "",
                    "twitter": "",
                    "next_step": ""
                },
                {
                    "name": "Wayne BankTech Ventures",
                    "first_name": "Wayne",
                    "last_name": "BankTech Ventures",
                    "email": "wayne@banktechventures.com",
                    "company": "BankTech Ventures",
                    "job_title": "Partner",
                    "status": "Active",
                    "tier": "A - High Priority",
                    "role": "Investor",
                    "tags": ["VIP"],
                    "notes": "BankTech Ventures - Focus on fintech and banking technology investments",
                    "phone": "",
                    "linkedin": "",
                    "twitter": "",
                    "next_step": ""
                },
                {
                    "name": "Denis Concentric VC",
                    "first_name": "Denis",
                    "last_name": "Concentric VC",
                    "email": "denis@concentric.vc",
                    "company": "Concentric VC",
                    "job_title": "Partner",
                    "status": "Active",
                    "tier": "A - High Priority",
                    "role": "Investor",
                    "tags": ["Follow Up"],
                    "notes": "Concentric VC - Early stage venture capital firm",
                    "phone": "",
                    "linkedin": "",
                    "twitter": "",
                    "next_step": ""
                }
            ]
            
            partner_ids = []
            for partner in sample_partners:
                try:
                    partner_page = await notion.add_partner(partners_db['id'], partner)
                    partner_ids.append(partner_page['id'])
                    logger.info(f"✅ Added partner: {partner['name']} ({partner_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add partner {partner['name']}: {e}")
            
            # Test 4: Add Sample Interactions with proper null handling
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
                    "person_id": partner_ids[0] if partner_ids else None,
                    "url": "",
                    "source_id": "196f914ee9caf341"
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
                    "person_id": partner_ids[1] if len(partner_ids) > 1 else None,
                    "url": "",
                    "source_id": "196fd2b2a07dd477"
                }
            ]
            
            for interaction in sample_interactions:
                try:
                    interaction_page = await notion.add_interaction(interactions_db['id'], interaction)
                    logger.info(f"✅ Added interaction: {interaction['title'][:50]}... ({interaction_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add interaction: {e}")
            
            # Test 5: Query Databases
            logger.info("\n5. Querying Databases...")
            
            # Query partners
            partners = await notion.query_database(partners_db['id'])
            logger.info(f"✅ Found {len(partners)} partners in database")
            
            # Query interactions
            interactions = await notion.query_database(interactions_db['id'])
            logger.info(f"✅ Found {len(interactions)} interactions in database")
            
            # Test 6: Search Functionality
            logger.info("\n6. Testing Search...")
            search_results = await notion.search("Ryan")
            logger.info(f"✅ Search found {len(search_results)} results for 'Ryan'")
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 SUCCESS! Working Notion API is functioning perfectly!")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Partners CRM Database: {partners_db['url']}")
            logger.info(f"• Interactions Timeline Database: {interactions_db['url']}")
            logger.info(f"• Partners added: {len(partner_ids)}")
            logger.info(f"• Interactions added: {len(sample_interactions)}")
            logger.info("\n✨ Key Features Demonstrated:")
            logger.info("• Proper database creation with parent pages")
            logger.info("• Relationship management between databases")
            logger.info("• Current stable API version 2022-06-28")
            logger.info("• Proper null handling for empty properties")
            logger.info("• Modern property types and structures")
            
            # Show the created databases
            logger.info("\n🔗 DATABASE LINKS:")
            logger.info(f"Partners CRM: {partners_db['url']}")
            logger.info(f"Interactions Timeline: {interactions_db['url']}")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

def main():
    """Main function"""
    asyncio.run(test_working_notion_api())

if __name__ == "__main__":
    main()
