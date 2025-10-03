#!/usr/bin/env python3
"""
Notion Schema Definition and Database Creation
Defines all required databases for the user data integration system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class NotionProperty:
    """Represents a Notion database property"""
    name: str
    type: str
    config: Dict[str, Any] = None
    
    def to_notion_format(self) -> Dict[str, Any]:
        """Convert to Notion API format"""
        if self.config is None:
            self.config = {}
        
        return {
            "name": self.name,
            "type": self.type,
            **self.config
        }

class NotionSchemaBuilder:
    """Builder for creating Notion workspace schema"""
    
    def __init__(self):
        self.databases = {}
    
    def create_people_database(self) -> Dict[str, Any]:
        """Create People database schema"""
        properties = {
            "Name": NotionProperty("Name", "title"),
            "Primary Email": NotionProperty("Primary Email", "email"),
            "LinkedIn URL": NotionProperty("LinkedIn URL", "url"),
            "X Handle": NotionProperty("X Handle", "rich_text"),
            "Role": NotionProperty("Role", "select", {
                "select": {
                    "options": [
                        {"name": "Founder", "color": "blue"},
                        {"name": "Investor", "color": "green"},
                        {"name": "Partner", "color": "purple"},
                        {"name": "Client", "color": "orange"}
                    ]
                }
            }),
            "Company": NotionProperty("Company", "rich_text"),
            "ATTIO Id": NotionProperty("ATTIO Id", "rich_text"),
            "Confidence": NotionProperty("Confidence", "number", {
                "number": {"format": "percent"}
            }),
            "Owner": NotionProperty("Owner", "people"),
            "Last Interaction": NotionProperty("Last Interaction", "date"),
            "Next Step": NotionProperty("Next Step", "rich_text"),
            "Status": NotionProperty("Status", "select", {
                "select": {
                    "options": [
                        {"name": "Active", "color": "green"},
                        {"name": "Warm", "color": "yellow"},
                        {"name": "Cold", "color": "gray"},
                        {"name": "Dormant", "color": "red"}
                    ]
                }
            }),
            "Tier": NotionProperty("Tier", "select", {
                "select": {
                    "options": [
                        {"name": "A", "color": "green"},
                        {"name": "B", "color": "yellow"},
                        {"name": "C", "color": "red"}
                    ]
                }
            })
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "People"}}],
            "description": [{"type": "text", "text": {"content": "Central database of all contacts and relationships"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_companies_database(self) -> Dict[str, Any]:
        """Create Companies database schema"""
        properties = {
            "Name": NotionProperty("Name", "title"),
            "Website": NotionProperty("Website", "url"),
            "Type": NotionProperty("Type", "select", {
                "select": {
                    "options": [
                        {"name": "Investor", "color": "green"},
                        {"name": "Partner", "color": "blue"},
                        {"name": "Client", "color": "orange"},
                        {"name": "Provider", "color": "purple"}
                    ]
                }
            }),
            "People": NotionProperty("People", "relation", {
                "relation": {
                    "database_id": "PEOPLE_DB_ID",  # Will be replaced with actual ID
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Open Deals": NotionProperty("Open Deals", "rich_text"),
            "Last Interaction": NotionProperty("Last Interaction", "rollup", {
                "rollup": {
                    "relation_property_name": "Company",
                    "rollup_property_name": "Timestamp",
                    "function": "max"
                }
            })
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Companies"}}],
            "description": [{"type": "text", "text": {"content": "Company information and relationships"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_threads_database(self) -> Dict[str, Any]:
        """Create Threads database schema"""
        properties = {
            "Title": NotionProperty("Title", "title"),
            "People": NotionProperty("People", "relation", {
                "relation": {
                    "database_id": "PEOPLE_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Company": NotionProperty("Company", "relation", {
                "relation": {
                    "database_id": "COMPANIES_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Origin": NotionProperty("Origin", "select", {
                "select": {
                    "options": [
                        {"name": "Email", "color": "blue"},
                        {"name": "Intro", "color": "green"},
                        {"name": "Meeting", "color": "purple"}
                    ]
                }
            }),
            "State": NotionProperty("State", "select", {
                "select": {
                    "options": [
                        {"name": "Active", "color": "green"},
                        {"name": "Waiting", "color": "yellow"},
                        {"name": "Closed", "color": "gray"}
                    ]
                }
            }),
            "Last Message At": NotionProperty("Last Message At", "date"),
            "Last From": NotionProperty("Last From", "select", {
                "select": {
                    "options": [
                        {"name": "Them", "color": "blue"},
                        {"name": "Us", "color": "green"}
                    ]
                }
            }),
            "SLA": NotionProperty("SLA", "number", {
                "number": {"format": "number"}
            })
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Threads"}}],
            "description": [{"type": "text", "text": {"content": "Conversation threads and communication sequences"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_interactions_database(self) -> Dict[str, Any]:
        """Create Interactions database schema"""
        properties = {
            "Type": NotionProperty("Type", "select", {
                "select": {
                    "options": [
                        {"name": "Email In", "color": "blue"},
                        {"name": "Email Out", "color": "green"},
                        {"name": "Meeting", "color": "purple"},
                        {"name": "Fathom Summary", "color": "orange"},
                        {"name": "Social Post", "color": "pink"},
                        {"name": "Social Comment", "color": "yellow"},
                        {"name": "Doc Event", "color": "gray"}
                    ]
                }
            }),
            "Timestamp": NotionProperty("Timestamp", "created_time"),
            "Channel": NotionProperty("Channel", "select", {
                "select": {
                    "options": [
                        {"name": "Gmail", "color": "red"},
                        {"name": "Calendar", "color": "blue"},
                        {"name": "Fathom", "color": "green"},
                        {"name": "LinkedIn", "color": "blue"},
                        {"name": "X", "color": "black"},
                        {"name": "DocuSign", "color": "purple"}
                    ]
                }
            }),
            "People": NotionProperty("People", "relation", {
                "relation": {
                    "database_id": "PEOPLE_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Company": NotionProperty("Company", "relation", {
                "relation": {
                    "database_id": "COMPANIES_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Thread": NotionProperty("Thread", "relation", {
                "relation": {
                    "database_id": "THREADS_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Subject/Title": NotionProperty("Subject/Title", "title"),
            "Snippet/Link": NotionProperty("Snippet/Link", "url"),
            "Source Id": NotionProperty("Source Id", "rich_text")
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Interactions"}}],
            "description": [{"type": "text", "text": {"content": "All interactions and touchpoints"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_tasks_database(self) -> Dict[str, Any]:
        """Create Tasks database schema"""
        properties = {
            "Title": NotionProperty("Title", "title"),
            "Owner": NotionProperty("Owner", "people"),
            "Due": NotionProperty("Due", "date"),
            "Priority": NotionProperty("Priority", "select", {
                "select": {
                    "options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "green"}
                    ]
                }
            }),
            "Status": NotionProperty("Status", "select", {
                "select": {
                    "options": [
                        {"name": "Todo", "color": "gray"},
                        {"name": "Doing", "color": "blue"},
                        {"name": "Blocked", "color": "red"},
                        {"name": "Done", "color": "green"}
                    ]
                }
            }),
            "Reason": NotionProperty("Reason", "select", {
                "select": {
                    "options": [
                        {"name": "Waiting on reply", "color": "yellow"},
                        {"name": "Social touch", "color": "blue"},
                        {"name": "Next step", "color": "green"},
                        {"name": "Doc", "color": "purple"}
                    ]
                }
            }),
            "Person": NotionProperty("Person", "relation", {
                "relation": {
                    "database_id": "PEOPLE_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Company": NotionProperty("Company", "relation", {
                "relation": {
                    "database_id": "COMPANIES_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Thread": NotionProperty("Thread", "relation", {
                "relation": {
                    "database_id": "THREADS_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Leaner Id": NotionProperty("Leaner Id", "rich_text")
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Tasks"}}],
            "description": [{"type": "text", "text": {"content": "Task management with Leaner synchronization"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_social_activity_database(self) -> Dict[str, Any]:
        """Create Social Activity database schema"""
        properties = {
            "Network": NotionProperty("Network", "select", {
                "select": {
                    "options": [
                        {"name": "LinkedIn", "color": "blue"},
                        {"name": "X", "color": "black"}
                    ]
                }
            }),
            "Activity Type": NotionProperty("Activity Type", "select", {
                "select": {
                    "options": [
                        {"name": "Post", "color": "blue"},
                        {"name": "Comment", "color": "green"},
                        {"name": "Mention", "color": "yellow"},
                        {"name": "Like", "color": "pink"}
                    ]
                }
            }),
            "Timestamp": NotionProperty("Timestamp", "created_time"),
            "URL": NotionProperty("URL", "url"),
            "Person": NotionProperty("Person", "relation", {
                "relation": {
                    "database_id": "PEOPLE_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Company": NotionProperty("Company", "relation", {
                "relation": {
                    "database_id": "COMPANIES_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Summary": NotionProperty("Summary", "rich_text"),
            "Action Suggestion": NotionProperty("Action Suggestion", "rich_text")
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Social Activity"}}],
            "description": [{"type": "text", "text": {"content": "Social media activity tracking and engagement"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_documents_database(self) -> Dict[str, Any]:
        """Create Documents database schema"""
        properties = {
            "Type": NotionProperty("Type", "select", {
                "select": {
                    "options": [
                        {"name": "DocuSign NDA", "color": "blue"},
                        {"name": "Term Sheet", "color": "green"},
                        {"name": "Data Room View", "color": "purple"}
                    ]
                }
            }),
            "Counterparty": NotionProperty("Counterparty", "relation", {
                "relation": {
                    "database_id": "PEOPLE_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "URL": NotionProperty("URL", "url"),
            "Status": NotionProperty("Status", "select", {
                "select": {
                    "options": [
                        {"name": "Pending", "color": "yellow"},
                        {"name": "Signed", "color": "green"},
                        {"name": "Viewed", "color": "blue"},
                        {"name": "Expired", "color": "red"}
                    ]
                }
            }),
            "Timestamp": NotionProperty("Timestamp", "created_time")
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Documents"}}],
            "description": [{"type": "text", "text": {"content": "Document tracking and status management"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def create_daily_brief_database(self) -> Dict[str, Any]:
        """Create Daily Brief database schema"""
        properties = {
            "Date": NotionProperty("Date", "date"),
            "Summary": NotionProperty("Summary", "rich_text"),
            "Waiting On": NotionProperty("Waiting On", "relation", {
                "relation": {
                    "database_id": "TASKS_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Due Today": NotionProperty("Due Today", "relation", {
                "relation": {
                    "database_id": "TASKS_DB_ID",
                    "type": "single_property",
                    "single_property": {}
                }
            }),
            "Drafts": NotionProperty("Drafts", "rich_text")
        }
        
        return {
            "title": [{"type": "text", "text": {"content": "Daily Brief"}}],
            "description": [{"type": "text", "text": {"content": "Daily action items and communication drafts"}}],
            "properties": {name: prop.to_notion_format() for name, prop in properties.items()}
        }
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all database schemas"""
        return {
            "people": self.create_people_database(),
            "companies": self.create_companies_database(),
            "threads": self.create_threads_database(),
            "interactions": self.create_interactions_database(),
            "tasks": self.create_tasks_database(),
            "social_activity": self.create_social_activity_database(),
            "documents": self.create_documents_database(),
            "daily_brief": self.create_daily_brief_database()
        }
    
    def update_relation_ids(self, schemas: Dict[str, Dict[str, Any]], 
                           db_ids: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Update relation database IDs in schemas"""
        updated_schemas = {}
        
        for db_name, schema in schemas.items():
            updated_schema = json.loads(json.dumps(schema))  # Deep copy
            
            # Update relation properties
            for prop_name, prop_config in updated_schema.get("properties", {}).items():
                if prop_config.get("type") == "relation":
                    relation_db_name = prop_config["relation"]["database_id"]
                    if relation_db_name in db_ids:
                        prop_config["relation"]["database_id"] = db_ids[relation_db_name]
            
            updated_schemas[db_name] = updated_schema
        
        return updated_schemas

# Example usage
if __name__ == "__main__":
    builder = NotionSchemaBuilder()
    schemas = builder.get_all_schemas()
    
    print("Notion Schema Builder - Ready!")
    print(f"Generated {len(schemas)} database schemas:")
    for name in schemas.keys():
        print(f"  - {name}")
    
    # Save schemas to file for reference
    with open("notion_schemas.json", "w") as f:
        json.dump(schemas, f, indent=2)
    
    print("\nSchemas saved to notion_schemas.json")
