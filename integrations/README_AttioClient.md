# AttioClient - Production-Ready Attio CRM API Client

A comprehensive, production-ready Python client for interacting with the Attio CRM API. This client provides robust error handling, comprehensive data retrieval capabilities, and proper type safety.

## Features

- ✅ **Production-Ready**: Comprehensive error handling, logging, and type hints
- ✅ **Async/Await Support**: Built with asyncio for high-performance async operations
- ✅ **Type Safety**: Full type hints and dataclasses for data structures
- ✅ **Comprehensive Data Retrieval**: Support for people, companies, and custom fields
- ✅ **Robust Error Handling**: Custom exceptions with detailed error information
- ✅ **Connection Testing**: Built-in API connection validation
- ✅ **Context Manager Support**: Proper resource management with async context managers
- ✅ **Extensible**: Easy to extend for additional Attio object types

## Installation

```bash
pip install aiohttp
```

## Quick Start

```python
import asyncio
from integrations.attio_client import AttioClient

async def main():
    async with AttioClient(api_key="your_attio_api_key") as client:
        # Test connection
        if await client.test_connection():
            print("✅ Connected to Attio API")
        
        # Get person by email
        person = await client.get_person_by_email("user@example.com")
        if person:
            print(f"Found: {person.name} ({person.primary_email})")
            
            # Get company information
            if person.company_id:
                company = await client.get_company_by_id(person.company_id)
                if company:
                    print(f"Company: {company.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### AttioClient

The main client class for interacting with the Attio API.

#### Constructor

```python
AttioClient(api_key: str, base_url: str = "https://api.attio.com/v2", timeout: int = 30)
```

**Parameters:**
- `api_key` (str): Your Attio API key (required)
- `base_url` (str): Base URL for the Attio API (default: "https://api.attio.com/v2")
- `timeout` (int): Request timeout in seconds (default: 30)

#### Methods

##### `async test_connection() -> bool`
Test the connection to the Attio API.

**Returns:** `True` if connection is successful, `False` otherwise.

##### `async get_person_by_email(email: str) -> Optional[AttioPerson]`
Get person data by email address.

**Parameters:**
- `email` (str): Email address to search for

**Returns:** `AttioPerson` object if found, `None` otherwise

**Raises:** `AttioAPIError` if the API request fails

##### `async get_company_by_id(company_id: str) -> Optional[AttioCompany]`
Get company data by company ID.

**Parameters:**
- `company_id` (str): Company record ID

**Returns:** `AttioCompany` object if found, `None` otherwise

**Raises:** `AttioAPIError` if the API request fails

##### `async get_people(limit: int = 100, offset: int = 0) -> List[AttioPerson]`
Get a list of people from Attio.

**Parameters:**
- `limit` (int): Maximum number of people to retrieve (default: 100)
- `offset` (int): Number of people to skip (default: 0)

**Returns:** List of `AttioPerson` objects

**Raises:** `AttioAPIError` if the API request fails

##### `async get_companies(limit: int = 100, offset: int = 0) -> List[AttioCompany]`
Get a list of companies from Attio.

**Parameters:**
- `limit` (int): Maximum number of companies to retrieve (default: 100)
- `offset` (int): Number of companies to skip (default: 0)

**Returns:** List of `AttioCompany` objects

**Raises:** `AttioAPIError` if the API request fails

### Data Classes

#### AttioPerson

Represents a person record from Attio.

```python
@dataclass
class AttioPerson:
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
```

#### AttioCompany

Represents a company record from Attio.

```python
@dataclass
class AttioCompany:
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
```

### Exceptions

#### AttioAPIError

Custom exception for Attio API errors.

```python
class AttioAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
```

## Examples

### Basic Usage

```python
import asyncio
from integrations.attio_client import AttioClient

async def get_user_info(email: str):
    async with AttioClient(api_key="your_api_key") as client:
        person = await client.get_person_by_email(email)
        if person:
            print(f"Name: {person.name}")
            print(f"Email: {person.primary_email}")
            print(f"Job Title: {person.job_title}")
            print(f"Connection Strength: {person.connection_strength}")
            
            if person.company_id:
                company = await client.get_company_by_id(person.company_id)
                if company:
                    print(f"Company: {company.name}")
                    print(f"Industry: {company.industry}")
                    print(f"Employee Count: {company.employee_count}")

asyncio.run(get_user_info("user@example.com"))
```

### Error Handling

```python
import asyncio
from integrations.attio_client import AttioClient, AttioAPIError

async def safe_get_person(email: str):
    try:
        async with AttioClient(api_key="your_api_key") as client:
            person = await client.get_person_by_email(email)
            return person
    except AttioAPIError as e:
        print(f"Attio API Error: {e}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")
        if e.response_data:
            print(f"Response: {e.response_data}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

asyncio.run(safe_get_person("user@example.com"))
```

### Batch Processing

```python
import asyncio
from integrations.attio_client import AttioClient

async def process_all_people():
    async with AttioClient(api_key="your_api_key") as client:
        # Get all people in batches
        offset = 0
        limit = 100
        
        while True:
            people = await client.get_people(limit=limit, offset=offset)
            if not people:
                break
            
            for person in people:
                print(f"Processing: {person.name} ({person.primary_email})")
                # Process person data here
            
            offset += limit

asyncio.run(process_all_people())
```

### Custom Field Access

```python
import asyncio
from integrations.attio_client import AttioClient

async def get_custom_fields(email: str):
    async with AttioClient(api_key="your_api_key") as client:
        person = await client.get_person_by_email(email)
        if person and person.custom_fields:
            print("Custom Fields:")
            for field_name, field_value in person.custom_fields.items():
                print(f"  {field_name}: {field_value}")

asyncio.run(get_custom_fields("user@example.com"))
```

## Testing

The client includes comprehensive unit tests. Run them with:

```bash
# Run all tests
python -m pytest tests/test_attio_client.py -v

# Run only unit tests (no API calls)
python -m pytest tests/test_attio_client.py -v -m "not integration"

# Run integration tests (requires API key)
python -m pytest tests/test_attio_client.py -v -m "integration"
```

## Configuration

Set your Attio API key in your environment or config:

```python
# Using environment variable
import os
api_key = os.getenv('ATTIO_API_KEY')

# Using config module
from config import Config
api_key = Config.ATTIO_API_KEY
```

## Logging

The client uses Python's standard logging module. Configure logging to see detailed information:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('integrations.attio_client')
logger.setLevel(logging.DEBUG)
```

## Performance Considerations

- The client uses async/await for non-blocking operations
- Connection pooling is handled by aiohttp
- Timeout settings can be adjusted based on your needs
- Batch operations are recommended for large datasets

## Error Handling Best Practices

1. Always use try-catch blocks around API calls
2. Check for `None` return values when records are not found
3. Handle `AttioAPIError` for API-specific errors
4. Use connection testing before making multiple API calls
5. Implement retry logic for transient errors

## Contributing

1. Follow the existing code style and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Ensure all tests pass before submitting changes

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the test cases for usage examples
2. Review the error messages and status codes
3. Ensure your API key has proper permissions
4. Verify network connectivity to Attio API
