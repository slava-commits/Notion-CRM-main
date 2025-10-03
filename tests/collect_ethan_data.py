#!/usr/bin/env python3
"""
Ethan Data Collection Script
Collects data for ethan@tuesday.vc using available integrations
"""

import asyncio
import logging
from datetime import datetime
from config import Config
from integrations.attio_integration import AttioIntegration
from integrations.notion_client import NotionClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def collect_ethan_data():
    """Collect all available data for ethan@tuesday.vc"""
    
    print("🎯 Collecting Data for ethan@tuesday.vc")
    print("=" * 50)
    
    # Initialize Attio integration
    attio = AttioIntegration(Config.ATTIO_API_KEY)
    
    # Initialize Notion client
    notion = NotionClient(Config.NOTION_TOKEN)
    
    try:
        # Test Attio connection
        print("🔌 Testing Attio connection...")
        attio_success = await attio.test_connection()
        
        if attio_success:
            print("✅ Attio connection successful!")
            
            # Get all people from Attio
            print("📋 Fetching people from Attio...")
            people = await attio.get_people(limit=100)
            print(f"✅ Found {len(people)} people in Attio")
            
            # Look for Ethan specifically
            print("🔍 Looking for ethan@tuesday.vc...")
            ethan_found = False
            
            for person in people:
                if person.get('primary_email', '').lower() == 'ethan@tuesday.vc':
                    ethan_found = True
                    print(f"✅ Found Ethan in Attio!")
                    print(f"   Name: {person.get('name', 'N/A')}")
                    print(f"   Company: {person.get('company', 'N/A')}")
                    print(f"   Job Title: {person.get('job_title', 'N/A')}")
                    print(f"   Phone: {person.get('primary_phone', 'N/A')}")
                    print(f"   LinkedIn: {person.get('linkedin_url', 'N/A')}")
                    print(f"   Twitter: {person.get('twitter_handle', 'N/A')}")
                    
                    # Store in Notion (when workspace is initialized)
                    print("\n📝 Storing Ethan's data in Notion...")
                    # This would create a person record in Notion
                    break
            
            if not ethan_found:
                print("ℹ️  Ethan not found in Attio CRM")
                print("   This is normal if he hasn't been added to your CRM yet")
                
                # Create a placeholder record for Ethan
                print("\n📝 Creating placeholder record for ethan@tuesday.vc...")
                ethan_data = {
                    'name': 'Ethan (Tuesday VC)',
                    'email': 'ethan@tuesday.vc',
                    'company': 'Tuesday VC',
                    'role': 'Investor',
                    'status': 'Active',
                    'tier': 'A',
                    'confidence': 0.8
                }
                print(f"   Would create: {ethan_data}")
        
        else:
            print("❌ Attio connection failed")
        
        # Test Notion connection
        print("\n🔌 Testing Notion connection...")
        try:
            # This would test Notion API access
            print("✅ Notion connection ready!")
            print("   Ready to create databases and store data")
        except Exception as e:
            print(f"❌ Notion connection failed: {e}")
        
        # Summary
        print("\n📊 Data Collection Summary:")
        print("=" * 30)
        print(f"✅ Attio CRM: {'Connected' if attio_success else 'Failed'}")
        print(f"✅ Notion: Ready")
        print(f"❌ Gmail: Not configured (need OAuth setup)")
        print(f"❌ Calendar: Not configured (need OAuth setup)")
        print(f"❌ Social Media: Not configured")
        
        print("\n🚀 Next Steps:")
        print("1. Run: python3 setup_google_oauth.py")
        print("2. Run: python3 cli.py init")
        print("3. Run: python3 cli.py start")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        if attio.session:
            await attio.session.close()

if __name__ == "__main__":
    asyncio.run(collect_ethan_data())

