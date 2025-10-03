#!/usr/bin/env python3
"""
Command Line Interface
Simple CLI for managing the user data integration system
"""

import argparse
import asyncio
import sys
import logging
from datetime import datetime

from config import Config
from main_integration_system import UserDataIntegrationSystem, SystemConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def init_workspace():
    """Initialize Notion workspace with all databases"""
    logger.info("Initializing Notion workspace...")
    
    # Validate configuration
    validation = Config.validate_config()
    missing_configs = [key for key, valid in validation.items() if not valid]
    
    if missing_configs:
        logger.error(f"Missing required configuration: {', '.join(missing_configs)}")
        logger.error("Please check your .env file and ensure all required API keys are set.")
        return False
    
    # Create system configuration
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
    
    # Create and initialize system
    system = UserDataIntegrationSystem(config)
    
    try:
        success = await system.initialize_workspace()
        if success:
            logger.info("✅ Workspace initialization completed successfully!")
            logger.info("All databases have been created in your Notion workspace.")
            return True
        else:
            logger.error("❌ Workspace initialization failed!")
            return False
    except Exception as e:
        logger.error(f"❌ Workspace initialization failed: {e}")
        return False

async def run_sync():
    """Run a one-time data synchronization"""
    logger.info("Running data synchronization...")
    
    # Validate configuration
    validation = Config.validate_config()
    missing_configs = [key for key, valid in validation.items() if not valid]
    
    if missing_configs:
        logger.error(f"Missing required configuration: {', '.join(missing_configs)}")
        return False
    
    # Create system configuration
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
    
    # Create system
    system = UserDataIntegrationSystem(config)
    
    try:
        # Set database IDs (assuming workspace is already initialized)
        # In a real implementation, these would be stored and retrieved
        system.db_ids = {
            "people": "placeholder_people_id",
            "companies": "placeholder_companies_id",
            "threads": "placeholder_threads_id",
            "interactions": "placeholder_interactions_id",
            "tasks": "placeholder_tasks_id",
            "social_activity": "placeholder_social_id",
            "documents": "placeholder_documents_id",
            "daily_brief": "placeholder_brief_id"
        }
        
        # Run sync
        sync_results = await system.full_sync()
        
        logger.info("✅ Data synchronization completed!")
        logger.info(f"Sync results: {sync_results}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data synchronization failed: {e}")
        return False

async def generate_brief():
    """Generate a daily brief"""
    logger.info("Generating daily brief...")
    
    # Validate configuration
    validation = Config.validate_config()
    missing_configs = [key for key, valid in validation.items() if not valid]
    
    if missing_configs:
        logger.error(f"Missing required configuration: {', '.join(missing_configs)}")
        return False
    
    # Create system configuration
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
    
    # Create system
    system = UserDataIntegrationSystem(config)
    
    try:
        # Set database IDs
        system.db_ids = {
            "people": "placeholder_people_id",
            "companies": "placeholder_companies_id",
            "threads": "placeholder_threads_id",
            "interactions": "placeholder_interactions_id",
            "tasks": "placeholder_tasks_id",
            "social_activity": "placeholder_social_id",
            "documents": "placeholder_documents_id",
            "daily_brief": "placeholder_brief_id"
        }
        
        # Generate brief
        await system.generate_daily_brief()
        
        logger.info("✅ Daily brief generated successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Daily brief generation failed: {e}")
        return False

async def start_system():
    """Start the full integration system"""
    logger.info("Starting User Data Integration System...")
    
    # Validate configuration
    validation = Config.validate_config()
    missing_configs = [key for key, valid in validation.items() if not valid]
    
    if missing_configs:
        logger.error(f"Missing required configuration: {', '.join(missing_configs)}")
        logger.error("Please check your .env file and ensure all required API keys are set.")
        return False
    
    # Create system configuration
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
        success = await system.start()
        if success:
            logger.info("✅ System started successfully!")
            logger.info("Press Ctrl+C to stop the system.")
            
            # Keep running
            while True:
                await asyncio.sleep(60)
        else:
            logger.error("❌ Failed to start system!")
            return False
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        return False
    finally:
        await system.stop()
        logger.info("System stopped")
    
    return True

def validate_config():
    """Validate system configuration"""
    logger.info("Validating system configuration...")
    
    validation = Config.validate_config()
    
    print("\n📋 Configuration Validation Results:")
    print("=" * 50)
    
    all_valid = True
    for key, is_valid in validation.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {key}")
        if not is_valid:
            all_valid = False
    
    print("=" * 50)
    
    if all_valid:
        print("✅ All required configuration is present!")
        return True
    else:
        print("❌ Some configuration is missing!")
        print("\nPlease create a .env file with the required values.")
        print("See config.py for the example .env file content.")
        return False

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="User Data Integration System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py init          # Initialize Notion workspace
  python cli.py sync          # Run one-time data sync
  python cli.py brief         # Generate daily brief
  python cli.py start         # Start full system
  python cli.py validate      # Validate configuration
        """
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'sync', 'brief', 'start', 'validate'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
    
    # Execute command
    try:
        if args.command == 'init':
            success = asyncio.run(init_workspace())
        elif args.command == 'sync':
            success = asyncio.run(run_sync())
        elif args.command == 'brief':
            success = asyncio.run(generate_brief())
        elif args.command == 'start':
            success = asyncio.run(start_system())
        elif args.command == 'validate':
            success = validate_config()
        else:
            logger.error(f"Unknown command: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

