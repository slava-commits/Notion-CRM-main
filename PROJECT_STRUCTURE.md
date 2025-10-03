# Project Structure

## Core Files
- `main_integration_system.py` - Main integration system
- `cli.py` - Command line interface
- `config.py` - Configuration and API keys
- `daily_brief_generator.py` - Daily brief generation
- `test_scenarios.py` - Comprehensive test scenarios

## Integrations
- `integrations/notion_client_updated.py` - Notion API client (stable)
- `integrations/attio_integration_fixed.py` - Attio API client
- `integrations/gmail_integration.py` - Gmail integration
- `integrations/calendar_integration.py` - Calendar integration
- `integrations/fathom_integration.py` - Fathom integration
- `integrations/social_integration.py` - Social media integration
- `integrations/leaner_integration.py` - Leaner integration

## Tests
- `tests/run_tests.py` - Test runner script
- `tests/test_*.py` - Individual test files (archived)

## Archive
- `archive/` - Old test files and temporary files

## Documentation
- `README.md` - Project overview
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `TESTING_GUIDE.md` - Testing procedures
- `data_mapping_report.md` - Attio-Notion mapping analysis

## Usage
1. Run tests: `python3 tests/run_tests.py`
2. Run main system: `python3 main_integration_system.py`
3. Use CLI: `python3 cli.py --help`
