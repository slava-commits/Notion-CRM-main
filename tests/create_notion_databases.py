#!/usr/bin/env python3
"""
Create Notion Databases
Creates all required databases in your Notion workspace
"""

import asyncio
import aiohttp
import json
from config import Config

async def create_notion_databases():
    """Create all required databases in Notion"""
    
    print("🏗️ Creating Notion Databases")
    print("=" * 40)
    
    # Notion API client
    headers = {
        "Authorization": f"Bearer {Config.NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Database schemas (simplified)
    databases = {
        "People": {
            "title": [{"type": "text", "text": {"content": "People"}}],
            "description": [{"type": "text", "text": {"content": "Central database of all contacts and relationships"}}],
            "properties": {
                "Name": {"title": {}},
                "Primary Email": {"email": {}},
                "LinkedIn URL": {"url": {}},
                "X Handle": {"rich_text": {}},
                "Role": {
                    "select": {
                        "options": [
                            {"name": "Founder", "color": "blue"},
                            {"name": "Investor", "color": "green"},
                            {"name": "Partner", "color": "purple"},
                            {"name": "Client", "color": "orange"}
                        ]
                    }
                },
                "Company": {"rich_text": {}},
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
                            {"name": "A", "color": "green"},
                            {"name": "B", "color": "yellow"},
                            {"name": "C", "color": "red"}
                        ]
                    }
                }
            }
        },
        "Companies": {
            "title": [{"type": "text", "text": {"content": "Companies"}}],
            "description": [{"type": "text", "text": {"content": "Company information and relationships"}}],
            "properties": {
                "Name": {"title": {}},
                "Website": {"url": {}},
                "Type": {
                    "select": {
                        "options": [
                            {"name": "Investor", "color": "green"},
                            {"name": "Partner", "color": "blue"},
                            {"name": "Client", "color": "orange"},
                            {"name": "Provider", "color": "purple"}
                        ]
                    }
                }
            }
        },
        "Interactions": {
            "title": [{"type": "text", "text": {"content": "Interactions"}}],
            "description": [{"type": "text", "text": {"content": "All interactions and touchpoints"}}],
            "properties": {
                "Type": {
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
                },
                "Channel": {
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
                },
                "Subject/Title": {"title": {}},
                "Snippet/Link": {"url": {}},
                "Source Id": {"rich_text": {}}
            }
        },
        "Tasks": {
            "title": [{"type": "text", "text": {"content": "Tasks"}}],
            "description": [{"type": "text", "text": {"content": "Task management with Leaner synchronization"}}],
            "properties": {
                "Title": {"title": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Todo", "color": "gray"},
                            {"name": "Doing", "color": "blue"},
                            {"name": "Blocked", "color": "red"},
                            {"name": "Done", "color": "green"}
                        ]
                    }
                },
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "green"}
                        ]
                    }
                },
                "Due": {"date": {}},
                "Reason": {
                    "select": {
                        "options": [
                            {"name": "Waiting on reply", "color": "yellow"},
                            {"name": "Social touch", "color": "blue"},
                            {"name": "Next step", "color": "green"},
                            {"name": "Doc", "color": "purple"}
                        ]
                    }
                }
            }
        }
    }
    
    created_dbs = {}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for db_name, schema in databases.items():
            try:
                print(f"📝 Creating database: {db_name}")
                
                # Create database
                async with session.post("https://api.notion.com/v1/databases", json=schema) as response:
                    if response.status == 200:
                        result = await response.json()
                        db_id = result["id"]
                        created_dbs[db_name] = db_id
                        print(f"✅ Created {db_name}: {db_id}")
                    else:
                        error = await response.json()
                        print(f"❌ Failed to create {db_name}: {error}")
                        
            except Exception as e:
                print(f"❌ Error creating {db_name}: {e}")
    
    print(f"\n🎉 Database creation complete!")
    print(f"Created {len(created_dbs)} databases:")
    for name, db_id in created_dbs.items():
        print(f"  - {name}: {db_id}")
    
    return created_dbs

if __name__ == "__main__":
    asyncio.run(create_notion_databases())

