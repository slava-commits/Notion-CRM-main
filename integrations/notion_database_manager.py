#!/usr/bin/env python3
"""
Production-Ready Notion Database Management System

This module provides comprehensive database management capabilities including:
- Safe deletion with confirmation requirements
- Duplicate detection and prevention
- Conflict resolution rules
- Database cleanup and maintenance
- Safety rules to prevent accidental data loss

Author: Development Team
Version: 1.0.0
License: MIT
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

from integrations.attio_notion_sync import NotionClient2025, NotionAPIError
from config import Config

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels for database operations"""
    LOW = "low"           # Minimal safety checks
    MEDIUM = "medium"     # Standard safety checks
    HIGH = "high"         # Strict safety checks
    MAXIMUM = "maximum"   # Maximum safety with confirmations


class OperationType(Enum):
    """Types of database operations"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BULK_DELETE = "bulk_delete"
    SCHEMA_CHANGE = "schema_change"
    CLEANUP = "cleanup"


@dataclass
class DuplicateRecord:
    """Represents a duplicate record found in the database"""
    page_id: str
    email: str
    name: str
    created_time: datetime
    last_edited_time: datetime
    similarity_score: float
    duplicate_reason: str


@dataclass
class SafetyRule:
    """Safety rule for database operations"""
    operation_type: OperationType
    safety_level: SafetyLevel
    requires_confirmation: bool
    max_records_per_operation: int
    allowed_properties: List[str]
    blocked_properties: List[str]
    confirmation_message: str


@dataclass
class DatabaseOperation:
    """Represents a database operation with safety checks"""
    operation_type: OperationType
    target_id: str
    data: Dict[str, Any]
    safety_level: SafetyLevel
    requires_confirmation: bool
    confirmation_token: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NotionDatabaseManager:
    """
    Production-ready Notion database management system with comprehensive safety features
    
    This class provides safe database operations including deletion, duplicate detection,
    conflict resolution, and maintenance operations with multiple safety levels.
    """
    
    def __init__(self, notion_token: str, database_id: str, safety_level: SafetyLevel = SafetyLevel.HIGH):
        """
        Initialize the database manager
        
        Args:
            notion_token: Notion integration token
            database_id: Notion database ID
            safety_level: Default safety level for operations
        """
        self.notion_client = NotionClient2025(notion_token)
        self.database_id = database_id
        self.safety_level = safety_level
        self.operation_history: List[DatabaseOperation] = []
        
        # Define safety rules
        self.safety_rules = self._create_safety_rules()
        
        # Confirmation tokens for high-risk operations
        self.confirmation_tokens: Dict[str, str] = {}
        
        if not notion_token:
            raise ValueError("Notion token is required")
    
    def _create_safety_rules(self) -> Dict[OperationType, SafetyRule]:
        """Create comprehensive safety rules for all operations"""
        return {
            OperationType.CREATE: SafetyRule(
                operation_type=OperationType.CREATE,
                safety_level=SafetyLevel.MEDIUM,
                requires_confirmation=False,
                max_records_per_operation=100,
                allowed_properties=[],
                blocked_properties=[],
                confirmation_message="Create new record"
            ),
            OperationType.UPDATE: SafetyRule(
                operation_type=OperationType.UPDATE,
                safety_level=SafetyLevel.MEDIUM,
                requires_confirmation=False,
                max_records_per_operation=50,
                allowed_properties=[],
                blocked_properties=["Name", "Email"],  # Prevent changing key identifiers
                confirmation_message="Update existing record"
            ),
            OperationType.DELETE: SafetyRule(
                operation_type=OperationType.DELETE,
                safety_level=SafetyLevel.MAXIMUM,
                requires_confirmation=True,
                max_records_per_operation=1,
                allowed_properties=[],
                blocked_properties=[],
                confirmation_message="DELETE RECORD - This action cannot be undone!"
            ),
            OperationType.BULK_DELETE: SafetyRule(
                operation_type=OperationType.BULK_DELETE,
                safety_level=SafetyLevel.MAXIMUM,
                requires_confirmation=True,
                max_records_per_operation=10,
                allowed_properties=[],
                blocked_properties=[],
                confirmation_message="BULK DELETE - This will delete multiple records permanently!"
            ),
            OperationType.SCHEMA_CHANGE: SafetyRule(
                operation_type=OperationType.SCHEMA_CHANGE,
                safety_level=SafetyLevel.HIGH,
                requires_confirmation=True,
                max_records_per_operation=1,
                allowed_properties=[],
                blocked_properties=[],
                confirmation_message="SCHEMA CHANGE - This will modify database structure!"
            ),
            OperationType.CLEANUP: SafetyRule(
                operation_type=OperationType.CLEANUP,
                safety_level=SafetyLevel.HIGH,
                requires_confirmation=True,
                max_records_per_operation=50,
                allowed_properties=[],
                blocked_properties=[],
                confirmation_message="DATABASE CLEANUP - This will remove duplicate/invalid records!"
            )
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.notion_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.notion_client.__aexit__(exc_type, exc_val, exc_tb)
    
    def _generate_confirmation_token(self, operation: DatabaseOperation) -> str:
        """Generate a confirmation token for high-risk operations"""
        data = f"{operation.operation_type.value}_{operation.target_id}_{operation.timestamp.isoformat()}"
        token = hashlib.sha256(data.encode()).hexdigest()[:8]
        self.confirmation_tokens[token] = operation.operation_type.value
        return token
    
    def _validate_safety_rule(self, operation: DatabaseOperation) -> Tuple[bool, str]:
        """
        Validate operation against safety rules
        
        Args:
            operation: Database operation to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        rule = self.safety_rules.get(operation.operation_type)
        if not rule:
            return False, f"No safety rule defined for {operation.operation_type.value}"
        
        # Check safety level
        if operation.safety_level.value < rule.safety_level.value:
            return False, f"Operation requires {rule.safety_level.value} safety level, got {operation.safety_level.value}"
        
        # Check confirmation requirement
        if rule.requires_confirmation and not operation.confirmation_token:
            return False, f"Operation requires confirmation token"
        
        # Validate confirmation token
        if operation.confirmation_token:
            expected_operation = self.confirmation_tokens.get(operation.confirmation_token)
            if expected_operation != operation.operation_type.value:
                return False, "Invalid confirmation token"
        
        return True, ""
    
    async def get_all_pages(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Get all pages from the database
        
        Args:
            page_size: Number of pages per request
            
        Returns:
            List of all pages in the database
        """
        try:
            all_pages = []
            has_more = True
            start_cursor = None
            
            while has_more:
                # Use search endpoint to get all pages
                search_data = {
                    "query": "",
                    "filter": {
                        "value": "page",
                        "property": "object"
                    },
                    "page_size": page_size
                }
                
                if start_cursor:
                    search_data["start_cursor"] = start_cursor
                
                response = await self.notion_client._make_request("POST", "search", search_data)
                pages = response.get('results', [])
                
                # Filter pages that belong to our database
                database_pages = []
                for page in pages:
                    parent = page.get('parent', {})
                    if parent.get('database_id') == self.database_id:
                        database_pages.append(page)
                
                all_pages.extend(database_pages)
                
                has_more = response.get('has_more', False)
                start_cursor = response.get('next_cursor')
            
            logger.info(f"Retrieved {len(all_pages)} pages from database")
            return all_pages
            
        except Exception as e:
            logger.error(f"Failed to get all pages: {e}")
            raise
    
    async def find_duplicates(self, similarity_threshold: float = 0.8) -> List[DuplicateRecord]:
        """
        Find duplicate records in the database
        
        Args:
            similarity_threshold: Minimum similarity score to consider duplicates
            
        Returns:
            List of duplicate records found
        """
        try:
            logger.info("🔍 Searching for duplicate records...")
            
            pages = await self.get_all_pages()
            duplicates = []
            
            # Group pages by email (primary identifier)
            email_groups = {}
            for page in pages:
                properties = page.get('properties', {})
                email_prop = properties.get('Email', {})
                email = email_prop.get('email', '') if email_prop else ''
                
                if email:
                    if email not in email_groups:
                        email_groups[email] = []
                    email_groups[email].append(page)
            
            # Find duplicates within each email group
            for email, pages_with_email in email_groups.items():
                if len(pages_with_email) > 1:
                    # Sort by creation time (keep oldest)
                    pages_with_email.sort(key=lambda p: p.get('created_time', ''))
                    
                    # Mark all but the first as duplicates
                    for i, page in enumerate(pages_with_email[1:], 1):
                        name_prop = page.get('properties', {}).get('Name', {})
                        name = "Unknown"
                        if name_prop and name_prop.get('title'):
                            title_list = name_prop.get('title', [])
                            if title_list and len(title_list) > 0:
                                name = title_list[0].get('text', {}).get('content', 'Unknown')
                        
                        duplicate = DuplicateRecord(
                            page_id=page['id'],
                            email=email,
                            name=name,
                            created_time=datetime.fromisoformat(page.get('created_time', '').replace('Z', '+00:00')),
                            last_edited_time=datetime.fromisoformat(page.get('last_edited_time', '').replace('Z', '+00:00')),
                            similarity_score=1.0,  # Same email = 100% similarity
                            duplicate_reason="Same email address"
                        )
                        duplicates.append(duplicate)
            
            # Also check for similar names (fuzzy matching)
            name_groups = {}
            for page in pages:
                properties = page.get('properties', {})
                name_prop = properties.get('Name', {})
                
                if name_prop and name_prop.get('title'):
                    title_list = name_prop.get('title', [])
                    if title_list and len(title_list) > 0:
                        name = title_list[0].get('text', {}).get('content', '').lower().strip()
                        
                        if name:
                            if name not in name_groups:
                                name_groups[name] = []
                            name_groups[name].append(page)
            
            # Find similar names
            for name, pages_with_name in name_groups.items():
                if len(pages_with_name) > 1:
                    # Check if they have different emails (potential duplicates with different emails)
                    emails = set()
                    for page in pages_with_name:
                        email_prop = page.get('properties', {}).get('Email', {})
                        email = email_prop.get('email', '')
                        if email:
                            emails.add(email)
                    
                    if len(emails) > 1:  # Same name, different emails
                        for page in pages_with_name[1:]:
                            email_prop = page.get('properties', {}).get('Email', {})
                            email = email_prop.get('email', '') if email_prop else ''
                            
                            name_prop = page.get('properties', {}).get('Name', {})
                            display_name = "Unknown"
                            if name_prop and name_prop.get('title'):
                                title_list = name_prop.get('title', [])
                                if title_list and len(title_list) > 0:
                                    display_name = title_list[0].get('text', {}).get('content', 'Unknown')
                            
                            duplicate = DuplicateRecord(
                                page_id=page['id'],
                                email=email,
                                name=display_name,
                                created_time=datetime.fromisoformat(page.get('created_time', '').replace('Z', '+00:00')),
                                last_edited_time=datetime.fromisoformat(page.get('last_edited_time', '').replace('Z', '+00:00')),
                                similarity_score=0.9,  # High similarity for same name
                                duplicate_reason="Same name, different email"
                            )
                            duplicates.append(duplicate)
            
            logger.info(f"Found {len(duplicates)} duplicate records")
            return duplicates
            
        except Exception as e:
            logger.error(f"Failed to find duplicates: {e}")
            raise
    
    async def safe_delete_page(self, page_id: str, confirmation_token: Optional[str] = None, 
                              force: bool = False) -> Dict[str, Any]:
        """
        Safely delete a page with confirmation requirements
        
        Args:
            page_id: ID of the page to delete
            confirmation_token: Confirmation token for high-risk operations
            force: Skip safety checks (use with extreme caution)
            
        Returns:
            Deletion result
        """
        try:
            if not force:
                # Create operation for validation
                operation = DatabaseOperation(
                    operation_type=OperationType.DELETE,
                    target_id=page_id,
                    data={},
                    safety_level=self.safety_level,
                    requires_confirmation=True,
                    confirmation_token=confirmation_token
                )
                
                # Validate safety rules
                is_valid, error_msg = self._validate_safety_rule(operation)
                if not is_valid:
                    return {
                        "success": False,
                        "error": f"Safety validation failed: {error_msg}",
                        "requires_confirmation": True,
                        "confirmation_token": self._generate_confirmation_token(operation)
                    }
            
            # Get page info before deletion
            page_info = await self.notion_client.get_page(page_id)
            page_title = "Unknown"
            if page_info.get('properties', {}).get('Name', {}).get('title'):
                page_title = page_info['properties']['Name']['title'][0]['text']['content']
            
            # Move page to trash (safer than permanent deletion)
            data = {"in_trash": True}
            result = await self.notion_client._make_request("PATCH", f"pages/{page_id}", data)
            
            # Log the operation
            operation = DatabaseOperation(
                operation_type=OperationType.DELETE,
                target_id=page_id,
                data={"page_title": page_title},
                safety_level=self.safety_level,
                requires_confirmation=True,
                confirmation_token=confirmation_token
            )
            self.operation_history.append(operation)
            
            logger.info(f"✅ Safely deleted page: {page_title} ({page_id})")
            
            return {
                "success": True,
                "action": "moved_to_trash",
                "page_id": page_id,
                "page_title": page_title,
                "message": "Page moved to trash (can be recovered)"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete page {page_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "page_id": page_id
            }
    
    async def bulk_delete_duplicates(self, duplicates: List[DuplicateRecord], 
                                   confirmation_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Safely delete duplicate records with confirmation
        
        Args:
            duplicates: List of duplicate records to delete
            confirmation_token: Confirmation token for bulk operation
            
        Returns:
            Bulk deletion result
        """
        try:
            if not duplicates:
                return {
                    "success": True,
                    "message": "No duplicates to delete",
                    "deleted_count": 0
                }
            
            # Create operation for validation
            operation = DatabaseOperation(
                operation_type=OperationType.BULK_DELETE,
                target_id="bulk_duplicates",
                data={"duplicate_count": len(duplicates)},
                safety_level=self.safety_level,
                requires_confirmation=True,
                confirmation_token=confirmation_token
            )
            
            # Validate safety rules
            is_valid, error_msg = self._validate_safety_rule(operation)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Safety validation failed: {error_msg}",
                    "requires_confirmation": True,
                    "confirmation_token": self._generate_confirmation_token(operation)
                }
            
            deleted_count = 0
            errors = []
            
            for duplicate in duplicates:
                try:
                    result = await self.safe_delete_page(duplicate.page_id, confirmation_token, force=True)
                    if result["success"]:
                        deleted_count += 1
                        logger.info(f"✅ Deleted duplicate: {duplicate.name} ({duplicate.email})")
                    else:
                        errors.append(f"Failed to delete {duplicate.name}: {result['error']}")
                except Exception as e:
                    errors.append(f"Failed to delete {duplicate.name}: {str(e)}")
            
            # Log the operation
            self.operation_history.append(operation)
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "total_duplicates": len(duplicates),
                "errors": errors,
                "message": f"Deleted {deleted_count} duplicate records"
            }
            
        except Exception as e:
            logger.error(f"Failed to bulk delete duplicates: {e}")
            return {
                "success": False,
                "error": str(e),
                "deleted_count": 0
            }
    
    async def cleanup_database(self, confirmation_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive database cleanup operation
        
        Args:
            confirmation_token: Confirmation token for cleanup operation
            
        Returns:
            Cleanup result
        """
        try:
            logger.info("🧹 Starting comprehensive database cleanup...")
            
            # Create operation for validation
            operation = DatabaseOperation(
                operation_type=OperationType.CLEANUP,
                target_id="database_cleanup",
                data={},
                safety_level=self.safety_level,
                requires_confirmation=True,
                confirmation_token=confirmation_token
            )
            
            # Validate safety rules
            is_valid, error_msg = self._validate_safety_rule(operation)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Safety validation failed: {error_msg}",
                    "requires_confirmation": True,
                    "confirmation_token": self._generate_confirmation_token(operation)
                }
            
            cleanup_results = {
                "duplicates_found": 0,
                "duplicates_deleted": 0,
                "invalid_records_found": 0,
                "invalid_records_deleted": 0,
                "total_pages_before": 0,
                "total_pages_after": 0,
                "errors": []
            }
            
            # Get initial page count
            all_pages = await self.get_all_pages()
            cleanup_results["total_pages_before"] = len(all_pages)
            
            # Find and delete duplicates
            duplicates = await self.find_duplicates()
            cleanup_results["duplicates_found"] = len(duplicates)
            
            if duplicates:
                duplicate_result = await self.bulk_delete_duplicates(duplicates, confirmation_token)
                if duplicate_result["success"]:
                    cleanup_results["duplicates_deleted"] = duplicate_result["deleted_count"]
                else:
                    cleanup_results["errors"].append(f"Duplicate deletion failed: {duplicate_result['error']}")
            
            # Find invalid records (missing required fields)
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
                        "reason": "Missing required fields (Name or Email)"
                    })
            
            cleanup_results["invalid_records_found"] = len(invalid_records)
            
            # Delete invalid records
            for invalid_record in invalid_records:
                try:
                    result = await self.safe_delete_page(invalid_record["page_id"], confirmation_token, force=True)
                    if result["success"]:
                        cleanup_results["invalid_records_deleted"] += 1
                        logger.info(f"✅ Deleted invalid record: {invalid_record['name']}")
                    else:
                        cleanup_results["errors"].append(f"Failed to delete invalid record {invalid_record['name']}: {result['error']}")
                except Exception as e:
                    cleanup_results["errors"].append(f"Failed to delete invalid record {invalid_record['name']}: {str(e)}")
            
            # Get final page count
            final_pages = await self.get_all_pages()
            cleanup_results["total_pages_after"] = len(final_pages)
            
            # Log the operation
            self.operation_history.append(operation)
            
            logger.info(f"✅ Database cleanup completed:")
            logger.info(f"   Duplicates found: {cleanup_results['duplicates_found']}")
            logger.info(f"   Duplicates deleted: {cleanup_results['duplicates_deleted']}")
            logger.info(f"   Invalid records found: {cleanup_results['invalid_records_found']}")
            logger.info(f"   Invalid records deleted: {cleanup_results['invalid_records_deleted']}")
            logger.info(f"   Total pages before: {cleanup_results['total_pages_before']}")
            logger.info(f"   Total pages after: {cleanup_results['total_pages_after']}")
            
            return {
                "success": True,
                "cleanup_results": cleanup_results,
                "message": "Database cleanup completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup database: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_operation_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all database operations
        
        Returns:
            List of operation history records
        """
        return [
            {
                "operation_type": op.operation_type.value,
                "target_id": op.target_id,
                "safety_level": op.safety_level.value,
                "timestamp": op.timestamp.isoformat(),
                "data": op.data
            }
            for op in self.operation_history
        ]
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics
        
        Returns:
            Database statistics
        """
        try:
            pages = await self.get_all_pages()
            
            # Analyze page properties
            total_pages = len(pages)
            pages_with_email = 0
            pages_with_name = 0
            pages_with_company = 0
            
            for page in pages:
                properties = page.get('properties', {})
                
                # Check for email
                email_prop = properties.get('Email', {})
                if email_prop and email_prop.get('email'):
                    pages_with_email += 1
                
                # Check for name
                name_prop = properties.get('Name', {})
                if name_prop and name_prop.get('title'):
                    pages_with_name += 1
                
                # Check for company name
                company_prop = properties.get('Company Name', {})
                if company_prop and company_prop.get('rich_text'):
                    pages_with_company += 1
            
            # Try to get duplicates, but don't fail if it errors
            duplicate_count = 0
            try:
                duplicates = await self.find_duplicates()
                duplicate_count = len(duplicates)
            except Exception as e:
                logger.warning(f"Could not get duplicate count: {e}")
                duplicate_count = 0
            
            return {
                "total_pages": total_pages,
                "pages_with_email": pages_with_email,
                "pages_with_name": pages_with_name,
                "pages_with_company": pages_with_company,
                "duplicate_count": duplicate_count,
                "data_completeness": {
                    "email_completeness": (pages_with_email / total_pages * 100) if total_pages > 0 else 0,
                    "name_completeness": (pages_with_name / total_pages * 100) if total_pages > 0 else 0,
                    "company_completeness": (pages_with_company / total_pages * 100) if total_pages > 0 else 0
                },
                "last_operation": self.operation_history[-1].timestamp.isoformat() if self.operation_history else None,
                "total_operations": len(self.operation_history)
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "error": str(e),
                "total_pages": 0,
                "pages_with_email": 0,
                "pages_with_name": 0,
                "pages_with_company": 0,
                "duplicate_count": 0,
                "data_completeness": {
                    "email_completeness": 0,
                    "name_completeness": 0,
                    "company_completeness": 0
                },
                "total_operations": 0
            }


# Example usage and testing
async def main():
    """Example usage of the NotionDatabaseManager"""
    
    # Get API keys from config
    notion_token = Config.NOTION_TOKEN
    database_id = "66ea7666-29df-4091-997a-f3ddf5cce582"
    
    if not notion_token:
        print("❌ NOTION_TOKEN not found in config")
        return
    
    try:
        # Initialize database manager with high safety level
        db_manager = NotionDatabaseManager(notion_token, database_id, SafetyLevel.HIGH)
        
        async with db_manager:
            # Get database statistics
            print("📊 Database Statistics:")
            stats = await db_manager.get_database_stats()
            print(f"   Total pages: {stats['total_pages']}")
            print(f"   Duplicates: {stats['duplicate_count']}")
            print(f"   Email completeness: {stats['data_completeness']['email_completeness']:.1f}%")
            
            # Find duplicates
            print("\n🔍 Finding duplicates...")
            duplicates = await db_manager.find_duplicates()
            if duplicates:
                print(f"Found {len(duplicates)} duplicates:")
                for dup in duplicates[:5]:  # Show first 5
                    print(f"   • {dup.name} ({dup.email}) - {dup.duplicate_reason}")
            else:
                print("✅ No duplicates found")
            
            # Get operation history
            print("\n📋 Operation History:")
            history = await db_manager.get_operation_history()
            if history:
                for op in history[-3:]:  # Show last 3 operations
                    print(f"   • {op['operation_type']} at {op['timestamp']}")
            else:
                print("   No operations recorded yet")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
