#!/usr/bin/env python3
"""
Holiday Fallback System for Paper Trading Engine
Provides simulated data when markets are closed
"""

import random
from datetime import datetime, timedelta
from market_status_checker import MarketStatusChecker

class HolidayFallbackData:
    """Provides fallback data when markets are closed"""
    
    def __init__(self):
        self.checker = MarketStatusChecker()
        
        # Last known market data (you can update these with actual values)
        self.last_known_data = {
            'nifty': {
                'price': 24631.0,
                'change': 0.0,
                'change_pct': 0.0,
                'date': '2025-08-14'
            },
            'vix': {
                'price': 12.0,
                'change': 0.0,
                'date': '2025-08-14'
            }
        }
    
    def get_market_data(self):
        """Get market data (live or simulated)"""
        market_open, reason = self.checker.is_market_open()
        
        if market_open:
            # Try to get live data
            live_accessible, live_reason = self.checker.check_live_data_access()
            if live_accessible:
                return self._get_live_data()
        
        # Fallback to simulated data
        return self._get_simulated_data()
    
    def _get_live_data(self):
        """Get live market data (placeholder)"""
        # This would be implemented to fetch real data
        return {
            'timestamp': datetime.now().isoformat(),
            'nifty_price': 24631.0,
            'vix_level': 12.0,
            'mmi_status': 'Extreme Fear',
            'nifty_change': 0.0,
            'nifty_change_pct': 0.0,
            'market_status': 'OPEN',
            'data_source': 'LIVE'
        }
    
    def _get_simulated_data(self):
        """Get simulated market data for holidays/closed markets"""
        # Simulate small random movements around last known values
        nifty_base = self.last_known_data['nifty']['price']
        vix_base = self.last_known_data['vix']['price']
        
        # Small random variation (±0.5%)
        nifty_variation = random.uniform(-0.005, 0.005)
        vix_variation = random.uniform(-0.02, 0.02)
        
        nifty_price = nifty_base * (1 + nifty_variation)
        vix_price = vix_base * (1 + vix_variation)
        
        nifty_change = nifty_price - nifty_base
        nifty_change_pct = (nifty_change / nifty_base) * 100
        
        return {
            'timestamp': datetime.now().isoformat(),
            'nifty_price': round(nifty_price, 2),
            'vix_level': round(vix_price, 2),
            'mmi_status': 'Extreme Fear',
            'nifty_change': round(nifty_change, 2),
            'nifty_change_pct': round(nifty_change_pct, 2),
            'market_status': 'CLOSED (Holiday)',
            'data_source': 'SIMULATED',
            'note': 'Using simulated data - market closed for Independence Day'
        }
    
    def get_option_prices(self, symbol, strike, option_type, expiry):
        """Get simulated option prices"""
        # This would calculate option prices using Black-Scholes
        # For now, return simulated prices
        
        base_price = random.uniform(100, 1000)
        volatility = random.uniform(0.15, 0.35)
        
        return {
            'symbol': symbol,
            'strike': strike,
            'option_type': option_type,
            'expiry': expiry,
            'price': round(base_price, 2),
            'delta': round(random.uniform(-1, 1), 4),
            'gamma': round(random.uniform(0, 0.01), 6),
            'theta': round(random.uniform(-50, -10), 2),
            'vega': round(random.uniform(50, 200), 2),
            'iv': round(volatility * 100, 2),
            'data_source': 'SIMULATED'
        }
    
    def get_portfolio_summary(self):
        """Get portfolio summary with simulated data"""
        return {
            'total_capital': 500000,
            'available_cash': 441450,  # 500000 - 38550 - 20000
            'invested_amount': 58550,
            'total_pnl': random.uniform(-2000, 2000),
            'market_status': 'CLOSED (Holiday)',
            'data_source': 'SIMULATED',
            'last_update': datetime.now().isoformat()
        }

def main():
    """Test the holiday fallback system"""
    fallback = HolidayFallbackData()
    
    print("🚀 Holiday Fallback System Test")
    print("=" * 50)
    
    # Get market data
    market_data = fallback.get_market_data()
    
    print("📊 Market Data:")
    print(f"   NIFTY: ₹{market_data['nifty_price']:,.2f} ({market_data['nifty_change_pct']:+.2f}%)")
    print(f"   VIX: {market_data['vix_level']:.2f}")
    print(f"   Status: {market_data['market_status']}")
    print(f"   Source: {market_data['data_source']}")
    print(f"   Note: {market_data.get('note', 'N/A')}")
    
    print("\n" + "=" * 50)
    
    # Get option prices
    print("📈 Simulated Option Prices:")
    option = fallback.get_option_prices("NIFTY26MAR24600CE", 24600, "CE", "2026-03-26")
    print(f"   {option['symbol']}: ₹{option['price']:.0f}")
    print(f"   Greeks: Δ{option['delta']:.3f}, Γ{option['gamma']:.6f}, Θ₹{option['theta']:.0f}")
    print(f"   IV: {option['iv']:.1f}%")
    
    print("\n" + "=" * 50)
    
    # Get portfolio summary
    portfolio = fallback.get_portfolio_summary()
    print("💰 Portfolio Summary:")
    print(f"   Total Capital: ₹{portfolio['total_capital']:,.0f}")
    print(f"   Available Cash: ₹{portfolio['available_cash']:,.0f}")
    print(f"   Invested Amount: ₹{portfolio['invested_amount']:,.0f}")
    print(f"   P&L: ₹{portfolio['total_pnl']:+,.0f}")
    print(f"   Status: {portfolio['market_status']}")
    
    print("\n" + "=" * 50)
    print("💡 This system allows paper trading to continue on holidays!")
    print("🔄 Switch to live data when market opens on Monday")

if __name__ == "__main__":
    main()
