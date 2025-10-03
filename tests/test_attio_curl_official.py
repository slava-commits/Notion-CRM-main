#!/usr/bin/env python3
"""
Test Attio API using the exact curl command from official documentation
"""

import subprocess
import json
from config import Config

def test_attio_curl_official():
    """Test Attio API using exact curl from official docs"""
    
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        print("❌ Attio API key not found")
        return
    
    # Test the exact curl command from the documentation
    curl_command = [
        "curl", "-X", "POST", 
        "https://api.attio.com/v2/records/search",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "query": "ethan@tuesday.vc",
            "objects": ["people"],
            "limit": 10
        })
    ]
    
    print("🚀 Testing Attio API with official curl command...")
    print(f"Command: {' '.join(curl_command[:6])} [API_KEY] {' '.join(curl_command[7:])}")
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
        
        print(f"Exit code: {result.returncode}")
        print(f"Response: {result.stdout}")
        
        if result.stderr:
            print(f"Error: {result.stderr}")
            
        # If successful, try to parse the response
        if result.returncode == 0 and result.stdout:
            try:
                response_data = json.loads(result.stdout)
                print("\n📊 Parsed Response:")
                print(json.dumps(response_data, indent=2))
                
                if 'data' in response_data and response_data['data']:
                    print(f"\n✅ Found {len(response_data['data'])} records!")
                    for i, record in enumerate(response_data['data']):
                        print(f"  {i+1}. {record.get('object')} - {record.get('record_id')}")
                        if 'attributes' in record:
                            attrs = record['attributes']
                            print(f"     Name: {attrs.get('name', 'N/A')}")
                            print(f"     Emails: {attrs.get('email_addresses', [])}")
                else:
                    print("❌ No data found in response")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
            
    except subprocess.TimeoutExpired:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error running curl: {e}")

if __name__ == "__main__":
    test_attio_curl_official()
