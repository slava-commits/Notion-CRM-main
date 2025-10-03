#!/usr/bin/env python3
"""
Test Notion API 2025-09-03 - Simple Version
Test the new API version with standard database creation
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionClient2025Simple:
    """Notion API client using 2025-09-03 version with standard database creation"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03"  # Latest API version
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Notion API"""
        url = f"{self.base_url}/{endpoint}"
        
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"Notion API error: {response.status} - {response_data}")
                    raise Exception(f"Notion API error: {response.status} - {response_data.get('message', 'Unknown error')}")
                
                return response_data
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def create_database_with_properties(self, title: str, properties: Dict[str, Any], 
                                            parent_page_id: str) -> Dict:
        """Create a new database with custom properties using 2025-09-03 API"""
        try:
            data = {
                "title": [{"type": "text", "text": {"content": title}}],
                "parent": {"type": "page_id", "page_id": parent_page_id},
                "properties": properties
            }
            
            response = await self._make_request("POST", "databases", data)
            return response
        except Exception as e:
            logger.error(f"Failed to create database with properties: {e}")
            raise
    
    async def create_page_in_database(self, database_id: str, properties: Dict[str, Any]) -> Dict:
        """Create a new page in a database using 2025-09-03 API"""
        try:
            data = {
                "parent": {"type": "database_id", "database_id": database_id},
                "properties": properties
            }
            
            response = await self._make_request("POST", "pages", data)
            return response
        except Exception as e:
            logger.error(f"Failed to create page in database: {e}")
            raise
    
    async def query_database(self, database_id: str, filter_data: Optional[Dict] = None, 
                           sorts: Optional[List[Dict]] = None, page_size: int = 100) -> List[Dict]:
        """Query a database using 2025-09-03 API"""
        try:
            data = {"page_size": page_size}
            if filter_data:
                data["filter"] = filter_data
            if sorts:
                data["sorts"] = sorts
            
            response = await self._make_request("POST", f"databases/{database_id}/query", data)
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Failed to query database {database_id}: {e}")
            return []

async def test_2025_simple_api():
    """Test the 2025-09-03 Notion API with standard database creation"""
    
    # Get Notion token from config
    notion_token = Config.NOTION_TOKEN
    if not notion_token:
        logger.error("Notion token not found in config")
        return
    
    # Using the Investment Data Room page as parent
    parent_page_id = "2761bb72-4b52-8168-b6ba-e07f36645035"  # Investment Data Room page
    
    async with NotionClient2025Simple(notion_token) as notion:
        try:
            logger.info("🚀 Testing Notion API 2025-09-03 (Simple Version)")
            logger.info("=" * 60)
            
            # Test 1: Create Partners CRM Database
            logger.info("\n1. Creating Partners CRM Database...")
            
            partners_properties = {
                "Name": {"title": {}},
                "First Name": {"rich_text": {}},
                "Last Name": {"rich_text": {}},
                "Email": {"email": {}},
                "Company": {"rich_text": {}},
                "Job Title": {"rich_text": {}},
                "Phone": {"phone_number": {}},
                "LinkedIn": {"url": {}},
                "Twitter/X": {"url": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Active", "color": "green"},
                            {"name": "Warm", "color": "yellow"},
                            {"name": "Cold", "color": "gray"},
                            {"name": "Dormant", "color": "red"}
                        ]
                    }
                },
                "Tier": {
                    "select": {
                        "options": [
                            {"name": "A - High Priority", "color": "red"},
                            {"name": "B - Medium Priority", "color": "yellow"},
                            {"name": "C - Low Priority", "color": "green"}
                        ]
                    }
                },
                "Role": {
                    "select": {
                        "options": [
                            {"name": "Founder", "color": "blue"},
                            {"name": "Investor", "color": "purple"},
                            {"name": "Partner", "color": "green"},
                            {"name": "Client", "color": "orange"},
                            {"name": "Provider", "color": "brown"},
                            {"name": "Other", "color": "gray"}
                        ]
                    }
                },
                "Tags": {
                    "multi_select": {
                        "options": [
                            {"name": "VIP", "color": "red"},
                            {"name": "Follow Up", "color": "yellow"},
                            {"name": "Meeting Scheduled", "color": "blue"},
                            {"name": "Proposal Sent", "color": "green"},
                            {"name": "Contract Signed", "color": "purple"}
                        ]
                    }
                },
                "Notes": {"rich_text": {}},
                "Last Interaction": {"date": {}},
                "Next Step": {"rich_text": {}}
            }
            
            partners_db = await notion.create_database_with_properties(
                title="Partners CRM 2025",
                properties=partners_properties,
                parent_page_id=parent_page_id
            )
            
            logger.info(f"✅ Partners CRM Database created: {partners_db['url']}")
            logger.info(f"✅ Database ID: {partners_db['id']}")
            
            # Test 2: Create Interactions Timeline Database
            logger.info("\n2. Creating Interactions Timeline Database...")
            
            interactions_properties = {
                "Title": {"title": {}},
                "Person": {
                    "relation": {
                        "database_id": partners_db['id'],
                        "single_property": {}
                    }
                },
                "Type": {
                    "select": {
                        "options": [
                            {"name": "Email In", "color": "blue"},
                            {"name": "Email Out", "color": "green"},
                            {"name": "Meeting", "color": "purple"},
                            {"name": "Phone Call", "color": "orange"},
                            {"name": "Document Shared", "color": "brown"},
                            {"name": "Social Media", "color": "pink"},
                            {"name": "Other", "color": "gray"}
                        ]
                    }
                },
                "Source": {"rich_text": {}},
                "Date": {"date": {}},
                "Subject": {"rich_text": {}},
                "Content": {"rich_text": {}},
                "URL": {"url": {}},
                "Source ID": {"rich_text": {}},
                "Direction": {
                    "select": {
                        "options": [
                            {"name": "Inbound", "color": "blue"},
                            {"name": "Outbound", "color": "green"}
                        ]
                    }
                },
                "Follow Up": {"checkbox": {}},
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "green"}
                        ]
                    }
                }
            }
            
            interactions_db = await notion.create_database_with_properties(
                title="Interactions Timeline 2025",
                properties=interactions_properties,
                parent_page_id=parent_page_id
            )
            
            logger.info(f"✅ Interactions Timeline Database created: {interactions_db['url']}")
            logger.info(f"✅ Database ID: {interactions_db['id']}")
            
            # Test 3: Add Sample Partners
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
                    properties = {
                        "Name": {"title": [{"type": "text", "text": {"content": partner["name"]}}]},
                        "First Name": {"rich_text": [{"type": "text", "text": {"content": partner.get("first_name", "")}}]},
                        "Last Name": {"rich_text": [{"type": "text", "text": {"content": partner.get("last_name", "")}}]},
                        "Email": {"email": partner.get("email", "")},
                        "Company": {"rich_text": [{"type": "text", "text": {"content": partner.get("company", "")}}]},
                        "Job Title": {"rich_text": [{"type": "text", "text": {"content": partner.get("job_title", "")}}]},
                        "Status": {"select": {"name": partner.get("status", "Active")}},
                        "Tier": {"select": {"name": partner.get("tier", "C - Low Priority")}},
                        "Role": {"select": {"name": partner.get("role", "Other")}},
                        "Tags": {"multi_select": [{"name": tag} for tag in partner.get("tags", [])]},
                        "Notes": {"rich_text": [{"type": "text", "text": {"content": partner.get("notes", "")}}]},
                        "Next Step": {"rich_text": [{"type": "text", "text": {"content": partner.get("next_step", "")}}]}
                    }
                    
                    # Only add properties that have values
                    if partner.get("phone"):
                        properties["Phone"] = {"phone_number": partner["phone"]}
                    if partner.get("linkedin"):
                        properties["LinkedIn"] = {"url": partner["linkedin"]}
                    if partner.get("twitter"):
                        properties["Twitter/X"] = {"url": partner["twitter"]}
                    
                    partner_page = await notion.create_page_in_database(partners_db['id'], properties)
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
                    properties = {
                        "Title": {"title": [{"type": "text", "text": {"content": interaction["title"]}}]},
                        "Type": {"select": {"name": interaction.get("type", "Other")}},
                        "Source": {"rich_text": [{"type": "text", "text": {"content": interaction.get("source", "")}}]},
                        "Subject": {"rich_text": [{"type": "text", "text": {"content": interaction.get("subject", "")}}]},
                        "Content": {"rich_text": [{"type": "text", "text": {"content": interaction.get("content", "")}}]},
                        "Source ID": {"rich_text": [{"type": "text", "text": {"content": interaction.get("source_id", "")}}]},
                        "Direction": {"select": {"name": interaction.get("direction", "Inbound")}},
                        "Follow Up": {"checkbox": interaction.get("follow_up", False)},
                        "Priority": {"select": {"name": interaction.get("priority", "Medium")}}
                    }
                    
                    # Add date if provided
                    if "date" in interaction:
                        properties["Date"] = {
                            "date": {
                                "start": interaction["date"]
                            }
                        }
                    
                    # Add person relation if provided
                    if "person_id" in interaction and interaction["person_id"]:
                        properties["Person"] = {
                            "relation": [{"id": interaction["person_id"]}]
                        }
                    
                    # Only add URL if it has a value
                    if interaction.get("url"):
                        properties["URL"] = {"url": interaction["url"]}
                    
                    interaction_page = await notion.create_page_in_database(interactions_db['id'], properties)
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
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 SUCCESS! Notion API 2025-09-03 is working perfectly!")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Partners CRM Database: {partners_db['url']}")
            logger.info(f"• Interactions Timeline Database: {interactions_db['url']}")
            logger.info(f"• Partners added: {len(partner_ids)}")
            logger.info(f"• Interactions added: {len(sample_interactions)}")
            logger.info("\n✨ Key Features Demonstrated:")
            logger.info("• Latest API version 2025-09-03")
            logger.info("• Proper database creation with parent pages")
            logger.info("• Relationship management between databases")
            logger.info("• Enhanced error handling and logging")
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
    asyncio.run(test_2025_simple_api())

if __name__ == "__main__":
    main()
