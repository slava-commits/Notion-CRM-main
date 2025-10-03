#!/usr/bin/env python3
"""
Get Ethan's complete information including company details from Attio
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttioCompleteIntegration:
    """Attio CRM API integration - Complete data with company details"""
    
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
    
    async def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Attio API"""
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
    
    async def get_person_by_email(self, email: str) -> Optional[Dict]:
        """Get person data using the working PUT endpoint"""
        try:
            url = f"{self.base_url}/objects/people/records?matching_attribute=email_addresses"
            data = {
                "data": {
                    "values": {
                        "email_addresses": [email]
                    }
                }
            }
            
            logger.info(f"Getting person data for {email} using PUT endpoint...")
            response = await self._make_request("PUT", url, data)
            
            if 'data' in response and response['data']:
                person_data = response['data']
                logger.info(f"✅ Successfully retrieved person data for {email}")
                return await self._parse_attio_person(person_data)
            else:
                logger.error(f"❌ No data found for {email}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get person by email {email}: {e}")
            return None
    
    async def get_company_by_id(self, company_id: str) -> Optional[Dict]:
        """Get company data by company ID using different endpoints"""
        try:
            # Try different possible endpoints for companies
            endpoints_to_try = [
                f"{self.base_url}/objects/companies/{company_id}",
                f"{self.base_url}/companies/{company_id}",
                f"{self.base_url}/objects/companies/records/{company_id}",
                f"{self.base_url}/companies/records/{company_id}"
            ]
            
            for url in endpoints_to_try:
                try:
                    logger.info(f"Trying endpoint: {url}")
                    response = await self._make_request("GET", url)
                    
                    if 'data' in response and response['data']:
                        company_data = response['data']
                        logger.info(f"✅ Successfully retrieved company data for ID: {company_id}")
                        return await self._parse_attio_company(company_data)
                        
                except Exception as e:
                    logger.warning(f"Endpoint {url} failed: {e}")
                    continue
            
            # If direct ID lookup fails, try to get all companies and filter
            logger.info("Direct company lookup failed, trying to get all companies...")
            return await self._get_company_from_list(company_id)
                
        except Exception as e:
            logger.error(f"Failed to get company by ID {company_id}: {e}")
            return None
    
    async def _get_company_from_list(self, company_id: str) -> Optional[Dict]:
        """Get company by searching through all companies"""
        try:
            # Try to get all companies
            endpoints_to_try = [
                f"{self.base_url}/objects/companies",
                f"{self.base_url}/companies",
                f"{self.base_url}/objects/companies/records"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Trying to get all companies from: {endpoint}")
                    response = await self._make_request("GET", endpoint)
                    
                    if 'data' in response and response['data']:
                        companies = response['data']
                        logger.info(f"Found {len(companies)} companies")
                        
                        # Search for the specific company ID
                        for company in companies:
                            if isinstance(company, dict):
                                # Check different possible ID fields
                                company_record_id = company.get('id', {}).get('record_id', '') if isinstance(company.get('id'), dict) else str(company.get('id', ''))
                                if company_record_id == company_id:
                                    logger.info(f"✅ Found company with ID: {company_id}")
                                    return await self._parse_attio_company(company)
                        
                        logger.warning(f"Company with ID {company_id} not found in {len(companies)} companies")
                        return None
                        
                except Exception as e:
                    logger.warning(f"Failed to get companies from {endpoint}: {e}")
                    continue
            
            logger.error("Could not retrieve companies from any endpoint")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get company from list: {e}")
            return None
    
    async def _parse_attio_person(self, person_data: Dict) -> Dict:
        """Parse Attio person data into standardized format"""
        try:
            # Extract basic info
            record_id = person_data['id']['record_id']
            values = person_data['values']
            
            # Extract name
            name_data = values.get('name', [{}])[0] if values.get('name') else {}
            full_name = name_data.get('full_name', '')
            first_name = name_data.get('first_name', '')
            last_name = name_data.get('last_name', '')
            
            # Extract email
            email_data = values.get('email_addresses', [{}])[0] if values.get('email_addresses') else {}
            primary_email = email_data.get('email_address', '')
            
            # Extract company
            company_data = values.get('company', [{}])[0] if values.get('company') else {}
            company_id = company_data.get('target_record_id', '') if company_data else ''
            
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
            connection_value = connection_strength.get('value', 0) if connection_strength else 0
            
            # Extract timestamps
            created_at = values.get('created_at', [{}])[0] if values.get('created_at') else {}
            created_timestamp = created_at.get('value', '') if created_at else ''
            
            # Extract custom fields
            custom_fields = {}
            for key, value in values.items():
                if key not in ['record_id', 'name', 'email_addresses', 'company', 'job_title', 
                              'phone_numbers', 'linkedin', 'twitter', 'first_email_interaction',
                              'last_email_interaction', 'first_calendar_interaction', 
                              'last_calendar_interaction', 'strongest_connection_strength_legacy',
                              'created_at', 'avatar_url', 'primary_location', 'website',
                              'telegram', 'comments', 'summary', 'fathomcalls', 'next_actions',
                              'linkedin_description', 'connection_degree_with_anna', 
                              'mutual_connections_with_anna', 'associated_deals', 'associated_users',
                              'created_by', 'angellist', 'facebook', 'instagram', 'twitter_follower_count',
                              'next_calendar_interaction', 'next_interaction', 'strongest_connection_strength',
                              'strongest_connection_user', 'description']:
                    if value and isinstance(value, list) and len(value) > 0:
                        field_value = value[0].get('value', '') if isinstance(value[0], dict) else str(value[0])
                        if field_value:
                            custom_fields[key] = field_value
            
            return {
                'attio_id': record_id,
                'name': full_name,
                'first_name': first_name,
                'last_name': last_name,
                'primary_email': primary_email,
                'company_id': company_id,
                'job_title': job_title,
                'primary_phone': primary_phone,
                'linkedin_url': linkedin_url,
                'twitter_handle': twitter_handle,
                'first_email_interaction': first_email.get('interacted_at', '') if first_email else '',
                'last_email_interaction': last_email.get('interacted_at', '') if last_email else '',
                'first_calendar_interaction': first_calendar.get('interacted_at', '') if first_calendar else '',
                'last_calendar_interaction': last_calendar.get('interacted_at', '') if last_calendar else '',
                'connection_strength': connection_value,
                'created_at': created_timestamp,
                'web_url': person_data.get('web_url', ''),
                'custom_fields': custom_fields,
                'source': 'attio_complete',
                'raw_data': person_data  # Include raw data for debugging
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Attio person: {e}")
            logger.error(f"Person data: {person_data}")
            return None
    
    async def _parse_attio_company(self, company_data: Dict) -> Dict:
        """Parse Attio company data into standardized format"""
        try:
            # Extract basic info
            record_id = company_data['id']['record_id']
            values = company_data['values']
            
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
            employee_count = employee_count_data.get('value', '') if employee_count_data else ''
            
            # Extract founded year
            founded_year_data = values.get('founded_year', [{}])[0] if values.get('founded_year') else {}
            founded_year = founded_year_data.get('value', '') if founded_year_data else ''
            
            # Extract timestamps
            created_at = values.get('created_at', [{}])[0] if values.get('created_at') else {}
            created_timestamp = created_at.get('value', '') if created_at else ''
            
            # Extract custom fields
            custom_fields = {}
            for key, value in values.items():
                if key not in ['record_id', 'name', 'domain', 'website', 'description', 
                              'industry', 'primary_location', 'employee_count', 'founded_year',
                              'created_at', 'updated_at', 'linkedin', 'twitter', 'facebook',
                              'instagram', 'angellist', 'crunchbase', 'pitchbook', 'associated_deals',
                              'associated_users', 'created_by', 'summary', 'next_actions']:
                    if value and isinstance(value, list) and len(value) > 0:
                        field_value = value[0].get('value', '') if isinstance(value[0], dict) else str(value[0])
                        if field_value:
                            custom_fields[key] = field_value
            
            return {
                'attio_id': record_id,
                'name': company_name,
                'domain': domain,
                'website': website,
                'description': description,
                'industry': industry,
                'location': location,
                'employee_count': employee_count,
                'founded_year': founded_year,
                'created_at': created_timestamp,
                'web_url': company_data.get('web_url', ''),
                'custom_fields': custom_fields,
                'source': 'attio_company',
                'raw_data': company_data  # Include raw data for debugging
            }
            
        except Exception as e:
            logger.error(f"Failed to parse Attio company: {e}")
            logger.error(f"Company data: {company_data}")
            return None

async def get_ethan_with_company():
    """Get Ethan's complete information including company details"""
    
    # Get API keys from config
    attio_api_key = Config.ATTIO_API_KEY
    
    if not attio_api_key:
        logger.error("Attio API key not found in config")
        return
    
    try:
        logger.info("🚀 Getting Ethan's Complete Information with Company Details")
        logger.info("=" * 70)
        
        async with AttioCompleteIntegration(attio_api_key) as attio:
            # Step 1: Get Ethan's person data
            logger.info("\n1. Getting Ethan's person data...")
            
            ethan_data = await attio.get_person_by_email("ethan@tuesday.vc")
            
            if not ethan_data:
                logger.error("❌ Could not get data for ethan@tuesday.vc")
                return
            
            # Step 2: Get company data if company_id exists
            company_data = None
            if ethan_data.get('company_id'):
                logger.info(f"\n2. Getting company data for ID: {ethan_data['company_id']}")
                company_data = await attio.get_company_by_id(ethan_data['company_id'])
                
                if company_data:
                    logger.info("✅ Successfully retrieved company data")
                else:
                    logger.warning("⚠️ Could not retrieve company data")
            else:
                logger.warning("⚠️ No company ID found for Ethan")
            
            # Step 3: Display complete information
            logger.info("\n3. Complete Information for Ethan Imboden:")
            logger.info("=" * 50)
            
            # Person Information
            logger.info("\n👤 PERSON INFORMATION:")
            logger.info("-" * 30)
            logger.info(f"  Name: {ethan_data.get('name', 'N/A')}")
            logger.info(f"  First Name: {ethan_data.get('first_name', 'N/A')}")
            logger.info(f"  Last Name: {ethan_data.get('last_name', 'N/A')}")
            logger.info(f"  Email: {ethan_data.get('primary_email', 'N/A')}")
            logger.info(f"  Job Title: {ethan_data.get('job_title', 'N/A')}")
            logger.info(f"  Phone: {ethan_data.get('primary_phone', 'N/A')}")
            logger.info(f"  LinkedIn: {ethan_data.get('linkedin_url', 'N/A')}")
            logger.info(f"  Twitter: {ethan_data.get('twitter_handle', 'N/A')}")
            logger.info(f"  Attio ID: {ethan_data.get('attio_id', 'N/A')}")
            logger.info(f"  Created: {ethan_data.get('created_at', 'N/A')}")
            logger.info(f"  Web URL: {ethan_data.get('web_url', 'N/A')}")
            
            # Interaction History
            logger.info("\n📧 INTERACTION HISTORY:")
            logger.info("-" * 30)
            logger.info(f"  First Email: {ethan_data.get('first_email_interaction', 'N/A')}")
            logger.info(f"  Last Email: {ethan_data.get('last_email_interaction', 'N/A')}")
            logger.info(f"  First Calendar: {ethan_data.get('first_calendar_interaction', 'N/A')}")
            logger.info(f"  Last Calendar: {ethan_data.get('last_calendar_interaction', 'N/A')}")
            logger.info(f"  Connection Strength: {ethan_data.get('connection_strength', 'N/A')}")
            
            # Company Information
            if company_data:
                logger.info("\n🏢 COMPANY INFORMATION:")
                logger.info("-" * 30)
                logger.info(f"  Company Name: {company_data.get('name', 'N/A')}")
                logger.info(f"  Domain: {company_data.get('domain', 'N/A')}")
                logger.info(f"  Website: {company_data.get('website', 'N/A')}")
                logger.info(f"  Description: {company_data.get('description', 'N/A')}")
                logger.info(f"  Industry: {company_data.get('industry', 'N/A')}")
                logger.info(f"  Location: {company_data.get('location', 'N/A')}")
                logger.info(f"  Employee Count: {company_data.get('employee_count', 'N/A')}")
                logger.info(f"  Founded Year: {company_data.get('founded_year', 'N/A')}")
                logger.info(f"  Company ID: {company_data.get('attio_id', 'N/A')}")
                logger.info(f"  Created: {company_data.get('created_at', 'N/A')}")
                logger.info(f"  Company Web URL: {company_data.get('web_url', 'N/A')}")
                
                # Company Custom Fields
                if company_data.get('custom_fields'):
                    logger.info("\n  Company Custom Fields:")
                    for field_key, field_value in company_data['custom_fields'].items():
                        if field_value:
                            logger.info(f"    • {field_key}: {field_value}")
            else:
                logger.info("\n🏢 COMPANY INFORMATION:")
                logger.info("-" * 30)
                logger.info("  Company ID: {ethan_data.get('company_id', 'N/A')}")
                logger.info("  ❌ Could not retrieve company details")
            
            # Person Custom Fields
            if ethan_data.get('custom_fields'):
                logger.info("\n🔧 PERSON CUSTOM FIELDS:")
                logger.info("-" * 30)
                for field_key, field_value in ethan_data['custom_fields'].items():
                    if field_value:
                        logger.info(f"  • {field_key}: {field_value}")
            
            logger.info("\n" + "=" * 70)
            logger.info("🎉 SUCCESS! Complete Ethan Information Retrieved")
            logger.info("\n📊 SUMMARY:")
            logger.info(f"• Person Data: ✅ Complete")
            logger.info(f"• Company Data: {'✅ Complete' if company_data else '❌ Not Available'}")
            logger.info(f"• Total Fields Retrieved: {len(ethan_data) + (len(company_data) if company_data else 0)}")
            
            return {
                'person': ethan_data,
                'company': company_data
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to get complete information: {e}")
        raise

def main():
    """Main function"""
    asyncio.run(get_ethan_with_company())

if __name__ == "__main__":
    main()
