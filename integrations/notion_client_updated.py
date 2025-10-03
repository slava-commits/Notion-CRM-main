#!/usr/bin/env python3
"""
Notion Client Updated - Using Current Stable API
Handles all Notion API interactions using the current stable API with proper database creation
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class NotionClientUpdated:
    """Notion API client using the current stable API with enhanced database creation"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # Current stable API version
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
    
    # ===== DATABASE MANAGEMENT =====
    
    async def create_database(self, title: str, description: str = "", parent_page_id: Optional[str] = None) -> Dict:
        """Create a new database with proper parent structure"""
        try:
            # If no parent specified, we need to find a workspace page or create in workspace
            if not parent_page_id:
                # For now, we'll require a parent page ID
                raise ValueError("Parent page ID is required for database creation")
            
            data = {
                "title": [{"type": "text", "text": {"content": title}}],
                "parent": {"type": "page_id", "page_id": parent_page_id},
                "properties": {
                    "Name": {"title": {}},
                    "Created": {"created_time": {}},
                    "Last Edited": {"last_edited_time": {}}
                }
            }
            
            response = await self._make_request("POST", "databases", data)
            return response
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    async def create_database_with_properties(self, title: str, properties: Dict[str, Any], 
                                            parent_page_id: Optional[str] = None) -> Dict:
        """Create a new database with custom properties"""
        try:
            if not parent_page_id:
                raise ValueError("Parent page ID is required for database creation")
            
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
    
    async def get_database(self, database_id: str) -> Dict:
        """Get database information"""
        try:
            response = await self._make_request("GET", f"databases/{database_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get database {database_id}: {e}")
            raise
    
    # ===== PAGE MANAGEMENT =====
    
    async def create_page_in_database(self, database_id: str, properties: Dict[str, Any]) -> Dict:
        """Create a new page in a database"""
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
    
    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict:
        """Update a page"""
        try:
            data = {"properties": properties}
            response = await self._make_request("PATCH", f"pages/{page_id}", data)
            return response
        except Exception as e:
            logger.error(f"Failed to update page {page_id}: {e}")
            raise
    
    async def get_page(self, page_id: str) -> Dict:
        """Get page information"""
        try:
            response = await self._make_request("GET", f"pages/{page_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to get page {page_id}: {e}")
            raise
    
    # ===== QUERYING =====
    
    async def query_database(self, database_id: str, filter_data: Optional[Dict] = None, 
                           sorts: Optional[List[Dict]] = None, page_size: int = 100) -> List[Dict]:
        """Query a database"""
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
    
    # ===== SEARCH =====
    
    async def search(self, query: str, filter_data: Optional[Dict] = None, 
                    page_size: int = 100) -> List[Dict]:
        """Search across workspace"""
        try:
            data = {"query": query, "page_size": page_size}
            if filter_data:
                data["filter"] = filter_data
            
            response = await self._make_request("POST", "search", data)
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    # ===== SPECIFIC BUSINESS LOGIC METHODS =====
    
    async def create_partners_crm_database(self, parent_page_id: str) -> Dict:
        """Create the Partners CRM database with proper schema"""
        try:
            properties = {
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
            
            database = await self.create_database_with_properties(
                title="Partners CRM",
                properties=properties,
                parent_page_id=parent_page_id
            )
            
            return database
            
        except Exception as e:
            logger.error(f"Failed to create Partners CRM database: {e}")
            raise
    
    async def create_interactions_timeline_database(self, partners_database_id: str, 
                                                   parent_page_id: str) -> Dict:
        """Create the Interactions Timeline database with relation to Partners CRM"""
        try:
            properties = {
                "Title": {"title": {}},
                "Person": {
                    "relation": {
                        "database_id": partners_database_id,
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
            
            database = await self.create_database_with_properties(
                title="Interactions Timeline",
                properties=properties,
                parent_page_id=parent_page_id
            )
            
            return database
            
        except Exception as e:
            logger.error(f"Failed to create Interactions Timeline database: {e}")
            raise
    
    # ===== PARTNER MANAGEMENT =====
    
    async def add_partner(self, database_id: str, partner_data: Dict[str, Any]) -> Dict:
        """Add a partner to the Partners CRM database"""
        try:
            properties = {
                "Name": {"title": [{"type": "text", "text": {"content": partner_data["name"]}}]},
                "First Name": {"rich_text": [{"type": "text", "text": {"content": partner_data.get("first_name", "")}}]},
                "Last Name": {"rich_text": [{"type": "text", "text": {"content": partner_data.get("last_name", "")}}]},
                "Email": {"email": partner_data.get("email", "")},
                "Company": {"rich_text": [{"type": "text", "text": {"content": partner_data.get("company", "")}}]},
                "Job Title": {"rich_text": [{"type": "text", "text": {"content": partner_data.get("job_title", "")}}]},
                "Status": {"select": {"name": partner_data.get("status", "Active")}},
                "Tier": {"select": {"name": partner_data.get("tier", "C - Low Priority")}},
                "Role": {"select": {"name": partner_data.get("role", "Other")}},
                "Tags": {"multi_select": [{"name": tag} for tag in partner_data.get("tags", [])]},
                "Notes": {"rich_text": [{"type": "text", "text": {"content": partner_data.get("notes", "")}}]},
                "Next Step": {"rich_text": [{"type": "text", "text": {"content": partner_data.get("next_step", "")}}]}
            }
            
            # Only add properties that have values (not None)
            if partner_data.get("phone"):
                properties["Phone"] = {"phone_number": partner_data["phone"]}
            if partner_data.get("linkedin"):
                properties["LinkedIn"] = {"url": partner_data["linkedin"]}
            if partner_data.get("twitter"):
                properties["Twitter/X"] = {"url": partner_data["twitter"]}
            
            # Add last interaction date if provided
            if "last_interaction" in partner_data:
                properties["Last Interaction"] = {
                    "date": {
                        "start": partner_data["last_interaction"]
                    }
                }
            
            response = await self.create_page_in_database(database_id, properties)
            return response
            
        except Exception as e:
            logger.error(f"Failed to add partner: {e}")
            raise
    
    async def add_interaction(self, database_id: str, interaction_data: Dict[str, Any]) -> Dict:
        """Add an interaction to the Interactions Timeline database"""
        try:
            properties = {
                "Title": {"title": [{"type": "text", "text": {"content": interaction_data["title"]}}]},
                "Type": {"select": {"name": interaction_data.get("type", "Other")}},
                "Source": {"rich_text": [{"type": "text", "text": {"content": interaction_data.get("source", "")}}]},
                "Subject": {"rich_text": [{"type": "text", "text": {"content": interaction_data.get("subject", "")}}]},
                "Content": {"rich_text": [{"type": "text", "text": {"content": interaction_data.get("content", "")}}]},
                "Source ID": {"rich_text": [{"type": "text", "text": {"content": interaction_data.get("source_id", "")}}]},
                "Direction": {"select": {"name": interaction_data.get("direction", "Inbound")}},
                "Follow Up": {"checkbox": interaction_data.get("follow_up", False)},
                "Priority": {"select": {"name": interaction_data.get("priority", "Medium")}}
            }
            
            # Only add URL if it has a value
            if interaction_data.get("url"):
                properties["URL"] = {"url": interaction_data["url"]}
            
            # Add date if provided
            if "date" in interaction_data:
                properties["Date"] = {
                    "date": {
                        "start": interaction_data["date"]
                    }
                }
            
            # Add person relation if provided
            if "person_id" in interaction_data:
                properties["Person"] = {
                    "relation": [{"id": interaction_data["person_id"]}]
                }
            
            response = await self.create_page_in_database(database_id, properties)
            return response
            
        except Exception as e:
            logger.error(f"Failed to add interaction: {e}")
            raise

# Example usage
if __name__ == "__main__":
    print("Notion Client Updated - Current Stable API - Ready to use!")
    print("This module provides all Notion API interactions using the current stable API.")
