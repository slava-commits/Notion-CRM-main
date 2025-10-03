#!/usr/bin/env python3
"""
Test Attio API using PUT request with matching_attribute
"""

import subprocess
import json
from config import Config

def test_attio_put_request():
    """Test Attio API using PUT request with matching_attribute"""
    
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        print("❌ Attio API key not found")
        return
    
    # Test the PUT request with matching_attribute
    url = "https://api.attio.com/v2/objects/people/records?matching_attribute=email_addresses"
    data = {
        "data": {
            "values": {
                "email_addresses": ["ethan@tuesday.vc"]
            }
        }
    }
    
    print("🚀 Testing Attio API with PUT request...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    curl_command = [
        "curl", "--request", "PUT",
        "--url", url,
        "--header", f"Authorization: Bearer {api_key}",
        "--header", "Content-Type: application/json",
        "--data", json.dumps(data)
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
        
        print(f"\nExit code: {result.returncode}")
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
                        
                elif 'data' in response_data and response_data['data']:
                    print(f"✅ SUCCESS! Found data in response")
                    print(f"Data: {response_data['data']}")
                elif 'id' in response_data:
                    print(f"✅ SUCCESS! Found id: {response_data['id']}")
                else:
                    print("❌ No record_id, data, or id found in response")
                    print(f"Response keys: {list(response_data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
            
    except subprocess.TimeoutExpired:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error running curl: {e}")

if __name__ == "__main__":
    test_attio_put_request()
