#!/usr/bin/env python3
"""
Test Attio API with data wrapper format
"""

import subprocess
import json
from config import Config

def test_attio_with_data_wrapper():
    """Test Attio API with data wrapper format"""
    
    api_key = Config.ATTIO_API_KEY
    if not api_key:
        print("❌ Attio API key not found")
        return
    
    # Test with data wrapper format
    endpoints_to_test = [
        # With data wrapper for people records
        ("POST", "https://api.attio.com/v2/objects/people/records", {
            "data": {
                "attributes": {
                    "name": "Ethan Imboden",
                    "email_addresses": ["ethan@tuesday.vc"]
                }
            }
        }),
        
        # With data wrapper for object ID
        ("POST", "https://api.attio.com/v2/objects/82febeeb-fef5-42f0-a91a-6a8956783666/records", {
            "data": {
                "attributes": {
                    "name": "Ethan Imboden",
                    "email_addresses": ["ethan@tuesday.vc"]
                }
            }
        }),
        
        # Try with values wrapper
        ("POST", "https://api.attio.com/v2/objects/people/records", {
            "data": {
                "values": {
                    "name": "Ethan Imboden",
                    "email_addresses": ["ethan@tuesday.vc"]
                }
            }
        }),
        
        # Try with different structure
        ("POST", "https://api.attio.com/v2/objects/people/records", {
            "data": {
                "matching_attribute": "email_addresses",
                "value": "ethan@tuesday.vc",
                "attributes": {
                    "name": "Ethan Imboden",
                    "email_addresses": ["ethan@tuesday.vc"]
                }
            }
        }),
    ]
    
    for i, (method, url, data) in enumerate(endpoints_to_test):
        print(f"\n🔍 Test {i+1}: {method} {url}")
        print("=" * 60)
        print(f"Data: {json.dumps(data, indent=2)}")
        
        curl_command = [
            "curl", "-X", method,
            url,
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(data)
        ]
        
        try:
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
            
            print(f"Exit code: {result.returncode}")
            print(f"Response: {result.stdout}")
            
            if result.stderr:
                print(f"Error: {result.stderr}")
                
            # Check if successful
            if result.returncode == 0 and result.stdout:
                try:
                    response_data = json.loads(result.stdout)
                    
                    if 'record_id' in response_data:
                        print(f"✅ SUCCESS! Found record_id: {response_data['record_id']}")
                        return response_data
                    elif 'data' in response_data and response_data['data']:
                        print(f"✅ SUCCESS! Found data: {response_data['data']}")
                        return response_data
                    elif 'status_code' in response_data and response_data['status_code'] == 200:
                        print(f"✅ SUCCESS! Status 200")
                        return response_data
                    elif 'id' in response_data:
                        print(f"✅ SUCCESS! Found id: {response_data['id']}")
                        return response_data
                    else:
                        print(f"❌ No success indicators found")
                        print(f"Response keys: {list(response_data.keys())}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON: {e}")
            else:
                print(f"❌ Request failed")
                
        except subprocess.TimeoutExpired:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n❌ No working endpoints found with data wrapper")

if __name__ == "__main__":
    test_attio_with_data_wrapper()
