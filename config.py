#!/usr/bin/env python3
"""
Configuration Management
Handles environment variables and system configuration
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """System configuration management"""
    
    # Notion Configuration
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    
    # Gmail Configuration
    GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
    GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
    GMAIL_REFRESH_TOKEN = os.getenv('GMAIL_REFRESH_TOKEN')
    
    # Google Calendar Configuration
    CALENDAR_CLIENT_ID = os.getenv('CALENDAR_CLIENT_ID')
    CALENDAR_CLIENT_SECRET = os.getenv('CALENDAR_CLIENT_SECRET')
    CALENDAR_REFRESH_TOKEN = os.getenv('CALENDAR_REFRESH_TOKEN')
    
    # Fathom Configuration
    FATHOM_API_KEY = os.getenv('FATHOM_API_KEY')
    
    # Social Media Configuration
    LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY')
    X_API_KEY = os.getenv('X_API_KEY')
    
    # Leaner Configuration
    LEANER_API_KEY = os.getenv('LEANER_API_KEY')
    
    # ATTIO Configuration
    ATTIO_API_KEY = os.getenv('ATTIO_API_KEY')
    
    # AI Service Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # System Configuration
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/London')
    DAILY_BRIEF_TIME = os.getenv('DAILY_BRIEF_TIME', '08:30')
    SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', '5'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'integration_system.log')
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate that all required configuration is present"""
        required_configs = {
            'NOTION_TOKEN': cls.NOTION_TOKEN,
            'ATTIO_API_KEY': cls.ATTIO_API_KEY,
            'GMAIL_CLIENT_ID': cls.GMAIL_CLIENT_ID,
            'GMAIL_CLIENT_SECRET': cls.GMAIL_CLIENT_SECRET,
            'GMAIL_REFRESH_TOKEN': cls.GMAIL_REFRESH_TOKEN,
            'CALENDAR_CLIENT_ID': cls.CALENDAR_CLIENT_ID,
            'CALENDAR_CLIENT_SECRET': cls.CALENDAR_CLIENT_SECRET,
            'CALENDAR_REFRESH_TOKEN': cls.CALENDAR_REFRESH_TOKEN,
            'FATHOM_API_KEY': cls.FATHOM_API_KEY,
            'LINKEDIN_API_KEY': cls.LINKEDIN_API_KEY,
            'X_API_KEY': cls.X_API_KEY,
            'LEANER_API_KEY': cls.LEANER_API_KEY
        }
        
        validation_results = {}
        for key, value in required_configs.items():
            validation_results[key] = value is not None and value.strip() != ''
        
        return validation_results
    
    @classmethod
    def get_gmail_credentials(cls) -> Dict[str, str]:
        """Get Gmail credentials"""
        return {
            'client_id': cls.GMAIL_CLIENT_ID,
            'client_secret': cls.GMAIL_CLIENT_SECRET,
            'refresh_token': cls.GMAIL_REFRESH_TOKEN
        }
    
    @classmethod
    def get_calendar_credentials(cls) -> Dict[str, str]:
        """Get Calendar credentials"""
        return {
            'client_id': cls.CALENDAR_CLIENT_ID,
            'client_secret': cls.CALENDAR_CLIENT_SECRET,
            'refresh_token': cls.CALENDAR_REFRESH_TOKEN
        }
    
    @classmethod
    def get_ai_config(cls) -> Dict[str, Optional[str]]:
        """Get AI service configuration"""
        return {
            'openai_api_key': cls.OPENAI_API_KEY,
            'anthropic_api_key': cls.ANTHROPIC_API_KEY
        }

# Example environment file content
ENV_EXAMPLE = """
# Copy this to .env and fill in your actual values

# Notion Configuration
NOTION_TOKEN=your_notion_integration_token_here

# Gmail Configuration
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token

# Google Calendar Configuration
CALENDAR_CLIENT_ID=your_calendar_client_id
CALENDAR_CLIENT_SECRET=your_calendar_client_secret
CALENDAR_REFRESH_TOKEN=your_calendar_refresh_token

# Fathom Configuration
FATHOM_API_KEY=your_fathom_api_key

# Social Media Configuration
LINKEDIN_API_KEY=your_linkedin_api_key
X_API_KEY=your_x_api_key

# Leaner Configuration
LEANER_API_KEY=your_leaner_api_key

# ATTIO Configuration (for identity resolution)
ATTIO_API_KEY=your_attio_api_key

# AI Service Configuration (optional)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# System Configuration
TIMEZONE=Europe/London
DAILY_BRIEF_TIME=08:30
SYNC_INTERVAL_MINUTES=5

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=integration_system.log
"""

if __name__ == "__main__":
    print("Configuration Management - Ready!")
    print("\nRequired environment variables:")
    validation = Config.validate_config()
    for key, is_valid in validation.items():
        status = "✓" if is_valid else "✗"
        print(f"  {status} {key}")
    
    if not all(validation.values()):
        print(f"\nMissing configuration detected!")
        print("Please create a .env file with the required values.")
        print("\nExample .env file content:")
        print(ENV_EXAMPLE)
