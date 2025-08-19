#!/usr/bin/env python3
"""
Test script to debug Kite API connection
"""

import sys
import traceback
from kiteconnect import KiteConnect
import config

def test_kite_connection():
    try:
        # Initialize Kite Connect
        kite = KiteConnect(api_key=config.KITE_API_KEY)
        kite.set_access_token(config.KITE_ACCESS_TOKEN)

        # Test various API endpoints
        print("🔍 Testing Kite API Connection 🔍")
        print("-" * 50)

        # 1. User Profile
        try:
            profile = kite.profile()
            print("✅ User Profile Retrieved Successfully")
            print(f"User ID: {profile.get('user_id')}")
            print(f"Username: {profile.get('username')}")
        except Exception as profile_error:
            print("❌ Failed to Retrieve User Profile")
            print(f"Error: {profile_error}")

        # 2. Instruments List (Typically works even with limited permissions)
        try:
            instruments = kite.instruments()
            print(f"✅ Instruments List Retrieved: {len(instruments)} instruments")
        except Exception as instruments_error:
            print("❌ Failed to Retrieve Instruments List")
            print(f"Error: {instruments_error}")

        # 3. NIFTY Quote
        try:
            nifty_token = 26000  # NIFTY 50 instrument token
            nifty_quote = kite.quote(nifty_token)
            print("✅ NIFTY Quote Retrieved Successfully")
            print(f"Last Price: {nifty_quote[str(nifty_token)]['last_price']}")
        except Exception as quote_error:
            print("❌ Failed to Retrieve NIFTY Quote")
            print(f"Error: {quote_error}")

        # 4. Holdings
        try:
            holdings = kite.holdings()
            print(f"✅ Holdings Retrieved: {len(holdings)} holdings")
            for holding in holdings:
                print(f"  - {holding.get('tradingsymbol')}: {holding.get('quantity')} shares")
        except Exception as holdings_error:
            print("❌ Failed to Retrieve Holdings")
            print(f"Error: {holdings_error}")

        # 5. Historical Data
        try:
            # Try to fetch historical data for NIFTY
            historical_data = kite.historical_data(
                instrument_token=26000,  # NIFTY 50
                from_date='2024-01-01',
                to_date='2024-01-02',
                interval='day'
            )
            print("✅ Historical Data Retrieved Successfully")
            print(f"Data Points: {len(historical_data)}")
        except Exception as historical_error:
            print("❌ Failed to Retrieve Historical Data")
            print(f"Error: {historical_error}")

    except Exception as e:
        print("❌ Critical Error in Kite Connection")
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_kite_connection()
