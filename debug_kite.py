#!/usr/bin/env python3
"""
Detailed debug script for Kite API connection
"""

import requests
import json

# Read credentials from config
from config import KITE_API_KEY, KITE_ACCESS_TOKEN

print("🔍 Kite API Debug Test")
print("=" * 50)
print(f"API Key: '{KITE_API_KEY}' (length: {len(KITE_API_KEY)})")
print(f"Access Token: '{KITE_ACCESS_TOKEN}' (length: {len(KITE_ACCESS_TOKEN)})")
print("=" * 50)

# Test different API endpoints
endpoints = [
    ("User Profile", "/user/profile"),
    ("NIFTY Quote", "/quote?i=NSE:NIFTY%2050"),
    ("VIX Quote", "/quote?i=NSE:INDIA%20VIX"),
    ("Instruments NSE", "/instruments/NSE"),
    ("Instruments NFO", "/instruments/NFO"),
]

base_url = "https://api.kite.trade"
headers = {
    "X-Kite-Version": "3",
    "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
}

print("📡 Testing API endpoints...")
print("=" * 50)

for name, endpoint in endpoints:
    try:
        url = base_url + endpoint
        print(f"\n🔍 Testing: {name}")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print(f"✅ {name}: SUCCESS")
        else:
            print(f"❌ {name}: FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
    
    print("-" * 30)

print("\n" + "=" * 50)
print("🔍 Debug Summary")
print("=" * 50)

# Test with different header formats
print("\n🧪 Testing different header formats...")

# Test 1: Standard format
headers1 = {
    "X-Kite-Version": "3",
    "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
}

# Test 2: Without X-Kite-Version
headers2 = {
    "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
}

# Test 3: Different token format
headers3 = {
    "X-Kite-Version": "3",
    "Authorization": f"Bearer {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
}

test_headers = [
    ("Standard", headers1),
    ("No Version", headers2),
    ("Bearer Token", headers3)
]

for name, test_headers in test_headers:
    try:
        response = requests.get(f"{base_url}/user/profile", headers=test_headers, timeout=10)
        print(f"{name}: {response.status_code} - {response.text[:100]}...")
    except Exception as e:
        print(f"{name}: ERROR - {e}")
