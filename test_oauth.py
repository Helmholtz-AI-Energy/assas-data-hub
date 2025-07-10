"""Test script for OAuth authentication."""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_oauth_endpoints():
    """Test OAuth endpoints."""
    base_url = "http://localhost:5000"
    
    print("Testing OAuth endpoints...")
    
    # Test auth page
    try:
        response = requests.get(f"{base_url}/auth/login")
        print(f"✓ Login page: {response.status_code}")
    except Exception as e:
        print(f"✗ Login page error: {e}")
    
    # Test GitHub login redirect
    try:
        response = requests.get(
            f"{base_url}/auth/login/github", 
            allow_redirects=False
        )
        print(f"✓ GitHub login redirect: {response.status_code}")
        if 'github.com' in response.headers.get('Location', ''):
            print("✓ Redirects to GitHub")
        else:
            print(f"✗ Unexpected redirect: {response.headers.get('Location')}")
    except Exception as e:
        print(f"✗ GitHub login error: {e}")
    
    # Test debug endpoint (if in debug mode)
    try:
        response = requests.get(f"{base_url}/auth/debug/session")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Debug endpoint: {data}")
        else:
            print(f"✓ Debug endpoint disabled (production mode)")
    except Exception as e:
        print(f"✗ Debug endpoint error: {e}")

if __name__ == "__main__":
    # Check environment variables
    github_client_id = os.getenv('GITHUB_CLIENT_ID')
    if github_client_id:
        print(f"✓ GitHub Client ID configured: {github_client_id[:8]}...")
    else:
        print("✗ GitHub Client ID not configured")
    
    test_oauth_endpoints()