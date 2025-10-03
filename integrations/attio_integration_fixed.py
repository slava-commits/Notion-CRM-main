#!/usr/bin/env python3
"""
Attio Integration - Fixed Version
Handles Attio CRM API interactions for client data synchronization
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AttioIntegrationFixed:
    """Attio CRM API integration - Fixed version"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.attio.com/v2"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Attio API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Attio API error: {response.status} - {error_text}")
                    raise Exception(f"Attio API error: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"Attio API request failed: {e}")
            raise
    
    async def get_people(self, limit: int = 100) -> List[Dict]:
        """Get all people from Attio"""
        try:
            response = await self._make_request("GET", f"objects/people?limit={limit}")
            
            people = []
            data = response.get('data', [])
            
            # Handle different response structures
            if isinstance(data, list):
                for person in data:
                    person_data = await self._parse_person(person)
                    if person_data:
                        people.append(person_data)
            elif isinstance(data, dict):
                # Sometimes the response is wrapped differently
                for person in data.get('results', []):
                    person_data = await self._parse_person(person)
                    if person_data:
                        people.append(person_data)
            
            return people
            
        except Exception as e:
            logger.error(f"Failed to get people from Attio: {e}")
            return []
    
    async def _parse_person(self, person: Dict) -> Optional[Dict]:
        """Parse Attio person into standardized format"""
        try:
            # Handle different response structures
            if isinstance(person, str):
                logger.warning(f"Received string instead of dict: {person}")
                return None
            
            person_id = person.get('id', {}).get('value', '') if isinstance(person.get('id'), dict) else str(person.get('id', ''))
            attributes = person.get('attributes', {})
            
            # Extract basic information
            name = attributes.get('name', {}).get('value', '') if isinstance(attributes.get('name'), dict) else str(attributes.get('name', ''))
            
            # Handle email addresses
            email_data = attributes.get('email_addresses', {})
            if isinstance(email_data, dict):
                email = email_data.get('value', [])
            else:
                email = [email_data] if email_data else []
            primary_email = email[0] if email else ''
            
            # Extract company information
            company = attributes.get('company', {}).get('value', '') if isinstance(attributes.get('company'), dict) else str(attributes.get('company', ''))
            job_title = attributes.get('job_title', {}).get('value', '') if isinstance(attributes.get('job_title'), dict) else str(attributes.get('job_title', ''))
            
            # Extract contact information
            phone_data = attributes.get('phone_numbers', {})
            if isinstance(phone_data, dict):
                phone = phone_data.get('value', [])
            else:
                phone = [phone_data] if phone_data else []
            primary_phone = phone[0] if phone else ''
            
            # Extract social media
            linkedin_url = attributes.get('linkedin_url', {}).get('value', '') if isinstance(attributes.get('linkedin_url'), dict) else str(attributes.get('linkedin_url', ''))
            twitter_handle = attributes.get('twitter_handle', {}).get('value', '') if isinstance(attributes.get('twitter_handle'), dict) else str(attributes.get('twitter_handle', ''))
            
            # Extract additional fields
            created_at = attributes.get('created_at', {}).get('value', '') if isinstance(attributes.get('created_at'), dict) else str(attributes.get('created_at', ''))
            updated_at = attributes.get('updated_at', {}).get('value', '') if isinstance(attributes.get('updated_at'), dict) else str(attributes.get('updated_at', ''))
            
            # Extract custom fields
            custom_fields = {}
            for key, value in attributes.items():
                if key not in ['name', 'email_addresses', 'company', 'job_title', 
                              'phone_numbers', 'linkedin_url', 'twitter_handle', 
                              'created_at', 'updated_at']:
                    if isinstance(value, dict):
                        custom_fields[key] = value.get('value', '')
                    else:
                        custom_fields[key] = str(value) if value is not None else ''
            
            return {
                'attio_id': person_id,
                'name': name,
                'primary_email': primary_email,
                'all_emails': email,
                'company': company,
                'job_title': job_title,
                'primary_phone': primary_phone,
                'linkedin_url': linkedin_url,
                'twitter_handle': twitter_handle,
                'created_at': created_at,
                'updated_at': updated_at,
                'custom_fields': custom_fields,
                'source': 'attio',
                'raw_data': person  # Include raw data for debugging
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Attio person: {e}")
            logger.error(f"Person data: {person}")
            return None
    
    async def search_people_by_email(self, email: str) -> List[Dict]:
        """Search for people by email address"""
        try:
            # Get all people and filter by email
            all_people = await self.get_people(limit=1000)
            
            matching_people = []
            for person in all_people:
                if email.lower() in person.get('primary_email', '').lower():
                    matching_people.append(person)
                elif email.lower() in [e.lower() for e in person.get('all_emails', [])]:
                    matching_people.append(person)
            
            return matching_people
            
        except Exception as e:
            logger.error(f"Failed to search people by email {email}: {e}")
            return []
    
    async def get_person_by_id(self, person_id: str) -> Optional[Dict]:
        """Get specific person by ID"""
        try:
            response = await self._make_request("GET", f"objects/people/{person_id}")
            return await self._parse_person(response.get('data', {}))
        except Exception as e:
            logger.error(f"Failed to get person {person_id}: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Test the Attio API connection"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            response = await self._make_request("GET", "objects/people?limit=1")
            return True
        except Exception as e:
            logger.error(f"Attio connection test failed: {e}")
            return False
    
    async def get_all_people(self) -> List[Dict]:
        """Get all people from Attio (alias for get_people)"""
        return await self.get_people(limit=1000)

# Example usage
if __name__ == "__main__":
    print("Attio Integration Fixed - Ready to use!")
    print("This module handles Attio CRM API interactions for client data synchronization.")
