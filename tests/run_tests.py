#!/usr/bin/env python3
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
