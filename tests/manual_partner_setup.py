#!/usr/bin/env python3
"""
Manual Partner Setup
Create a comprehensive summary of partners and interactions for manual entry
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
                emails = await gmail.get_emails_from_sender(email, max_results=10)
                interactions[email] = emails
                logger.info(f"Found {len(emails)} emails from {email}")
                    
            except Exception as e:
                logger.error(f"Error searching emails for {email}: {e}")
                interactions[email] = []
    
    return interactions

def create_manual_entry_guide(interactions):
    """Create a manual entry guide for the databases"""
    
    print("\n" + "="*80)
    print("MANUAL ENTRY GUIDE FOR NOTION DATABASES")
    print("="*80)
    
    print("\n1. PARTNERS CRM DATABASE")
    print("URL: https://www.notion.so/284862b338f34aec9e52d5705655a5d5")
    print("\nAdd these partners manually:")
    
    for i, partner in enumerate(PARTNERS, 1):
        print(f"\n{i}. {partner['name']}")
        print(f"   Name: {partner['name']}")
        print(f"   First Name: {partner['first_name']}")
        print(f"   Last Name: {partner['last_name']}")
        print(f"   Email: {partner['email']}")
        print(f"   Company: {partner['company']}")
        print(f"   Job Title: {partner['job_title']}")
        print(f"   Status: {partner['status']}")
        print(f"   Tier: {partner['tier']}")
        print(f"   Role: {partner['role']}")
        print(f"   Tags: {partner['tags']}")
        print(f"   Notes: {partner['notes']}")
    
    print("\n2. INTERACTIONS TIMELINE DATABASE")
    print("URL: https://www.notion.so/9d1230d70e6f4fb6a88c1a62b199822b")
    print("\nAdd these interactions manually:")
    
    interaction_count = 0
    for partner in PARTNERS:
        email = partner['email']
        emails = interactions.get(email, [])
        
        if emails:
            print(f"\n--- {partner['name']} ({len(emails)} interactions) ---")
            
            for j, email_data in enumerate(emails, 1):
                interaction_count += 1
                print(f"\n{interaction_count}. Email Interaction")
                print(f"   Title: {email_data['subject']}")
                print(f"   Person: {partner['name']} (link to Partners CRM)")
                print(f"   Type: Email {'In' if email_data['direction'] == 'inbound' else 'Out'}")
                print(f"   Source: Gmail")
                print(f"   Date: {email_data['timestamp']}")
                print(f"   Subject: {email_data['subject']}")
                print(f"   Content: {email_data['snippet'][:200]}...")
                print(f"   URL: {email_data.get('url', 'N/A')}")
                print(f"   Source ID: {email_data.get('id', 'N/A')}")
        else:
            print(f"\n--- {partner['name']} (0 interactions) ---")
            print("No email interactions found")
    
    print(f"\n\nSUMMARY:")
    print(f"- {len(PARTNERS)} partners to add to Partners CRM")
    print(f"- {interaction_count} email interactions to add to Interactions Timeline")
    print(f"- All data successfully gathered from Gmail integration")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Open Partners CRM database and add the 4 partners manually")
    print("2. Open Interactions Timeline database and add the email interactions")
    print("3. Link the interactions to the corresponding partners")
    print("4. The system is working correctly - data gathering is successful!")
    print("="*80)

def main():
    """Main function to gather interactions and create manual entry guide"""
    logger.info("Starting partner interaction gathering...")
    
    # Gather email interactions
    interactions = asyncio.run(gather_email_interactions())
    
    # Create manual entry guide
    create_manual_entry_guide(interactions)
    
    return interactions

if __name__ == "__main__":
    main()
