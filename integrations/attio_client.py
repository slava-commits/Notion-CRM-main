#!/usr/bin/env python3
"""
Production-ready Attio CRM API Client

This module provides a comprehensive, production-ready client for interacting with the Attio CRM API.
It includes proper error handling, logging, type hints, and comprehensive data retrieval capabilities.

Author: Development Team
Version: 1.0.0
License: MIT
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AttioObjectType(Enum):
    """Enumeration of Attio object types"""
    PEOPLE = "people"
    COMPANIES = "companies"
    DEALS = "deals"
    TASKS = "tasks"


@dataclass
class AttioPerson:
    """Data class representing an Attio person record"""
    attio_id: str
    name: str
    first_name: str
    last_name: str
    primary_email: str
    all_emails: List[str]
    company_id: Optional[str]
    job_title: str
    primary_phone: str
    linkedin_url: str
    twitter_handle: str
    first_email_interaction: Optional[datetime]
    last_email_interaction: Optional[datetime]
    first_calendar_interaction: Optional[datetime]
    last_calendar_interaction: Optional[datetime]
    connection_strength: float
    created_at: Optional[datetime]
    web_url: str
    custom_fields: Dict[str, Any]
    raw_data: Dict[str, Any]


@dataclass
class AttioCompany:
    """Data class representing an Attio company record"""
    attio_id: str
    name: str
    domain: str
    website: str
    description: str
    industry: str
    location: str
    employee_count: Optional[int]
    founded_year: Optional[int]
    created_at: Optional[datetime]
    web_url: str
    custom_fields: Dict[str, Any]
    raw_data: Dict[str, Any]


class AttioAPIError(Exception):
    """Custom exception for Attio API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AttioClient:
    """
    Production-ready Attio CRM API client
    
    This class provides comprehensive functionality for interacting with the Attio CRM API,
    including person and company data retrieval, search capabilities, and proper error handling.
    
    Example:
        async with AttioClient(api_key="your_api_key") as client:
            person = await client.get_person_by_email("user@example.com")
            company = await client.get_company_by_id(person.company_id)
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.attio.com/v2", timeout: int = 30):
        """
        Initialize the Attio client
        
        Args:
            api_key: Attio API key for authentication
            base_url: Base URL for the Attio API (default: https://api.attio.com/v2)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not api_key:
            raise ValueError("API key is required")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AttioClient/1.0.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Attio API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            AttioAPIError: If the API request fails
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = f"Attio API error: {response.status}"
                    if isinstance(response_data, dict):
                        error_msg += f" - {response_data.get('message', 'Unknown error')}"
                    
                    logger.error(f"{error_msg} for {method} {url}")
                    raise AttioAPIError(
                        message=error_msg,
                        status_code=response.status,
                        response_data=response_data
                    )
                
                logger.debug(f"Successfully completed {method} request to {url}")
                return response_data
                
        except aiohttp.ClientError as e:
            error_msg = f"Network error during {method} request to {url}: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from {url}: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during {method} request to {url}: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
    
    async def test_connection(self) -> bool:
        """
        Test the connection to the Attio API
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            await self._make_request("GET", "objects/people?limit=1")
            logger.info("✅ Attio API connection test successful")
            return True
        except AttioAPIError as e:
            logger.error(f"❌ Attio API connection test failed: {e}")
            return False
    
    async def get_person_by_email(self, email: str) -> Optional[AttioPerson]:
        """
        Get person data by email address using the working PUT endpoint
        
        Args:
            email: Email address to search for
            
        Returns:
            AttioPerson object if found, None otherwise
            
        Raises:
            AttioAPIError: If the API request fails
        """
        try:
            endpoint = "objects/people/records?matching_attribute=email_addresses"
            data = {
                "data": {
                    "values": {
                        "email_addresses": [email]
                    }
                }
            }
            
            logger.info(f"Searching for person with email: {email}")
            response = await self._make_request("PUT", endpoint, data)
            
            if 'data' in response and response['data']:
                person_data = response['data']
                logger.info(f"✅ Found person: {email}")
                return self._parse_person_data(person_data)
            else:
                logger.warning(f"⚠️ No person found with email: {email}")
                return None
                
        except AttioAPIError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting person by email {email}: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
    
    async def get_company_by_id(self, company_id: str) -> Optional[AttioCompany]:
        """
        Get company data by company ID
        
        Args:
            company_id: Company record ID
            
        Returns:
            AttioCompany object if found, None otherwise
            
        Raises:
            AttioAPIError: If the API request fails
        """
        try:
            # Try the working endpoint first
            endpoint = f"objects/companies/records/{company_id}"
            
            logger.info(f"Getting company data for ID: {company_id}")
            response = await self._make_request("GET", endpoint)
            
            if 'data' in response and response['data']:
                company_data = response['data']
                logger.info(f"✅ Found company with ID: {company_id}")
                return self._parse_company_data(company_data)
            else:
                logger.warning(f"⚠️ No company found with ID: {company_id}")
                return None
                
        except AttioAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Company with ID {company_id} not found")
                return None
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting company by ID {company_id}: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
    
    async def get_people(self, limit: int = 100, offset: int = 0) -> List[AttioPerson]:
        """
        Get a list of people from Attio
        
        Args:
            limit: Maximum number of people to retrieve (default: 100)
            offset: Number of people to skip (default: 0)
            
        Returns:
            List of AttioPerson objects
            
        Raises:
            AttioAPIError: If the API request fails
        """
        try:
            endpoint = f"objects/people?limit={limit}&offset={offset}"
            
            logger.info(f"Getting {limit} people (offset: {offset})")
            response = await self._make_request("GET", endpoint)
            
            people = []
            if 'data' in response and isinstance(response['data'], list):
                for person_data in response['data']:
                    try:
                        person = self._parse_person_data(person_data)
                        if person:
                            people.append(person)
                    except Exception as e:
                        logger.warning(f"Failed to parse person data: {e}")
                        continue
            
            logger.info(f"✅ Retrieved {len(people)} people")
            return people
            
        except AttioAPIError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting people: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
    
    async def get_companies(self, limit: int = 100, offset: int = 0) -> List[AttioCompany]:
        """
        Get a list of companies from Attio
        
        Args:
            limit: Maximum number of companies to retrieve (default: 100)
            offset: Number of companies to skip (default: 0)
            
        Returns:
            List of AttioCompany objects
            
        Raises:
            AttioAPIError: If the API request fails
        """
        try:
            endpoint = f"objects/companies?limit={limit}&offset={offset}"
            
            logger.info(f"Getting {limit} companies (offset: {offset})")
            response = await self._make_request("GET", endpoint)
            
            companies = []
            if 'data' in response and isinstance(response['data'], list):
                for company_data in response['data']:
                    try:
                        company = self._parse_company_data(company_data)
                        if company:
                            companies.append(company)
                    except Exception as e:
                        logger.warning(f"Failed to parse company data: {e}")
                        continue
            
            logger.info(f"✅ Retrieved {len(companies)} companies")
            return companies
            
        except AttioAPIError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting companies: {str(e)}"
            logger.error(error_msg)
            raise AttioAPIError(message=error_msg)
    
    def _parse_person_data(self, person_data: Dict[str, Any]) -> Optional[AttioPerson]:
        """
        Parse raw Attio person data into AttioPerson object
        
        Args:
            person_data: Raw person data from Attio API
            
        Returns:
            AttioPerson object or None if parsing fails
        """
        try:
            # Extract basic info
            record_id = person_data.get('id', {}).get('record_id', '')
            values = person_data.get('values', {})
            
            # Extract name
            name_data = values.get('name', [{}])[0] if values.get('name') else {}
            full_name = name_data.get('full_name', '')
            first_name = name_data.get('first_name', '')
            last_name = name_data.get('last_name', '')
            
            # Extract email
            email_data = values.get('email_addresses', [{}])[0] if values.get('email_addresses') else {}
            primary_email = email_data.get('email_address', '')
            all_emails = [primary_email] if primary_email else []
            
            # Extract company
            company_data = values.get('company', [{}])[0] if values.get('company') else {}
            company_id = company_data.get('target_record_id', '') if company_data else None
            
            # Extract job title
            job_title_data = values.get('job_title', [{}])[0] if values.get('job_title') else {}
            job_title = job_title_data.get('value', '') if job_title_data else ''
            
            # Extract phone
            phone_data = values.get('phone_numbers', [{}])[0] if values.get('phone_numbers') else {}
            primary_phone = phone_data.get('value', '') if phone_data else ''
            
            # Extract social media
            linkedin_data = values.get('linkedin', [{}])[0] if values.get('linkedin') else {}
            linkedin_url = linkedin_data.get('value', '') if linkedin_data else ''
            
            twitter_data = values.get('twitter', [{}])[0] if values.get('twitter') else {}
            twitter_handle = twitter_data.get('value', '') if twitter_data else ''
            
            # Extract interaction data
            first_email = values.get('first_email_interaction', [{}])[0] if values.get('first_email_interaction') else {}
            last_email = values.get('last_email_interaction', [{}])[0] if values.get('last_email_interaction') else {}
            first_calendar = values.get('first_calendar_interaction', [{}])[0] if values.get('first_calendar_interaction') else {}
            last_calendar = values.get('last_calendar_interaction', [{}])[0] if values.get('last_calendar_interaction') else {}
            
            # Extract connection strength
            connection_strength = values.get('strongest_connection_strength_legacy', [{}])[0] if values.get('strongest_connection_strength_legacy') else {}
            connection_value = connection_strength.get('value', 0.0) if connection_strength else 0.0
            
            # Extract timestamps
            created_at = values.get('created_at', [{}])[0] if values.get('created_at') else {}
            created_timestamp = created_at.get('value', '') if created_at else ''
            
            # Parse datetime fields
            first_email_dt = self._parse_datetime(first_email.get('interacted_at', '')) if first_email else None
            last_email_dt = self._parse_datetime(last_email.get('interacted_at', '')) if last_email else None
            first_calendar_dt = self._parse_datetime(first_calendar.get('interacted_at', '')) if first_calendar else None
            last_calendar_dt = self._parse_datetime(last_calendar.get('interacted_at', '')) if last_calendar else None
            created_dt = self._parse_datetime(created_timestamp) if created_timestamp else None
            
            # Extract custom fields
            custom_fields = {}
            excluded_fields = {
                'record_id', 'name', 'email_addresses', 'company', 'job_title', 
                'phone_numbers', 'linkedin', 'twitter', 'first_email_interaction',
                'last_email_interaction', 'first_calendar_interaction', 
                'last_calendar_interaction', 'strongest_connection_strength_legacy',
                'created_at', 'avatar_url', 'primary_location', 'website',
                'telegram', 'comments', 'summary', 'fathomcalls', 'next_actions',
                'linkedin_description', 'connection_degree_with_anna', 
                'mutual_connections_with_anna', 'associated_deals', 'associated_users',
                'created_by', 'angellist', 'facebook', 'instagram', 'twitter_follower_count',
                'next_calendar_interaction', 'next_interaction', 'strongest_connection_strength',
                'strongest_connection_user', 'description'
            }
            
            for key, value in values.items():
                if key not in excluded_fields and value and isinstance(value, list) and len(value) > 0:
                    field_value = value[0].get('value', '') if isinstance(value[0], dict) else str(value[0])
                    if field_value:
                        custom_fields[key] = field_value
            
            return AttioPerson(
                attio_id=record_id,
                name=full_name,
                first_name=first_name,
                last_name=last_name,
                primary_email=primary_email,
                all_emails=all_emails,
                company_id=company_id,
                job_title=job_title,
                primary_phone=primary_phone,
                linkedin_url=linkedin_url,
                twitter_handle=twitter_handle,
                first_email_interaction=first_email_dt,
                last_email_interaction=last_email_dt,
                first_calendar_interaction=first_calendar_dt,
                last_calendar_interaction=last_calendar_dt,
                connection_strength=connection_value,
                created_at=created_dt,
                web_url=person_data.get('web_url', ''),
                custom_fields=custom_fields,
                raw_data=person_data
            )
            
        except Exception as e:
            logger.error(f"Failed to parse person data: {e}")
            logger.debug(f"Person data: {person_data}")
            return None
    
    def _parse_company_data(self, company_data: Dict[str, Any]) -> Optional[AttioCompany]:
        """
        Parse raw Attio company data into AttioCompany object
        
        Args:
            company_data: Raw company data from Attio API
            
        Returns:
            AttioCompany object or None if parsing fails
        """
        try:
            # Extract basic info
            record_id = company_data.get('id', {}).get('record_id', '')
            values = company_data.get('values', {})
            
            # Extract company name
            name_data = values.get('name', [{}])[0] if values.get('name') else {}
            company_name = name_data.get('value', '') if name_data else ''
            
            # Extract domain
            domain_data = values.get('domain', [{}])[0] if values.get('domain') else {}
            domain = domain_data.get('value', '') if domain_data else ''
            
            # Extract website
            website_data = values.get('website', [{}])[0] if values.get('website') else {}
            website = website_data.get('value', '') if website_data else ''
            
            # Extract description
            description_data = values.get('description', [{}])[0] if values.get('description') else {}
            description = description_data.get('value', '') if description_data else ''
            
            # Extract industry
            industry_data = values.get('industry', [{}])[0] if values.get('industry') else {}
            industry = industry_data.get('value', '') if industry_data else ''
            
            # Extract location
            location_data = values.get('primary_location', [{}])[0] if values.get('primary_location') else {}
            location = location_data.get('value', '') if location_data else ''
            
            # Extract employee count
            employee_count_data = values.get('employee_count', [{}])[0] if values.get('employee_count') else {}
            employee_count = employee_count_data.get('value', None) if employee_count_data else None
            if employee_count is not None:
                try:
                    employee_count = int(employee_count)
                except (ValueError, TypeError):
                    employee_count = None
            
            # Extract founded year
            founded_year_data = values.get('founded_year', [{}])[0] if values.get('founded_year') else {}
            founded_year = founded_year_data.get('value', None) if founded_year_data else None
            if founded_year is not None:
                try:
                    founded_year = int(founded_year)
                except (ValueError, TypeError):
                    founded_year = None
            
            # Extract timestamps
            created_at = values.get('created_at', [{}])[0] if values.get('created_at') else {}
            created_timestamp = created_at.get('value', '') if created_at else ''
            created_dt = self._parse_datetime(created_timestamp) if created_timestamp else None
            
            # Extract custom fields
            custom_fields = {}
            excluded_fields = {
                'record_id', 'name', 'domain', 'website', 'description', 
                'industry', 'primary_location', 'employee_count', 'founded_year',
                'created_at', 'updated_at', 'linkedin', 'twitter', 'facebook',
                'instagram', 'angellist', 'crunchbase', 'pitchbook', 'associated_deals',
                'associated_users', 'created_by', 'summary', 'next_actions'
            }
            
            for key, value in values.items():
                if key not in excluded_fields and value and isinstance(value, list) and len(value) > 0:
                    field_value = value[0].get('value', '') if isinstance(value[0], dict) else str(value[0])
                    if field_value:
                        custom_fields[key] = field_value
            
            return AttioCompany(
                attio_id=record_id,
                name=company_name,
                domain=domain,
                website=website,
                description=description,
                industry=industry,
                location=location,
                employee_count=employee_count,
                founded_year=founded_year,
                created_at=created_dt,
                web_url=company_data.get('web_url', ''),
                custom_fields=custom_fields,
                raw_data=company_data
            )
            
        except Exception as e:
            logger.error(f"Failed to parse company data: {e}")
            logger.debug(f"Company data: {company_data}")
            return None
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Parse datetime string from Attio API
        
        Args:
            datetime_str: Datetime string from Attio API
            
        Returns:
            datetime object or None if parsing fails
        """
        if not datetime_str:
            return None
        
        try:
            # Handle different datetime formats from Attio
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse datetime: {datetime_str}")
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing datetime {datetime_str}: {e}")
            return None


# Example usage and testing
async def main():
    """Example usage of the AttioClient"""
    import os
    from config import Config
    
    # Get API key from config
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        print("❌ ATTIO_API_KEY not found in config")
        return
    
    try:
        async with AttioClient(api_key) as client:
            # Test connection
            if not await client.test_connection():
                print("❌ Connection test failed")
                return
            
            # Get person by email
            person = await client.get_person_by_email("ethan@tuesday.vc")
            if person:
                print(f"✅ Found person: {person.name} ({person.primary_email})")
                
                # Get company if available
                if person.company_id:
                    company = await client.get_company_by_id(person.company_id)
                    if company:
                        print(f"✅ Found company: {company.name}")
                    else:
                        print("⚠️ Company not found")
                else:
                    print("⚠️ No company associated")
            else:
                print("❌ Person not found")
                
    except AttioAPIError as e:
        print(f"❌ Attio API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
