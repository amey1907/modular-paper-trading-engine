#!/usr/bin/env python3
"""
Debug script for historical data access
"""

import requests
import json
from datetime import datetime, timedelta
from config import KITE_API_KEY, KITE_ACCESS_TOKEN

def debug_historical_access():
    """Debug historical data access step by step"""
    
    print("🔍 Debugging Historical Data Access")
    print("=" * 60)
    print(f"API Key: {KITE_API_KEY}")
    print(f"Access Token: {KITE_ACCESS_TOKEN}")
    print(f"Current Time: {datetime.now()}")
    print("=" * 60)
    
    base_url = "https://api.kite.trade"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {KITE_API_KEY}:{KITE_ACCESS_TOKEN}"
    }
    
    # Test 1: Check if we can get instruments first
    print("\n📋 Test 1: Getting NSE Instruments")
    try:
        response = requests.get(f"{base_url}/instruments/NSE", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Find NIFTY 50 in the instruments
            lines = response.text.split('\n')
            nifty_line = None
            for line in lines:
                if 'NIFTY 50' in line and 'INDICES' in line:
                    nifty_line = line
                    break
            
            if nifty_line:
                print(f"✅ Found NIFTY 50: {nifty_line}")
                parts = nifty_line.split(',')
                if len(parts) > 0:
                    token = parts[0]
                    print(f"📊 NIFTY Token: {token}")
                else:
                    print("❌ Could not parse NIFTY token")
            else:
                print("❌ NIFTY 50 not found in instruments")
        else:
            print(f"❌ Instruments fetch failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Try different historical data endpoints
    print("\n📊 Test 2: Historical Data Endpoints")
    
    # Test with different dates
    test_dates = [
        ('2025-08-14', 'Yesterday'),
        ('2025-08-13', 'Day before yesterday'),
        ('2025-08-12', '3 days ago'),
        ('2025-08-11', '4 days ago')
    ]
    
    # Test with different instrument tokens
    test_tokens = [
        ('256265', 'NIFTY 50'),
        ('260105', 'VIX'),
        ('256777', 'NIFTY MIDCAP 100')
    ]
    
    for token, name in test_tokens:
        print(f"\n🔍 Testing {name} (Token: {token}):")
        
        for date, desc in test_dates:
            try:
                url = f"{base_url}/instruments/historical/{token}/day"
                params = {'from': date, 'to': date}
                
                print(f"  📅 {desc} ({date}): ", end="")
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                print(f"HTTP {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'candles' in data['data']:
                        candles = data['data']['candles']
                        if candles:
                            last_candle = candles[-1]
                            print(f"    ✅ Success: {len(candles)} candles, Last: {last_candle}")
                        else:
                            print(f"    ⚠️  No data for {date}")
                    else:
                        print(f"    ❌ Unexpected response format")
                elif response.status_code == 403:
                    print(f"    ❌ 403 Forbidden - Check permissions")
                elif response.status_code == 404:
                    print(f"    ❌ 404 Not Found - Check token/date")
                else:
                    print(f"    ❓ Unexpected: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Check different intervals
    print("\n⏰ Test 3: Different Time Intervals")
    
    intervals = ['day', 'minute', '5minute', '15minute', '30minute', '60minute']
    
    for interval in intervals:
        try:
            url = f"{base_url}/instruments/historical/256265/{interval}"
            params = {'from': '2025-08-14', 'to': '2025-08-14'}
            
            print(f"📊 {interval} interval: ", end="")
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"HTTP {response.status_code}")
            
            if response.status_code == 200:
                print(f"    ✅ {interval} data accessible")
            elif response.status_code == 403:
                print(f"    ❌ 403 - {interval} not permitted")
            else:
                print(f"    ❓ {response.status_code} - {response.text[:100]}...")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Check API documentation endpoint
    print("\n📚 Test 4: API Documentation Access")
    try:
        response = requests.get(f"{base_url}/", headers=headers, timeout=10)
        print(f"API Root Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_historical_access()
