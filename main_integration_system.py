#!/usr/bin/env python3
"""
Main Integration System
Orchestrates all data integrations and maintains the central Notion workspace
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import schedule
import time
from threading import Thread

from integration_implementation import EmailDeduplicationEngine, Contact, Event
from notion_schema import NotionSchemaBuilder
from integrations.gmail_integration import GmailIntegration
from integrations.calendar_integration import CalendarIntegration
from integrations.fathom_integration import FathomIntegration
from integrations.social_integration import SocialIntegration
from integrations.leaner_integration import LeanerIntegration
from integrations.notion_client import NotionClient
from daily_brief_generator import DailyBriefGenerator
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemConfig:
    """System configuration"""
    notion_token: str
    gmail_credentials: Dict[str, str]
    calendar_credentials: Dict[str, str]
    fathom_api_key: str
    linkedin_api_key: str
    x_api_key: str
    leaner_api_key: str
    attio_api_key: str
    timezone: str = "Europe/London"
    daily_brief_time: str = "08:30"
    sync_interval_minutes: int = 5

class UserDataIntegrationSystem:
    """Main system orchestrator"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.notion_client = NotionClient(config.notion_token)
        self.email_engine = EmailDeduplicationEngine()
        self.daily_brief_generator = DailyBriefGenerator(self.notion_client)
        
        # Initialize integrations
        self.gmail = GmailIntegration(config.gmail_credentials)
        self.calendar = CalendarIntegration(config.calendar_credentials)
        self.fathom = FathomIntegration(config.fathom_api_key)
        self.social = SocialIntegration(config.linkedin_api_key, config.x_api_key)
        self.leaner = LeanerIntegration(config.leaner_api_key)
        
        # Database IDs (will be populated after creation)
        self.db_ids = {}
        
        # System state
        self.is_running = False
        self.last_sync = None
        
    async def initialize_workspace(self) -> bool:
        """Initialize the Notion workspace with all required databases"""
        try:
            logger.info("Initializing Notion workspace...")
            
            # Create database schemas
            schema_builder = NotionSchemaBuilder()
            schemas = schema_builder.get_all_schemas()
            
            # Create databases in Notion
            created_dbs = {}
            for db_name, schema in schemas.items():
                logger.info(f"Creating database: {db_name}")
                db_id = await self.notion_client.create_database(schema)
                created_dbs[db_name] = db_id
                logger.info(f"Created {db_name} with ID: {db_id}")
            
            # Update relation IDs
            self.db_ids = created_dbs
            updated_schemas = schema_builder.update_relation_ids(schemas, created_dbs)
            
            # Update databases with correct relation IDs
            for db_name, schema in updated_schemas.items():
                await self.notion_client.update_database(created_dbs[db_name], schema)
            
            logger.info("Workspace initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace: {e}")
            return False
    
    async def sync_email_data(self) -> int:
        """Sync email data from Gmail"""
        try:
            logger.info("Syncing email data...")
            
            # Get recent emails
            emails = await self.gmail.get_recent_emails(hours=24)
            synced_count = 0
            
            for email in emails:
                # Process email through deduplication engine
                contact_id = self.email_engine.add_or_update_contact(
                    email['from_email'],
                    email['from_name'],
                    email.get('company', ''),
                    'professional'
                )
                
                # Create interaction record
                interaction_data = {
                    'type': 'Email In' if email['direction'] == 'inbound' else 'Email Out',
                    'timestamp': email['timestamp'],
                    'channel': 'Gmail',
                    'people': [contact_id],
                    'subject': email['subject'],
                    'snippet': email['snippet'],
                    'source_id': email['message_id']
                }
                
                # Add to Notion
                await self.notion_client.create_interaction(interaction_data)
                synced_count += 1
            
            logger.info(f"Synced {synced_count} emails")
            return synced_count
            
        except Exception as e:
            logger.error(f"Email sync failed: {e}")
            return 0
    
    async def sync_calendar_data(self) -> int:
        """Sync calendar data"""
        try:
            logger.info("Syncing calendar data...")
            
            # Get recent meetings
            meetings = await self.calendar.get_recent_meetings(hours=24)
            synced_count = 0
            
            for meeting in meetings:
                # Extract attendees
                attendee_contacts = []
                for attendee in meeting['attendees']:
                    contact_id = self.email_engine.add_or_update_contact(
                        attendee['email'],
                        attendee['name'],
                        attendee.get('company', ''),
                        'professional'
                    )
                    attendee_contacts.append(contact_id)
                
                # Create interaction record
                interaction_data = {
                    'type': 'Meeting',
                    'timestamp': meeting['start_time'],
                    'channel': 'Calendar',
                    'people': attendee_contacts,
                    'subject': meeting['title'],
                    'snippet': meeting.get('description', ''),
                    'source_id': meeting['event_id']
                }
                
                # Add to Notion
                await self.notion_client.create_interaction(interaction_data)
                synced_count += 1
            
            logger.info(f"Synced {synced_count} meetings")
            return synced_count
            
        except Exception as e:
            logger.error(f"Calendar sync failed: {e}")
            return 0
    
    async def sync_fathom_data(self) -> int:
        """Sync Fathom meeting summaries"""
        try:
            logger.info("Syncing Fathom data...")
            
            # Get recent recordings
            recordings = await self.fathom.get_recent_recordings(hours=24)
            synced_count = 0
            
            for recording in recordings:
                # Extract participants
                participant_contacts = []
                for participant in recording['participants']:
                    contact_id = self.email_engine.add_or_update_contact(
                        participant['email'],
                        participant['name'],
                        participant.get('company', ''),
                        'professional'
                    )
                    participant_contacts.append(contact_id)
                
                # Create interaction record
                interaction_data = {
                    'type': 'Fathom Summary',
                    'timestamp': recording['created_at'],
                    'channel': 'Fathom',
                    'people': participant_contacts,
                    'subject': recording['title'],
                    'snippet': recording['summary'],
                    'source_id': recording['recording_id']
                }
                
                # Add to Notion
                await self.notion_client.create_interaction(interaction_data)
                synced_count += 1
            
            logger.info(f"Synced {synced_count} Fathom recordings")
            return synced_count
            
        except Exception as e:
            logger.error(f"Fathom sync failed: {e}")
            return 0
    
    async def sync_social_data(self) -> int:
        """Sync social media activity"""
        try:
            logger.info("Syncing social media data...")
            
            # Get recent social activity
            activity = await self.social.get_recent_activity(hours=24)
            synced_count = 0
            
            for item in activity:
                # Find or create contact
                contact_id = self.email_engine.add_or_update_contact(
                    item.get('email', ''),
                    item['name'],
                    item.get('company', ''),
                    'social'
                )
                
                # Create social activity record
                social_data = {
                    'network': item['network'],
                    'activity_type': item['type'],
                    'timestamp': item['timestamp'],
                    'url': item['url'],
                    'person': contact_id,
                    'summary': item.get('content', ''),
                    'action_suggestion': item.get('action_suggestion', '')
                }
                
                # Add to Notion
                await self.notion_client.create_social_activity(social_data)
                synced_count += 1
            
            logger.info(f"Synced {synced_count} social activities")
            return synced_count
            
        except Exception as e:
            logger.error(f"Social sync failed: {e}")
            return 0
    
    async def sync_leaner_tasks(self) -> int:
        """Sync tasks with Leaner"""
        try:
            logger.info("Syncing Leaner tasks...")
            
            # Get tasks from Leaner
            leaner_tasks = await self.leaner.get_tasks()
            
            # Get existing tasks from Notion
            notion_tasks = await self.notion_client.get_tasks()
            
            # Sync tasks
            synced_count = 0
            for task in leaner_tasks:
                # Check if task exists in Notion
                existing_task = next(
                    (t for t in notion_tasks if t.get('leaner_id') == task['id']),
                    None
                )
                
                if existing_task:
                    # Update existing task
                    await self.notion_client.update_task(
                        existing_task['id'],
                        {
                            'status': task['status'],
                            'due': task.get('due_date'),
                            'title': task['title']
                        }
                    )
                else:
                    # Create new task
                    task_data = {
                        'title': task['title'],
                        'status': task['status'],
                        'due': task.get('due_date'),
                        'priority': task.get('priority', 'Medium'),
                        'leaner_id': task['id']
                    }
                    await self.notion_client.create_task(task_data)
                
                synced_count += 1
            
            logger.info(f"Synced {synced_count} Leaner tasks")
            return synced_count
            
        except Exception as e:
            logger.error(f"Leaner sync failed: {e}")
            return 0
    
    async def full_sync(self) -> Dict[str, int]:
        """Perform full data synchronization"""
        logger.info("Starting full data sync...")
        
        sync_results = {
            'emails': await self.sync_email_data(),
            'meetings': await self.sync_calendar_data(),
            'fathom': await self.sync_fathom_data(),
            'social': await self.sync_social_data(),
            'tasks': await self.sync_leaner_tasks()
        }
        
        self.last_sync = datetime.now()
        
        total_synced = sum(sync_results.values())
        logger.info(f"Full sync complete. Total items synced: {total_synced}")
        
        return sync_results
    
    async def generate_daily_brief(self):
        """Generate daily brief"""
        try:
            logger.info("Generating daily brief...")
            await self.daily_brief_generator.generate_brief()
            logger.info("Daily brief generated successfully")
        except Exception as e:
            logger.error(f"Daily brief generation failed: {e}")
    
    def setup_scheduler(self):
        """Setup scheduled tasks"""
        # Schedule daily brief generation
        schedule.every().day.at(self.config.daily_brief_time).do(
            lambda: asyncio.create_task(self.generate_daily_brief())
        )
        
        # Schedule regular sync
        schedule.every(self.config.sync_interval_minutes).minutes.do(
            lambda: asyncio.create_task(self.full_sync())
        )
    
    async def start(self):
        """Start the integration system"""
        logger.info("Starting User Data Integration System...")
        
        # Initialize workspace
        if not await self.initialize_workspace():
            logger.error("Failed to initialize workspace")
            return False
        
        # Setup scheduler
        self.setup_scheduler()
        
        # Perform initial sync
        await self.full_sync()
        
        # Start scheduler in background thread
        self.is_running = True
        scheduler_thread = Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("System started successfully!")
        return True
    
    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def stop(self):
        """Stop the integration system"""
        logger.info("Stopping User Data Integration System...")
        self.is_running = False
        logger.info("System stopped")

# Example usage
async def main():
    """Main entry point"""
    # Load configuration from environment
    config = SystemConfig(
        notion_token=Config.NOTION_TOKEN,
        gmail_credentials=Config.get_gmail_credentials(),
        calendar_credentials=Config.get_calendar_credentials(),
        fathom_api_key=Config.FATHOM_API_KEY,
        linkedin_api_key=Config.LINKEDIN_API_KEY,
        x_api_key=Config.X_API_KEY,
        leaner_api_key=Config.LEANER_API_KEY,
        attio_api_key=Config.ATTIO_API_KEY,
        timezone=Config.TIMEZONE,
        daily_brief_time=Config.DAILY_BRIEF_TIME,
        sync_interval_minutes=Config.SYNC_INTERVAL_MINUTES
    )
    
    # Create and start system
    system = UserDataIntegrationSystem(config)
    
    try:
        await system.start()
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())
