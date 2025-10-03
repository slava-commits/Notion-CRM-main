#!/usr/bin/env python3
"""
Safe Attio-to-Notion Synchronization with Database Management

This module provides safe synchronization between Attio CRM and Notion databases
with comprehensive database management, duplicate prevention, and safety rules.

Author: Development Team
Version: 1.0.0
License: MIT
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from integrations.attio_notion_sync import AttioNotionSync, NotionAPIError
from integrations.notion_database_manager import (
    NotionDatabaseManager, 
    SafetyLevel, 
    OperationType,
    DuplicateRecord
)
from integrations.attio_client import AttioClient, AttioPerson, AttioCompany
from config import Config

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a synchronization operation"""
    success: bool
    action: str  # created, updated, skipped, error
    page_id: Optional[str] = None
    page_url: Optional[str] = None
    email: Optional[str] = None
    person_name: Optional[str] = None
    error: Optional[str] = None
    duplicates_found: int = 0
    duplicates_resolved: int = 0
    safety_checks_passed: bool = False


class SafeAttioNotionSync:
    """
    Safe Attio-to-Notion synchronization with comprehensive database management
    
    This class provides safe synchronization with duplicate detection, conflict resolution,
    and safety rules to prevent accidental data loss.
    """
    
    def __init__(self, attio_api_key: str, notion_token: str, database_id: str, 
                 safety_level: SafetyLevel = SafetyLevel.HIGH):
        """
        Initialize the safe sync client
        
        Args:
            attio_api_key: Attio API key
            notion_token: Notion integration token
            database_id: Notion database ID
            safety_level: Safety level for operations
        """
        self.attio_sync = AttioNotionSync(attio_api_key, notion_token, database_id)
        self.db_manager = NotionDatabaseManager(notion_token, database_id, safety_level)
        self.safety_level = safety_level
        
        # Sync statistics
        self.sync_stats = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "duplicates_found": 0,
            "duplicates_resolved": 0,
            "safety_violations": 0
        }
    
    async def initialize(self) -> bool:
        """
        Initialize both sync and database management systems
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("🚀 Initializing Safe Attio-Notion Sync")
            
            # Initialize sync system
            if not await self.attio_sync.initialize():
                logger.error("❌ Attio-Notion sync initialization failed")
                return False
            
            # Initialize database manager
            await self.db_manager.__aenter__()
            
            # Ensure schema is ready
            if not await self.attio_sync.ensure_schema():
                logger.error("❌ Schema setup failed")
                return False
            
            logger.info("✅ Safe sync system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def close(self):
        """Close the sync system and database manager"""
        try:
            await self.db_manager.__aexit__(None, None, None)
            logger.info("✅ Safe sync system closed")
        except Exception as e:
            logger.error(f"Error closing sync system: {e}")
    
    async def safe_sync_person(self, email: str, handle_duplicates: bool = True, 
                              confirmation_token: Optional[str] = None) -> SyncResult:
        """
        Safely sync a person from Attio to Notion with duplicate handling
        
        Args:
            email: Person's email address
            handle_duplicates: Whether to automatically handle duplicates
            confirmation_token: Confirmation token for high-risk operations
            
        Returns:
            Sync result with detailed information
        """
        try:
            logger.info(f"🔄 Safe syncing person: {email}")
            self.sync_stats["total_syncs"] += 1
            
            # Step 1: Check for existing duplicates
            duplicates = await self.db_manager.find_duplicates()
            email_duplicates = [d for d in duplicates if d.email.lower() == email.lower()]
            
            if email_duplicates:
                logger.warning(f"⚠️ Found {len(email_duplicates)} duplicates for {email}")
                self.sync_stats["duplicates_found"] += len(email_duplicates)
                
                if handle_duplicates:
                    # Resolve duplicates with confirmation
                    if confirmation_token:
                        duplicate_result = await self.db_manager.bulk_delete_duplicates(
                            email_duplicates, confirmation_token
                        )
                        if duplicate_result["success"]:
                            self.sync_stats["duplicates_resolved"] += duplicate_result["deleted_count"]
                            logger.info(f"✅ Resolved {duplicate_result['deleted_count']} duplicates")
                        else:
                            logger.error(f"❌ Failed to resolve duplicates: {duplicate_result['error']}")
                    else:
                        logger.warning("⚠️ Duplicates found but no confirmation token provided")
                        return SyncResult(
                            success=False,
                            action="error",
                            email=email,
                            error="Duplicates found but no confirmation token provided",
                            duplicates_found=len(email_duplicates),
                            safety_checks_passed=False
                        )
            
            # Step 2: Perform safe sync
            result = await self.attio_sync.sync_person(email, update_existing=True)
            
            if result["success"]:
                self.sync_stats["successful_syncs"] += 1
                logger.info(f"✅ Safe sync successful: {result['action']} page for {email}")
                
                return SyncResult(
                    success=True,
                    action=result["action"],
                    page_id=result["page_id"],
                    page_url=result["page_url"],
                    email=result["email"],
                    person_name=result.get("person_name"),
                    duplicates_found=len(email_duplicates),
                    duplicates_resolved=self.sync_stats["duplicates_resolved"],
                    safety_checks_passed=True
                )
            else:
                self.sync_stats["failed_syncs"] += 1
                logger.error(f"❌ Safe sync failed: {result['error']}")
                
                return SyncResult(
                    success=False,
                    action="error",
                    email=email,
                    error=result["error"],
                    duplicates_found=len(email_duplicates),
                    safety_checks_passed=True
                )
                
        except Exception as e:
            self.sync_stats["failed_syncs"] += 1
            logger.error(f"❌ Unexpected error in safe sync: {e}")
            
            return SyncResult(
                success=False,
                action="error",
                email=email,
                error=str(e),
                safety_checks_passed=False
            )
    
    async def safe_sync_multiple_people(self, emails: List[str], 
                                      handle_duplicates: bool = True,
                                      confirmation_token: Optional[str] = None) -> List[SyncResult]:
        """
        Safely sync multiple people with duplicate handling
        
        Args:
            emails: List of email addresses
            handle_duplicates: Whether to automatically handle duplicates
            confirmation_token: Confirmation token for bulk operations
            
        Returns:
            List of sync results
        """
        results = []
        
        logger.info(f"🔄 Safe syncing {len(emails)} people")
        
        # First, handle all duplicates if requested
        if handle_duplicates and confirmation_token:
            duplicates = await self.db_manager.find_duplicates()
            if duplicates:
                logger.info(f"🧹 Resolving {len(duplicates)} duplicates before sync")
                duplicate_result = await self.db_manager.bulk_delete_duplicates(
                    duplicates, confirmation_token
                )
                if duplicate_result["success"]:
                    self.sync_stats["duplicates_resolved"] += duplicate_result["deleted_count"]
                    logger.info(f"✅ Resolved {duplicate_result['deleted_count']} duplicates")
        
        # Then sync each person
        for email in emails:
            try:
                result = await self.safe_sync_person(email, handle_duplicates=False)
                results.append(result)
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to sync {email}: {e}")
                results.append(SyncResult(
                    success=False,
                    action="error",
                    email=email,
                    error=str(e)
                ))
        
        return results
    
    async def safe_cleanup_database(self, confirmation_token: str) -> Dict[str, Any]:
        """
        Safely cleanup the database with confirmation
        
        Args:
            confirmation_token: Confirmation token for cleanup operation
            
        Returns:
            Cleanup result
        """
        try:
            logger.info("🧹 Starting safe database cleanup")
            
            result = await self.db_manager.cleanup_database(confirmation_token)
            
            if result["success"]:
                cleanup_results = result["cleanup_results"]
                self.sync_stats["duplicates_resolved"] += cleanup_results["duplicates_deleted"]
                logger.info("✅ Safe database cleanup completed")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Safe cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_sync_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive sync and database summary
        
        Returns:
            Summary statistics
        """
        try:
            # Get sync statistics
            sync_summary = await self.attio_sync.get_sync_summary()
            
            # Get database statistics
            db_stats = await self.db_manager.get_database_stats()
            
            # Get operation history
            operation_history = await self.db_manager.get_operation_history()
            
            return {
                "sync_statistics": {
                    "total_syncs": self.sync_stats["total_syncs"],
                    "successful_syncs": self.sync_stats["successful_syncs"],
                    "failed_syncs": self.sync_stats["failed_syncs"],
                    "duplicates_found": self.sync_stats["duplicates_found"],
                    "duplicates_resolved": self.sync_stats["duplicates_resolved"],
                    "safety_violations": self.sync_stats["safety_violations"],
                    "success_rate": (
                        self.sync_stats["successful_syncs"] / self.sync_stats["total_syncs"] * 100
                        if self.sync_stats["total_syncs"] > 0 else 0
                    )
                },
                "database_statistics": db_stats,
                "notion_summary": sync_summary,
                "operation_history": {
                    "total_operations": len(operation_history),
                    "recent_operations": operation_history[-5:] if operation_history else []
                },
                "safety_level": self.safety_level.value,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync summary: {e}")
            return {
                "error": str(e),
                "sync_statistics": self.sync_stats,
                "safety_level": self.safety_level.value
            }
    
    async def validate_database_integrity(self) -> Dict[str, Any]:
        """
        Validate database integrity and data quality
        
        Returns:
            Integrity validation results
        """
        try:
            logger.info("🔍 Validating database integrity")
            
            # Get database statistics
            db_stats = await self.db_manager.get_database_stats()
            
            # Find duplicates
            duplicates = await self.db_manager.find_duplicates()
            
            # Check for invalid records
            all_pages = await self.db_manager.get_all_pages()
            invalid_records = []
            
            for page in all_pages:
                properties = page.get('properties', {})
                name_prop = properties.get('Name', {})
                email_prop = properties.get('Email', {})
                
                name = name_prop.get('title', [{}])[0].get('text', {}).get('content', '').strip()
                email = email_prop.get('email', '').strip()
                
                if not name or not email:
                    invalid_records.append({
                        "page_id": page['id'],
                        "name": name or "Unknown",
                        "email": email or "No email",
                        "reason": "Missing required fields"
                    })
            
            # Calculate integrity score
            total_pages = db_stats["total_pages"]
            integrity_issues = len(duplicates) + len(invalid_records)
            integrity_score = max(0, 100 - (integrity_issues / total_pages * 100)) if total_pages > 0 else 100
            
            return {
                "integrity_score": integrity_score,
                "total_pages": total_pages,
                "duplicates_found": len(duplicates),
                "invalid_records": len(invalid_records),
                "data_completeness": db_stats.get("data_completeness", {}),
                "recommendations": self._generate_recommendations(duplicates, invalid_records),
                "last_validated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to validate database integrity: {e}")
            return {
                "error": str(e),
                "integrity_score": 0
            }
    
    def _generate_recommendations(self, duplicates: List[DuplicateRecord], 
                                invalid_records: List[Dict]) -> List[str]:
        """Generate recommendations based on integrity issues"""
        recommendations = []
        
        if duplicates:
            recommendations.append(f"Resolve {len(duplicates)} duplicate records")
        
        if invalid_records:
            recommendations.append(f"Fix {len(invalid_records)} invalid records with missing data")
        
        if not duplicates and not invalid_records:
            recommendations.append("Database integrity is excellent - no issues found")
        
        return recommendations


# Example usage and testing
async def main():
    """Example usage of the SafeAttioNotionSync"""
    
    # Get API keys from config
    attio_api_key = Config.ATTIO_API_KEY
    notion_token = Config.NOTION_TOKEN
    database_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    if not attio_api_key or not notion_token:
        print("❌ API keys not found in config")
        return
    
    try:
        # Initialize safe sync with high safety level
        safe_sync = SafeAttioNotionSync(attio_api_key, notion_token, database_id, SafetyLevel.HIGH)
        
        if not await safe_sync.initialize():
            print("❌ Safe sync initialization failed")
            return
        
        # Test safe sync with Ethan
        print("🔄 Testing safe sync with Ethan...")
        result = await safe_sync.safe_sync_person("ethan@tuesday.vc")
        
        if result.success:
            print(f"✅ Safe sync successful: {result.action}")
            print(f"   Person: {result.person_name}")
            print(f"   Page URL: {result.page_url}")
            print(f"   Duplicates found: {result.duplicates_found}")
            print(f"   Safety checks passed: {result.safety_checks_passed}")
        else:
            print(f"❌ Safe sync failed: {result.error}")
        
        # Get comprehensive summary
        print("\n📊 Getting comprehensive summary...")
        summary = await safe_sync.get_sync_summary()
        
        print(f"Sync Statistics:")
        print(f"   Total syncs: {summary['sync_statistics']['total_syncs']}")
        print(f"   Success rate: {summary['sync_statistics']['success_rate']:.1f}%")
        print(f"   Duplicates resolved: {summary['sync_statistics']['duplicates_resolved']}")
        
        print(f"Database Statistics:")
        print(f"   Total pages: {summary['database_statistics']['total_pages']}")
        print(f"   Duplicates: {summary['database_statistics']['duplicate_count']}")
        
        # Validate database integrity
        print("\n🔍 Validating database integrity...")
        integrity = await safe_sync.validate_database_integrity()
        
        print(f"Integrity Score: {integrity['integrity_score']:.1f}%")
        print(f"Recommendations:")
        for rec in integrity['recommendations']:
            print(f"   • {rec}")
        
        # Close the system
        await safe_sync.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
