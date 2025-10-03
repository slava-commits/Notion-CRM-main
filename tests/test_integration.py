#!/usr/bin/env python3
"""
Integration Tests
Tests for the user data integration system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from integration_implementation import EmailDeduplicationEngine, Contact, Event
from notion_schema import NotionSchemaBuilder
from integrations.notion_client import NotionClient
from integrations.gmail_integration import GmailIntegration
from integrations.calendar_integration import CalendarIntegration
from integrations.fathom_integration import FathomIntegration
from integrations.social_integration import SocialIntegration
from integrations.leaner_integration import LeanerIntegration
from daily_brief_generator import DailyBriefGenerator

class TestEmailDeduplicationEngine:
    """Test email deduplication functionality"""
    
    def setup_method(self):
        self.engine = EmailDeduplicationEngine()
    
    def test_normalize_name(self):
        """Test name normalization"""
        assert self.engine.normalize_name("Dr. John Smith Jr.") == "john smith"
        assert self.engine.normalize_name("Ms. Jane Doe") == "jane doe"
        assert self.engine.normalize_name("") == ""
    
    def test_calculate_name_similarity(self):
        """Test name similarity calculation"""
        # Exact match
        assert self.engine.calculate_name_similarity("John Smith", "John Smith") == 1.0
        
        # Similar names
        assert self.engine.calculate_name_similarity("John Smith", "Johnny Smith") > 0.7
        
        # Different names
        assert self.engine.calculate_name_similarity("John Smith", "Jane Doe") < 0.5
    
    def test_add_or_update_contact(self):
        """Test contact addition and updating"""
        # Add new contact
        contact_id = self.engine.add_or_update_contact(
            "john@example.com", "John Smith", "Example Corp"
        )
        
        assert contact_id in self.engine.contacts
        assert self.engine.contacts[contact_id].name == "John Smith"
        assert self.engine.contacts[contact_id].company == "Example Corp"
        
        # Update existing contact
        same_contact_id = self.engine.add_or_update_contact(
            "john@example.com", "John Smith", "Example Corp"
        )
        
        assert contact_id == same_contact_id

class TestNotionSchemaBuilder:
    """Test Notion schema generation"""
    
    def setup_method(self):
        self.builder = NotionSchemaBuilder()
    
    def test_create_people_database(self):
        """Test people database schema creation"""
        schema = self.builder.create_people_database()
        
        assert "properties" in schema
        assert "Name" in schema["properties"]
        assert "Primary Email" in schema["properties"]
        assert "Role" in schema["properties"]
        assert "Status" in schema["properties"]
    
    def test_create_companies_database(self):
        """Test companies database schema creation"""
        schema = self.builder.create_companies_database()
        
        assert "properties" in schema
        assert "Name" in schema["properties"]
        assert "Website" in schema["properties"]
        assert "Type" in schema["properties"]
    
    def test_get_all_schemas(self):
        """Test getting all database schemas"""
        schemas = self.builder.get_all_schemas()
        
        expected_databases = [
            "people", "companies", "threads", "interactions",
            "tasks", "social_activity", "documents", "daily_brief"
        ]
        
        for db_name in expected_databases:
            assert db_name in schemas

@pytest.mark.asyncio
class TestNotionClient:
    """Test Notion client functionality"""
    
    @pytest.fixture
    def mock_notion_client(self):
        client = NotionClient("test_token")
        client.db_ids = {
            "people": "test_people_id",
            "companies": "test_companies_id",
            "tasks": "test_tasks_id"
        }
        return client
    
    async def test_create_person(self, mock_notion_client):
        """Test person creation"""
        with patch.object(mock_notion_client, 'create_page') as mock_create:
            mock_create.return_value = "test_person_id"
            
            person_data = {
                "name": "John Smith",
                "email": "john@example.com",
                "role": "Client",
                "status": "Active"
            }
            
            result = await mock_notion_client.create_person(person_data)
            
            assert result == "test_person_id"
            mock_create.assert_called_once()
    
    async def test_create_task(self, mock_notion_client):
        """Test task creation"""
        with patch.object(mock_notion_client, 'create_page') as mock_create:
            mock_create.return_value = "test_task_id"
            
            task_data = {
                "title": "Test Task",
                "status": "Todo",
                "priority": "High",
                "reason": "Next step"
            }
            
            result = await mock_notion_client.create_task(task_data)
            
            assert result == "test_task_id"
            mock_create.assert_called_once()

@pytest.mark.asyncio
class TestGmailIntegration:
    """Test Gmail integration functionality"""
    
    @pytest.fixture
    def mock_gmail(self):
        credentials = {
            'client_id': 'test_id',
            'client_secret': 'test_secret',
            'refresh_token': 'test_token'
        }
        return GmailIntegration(credentials)
    
    async def test_parse_email_address(self, mock_gmail):
        """Test email address parsing"""
        # Test "Name <email@domain.com>" format
        email, name = mock_gmail._parse_email_address("John Smith <john@example.com>")
        assert email == "john@example.com"
        assert name == "John Smith"
        
        # Test "email@domain.com" format
        email, name = mock_gmail._parse_email_address("john@example.com")
        assert email == "john@example.com"
        assert name == ""
    
    async def test_get_contacts_from_emails(self, mock_gmail):
        """Test contact extraction from emails"""
        emails = [
            {
                'from_email': 'john@example.com',
                'from_name': 'John Smith',
                'direction': 'inbound',
                'timestamp': '2024-01-01T10:00:00Z'
            },
            {
                'to_email': 'jane@example.com',
                'to_name': 'Jane Doe',
                'direction': 'outbound',
                'timestamp': '2024-01-01T11:00:00Z'
            }
        ]
        
        contacts = await mock_gmail.get_contacts_from_emails(emails)
        
        assert len(contacts) == 2
        assert contacts[0]['email'] == 'john@example.com'
        assert contacts[1]['email'] == 'jane@example.com'

@pytest.mark.asyncio
class TestDailyBriefGenerator:
    """Test daily brief generation"""
    
    @pytest.fixture
    def mock_brief_generator(self):
        mock_notion_client = Mock()
        return DailyBriefGenerator(mock_notion_client)
    
    async def test_generate_fallback_summary(self, mock_brief_generator):
        """Test fallback summary generation"""
        brief_data = {
            'waiting_tasks': [{'id': '1'}, {'id': '2'}],
            'due_today_tasks': [{'id': '3'}],
            'overdue_tasks': [{'id': '4'}],
            'recent_interactions': [{'id': '5'}],
            'social_activity': [{'id': '6'}]
        }
        
        summary = mock_brief_generator._generate_fallback_summary(brief_data)
        
        assert "Daily Brief Summary" in summary
        assert "2 tasks waiting on replies" in summary
        assert "1 tasks due today" in summary
        assert "1 overdue tasks" in summary
    
    async def test_generate_action_items(self, mock_brief_generator):
        """Test action item generation"""
        brief_data = {
            'waiting_tasks': [
                {
                    'id': '1',
                    'title': 'Follow up with client',
                    'reason': 'Waiting on reply',
                    'person_id': 'person_1'
                }
            ],
            'due_today_tasks': [
                {
                    'id': '2',
                    'title': 'Send proposal',
                    'reason': 'Next step',
                    'person_id': 'person_2'
                }
            ],
            'overdue_tasks': [
                {
                    'id': '3',
                    'title': 'Review contract',
                    'reason': 'Doc',
                    'person_id': 'person_3'
                }
            ],
            'social_activity': []
        }
        
        action_items = await mock_brief_generator._generate_action_items(brief_data)
        
        assert len(action_items) >= 3
        assert any(item['type'] == 'follow_up' for item in action_items)
        assert any(item['type'] == 'due_today' for item in action_items)
        assert any(item['type'] == 'overdue' for item in action_items)

class TestSystemIntegration:
    """Test system integration functionality"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        from config import Config
        
        # This will test the validation logic
        validation_results = Config.validate_config()
        
        # Should return a dictionary with validation results
        assert isinstance(validation_results, dict)
        assert 'NOTION_TOKEN' in validation_results
        assert 'GMAIL_CLIENT_ID' in validation_results
    
    def test_email_deduplication_integration(self):
        """Test email deduplication with real-world scenarios"""
        engine = EmailDeduplicationEngine()
        
        # Add multiple contacts that should be merged
        contact1_id = engine.add_or_update_contact(
            "john.smith@company.com", "John Smith", "Company Inc"
        )
        
        contact2_id = engine.add_or_update_contact(
            "john.smith@company.com", "John Smith", "Company Inc"
        )
        
        # Should be the same contact due to exact email match
        assert contact1_id == contact2_id
        
        # Should have one email address (no duplicates)
        contact = engine.contacts[contact1_id]
        assert len(contact.email_addresses) == 1

# Integration test that requires actual API keys
@pytest.mark.integration
class TestRealAPIIntegration:
    """Integration tests that require real API keys"""
    
    @pytest.mark.skip(reason="Requires real API keys")
    async def test_notion_workspace_creation(self):
        """Test actual Notion workspace creation"""
        from config import Config
        
        if not Config.NOTION_TOKEN:
            pytest.skip("Notion token not configured")
        
        client = NotionClient(Config.NOTION_TOKEN)
        schema_builder = NotionSchemaBuilder()
        
        # Test creating a single database
        schema = schema_builder.create_people_database()
        db_id = await client.create_database(schema)
        
        assert db_id is not None
        assert len(db_id) > 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
