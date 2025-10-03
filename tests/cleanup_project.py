#!/usr/bin/env python3
"""
Clean up project files and organize test scripts
Remove duplicates and organize the project structure
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up and organize the project files"""
    
    print("🧹 Starting Project Cleanup")
    print("=" * 50)
    
    # Define directories
    project_root = Path("/Users/wwsharkgmail.com/user-data-integration/user-data-integration")
    tests_dir = project_root / "tests"
    archive_dir = project_root / "archive"
    
    # Create directories if they don't exist
    tests_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)
    
    # Files to keep (core functionality)
    keep_files = {
        "main_integration_system.py",
        "cli.py", 
        "config.py",
        "daily_brief_generator.py",
        "requirements.txt",
        "README.md",
        "IMPLEMENTATION_SUMMARY.md",
        "TESTING_GUIDE.md",
        "data_mapping_report.md",
        "test_scenarios.py",  # Our new comprehensive test
        "client_secret.json"
    }
    
    # Integration files to keep
    integration_files = {
        "integrations/notion_client_updated.py",  # Stable Notion client
        "integrations/attio_integration_fixed.py",  # Working Attio client
        "integrations/gmail_integration.py",
        "integrations/calendar_integration.py",
        "integrations/fathom_integration.py",
        "integrations/social_integration.py",
        "integrations/leaner_integration.py"
    }
    
    # Files to archive (old test files)
    archive_patterns = [
        "test_attio_*.py",
        "test_2025_*.py", 
        "test_latest_*.py",
        "test_stable_*.py",
        "test_working_*.py",
        "test_new_*.py",
        "debug_*.py",
        "explore_*.py",
        "check_*.py",
        "fix_*.py",
        "cleanup_*.py",
        "move_*.py",
        "update_*.py",
        "create_*.py",
        "add_*.py",
        "collect_*.py",
        "store_*.py",
        "final_*.py",
        "get_*.py",
        "compare_*.py",
        "fixed_*.py",
        "attio_*.py",
        "notion_*.py",
        "integration_*.py",
        "setup_*.py",
        "manual_*.py"
    ]
    
    # Files to delete (duplicates and temporary files)
    delete_patterns = [
        "*.json.backup",
        "*.py.bak",
        "*.tmp",
        "temp_*.py"
    ]
    
    print("\n📁 Organizing files...")
    
    # Move test files to tests directory
    test_files_moved = 0
    for pattern in archive_patterns:
        for file_path in project_root.glob(pattern):
            if file_path.is_file() and file_path.name not in keep_files:
                try:
                    shutil.move(str(file_path), str(tests_dir / file_path.name))
                    print(f"  📦 Moved to tests/: {file_path.name}")
                    test_files_moved += 1
                except Exception as e:
                    print(f"  ⚠️ Could not move {file_path.name}: {e}")
    
    # Move some files to archive
    archive_files = [
        "attio_record_972bb59b-a767-4ac6-8031-020392cb2111.json",
        "notion_schema.py"
    ]
    
    for file_name in archive_files:
        file_path = project_root / file_name
        if file_path.exists():
            try:
                shutil.move(str(file_path), str(archive_dir / file_name))
                print(f"  📦 Moved to archive/: {file_name}")
            except Exception as e:
                print(f"  ⚠️ Could not move {file_name}: {e}")
    
    # Clean up integration directory
    print("\n🔧 Cleaning integrations directory...")
    integration_dir = project_root / "integrations"
    
    # Keep only the working integration files
    for file_path in integration_dir.iterdir():
        if file_path.is_file() and file_path.name not in [
            "notion_client_updated.py",
            "attio_integration_fixed.py", 
            "gmail_integration.py",
            "calendar_integration.py",
            "fathom_integration.py",
            "social_integration.py",
            "leaner_integration.py"
        ]:
            try:
                shutil.move(str(file_path), str(archive_dir / file_path.name))
                print(f"  📦 Moved to archive/: {file_path.name}")
            except Exception as e:
                print(f"  ⚠️ Could not move {file_path.name}: {e}")
    
    # Create a clean test runner
    create_test_runner(tests_dir)
    
    # Create project structure documentation
    create_project_structure_doc(project_root)
    
    print(f"\n✅ Cleanup complete!")
    print(f"  📦 Moved {test_files_moved} test files to tests/ directory")
    print(f"  🗂️ Organized integration files")
    print(f"  📋 Created project structure documentation")

def create_test_runner(tests_dir):
    """Create a clean test runner script"""
    test_runner_content = '''#!/usr/bin/env python3
"""
Test Runner for User Data Integration System
Runs all test scenarios and generates reports
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from test_scenarios import TestScenarios

async def run_tests():
    """Run all test scenarios"""
    print("🚀 Running User Data Integration Tests")
    print("=" * 50)
    
    test_scenarios = TestScenarios()
    await test_scenarios.run_all_scenarios()

if __name__ == "__main__":
    asyncio.run(run_tests())
'''
    
    test_runner_path = tests_dir / "run_tests.py"
    with open(test_runner_path, 'w') as f:
        f.write(test_runner_content)
    
    # Make it executable
    os.chmod(test_runner_path, 0o755)
    print(f"  ✅ Created test runner: {test_runner_path}")

def create_project_structure_doc(project_root):
    """Create project structure documentation"""
    doc_content = '''# Project Structure

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
'''
    
    doc_path = project_root / "PROJECT_STRUCTURE.md"
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    print(f"  ✅ Created project structure documentation: {doc_path}")

if __name__ == "__main__":
    cleanup_project()
