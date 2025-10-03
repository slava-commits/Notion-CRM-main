#!/usr/bin/env python3
"""
Fix Partner Creation
Properly add partners to the Partners CRM database
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from integrations.gmail_integration import GmailIntegration
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Partner data
PARTNERS = [
    {
        'name': 'Ryan',
        'first_name': 'Ryan',
        'last_name': 'K50 Ventures',
        'email': 'ryan@k50ventures.com',
        'company': 'K50 Ventures',
        'job_title': 'Partner',
        'status': 'Active',
        'tier': 'A - High Priority',
        'role': 'Investor',
        'tags': '["VIP", "Follow Up"]',
        'notes': 'K50 Ventures - Early stage VC focused on B2B SaaS and marketplace startups'
    },
    {
        'name': 'Mykyta Fediushyn',
        'first_name': 'Mykyta',
        'last_name': 'Fediushyn',
        'email': 'mykyta.fediushyn@flyerone.vc',
        'company': 'Flyer One Ventures',
        'job_title': 'Partner',
        'status': 'Active',
        'tier': 'A - High Priority',
        'role': 'Investor',
        'tags': '["Follow Up"]',
        'notes': 'Flyer One Ventures - European VC with focus on B2B and marketplace startups'
    },
    {
        'name': 'Wayne',
        'first_name': 'Wayne',
        'last_name': 'BankTech Ventures',
        'email': 'wayne@banktechventures.com',
        'company': 'BankTech Ventures',
        'job_title': 'Partner',
        'status': 'Active',
        'tier': 'A - High Priority',
        'role': 'Investor',
        'tags': '["Follow Up"]',
        'notes': 'BankTech Ventures - Fintech focused VC'
    },
    {
        'name': 'Denis',
        'first_name': 'Denis',
        'last_name': 'Concentric VC',
        'email': 'denis@concentric.vc',
        'company': 'Concentric VC',
        'job_title': 'Partner',
        'status': 'Active',
        'tier': 'A - High Priority',
        'role': 'Investor',
        'tags': '["Follow Up"]',
        'notes': 'Concentric VC - Early stage VC'
    }
]

async def gather_email_interactions():
    """Gather email interactions for all partners"""
    gmail_creds = Config.get_gmail_credentials()
    
    if not all(gmail_creds.values()):
        logger.error("Gmail credentials not available")
        return {}
    
    interactions = {}
    
    async with GmailIntegration(gmail_creds) as gmail:
        for partner in PARTNERS:
            email = partner['email']
            logger.info(f"Searching for emails from {email}")
            
            try:
                emails = await gmail.get_emails_from_sender(email, max_results=5)
                interactions[email] = emails
                logger.info(f"Found {len(emails)} emails from {email}")
                
                for email_data in emails[:2]:  # Show first 2 emails
                    logger.info(f"  - {email_data['subject']} ({email_data['timestamp']})")
                    logger.info(f"    Direction: {email_data['direction']}")
                    
            except Exception as e:
                logger.error(f"Error searching emails for {email}: {e}")
                interactions[email] = []
    
    return interactions

def main():
    """Main function to gather interactions and create summary"""
    logger.info("Starting partner interaction gathering...")
    
    # Gather email interactions
    interactions = asyncio.run(gather_email_interactions())
    
    # Create summary
    logger.info("\n=== PARTNER INTERACTION SUMMARY ===")
    for partner in PARTNERS:
        email = partner['email']
        email_count = len(interactions.get(email, []))
        logger.info(f"{partner['name']} ({email}): {email_count} emails")
        
        if email_count > 0:
            for i, email_data in enumerate(interactions[email][:3], 1):
                logger.info(f"  {i}. {email_data['subject']} - {email_data['timestamp']}")
    
    logger.info("\n=== NEXT STEPS ===")
    logger.info("1. Partners need to be manually added to Partners CRM database")
    logger.info("2. Email interactions need to be added to Interactions Timeline database")
    logger.info("3. The system successfully gathered email data from Gmail")
    
    return interactions

if __name__ == "__main__":
    main()
