#!/usr/bin/env python3
"""
Test script for the delete request feature
"""

import requests
import json

# Base URL for the application
BASE_URL = "http://127.0.0.1:5000"

def test_delete_request_feature():
    """Test the delete request functionality"""
    
    print("🧪 Testing Delete Request Feature")
    print("=" * 50)
    
    # Test 1: Try to access delete endpoint without authentication
    print("\n1. Testing delete endpoint without authentication...")
    try:
        response = requests.delete(f"{BASE_URL}/api/requests/1")
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Try to access delete endpoint as non-admin (would need login)
    print("\n2. Testing delete endpoint as non-admin...")
    print("   ℹ️  This would require logging in as a regular user")
    print("   ℹ️  Expected: 403 Access Denied")
    
    # Test 3: Check if user-info endpoint exists
    print("\n3. Testing user-info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/user-info")
        if response.status_code == 401:
            print("   ✅ User-info endpoint exists and requires authentication")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Manual Testing Instructions:")
    print("1. Open your browser and go to http://127.0.0.1:5000")
    print("2. Login as admin (admin@company.com / admin123)")
    print("3. Go to 'My Requests' or 'Approvals' page")
    print("4. Look for the red trash icon (🗑️) next to requests")
    print("5. Click the delete button to see the confirmation modal")
    print("6. Confirm deletion to test the full flow")
    print("\n🔒 Security Features:")
    print("- Only admins can see delete buttons")
    print("- Delete requires confirmation modal")
    print("- Proper cleanup of related data")
    print("- Role-based access control enforced")

if __name__ == "__main__":
    test_delete_request_feature()
