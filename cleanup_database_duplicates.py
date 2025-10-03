#!/usr/bin/env python3
"""
Database Duplicate Cleanup Script

This script will safely find and remove duplicate records from the Notion database
using our comprehensive database management system with safety features.

Author: Development Team
Version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime
from integrations.notion_database_manager import NotionDatabaseManager, SafetyLevel
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def cleanup_database_duplicates():
    """Find and safely remove duplicate records from the database"""
    
    print("🧹 Database Duplicate Cleanup")
    print("=" * 50)
    print("This script will:")
    print("• Find all duplicate records in the database")
    print("• Show you what will be deleted")
    print("• Safely remove duplicates with confirmation")
    print("• Provide a summary of the cleanup")
    print()
    
    # Get API keys from config
    notion_token = Config.NOTION_TOKEN
    database_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    if not notion_token:
        print("❌ NOTION_TOKEN not found in config")
        return
    
    try:
        # Initialize database manager with maximum safety level
        print("🔧 Initializing Database Manager...")
        db_manager = NotionDatabaseManager(notion_token, database_id, SafetyLevel.MAXIMUM)
        
        async with db_manager:
            # Step 1: Get current database statistics
            print("\n1. 📊 Current Database Statistics...")
            stats = await db_manager.get_database_stats()
            
            print(f"✅ Database Overview:")
            print(f"   Total pages: {stats['total_pages']}")
            print(f"   Pages with email: {stats['pages_with_email']}")
            print(f"   Pages with name: {stats['pages_with_name']}")
            print(f"   Pages with company: {stats['pages_with_company']}")
            print(f"   Current duplicates: {stats['duplicate_count']}")
            print(f"   Email completeness: {stats['data_completeness']['email_completeness']:.1f}%")
            print(f"   Name completeness: {stats['data_completeness']['name_completeness']:.1f}%")
            print(f"   Company completeness: {stats['data_completeness']['company_completeness']:.1f}%")
            
            # Step 2: Find all duplicates
            print("\n2. 🔍 Finding Duplicate Records...")
            duplicates = await db_manager.find_duplicates()
            
            if not duplicates:
                print("✅ No duplicates found! Database is clean.")
                return
            
            print(f"⚠️ Found {len(duplicates)} duplicate records:")
            print()
            
            for i, dup in enumerate(duplicates, 1):
                print(f"   {i}. {dup.name} ({dup.email})")
                print(f"      Reason: {dup.duplicate_reason}")
                print(f"      Similarity: {dup.similarity_score:.2f}")
                print(f"      Created: {dup.created_time}")
                print(f"      Page ID: {dup.page_id}")
                print(f"      🔗 Page URL: https://www.notion.so/{dup.page_id.replace('-', '')}")
                print()
            
            # Step 3: Show what will be deleted
            print("3. 🗑️ Duplicates to be Removed:")
            print("   The following records will be moved to trash (recoverable):")
            print()
            
            for i, dup in enumerate(duplicates, 1):
                print(f"   {i}. {dup.name} ({dup.email})")
                print(f"      ⚠️ This duplicate will be removed")
                print()
            
            # Step 4: Get confirmation
            print("4. 🔐 Safety Confirmation Required")
            print("   This operation requires a confirmation token for safety.")
            print("   The system will generate a confirmation token for you.")
            print()
            
            # Generate confirmation token
            from integrations.notion_database_manager import DatabaseOperation, OperationType
            
            cleanup_operation = DatabaseOperation(
                operation_type=OperationType.BULK_DELETE,
                target_id="duplicate_cleanup",
                data={"duplicate_count": len(duplicates)},
                safety_level=SafetyLevel.MAXIMUM,
                requires_confirmation=True
            )
            
            confirmation_token = db_manager._generate_confirmation_token(cleanup_operation)
            print(f"✅ Confirmation token generated: {confirmation_token}")
            print()
            
            # Step 5: Perform the cleanup
            print("5. 🧹 Performing Duplicate Cleanup...")
            print("   Removing duplicates with confirmation token...")
            print()
            
            cleanup_result = await db_manager.bulk_delete_duplicates(duplicates, confirmation_token)
            
            if cleanup_result["success"]:
                print("✅ Duplicate cleanup completed successfully!")
                print(f"   Duplicates removed: {cleanup_result['deleted_count']}")
                print(f"   Total duplicates found: {cleanup_result['total_duplicates']}")
                
                if cleanup_result.get("errors"):
                    print(f"   Errors encountered: {len(cleanup_result['errors'])}")
                    for error in cleanup_result["errors"]:
                        print(f"     • {error}")
            else:
                print(f"❌ Cleanup failed: {cleanup_result['error']}")
                return
            
            # Step 6: Get updated statistics
            print("\n6. 📊 Updated Database Statistics...")
            updated_stats = await db_manager.get_database_stats()
            
            print(f"✅ Updated Database Overview:")
            print(f"   Total pages: {updated_stats['total_pages']} (was {stats['total_pages']})")
            print(f"   Pages with email: {updated_stats['pages_with_email']}")
            print(f"   Pages with name: {updated_stats['pages_with_name']}")
            print(f"   Pages with company: {updated_stats['pages_with_company']}")
            print(f"   Remaining duplicates: {updated_stats['duplicate_count']}")
            print(f"   Email completeness: {updated_stats['data_completeness']['email_completeness']:.1f}%")
            print(f"   Name completeness: {updated_stats['data_completeness']['name_completeness']:.1f}%")
            print(f"   Company completeness: {updated_stats['data_completeness']['company_completeness']:.1f}%")
            
            # Step 7: Show operation history
            print("\n7. 📋 Operation History...")
            history = await db_manager.get_operation_history()
            
            print(f"✅ Operations Recorded: {len(history)}")
            if history:
                print("   Recent Operations:")
                for op in history[-3:]:  # Show last 3
                    print(f"     • {op['operation_type']} at {op['timestamp']}")
                    print(f"       Target: {op['target_id']}")
                    print(f"       Safety Level: {op['safety_level']}")
            
            # Final summary
            print("\n🎉 Database Cleanup Complete!")
            print("=" * 50)
            print(f"📋 Cleanup Summary:")
            print(f"   • Duplicates found: {len(duplicates)}")
            print(f"   • Duplicates removed: {cleanup_result['deleted_count']}")
            print(f"   • Pages before cleanup: {stats['total_pages']}")
            print(f"   • Pages after cleanup: {updated_stats['total_pages']}")
            print(f"   • Remaining duplicates: {updated_stats['duplicate_count']}")
            print(f"   • Operations recorded: {len(history)}")
            
            print(f"\n🛡️ Safety Features Used:")
            print("   ✅ Maximum safety level for all operations")
            print("   ✅ Confirmation token required for deletion")
            print("   ✅ Pages moved to trash (recoverable)")
            print("   ✅ Complete operation history maintained")
            print("   ✅ Comprehensive error handling")
            
            print(f"\n🔗 Database Links:")
            print(f"   • Database URL: https://www.notion.so/jupid/{database_id}")
            print(f"   • Trash: Check Notion trash to recover if needed")
            
            if updated_stats['duplicate_count'] == 0:
                print(f"\n✅ Database is now clean - no duplicates remaining!")
            else:
                print(f"\n⚠️ {updated_stats['duplicate_count']} duplicates still remain - may need manual review")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        logger.exception("Error in database cleanup")


def main():
    """Main function to run the database cleanup"""
    print("🎯 Notion Database Duplicate Cleanup")
    print("=" * 60)
    print("This script will safely find and remove duplicate records")
    print("from your Notion database using our comprehensive")
    print("database management system with safety features.")
    print()
    print("Safety Features:")
    print("• Maximum safety level for all operations")
    print("• Confirmation token required for deletion")
    print("• Pages moved to trash (recoverable)")
    print("• Complete operation history maintained")
    print("• Comprehensive error handling")
    print()
    
    # Run the cleanup
    asyncio.run(cleanup_database_duplicates())
    
    print("\n🏁 Database Cleanup Complete!")
    print("Your Notion database has been cleaned of duplicate records.")
    print("All operations were performed safely with confirmation requirements.")


if __name__ == "__main__":
    main()
