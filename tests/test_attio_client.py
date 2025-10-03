#!/usr/bin/env python3
"""
Unit tests for the production AttioClient

This module contains comprehensive unit tests for the AttioClient class,
including tests for data parsing, error handling, and API interactions.

Author: Development Team
Version: 1.0.0
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import json

from integrations.attio_client import (
    AttioClient, 
    AttioPerson, 
    AttioCompany, 
    AttioAPIError,
    AttioObjectType
)


class TestAttioClient:
    """Test cases for AttioClient class"""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance"""
        return AttioClient(api_key="test_api_key")
    
    @pytest.fixture
    def sample_person_data(self):
        """Sample person data from Attio API"""
        return {
            "id": {"record_id": "test-person-id"},
            "values": {
                "name": [{"full_name": "John Doe", "first_name": "John", "last_name": "Doe"}],
                "email_addresses": [{"email_address": "john@example.com"}],
                "company": [{"target_record_id": "test-company-id"}],
                "job_title": [{"value": "Software Engineer"}],
                "phone_numbers": [{"value": "+1234567890"}],
                "linkedin": [{"value": "https://linkedin.com/in/johndoe"}],
                "twitter": [{"value": "@johndoe"}],
                "first_email_interaction": [{"interacted_at": "2025-01-01T10:00:00Z"}],
                "last_email_interaction": [{"interacted_at": "2025-01-15T15:30:00Z"}],
                "first_calendar_interaction": [{"interacted_at": "2025-01-05T14:00:00Z"}],
                "last_calendar_interaction": [{"interacted_at": "2025-01-10T16:00:00Z"}],
                "strongest_connection_strength_legacy": [{"value": 85.5}],
                "created_at": [{"value": "2025-01-01T08:00:00Z"}]
            },
            "web_url": "https://app.attio.com/person/test-person-id"
        }
    
    @pytest.fixture
    def sample_company_data(self):
        """Sample company data from Attio API"""
        return {
            "id": {"record_id": "test-company-id"},
            "values": {
                "name": [{"value": "Test Company Inc."}],
                "domain": [{"value": "testcompany.com"}],
                "website": [{"value": "https://testcompany.com"}],
                "description": [{"value": "A test company for unit testing"}],
                "industry": [{"value": "Technology"}],
                "primary_location": [{"value": "San Francisco, CA"}],
                "employee_count": [{"value": "50"}],
                "founded_year": [{"value": "2020"}],
                "created_at": [{"value": "2025-01-01T08:00:00Z"}]
            },
            "web_url": "https://app.attio.com/company/test-company-id"
        }
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = AttioClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.attio.com/v2"
        assert client.timeout.total == 30
    
    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters"""
        client = AttioClient(
            api_key="test_key",
            base_url="https://custom.attio.com/v3",
            timeout=60
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.attio.com/v3"
        assert client.timeout.total == 60
    
    def test_client_initialization_without_api_key(self):
        """Test that client raises error without API key"""
        with pytest.raises(ValueError, match="API key is required"):
            AttioClient(api_key="")
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager functionality"""
        async with client as ctx:
            assert ctx is client
            assert client.session is not None
            assert isinstance(client.session, aiohttp.ClientSession)
        
        # Session should be closed after context exit
        assert client.session.closed
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test successful API request"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})
        
        with patch.object(client.session, 'request', return_value=mock_response) as mock_request:
            async with client:
                result = await client._make_request("GET", "test/endpoint")
                assert result == {"data": "test"}
                mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_api_error(self, client):
        """Test API error handling"""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={"message": "Not found"})
        
        with patch.object(client.session, 'request', return_value=mock_response):
            async with client:
                with pytest.raises(AttioAPIError) as exc_info:
                    await client._make_request("GET", "test/endpoint")
                
                assert exc_info.value.status_code == 404
                assert "Not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        """Test network error handling"""
        with patch.object(client.session, 'request', side_effect=aiohttp.ClientError("Network error")):
            async with client:
                with pytest.raises(AttioAPIError) as exc_info:
                    await client._make_request("GET", "test/endpoint")
                
                assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_without_session(self, client):
        """Test that request fails without initialized session"""
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client._make_request("GET", "test/endpoint")
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, client):
        """Test successful connection test"""
        with patch.object(client, '_make_request', return_value={"data": []}):
            async with client:
                result = await client.test_connection()
                assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, client):
        """Test failed connection test"""
        with patch.object(client, '_make_request', side_effect=AttioAPIError("Connection failed")):
            async with client:
                result = await client.test_connection()
                assert result is False
    
    @pytest.mark.asyncio
    async def test_get_person_by_email_success(self, client, sample_person_data):
        """Test successful person retrieval by email"""
        with patch.object(client, '_make_request', return_value={"data": sample_person_data}):
            async with client:
                person = await client.get_person_by_email("john@example.com")
                
                assert person is not None
                assert isinstance(person, AttioPerson)
                assert person.attio_id == "test-person-id"
                assert person.name == "John Doe"
                assert person.primary_email == "john@example.com"
                assert person.company_id == "test-company-id"
    
    @pytest.mark.asyncio
    async def test_get_person_by_email_not_found(self, client):
        """Test person not found by email"""
        with patch.object(client, '_make_request', return_value={"data": None}):
            async with client:
                person = await client.get_person_by_email("nonexistent@example.com")
                assert person is None
    
    @pytest.mark.asyncio
    async def test_get_company_by_id_success(self, client, sample_company_data):
        """Test successful company retrieval by ID"""
        with patch.object(client, '_make_request', return_value={"data": sample_company_data}):
            async with client:
                company = await client.get_company_by_id("test-company-id")
                
                assert company is not None
                assert isinstance(company, AttioCompany)
                assert company.attio_id == "test-company-id"
                assert company.name == "Test Company Inc."
                assert company.domain == "testcompany.com"
                assert company.employee_count == 50
                assert company.founded_year == 2020
    
    @pytest.mark.asyncio
    async def test_get_company_by_id_not_found(self, client):
        """Test company not found by ID"""
        with patch.object(client, '_make_request', side_effect=AttioAPIError("Not found", 404)):
            async with client:
                company = await client.get_company_by_id("nonexistent-id")
                assert company is None
    
    @pytest.mark.asyncio
    async def test_get_people_success(self, client, sample_person_data):
        """Test successful people list retrieval"""
        with patch.object(client, '_make_request', return_value={"data": [sample_person_data]}):
            async with client:
                people = await client.get_people(limit=10)
                
                assert len(people) == 1
                assert isinstance(people[0], AttioPerson)
                assert people[0].name == "John Doe"
    
    @pytest.mark.asyncio
    async def test_get_companies_success(self, client, sample_company_data):
        """Test successful companies list retrieval"""
        with patch.object(client, '_make_request', return_value={"data": [sample_company_data]}):
            async with client:
                companies = await client.get_companies(limit=10)
                
                assert len(companies) == 1
                assert isinstance(companies[0], AttioCompany)
                assert companies[0].name == "Test Company Inc."
    
    def test_parse_person_data_complete(self, client, sample_person_data):
        """Test parsing complete person data"""
        person = client._parse_person_data(sample_person_data)
        
        assert person is not None
        assert person.attio_id == "test-person-id"
        assert person.name == "John Doe"
        assert person.first_name == "John"
        assert person.last_name == "Doe"
        assert person.primary_email == "john@example.com"
        assert person.company_id == "test-company-id"
        assert person.job_title == "Software Engineer"
        assert person.primary_phone == "+1234567890"
        assert person.linkedin_url == "https://linkedin.com/in/johndoe"
        assert person.twitter_handle == "@johndoe"
        assert person.connection_strength == 85.5
        assert person.web_url == "https://app.attio.com/person/test-person-id"
        assert isinstance(person.first_email_interaction, datetime)
        assert isinstance(person.last_email_interaction, datetime)
        assert isinstance(person.created_at, datetime)
    
    def test_parse_person_data_minimal(self, client):
        """Test parsing minimal person data"""
        minimal_data = {
            "id": {"record_id": "minimal-id"},
            "values": {
                "name": [{"full_name": "Jane Doe"}],
                "email_addresses": [{"email_address": "jane@example.com"}]
            },
            "web_url": "https://app.attio.com/person/minimal-id"
        }
        
        person = client._parse_person_data(minimal_data)
        
        assert person is not None
        assert person.attio_id == "minimal-id"
        assert person.name == "Jane Doe"
        assert person.primary_email == "jane@example.com"
        assert person.company_id is None
        assert person.job_title == ""
        assert person.connection_strength == 0.0
        assert person.first_email_interaction is None
    
    def test_parse_company_data_complete(self, client, sample_company_data):
        """Test parsing complete company data"""
        company = client._parse_company_data(sample_company_data)
        
        assert company is not None
        assert company.attio_id == "test-company-id"
        assert company.name == "Test Company Inc."
        assert company.domain == "testcompany.com"
        assert company.website == "https://testcompany.com"
        assert company.description == "A test company for unit testing"
        assert company.industry == "Technology"
        assert company.location == "San Francisco, CA"
        assert company.employee_count == 50
        assert company.founded_year == 2020
        assert company.web_url == "https://app.attio.com/company/test-company-id"
        assert isinstance(company.created_at, datetime)
    
    def test_parse_company_data_minimal(self, client):
        """Test parsing minimal company data"""
        minimal_data = {
            "id": {"record_id": "minimal-company-id"},
            "values": {
                "name": [{"value": "Minimal Company"}]
            },
            "web_url": "https://app.attio.com/company/minimal-company-id"
        }
        
        company = client._parse_company_data(minimal_data)
        
        assert company is not None
        assert company.attio_id == "minimal-company-id"
        assert company.name == "Minimal Company"
        assert company.domain == ""
        assert company.employee_count is None
        assert company.founded_year is None
        assert company.created_at is None
    
    def test_parse_datetime_valid_formats(self, client):
        """Test datetime parsing with valid formats"""
        test_cases = [
            ("2025-01-01T10:00:00.000000Z", datetime(2025, 1, 1, 10, 0, 0)),
            ("2025-01-01T10:00:00Z", datetime(2025, 1, 1, 10, 0, 0)),
            ("2025-01-01 10:00:00", datetime(2025, 1, 1, 10, 0, 0)),
            ("2025-01-01", datetime(2025, 1, 1, 0, 0, 0))
        ]
        
        for datetime_str, expected in test_cases:
            result = client._parse_datetime(datetime_str)
            assert result == expected, f"Failed to parse {datetime_str}"
    
    def test_parse_datetime_invalid_formats(self, client):
        """Test datetime parsing with invalid formats"""
        invalid_cases = [
            "",
            "invalid-date",
            "2025-13-01T10:00:00Z",  # Invalid month
            None
        ]
        
        for invalid_date in invalid_cases:
            result = client._parse_datetime(invalid_date)
            assert result is None, f"Should return None for {invalid_date}"
    
    def test_parse_person_data_invalid(self, client):
        """Test parsing invalid person data"""
        invalid_data = {
            "id": "invalid-id-format",  # Should be dict with record_id
            "values": "invalid-values-format"  # Should be dict
        }
        
        person = client._parse_person_data(invalid_data)
        assert person is None
    
    def test_parse_company_data_invalid(self, client):
        """Test parsing invalid company data"""
        invalid_data = {
            "id": "invalid-id-format",  # Should be dict with record_id
            "values": "invalid-values-format"  # Should be dict
        }
        
        company = client._parse_company_data(invalid_data)
        assert company is None


class TestAttioPerson:
    """Test cases for AttioPerson dataclass"""
    
    def test_attio_person_creation(self):
        """Test AttioPerson object creation"""
        person = AttioPerson(
            attio_id="test-id",
            name="Test Person",
            first_name="Test",
            last_name="Person",
            primary_email="test@example.com",
            all_emails=["test@example.com"],
            company_id="company-id",
            job_title="Engineer",
            primary_phone="+1234567890",
            linkedin_url="https://linkedin.com/in/test",
            twitter_handle="@test",
            first_email_interaction=datetime(2025, 1, 1),
            last_email_interaction=datetime(2025, 1, 15),
            first_calendar_interaction=datetime(2025, 1, 5),
            last_calendar_interaction=datetime(2025, 1, 10),
            connection_strength=75.5,
            created_at=datetime(2025, 1, 1),
            web_url="https://app.attio.com/person/test-id",
            custom_fields={"custom_field": "value"},
            raw_data={"id": "test-id"}
        )
        
        assert person.attio_id == "test-id"
        assert person.name == "Test Person"
        assert person.primary_email == "test@example.com"
        assert person.connection_strength == 75.5


class TestAttioCompany:
    """Test cases for AttioCompany dataclass"""
    
    def test_attio_company_creation(self):
        """Test AttioCompany object creation"""
        company = AttioCompany(
            attio_id="company-id",
            name="Test Company",
            domain="testcompany.com",
            website="https://testcompany.com",
            description="A test company",
            industry="Technology",
            location="San Francisco, CA",
            employee_count=100,
            founded_year=2020,
            created_at=datetime(2025, 1, 1),
            web_url="https://app.attio.com/company/company-id",
            custom_fields={"custom_field": "value"},
            raw_data={"id": "company-id"}
        )
        
        assert company.attio_id == "company-id"
        assert company.name == "Test Company"
        assert company.employee_count == 100
        assert company.founded_year == 2020


class TestAttioAPIError:
    """Test cases for AttioAPIError exception"""
    
    def test_attio_api_error_creation(self):
        """Test AttioAPIError creation"""
        error = AttioAPIError("Test error", 404, {"message": "Not found"})
        
        assert str(error) == "Test error"
        assert error.status_code == 404
        assert error.response_data == {"message": "Not found"}
    
    def test_attio_api_error_minimal(self):
        """Test AttioAPIError creation with minimal parameters"""
        error = AttioAPIError("Test error")
        
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_data is None


# Integration test (requires real API key)
@pytest.mark.integration
class TestAttioClientIntegration:
    """Integration tests for AttioClient (requires real API key)"""
    
    @pytest.mark.asyncio
    async def test_real_api_connection(self):
        """Test connection to real Attio API"""
        import os
        from config import Config
        
        api_key = Config.ATTIO_API_KEY
        if not api_key:
            pytest.skip("ATTIO_API_KEY not available for integration test")
        
        async with AttioClient(api_key) as client:
            result = await client.test_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_real_person_retrieval(self):
        """Test real person retrieval from Attio API"""
        import os
        from config import Config
        
        api_key = Config.ATTIO_API_KEY
        if not api_key:
            pytest.skip("ATTIO_API_KEY not available for integration test")
        
        async with AttioClient(api_key) as client:
            person = await client.get_person_by_email("ethan@tuesday.vc")
            if person:
                assert isinstance(person, AttioPerson)
                assert person.primary_email == "ethan@tuesday.vc"
                assert person.name is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
