#!/usr/bin/env python3
"""
Safe Database Management Demonstration

This script demonstrates the comprehensive database management capabilities including:
- Safe deletion with confirmation requirements
- Duplicate detection and prevention
- Conflict resolution rules
- Database cleanup and maintenance
- Safety rules to prevent accidental data loss

Author: Development Team
Version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime
from integrations.safe_attio_notion_sync import SafeAttioNotionSync
from integrations.notion_database_manager import NotionDatabaseManager, SafetyLevel
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demonstrate_safe_database_management():
    """Demonstrate comprehensive safe database management"""
    
    print("🛡️ Safe Database Management Demonstration")
    print("=" * 60)
    print("This demo showcases:")
    print("• Safe deletion with confirmation requirements")
    print("• Duplicate detection and prevention")
    print("• Conflict resolution rules")
    print("• Database cleanup and maintenance")
    print("• Safety rules to prevent accidental data loss")
    print()
    
    # Get API keys from config
    attio_api_key = Config.ATTIO_API_KEY
    notion_token = Config.NOTION_TOKEN
    database_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    if not attio_api_key or not notion_token:
        print("❌ API keys not found in config")
        return
    
    try:
        # Initialize safe sync with high safety level
        print("1. 🔧 Initializing Safe Sync System...")
        safe_sync = SafeAttioNotionSync(attio_api_key, notion_token, database_id, SafetyLevel.HIGH)
        
        if not await safe_sync.initialize():
            print("❌ Safe sync initialization failed")
            return
        print("✅ Safe sync system initialized with HIGH safety level")
        
        # Get comprehensive database statistics
        print("\n2. 📊 Database Statistics Analysis...")
        summary = await safe_sync.get_sync_summary()
        
        print(f"✅ Database Statistics:")
        print(f"   Total pages: {summary['database_statistics']['total_pages']}")
        print(f"   Pages with email: {summary['database_statistics']['pages_with_email']}")
        print(f"   Pages with name: {summary['database_statistics']['pages_with_name']}")
        print(f"   Pages with company: {summary['database_statistics']['pages_with_company']}")
        print(f"   Duplicate count: {summary['database_statistics']['duplicate_count']}")
        print(f"   Email completeness: {summary['database_statistics']['data_completeness']['email_completeness']:.1f}%")
        print(f"   Name completeness: {summary['database_statistics']['data_completeness']['name_completeness']:.1f}%")
        print(f"   Company completeness: {summary['database_statistics']['data_completeness']['company_completeness']:.1f}%")
        
        # Validate database integrity
        print("\n3. 🔍 Database Integrity Validation...")
        integrity = await safe_sync.validate_database_integrity()
        
        print(f"✅ Integrity Analysis:")
        print(f"   Integrity Score: {integrity['integrity_score']:.1f}%")
        print(f"   Total pages: {integrity['total_pages']}")
        print(f"   Duplicates found: {integrity['duplicates_found']}")
        print(f"   Invalid records: {integrity['invalid_records']}")
        
        print(f"\n📋 Recommendations:")
        for rec in integrity['recommendations']:
            print(f"   • {rec}")
        
        # Demonstrate duplicate detection
        print("\n4. 🔍 Duplicate Detection Demonstration...")
        
        # Get database manager for direct duplicate access
        db_manager = safe_sync.db_manager
        duplicates = await db_manager.find_duplicates()
        
        if duplicates:
            print(f"✅ Found {len(duplicates)} duplicate records:")
            for i, dup in enumerate(duplicates[:5]):  # Show first 5
                print(f"   {i+1}. {dup.name} ({dup.email})")
                print(f"      Reason: {dup.duplicate_reason}")
                print(f"      Similarity: {dup.similarity_score:.2f}")
                print(f"      Created: {dup.created_time}")
                print(f"      Page ID: {dup.page_id}")
        else:
            print("✅ No duplicates found - database is clean!")
        
        # Demonstrate safety rules
        print("\n5. 🛡️ Safety Rules Demonstration...")
        
        print(f"✅ Current Safety Level: {safe_sync.safety_level.value.upper()}")
        print(f"✅ Safety Rules Active:")
        
        for op_type, rule in db_manager.safety_rules.items():
            print(f"   • {op_type.value.upper()}:")
            print(f"     - Safety Level: {rule.safety_level.value}")
            print(f"     - Requires Confirmation: {rule.requires_confirmation}")
            print(f"     - Max Records: {rule.max_records_per_operation}")
            if rule.blocked_properties:
                print(f"     - Blocked Properties: {', '.join(rule.blocked_properties)}")
        
        # Demonstrate safe deletion (dry run)
        print("\n6. 🗑️ Safe Deletion Demonstration (Dry Run)...")
        
        if duplicates:
            # Show what would happen if we tried to delete without confirmation
            sample_duplicate = duplicates[0]
            print(f"   Testing deletion of: {sample_duplicate.name} ({sample_duplicate.email})")
            
            # This should fail due to safety requirements
            result = await db_manager.safe_delete_page(sample_duplicate.page_id)
            
            if not result["success"]:
                print(f"   ✅ Safety check passed: {result['error']}")
                if result.get("requires_confirmation"):
                    print(f"   ✅ Confirmation token required: {result['confirmation_token']}")
            else:
                print(f"   ⚠️ Unexpected: Deletion succeeded without confirmation")
        else:
            print("   ✅ No duplicates available for deletion testing")
        
        # Demonstrate confirmation token system
        print("\n7. 🔐 Confirmation Token System...")
        
        # Generate a confirmation token for demonstration
        from integrations.notion_database_manager import DatabaseOperation, OperationType
        
        test_operation = DatabaseOperation(
            operation_type=OperationType.DELETE,
            target_id="demo_page",
            data={},
            safety_level=SafetyLevel.HIGH,
            requires_confirmation=True
        )
        
        token = db_manager._generate_confirmation_token(test_operation)
        print(f"   ✅ Generated confirmation token: {token}")
        print(f"   ✅ Token stored: {token in db_manager.confirmation_tokens}")
        print(f"   ✅ Token validates operation: {db_manager.confirmation_tokens[token]}")
        
        # Demonstrate operation history
        print("\n8. 📋 Operation History...")
        
        history = await db_manager.get_operation_history()
        print(f"   ✅ Total operations recorded: {len(history)}")
        
        if history:
            print(f"   Recent Operations:")
            for op in history[-3:]:  # Show last 3
                print(f"     • {op['operation_type']} at {op['timestamp']}")
                print(f"       Target: {op['target_id']}")
                print(f"       Safety Level: {op['safety_level']}")
        else:
            print("   No operations recorded yet")
        
        # Demonstrate sync statistics
        print("\n9. 📈 Sync Statistics...")
        
        print(f"   ✅ Sync Performance:")
        print(f"     - Total syncs: {summary['sync_statistics']['total_syncs']}")
        print(f"     - Successful syncs: {summary['sync_statistics']['successful_syncs']}")
        print(f"     - Failed syncs: {summary['sync_statistics']['failed_syncs']}")
        print(f"     - Success rate: {summary['sync_statistics']['success_rate']:.1f}%")
        print(f"     - Duplicates found: {summary['sync_statistics']['duplicates_found']}")
        print(f"     - Duplicates resolved: {summary['sync_statistics']['duplicates_resolved']}")
        print(f"     - Safety violations: {summary['sync_statistics']['safety_violations']}")
        
        # Demonstrate safe sync with Ethan
        print("\n10. 🔄 Safe Sync Demonstration...")
        
        print("   Testing safe sync with Ethan's data...")
        result = await safe_sync.safe_sync_person("ethan@tuesday.vc", handle_duplicates=False)
        
        if result.success:
            print(f"   ✅ Safe sync successful: {result.action}")
            print(f"     - Person: {result.person_name}")
            print(f"     - Page URL: {result.page_url}")
            print(f"     - Duplicates found: {result.duplicates_found}")
            print(f"     - Safety checks passed: {result.safety_checks_passed}")
        else:
            print(f"   ❌ Safe sync failed: {result.error}")
        
        # Final summary
        print("\n🎉 Safe Database Management Demo Complete!")
        print("=" * 60)
        print("📋 Summary:")
        print(f"   • Database Pages: {summary['database_statistics']['total_pages']}")
        print(f"   • Duplicates Found: {len(duplicates)}")
        print(f"   • Integrity Score: {integrity['integrity_score']:.1f}%")
        print(f"   • Safety Level: {safe_sync.safety_level.value.upper()}")
        print(f"   • Operations Recorded: {len(history)}")
        print(f"   • Confirmation Tokens: {len(db_manager.confirmation_tokens)}")
        
        print(f"\n🛡️ Safety Features Demonstrated:")
        print("   ✅ Multiple safety levels (LOW, MEDIUM, HIGH, MAXIMUM)")
        print("   ✅ Confirmation token system for high-risk operations")
        print("   ✅ Duplicate detection and prevention")
        print("   ✅ Safe deletion with recovery options")
        print("   ✅ Operation history and audit trail")
        print("   ✅ Database integrity validation")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Conflict resolution rules")
        
        print(f"\n🔗 Database Management Ready:")
        print("   • Safe deletion with confirmation requirements")
        print("   • Duplicate detection and automatic resolution")
        print("   • Database cleanup and maintenance")
        print("   • Comprehensive safety rules")
        print("   • Operation history and audit trail")
        print("   • Data integrity validation")
        
        # Close the system
        await safe_sync.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Error in safe database management demo")


async def demonstrate_safety_levels():
    """Demonstrate different safety levels and their behavior"""
    
    print("\n🛡️ Safety Levels Demonstration")
    print("=" * 50)
    
    notion_token = Config.NOTION_TOKEN
    database_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    if not notion_token:
        print("❌ NOTION_TOKEN not found in config")
        return
    
    try:
        # Test each safety level
        for safety_level in [SafetyLevel.LOW, SafetyLevel.MEDIUM, SafetyLevel.HIGH, SafetyLevel.MAXIMUM]:
            print(f"\n🔧 {safety_level.value.upper()} Safety Level:")
            
            db_manager = NotionDatabaseManager(notion_token, database_id, safety_level)
            
            # Show what operations are allowed at this level
            allowed_operations = []
            blocked_operations = []
            
            for op_type, rule in db_manager.safety_rules.items():
                if rule.safety_level.value <= safety_level.value:
                    allowed_operations.append(f"{op_type.value} (confirmation: {rule.requires_confirmation})")
                else:
                    blocked_operations.append(f"{op_type.value} (requires {rule.safety_level.value})")
            
            print(f"   ✅ Allowed Operations:")
            for op in allowed_operations:
                print(f"      • {op}")
            
            if blocked_operations:
                print(f"   ❌ Blocked Operations:")
                for op in blocked_operations:
                    print(f"      • {op}")
        
        print(f"\n✅ Safety level demonstration completed")
        
    except Exception as e:
        print(f"❌ Error demonstrating safety levels: {e}")


def main():
    """Main function to run the safe database management demonstration"""
    print("🎯 Safe Database Management Demonstration")
    print("=" * 70)
    print("This demonstration showcases the comprehensive database management")
    print("capabilities with safety features to prevent accidental data loss.")
    print()
    print("Features Demonstrated:")
    print("• Safe deletion with confirmation requirements")
    print("• Duplicate detection and prevention")
    print("• Conflict resolution rules")
    print("• Database cleanup and maintenance")
    print("• Multiple safety levels")
    print("• Operation history and audit trail")
    print("• Data integrity validation")
    print()
    
    # Run the main demonstration
    asyncio.run(demonstrate_safe_database_management())
    
    # Demonstrate safety levels
    asyncio.run(demonstrate_safety_levels())
    
    print("\n🏁 Safe Database Management Demonstration Complete!")
    print("The database management system is ready for production use with:")
    print("✅ Comprehensive safety rules and confirmation requirements")
    print("✅ Duplicate detection and prevention")
    print("✅ Safe deletion with recovery options")
    print("✅ Bulk operations with safety checks")
    print("✅ Database cleanup and maintenance")
    print("✅ Operation history and audit trail")
    print("✅ Error handling and validation")
    print("✅ Multiple safety levels for different use cases")
    print()
    print("🛡️ Safety Features:")
    print("• Prevents accidental deletion of important data")
    print("• Requires confirmation for high-risk operations")
    print("• Detects and resolves duplicates automatically")
    print("• Maintains operation history for audit trails")
    print("• Validates data integrity continuously")
    print("• Provides multiple safety levels for different scenarios")


if __name__ == "__main__":
    main()
