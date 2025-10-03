#!/usr/bin/env python3
"""
Test Attio API using the exact assert curl command
"""

import subprocess
import json
from config import Config

def test_attio_assert_curl():
    """Test Attio API using exact assert curl command"""
    
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        print("❌ Attio API key not found")
        return
    
    # Test the exact assert curl command
    curl_command = [
        "curl", "-X", "POST", 
        "https://api.attio.com/v2/objects/people/records/assert",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "matching_attribute": "email_addresses",
            "value": "ethan@tuesday.vc",
            "attributes": {
                "email_addresses": ["ethan@tuesday.vc"]
            }
        })
    ]
    
    print("🚀 Testing Attio API with assert curl command...")
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
                
                if 'record_id' in response_data:
                    print(f"\n✅ SUCCESS! Person created/found with record_id: {response_data['record_id']}")
                    
                    # Now try to get the full person record
                    print("\n🔍 Getting full person record...")
                    get_curl_command = [
                        "curl", "-X", "GET",
                        f"https://api.attio.com/v2/records/people/{response_data['record_id']}",
                        "-H", f"Authorization: Bearer {api_key}",
                        "-H", "Content-Type: application/json"
                    ]
                    
                    get_result = subprocess.run(get_curl_command, capture_output=True, text=True, timeout=30)
                    
                    if get_result.returncode == 0:
                        get_response = json.loads(get_result.stdout)
                        print("📋 Full Person Record:")
                        print(json.dumps(get_response, indent=2))
                    else:
                        print(f"❌ Failed to get full record: {get_result.stderr}")
                        
                elif 'data' in response_data:
                    print(f"✅ SUCCESS! Found data in response")
                    print(f"Data: {response_data['data']}")
                else:
                    print("❌ No record_id or data found in response")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
            
    except subprocess.TimeoutExpired:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error running curl: {e}")

if __name__ == "__main__":
    test_attio_assert_curl()
