#!/usr/bin/env python3
"""
Market Status Checker with Holiday Handling
"""

import requests
from datetime import datetime, timedelta
from config import KITE_API_KEY, KITE_ACCESS_TOKEN

class MarketStatusChecker:
    """Check market status and provide fallback data"""
    
    def __init__(self):
        self.api_key = KITE_API_KEY
        self.access_token = KITE_ACCESS_TOKEN
        self.base_url = "https://api.kite.trade"
        self.headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}"
        }
        
        # Known Indian market holidays (2025)
        self.holidays_2025 = [
            "2025-01-26",  # Republic Day
            "2025-03-07",  # Holi
            "2025-04-11",  # Ram Navami
            "2025-05-01",  # Maharashtra Day
            "2025-08-15",  # Independence Day
            "2025-10-02",  # Gandhi Jayanti
            "2025-11-14",  # Diwali
            "2025-12-25",  # Christmas
        ]
    
    def is_holiday(self, date=None):
        """Check if given date is a holiday"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        return date_str in self.holidays_2025
    
    def is_weekend(self, date=None):
        """Check if given date is weekend"""
        if date is None:
            date = datetime.now()
        
        return date.weekday() >= 5  # Saturday = 5, Sunday = 6
    
    def is_market_open(self):
        """Check if market is currently open"""
        now = datetime.now()
        
        # Check if it's a holiday
        if self.is_holiday(now):
            return False, "Holiday"
        
        # Check if it's weekend
        if self.is_weekend(now):
            return False, "Weekend"
        
        # Check market hours (9:15 AM to 3:30 PM IST)
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if market_start <= now <= market_end:
            return True, "Market Hours"
        else:
            return False, "Outside Market Hours"
    
    def check_live_data_access(self):
        """Check if live market data is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/quote?i=NSE:NIFTY%2050", 
                headers=self.headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Live data accessible"
            elif response.status_code == 403:
                return False, "Live data not accessible (market closed or permission issue)"
            else:
                return False, f"Unexpected status: {response.status_code}"
                
        except Exception as e:
            return False, f"Error: {e}"
    
    def get_historical_data(self, instrument_token, from_date, to_date, interval="day"):
        """Get historical data for an instrument"""
        try:
            url = f"{self.base_url}/instruments/historical/{instrument_token}/{interval}"
            params = {
                'from': from_date,
                'to': to_date
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'candles' in data['data']:
                    return True, data['data']['candles']
                else:
                    return False, "No data in response"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Error: {e}"
    
    def get_last_available_data(self):
        """Get the last available market data (live or historical)"""
        market_open, reason = self.is_market_open()
        live_accessible, live_reason = self.check_live_data_access()
        
        print(f"🔍 Market Status Check")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏪 Market Open: {market_open} ({reason})")
        print(f"📊 Live Data: {live_accessible} ({live_reason})")
        print("=" * 50)
        
        if live_accessible:
            print("🟢 Live market data is available!")
            return "LIVE", None
        else:
            print("🔒 Live data not available, trying historical data...")
            
            # Try to get yesterday's data
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Get NIFTY data
            success, nifty_data = self.get_historical_data(256265, yesterday, yesterday)
            if success:
                print(f"✅ NIFTY historical data: {len(nifty_data)} candles")
                if nifty_data:
                    last_nifty = nifty_data[-1]
                    print(f"📈 Last NIFTY close: {last_nifty[4]} (₹{last_nifty[4]:,.2f})")
            else:
                print(f"❌ NIFTY historical data failed: {nifty_data}")
            
            # Get VIX data
            success, vix_data = self.get_historical_data(260105, yesterday, yesterday)
            if success:
                print(f"✅ VIX historical data: {len(vix_data)} candles")
                if vix_data:
                    last_vix = vix_data[-1]
                    print(f"📈 Last VIX close: {last_vix[4]:.2f}")
            else:
                print(f"❌ VIX historical data failed: {vix_data}")
            
            return "HISTORICAL", {
                'nifty': nifty_data[-1] if success and nifty_data else None,
                'vix': vix_data[-1] if success and vix_data else None,
                'date': yesterday
            }

def main():
    """Main function to test market status"""
    checker = MarketStatusChecker()
    
    print("🚀 Market Status Checker")
    print("=" * 50)
    
    # Check current status
    data_type, data = checker.get_last_available_data()
    
    print(f"\n📊 Data Type Available: {data_type}")
    if data_type == "HISTORICAL" and data:
        print(f"📅 Historical Data Date: {data['date']}")
        if data['nifty']:
            print(f"📈 NIFTY: ₹{data['nifty'][4]:,.2f}")
        if data['vix']:
            print(f"📊 VIX: {data['vix'][4]:.2f}")
    
    print("\n" + "=" * 50)
    print("💡 Recommendations:")
    
    if data_type == "LIVE":
        print("✅ Use live market data for real-time trading")
    elif data_type == "HISTORICAL":
        print("📅 Use historical data for backtesting and analysis")
        print("🔄 Switch to live data when market opens")
    else:
        print("❌ No data available - check API permissions")

if __name__ == "__main__":
    main()
