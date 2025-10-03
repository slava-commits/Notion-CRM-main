#!/usr/bin/env python3
"""
Add Interactions to Notion Timeline Database
This script adds the gathered email interactions to the Interactions Timeline database
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

# Partner data with their Notion page IDs (we'll need to get these)
PARTNERS = [
    {
        'name': 'Ryan',
        'email': 'ryan@k50ventures.com',
        'company': 'K50 Ventures',
        'notion_page_id': None  # Will be filled when we find the page
    },
    {
        'name': 'Mykyta Fediushyn',
        'email': 'mykyta.fediushyn@flyerone.vc',
        'company': 'Flyer One Ventures',
        'notion_page_id': None
    },
    {
        'name': 'Wayne',
        'email': 'wayne@banktechventures.com',
        'company': 'BankTech Ventures',
        'notion_page_id': None
    },
    {
        'name': 'Denis',
        'email': 'denis@concentric.vc',
        'company': 'Concentric VC',
        'notion_page_id': None
    }
]

async def gather_email_interactions():
    """Gather email interactions for all partners"""
    gmail_creds = Config.get_gmail_credentials()
    
    if not all(gmail_creds.values()):
        logger.error("Gmail credentials not available")
        return []
    
    all_interactions = []
    
    async with GmailIntegration(gmail_creds) as gmail:
        for partner in PARTNERS:
            logger.info(f"Gathering emails for {partner['name']} ({partner['email']})")
            
            try:
                emails = await gmail.get_emails_from_sender(partner['email'], max_results=10)
                logger.info(f"Found {len(emails)} emails from {partner['name']}")
                
                for email in emails:
                    interaction = {
                        'partner': partner,
                        'title': email['subject'] or 'Email Interaction',
                        'type': 'Email In' if email['direction'] == 'inbound' else 'Email Out',
                        'source': 'Gmail',
                        'date': email['timestamp'],
                        'subject': email['subject'],
                        'content': email['snippet'],
                        'direction': 'Inbound' if email['direction'] == 'inbound' else 'Outbound',
                        'priority': 'High' if 'urgent' in email['subject'].lower() else 'Medium',
                        'follow_up_required': 'Follow Up' in partner.get('tags', ''),
                        'notes': f"Email from {partner['company']} - {email['snippet'][:100]}...",
                        'tags': '["Important", "Email"]',
                        'source_id': email['message_id']
                    }
                    all_interactions.append(interaction)
                    
            except Exception as e:
                logger.error(f"Error gathering emails for {partner['name']}: {e}")
    
    return all_interactions

def print_interaction_summary(interactions):
    """Print summary of gathered interactions"""
    print("\n" + "="*60)
    print("INTERACTIONS TO ADD TO NOTION TIMELINE")
    print("="*60)
    
    if not interactions:
        print("No interactions found")
        return
    
    # Group by partner
    by_partner = {}
    for interaction in interactions:
        partner_name = interaction['partner']['name']
        if partner_name not in by_partner:
            by_partner[partner_name] = []
        by_partner[partner_name].append(interaction)
    
    for partner_name, partner_interactions in by_partner.items():
        print(f"\n{partner_name} ({len(partner_interactions)} interactions):")
        for i, interaction in enumerate(partner_interactions[:3], 1):  # Show first 3
            print(f"  {i}. {interaction['type']}: {interaction['title']}")
            print(f"     Date: {interaction['date']}")
            print(f"     Direction: {interaction['direction']}")
            print(f"     Content: {interaction['content'][:80]}...")
            print(f"     Priority: {interaction['priority']}")
            print()

async def main():
    """Main function"""
    print("🚀 Adding Interactions to Notion Timeline Database")
    print("="*60)
    
    # Gather interactions
    interactions = await gather_email_interactions()
    
    # Print summary
    print_interaction_summary(interactions)
    
    print(f"\n✅ Found {len(interactions)} total interactions to add")
    print("\nNext steps:")
    print("1. Get the Notion page IDs for each partner")
    print("2. Add interactions to the Interactions Timeline database")
    print("3. Link each interaction to the correct partner")
    print("4. Create timeline view showing all interactions per partner")

if __name__ == "__main__":
    asyncio.run(main())
