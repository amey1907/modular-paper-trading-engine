#!/usr/bin/env python3
"""
Fresh test script for Kite API connection
"""

import requests

# Read config directly
with open('config.py', 'r') as f:
    content = f.read()

# Extract credentials manually
api_key = None
access_token = None

for line in content.split('\n'):
    if 'KITE_API_KEY' in line and '=' in line and '"' in line:
        parts = line.split('"')
        if len(parts) >= 2:
            api_key = parts[1]
    elif 'KITE_ACCESS_TOKEN' in line and '=' in line and '"' in line:
        parts = line.split('"')
        if len(parts) >= 2:
            access_token = parts[1]

if not api_key or not access_token:
    print("❌ Could not extract credentials from config.py")
    exit(1)

print(f"🔑 API Key: {api_key[:10]}...")
print(f"🔑 Access Token: {access_token[:10]}...")
print("="*50)

# Test connection
base_url = "https://api.kite.trade"
headers = {
    "X-Kite-Version": "3",
    "Authorization": f"token {api_key}:{access_token}"
}

print("📡 Testing API connection...")
try:
    response = requests.get(f"{base_url}/user/profile", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("✅ Authentication successful!")
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
