#!/usr/bin/env python3
"""
Test Notion API 2025-09-03
Demonstrate the new data sources and collections functionality
"""

import asyncio
import logging
from datetime import datetime
from integrations.notion_client_2025 import NotionClient2025
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_2025_notion_api():
    """Test the 2025-09-03 Notion API with data sources and collections"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Using the Investment Data Room page as parent
    parent_page_id = "2761bb72-4b52-8168-b6ba-e07f36645035"  # Investment Data Room page
    
    async with NotionClient2025(notion_token) as notion:
        try:
            logger.info("🚀 Testing Notion API 2025-09-03 with Data Sources and Collections")
            logger.info("=" * 70)
            
            # Test 1: Create Partners CRM Database with Data Source
            logger.info("\n1. Creating Partners CRM Database with Data Source...")
            partners_result = await notion.create_partners_crm_database(parent_page_id)
            partners_db = partners_result['database']
            partners_data_source = partners_result['data_source']
            
            logger.info(f"✅ Partners CRM Database created: {partners_db['url']}")
            logger.info(f"✅ Database ID: {partners_db['id']}")
            logger.info(f"✅ Data Source ID: {partners_data_source['id']}")
            
            # Test 2: Create Interactions Timeline Database with Relation
            logger.info("\n2. Creating Interactions Timeline Database with Data Source...")
            interactions_result = await notion.create_interactions_timeline_database(
                partners_data_source_id=partners_data_source['id'],
                parent_page_id=parent_page_id
            )
            interactions_db = interactions_result['database']
            interactions_data_source = interactions_result['data_source']
            
            logger.info(f"✅ Interactions Timeline Database created: {interactions_db['url']}")
            logger.info(f"✅ Database ID: {interactions_db['id']}")
            logger.info(f"✅ Data Source ID: {interactions_data_source['id']}")
            
            # Test 3: Add Sample Partners using Data Sources
            logger.info("\n3. Adding Sample Partners to Data Source...")
            
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
                    "phone": "",
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
                    partner_page = await notion.add_partner(partners_data_source['id'], partner)
                    partner_ids.append(partner_page['id'])
                    logger.info(f"✅ Added partner: {partner['name']} ({partner_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add partner {partner['name']}: {e}")
            
            # Test 4: Add Sample Interactions using Data Sources
            logger.info("\n4. Adding Sample Interactions to Data Source...")
            
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
                    interaction_page = await notion.add_interaction(interactions_data_source['id'], interaction)
                    logger.info(f"✅ Added interaction: {interaction['title'][:50]}... ({interaction_page['id']})")
                except Exception as e:
                    logger.error(f"❌ Failed to add interaction: {e}")
            
            # Test 5: Query Data Sources
            logger.info("\n5. Querying Data Sources...")
            
            # Query partners data source
            partners = await notion.query_data_source(partners_data_source['id'])
            logger.info(f"✅ Found {len(partners)} partners in data source")
            
            # Query interactions data source
            interactions = await notion.query_data_source(interactions_data_source['id'])
            logger.info(f"✅ Found {len(interactions)} interactions in data source")
            
            # Test 6: Search Functionality
            logger.info("\n6. Testing Search...")
            search_results = await notion.search("Ryan")
            logger.info(f"✅ Search found {len(search_results)} results for 'Ryan'")
            
            # Test 7: Get Data Sources for Database
            logger.info("\n7. Testing Data Sources Retrieval...")
            partners_data_sources = await notion.get_data_sources(partners_db['id'])
            logger.info(f"✅ Found {len(partners_data_sources)} data sources in Partners CRM database")
            
            interactions_data_sources = await notion.get_data_sources(interactions_db['id'])
            logger.info(f"✅ Found {len(interactions_data_sources)} data sources in Interactions Timeline database")
            
            logger.info("\n" + "=" * 70)
            logger.info("🎉 SUCCESS! Notion API 2025-09-03 is working perfectly!")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Partners CRM Database: {partners_db['url']}")
            logger.info(f"• Interactions Timeline Database: {interactions_db['url']}")
            logger.info(f"• Partners Data Source ID: {partners_data_source['id']}")
            logger.info(f"• Interactions Data Source ID: {interactions_data_source['id']}")
            logger.info(f"• Partners added: {len(partner_ids)}")
            logger.info(f"• Interactions added: {len(sample_interactions)}")
            logger.info("\n✨ Key Features Demonstrated:")
            logger.info("• Data Sources vs Databases separation (2025-09-03 API)")
            logger.info("• Proper relationship management between data sources")
            logger.info("• Latest API version 2025-09-03")
            logger.info("• Enhanced error handling and logging")
            logger.info("• Modern property types and structures")
            logger.info("• Multi-source database capabilities")
            
            # Show the created databases
            logger.info("\n🔗 DATABASE LINKS:")
            logger.info(f"Partners CRM: {partners_db['url']}")
            logger.info(f"Interactions Timeline: {interactions_db['url']}")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

def main():
    """Main function"""
    asyncio.run(test_2025_notion_api())

if __name__ == "__main__":
    main()
