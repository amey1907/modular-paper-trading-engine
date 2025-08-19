#!/usr/bin/env python3
"""
Test script for historical data and market status
"""

import requests
import json
from datetime import datetime, timedelta
from config import KITE_API_KEY, KITE_ACCESS_TOKEN

def test_historical_data():
    """Test historical data access"""
    
    print("🔍 Testing Historical Data Access")
    print("=" * 50)
    print(f"API Key: {KITE_API_KEY[:10]}...")
    print(f"Access Token: {KITE_ACCESS_TOKEN[:10]}...")
    print(f"Current Time: {datetime.now()}")
    print("=" * 50)
    
    base_url = "https://api.kite.trade"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
    }
    
    # Test 1: Check if we can get historical data for NIFTY
    print("\n📊 Testing 1: Historical Data for NIFTY")
    try:
        # Get yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test historical data endpoint
        url = f"{base_url}/instruments/historical/256265/day"  # 256265 is NIFTY 50 token
        params = {
            'from': yesterday,
            'to': yesterday
        }
        
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            print("✅ Historical data access successful!")
            data = response.json()
            if 'data' in data and 'candles' in data['data']:
                candles = data['data']['candles']
                print(f"📈 Retrieved {len(candles)} historical candles")
                if candles:
                    print(f"Sample candle: {candles[0]}")
        else:
            print(f"❌ Historical data access failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Check if we can get historical data for VIX
    print("\n📈 Testing 2: Historical Data for VIX")
    try:
        # Test VIX historical data
        url = f"{base_url}/instruments/historical/260105/day"  # VIX token
        params = {
            'from': yesterday,
            'to': yesterday
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            print("✅ VIX historical data access successful!")
        else:
            print(f"❌ VIX historical data access failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Check market status
    print("\n🕐 Testing 3: Market Status Check")
    try:
        # Try to get current market data to see if market is open
        response = requests.get(f"{base_url}/quote?i=NSE:NIFTY%2050", headers=headers, timeout=10)
        print(f"Live quote status: {response.status_code}")
        
        if response.status_code == 403:
            print("🔒 Market is closed (holiday/weekend)")
            print("📅 Using historical data instead")
        elif response.status_code == 200:
            print("🟢 Market is open - live data available")
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 4: Check what instruments we can access
    print("\n📋 Testing 4: Available Data Types")
    
    data_types = [
        ("Instruments NSE", "/instruments/NSE"),
        ("Instruments NFO", "/instruments/NFO"),
        ("Instruments CDS", "/instruments/CDS"),
        ("Instruments MCX", "/instruments/MCX"),
    ]
    
    for name, endpoint in data_types:
        try:
            response = requests.get(base_url + endpoint, headers=headers, timeout=10)
            print(f"{name}: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
        except Exception as e:
            print(f"{name}: ERROR - {e}")

if __name__ == "__main__":
    test_historical_data()
