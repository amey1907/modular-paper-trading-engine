#!/usr/bin/env python3
"""
Modular Paper Trading Engine
Supports multiple strategies with live Kite data
"""

import json
import time
import datetime
import pandas as pd
import numpy as np
import requests
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import sqlite3
import schedule
import math
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VirtualTrade:
    """Virtual trade record for ledger"""
    trade_id: str
    date: str
    time: str
    action: str  # BUY, SELL, ROLL, ADJUST
    symbol: str
    tradingsymbol: str
    quantity: int
    price: float
    total_value: float
    fees: float
    cash_impact: float
    balance_after: float
    strategy: str
    notes: str = ""

@dataclass
class MarketSnapshot:
    """Market data snapshot from Kite API"""
    timestamp: str
    nifty_price: float
    vix_level: float
    mmi_status: str
    nifty_change: float
    nifty_change_pct: float
    market_status: str
    trading_day: int

class KiteDataFetcher:
    """Live market data fetcher using Kite API (Read-Only)"""
    
    def __init__(self, api_key: str, access_token: str):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = "https://api.kite.trade"
        self.headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {api_key}:{access_token}"
        }
        self.instruments_cache = {}
        logger.info("Kite Data Fetcher initialized (Read-Only Mode)")
    
    def get_instruments(self, exchange: str = "NFO") -> pd.DataFrame:
        """Fetch instruments list from Kite"""
        try:
            url = f"{self.base_url}/instruments/{exchange}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                from io import StringIO
                instruments_df = pd.read_csv(StringIO(response.text))
                self.instruments_cache[exchange] = instruments_df
                logger.info(f"Fetched {len(instruments_df)} instruments from {exchange}")
                return instruments_df
            else:
                logger.error(f"Failed to fetch instruments: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return pd.DataFrame()
    
    def get_quote(self, instruments: List[str]) -> Dict:
        """Get live quotes for instruments"""
        try:
            instrument_string = "&i=".join(instruments)
            url = f"{self.base_url}/quote?i={instrument_string}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()['data']
                logger.info(f"Fetched quotes for {len(data)} instruments")
                return data
            else:
                logger.error(f"Failed to get quotes: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error getting quotes: {e}")
            return {}

class ModularPaperTradingEngine:
    """Modular Paper Trading Engine supporting multiple strategies"""
    
    def __init__(self, api_key: str, access_token: str):
        """Initialize the modular paper trading engine"""
        
        # Kite Data Connection (Read-Only)
        self.kite = KiteDataFetcher(api_key, access_token)
        
        # Portfolio Settings
        self.total_capital = 500000  # ₹5 Lakh
        self.strategies: Dict[str, object] = {}
        self.strategy_allocations: Dict[str, float] = {}
        
        # Trading Settings
        self.brokerage_per_lot = 20
        self.trade_counter = 1
        self.trade_ledger: List[VirtualTrade] = []
        self.daily_portfolio_values: List[Dict] = []
        
        # Database setup
        self.setup_database()
        
        logger.info("Modular Paper Trading Engine initialized")
    
    def add_strategy(self, strategy: object, allocation: float):
        """Add a strategy to the portfolio"""
        self.strategies[strategy.name] = strategy
        self.strategy_allocations[strategy.name] = allocation
        logger.info(f"Added strategy: {strategy.name} with allocation: ₹{allocation:,.0f}")
    
    def setup_database(self):
        """Setup SQLite database for paper trading data"""
        self.db_path = Path("modular_paper_trading.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Create tables
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                name TEXT PRIMARY KEY,
                allocation REAL,
                cash_balance REAL,
                invested_amount REAL
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS strategy_positions (
                strategy_name TEXT,
                symbol TEXT,
                tradingsymbol TEXT,
                instrument_token INTEGER,
                strike REAL,
                option_type TEXT,
                expiry TEXT,
                quantity INTEGER,
                entry_price REAL,
                entry_date TEXT,
                current_price REAL,
                status TEXT,
                notes TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS trade_ledger (
                trade_id TEXT,
                date TEXT,
                time TEXT,
                action TEXT,
                symbol TEXT,
                tradingsymbol TEXT,
                quantity INTEGER,
                price REAL,
                total_value REAL,
                fees REAL,
                cash_impact REAL,
                balance_after REAL,
                strategy TEXT,
                notes TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_portfolio (
                date TEXT PRIMARY KEY,
                total_portfolio_value REAL,
                total_cash REAL,
                total_invested REAL,
                strategy_count INTEGER,
                notes TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("Database initialized")
    
    def get_live_market_data(self) -> MarketSnapshot:
        """Fetch live market data using Kite API"""
        try:
            quotes = self.kite.get_quote([
                "NSE:NIFTY 50",
                "NSE:INDIA VIX"
            ])
            
            nifty_data = quotes.get("NSE:NIFTY 50", {})
            vix_data = quotes.get("NSE:INDIA VIX", {})
            
            nifty_price = nifty_data.get('last_price', 0)
            vix_level = vix_data.get('last_price', 0)
            nifty_change = nifty_data.get('net_change', 0)
            nifty_change_pct = nifty_data.get('percentage_change', 0)
            
            return MarketSnapshot(
                timestamp=datetime.datetime.now().isoformat(),
                nifty_price=nifty_price,
                vix_level=vix_level,
                mmi_status="Extreme Fear",  # Placeholder
                nifty_change=nifty_change,
                nifty_change_pct=nifty_change_pct,
                market_status="OPEN" if self.is_market_open() else "CLOSED",
                trading_day=1
            )
            
        except Exception as e:
            logger.error(f"Error fetching live market data: {e}")
            return MarketSnapshot("", 0, 0, "Error", 0, 0, "ERROR", 0)
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.datetime.now()
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        is_weekday = now.weekday() < 5
        is_market_hours = market_start <= now <= market_end
        
        return is_weekday and is_market_hours
    
    def daily_review(self):
        """Perform comprehensive daily review for all strategies"""
        logger.info("Starting daily review for all strategies...")
        
        try:
            # Get live market data
            market_data = self.get_live_market_data()
            
            if market_data.nifty_price == 0:
                logger.warning("Could not fetch market data, skipping review")
                return
            
            # Generate comprehensive report
            report = self.generate_daily_report(market_data)
            print(report)
            
            # Save daily data
            self.save_daily_data(market_data)
            
            logger.info("Daily review completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily review: {e}")
    
    def generate_daily_report(self, market_data: MarketSnapshot) -> str:
        """Generate comprehensive daily report for all strategies"""
        
        report = f"""
{'='*60}
MODULAR PAPER TRADING DAILY REPORT
Date: {datetime.date.today()} | Market: {market_data.market_status}
{'='*60}

📊 MARKET DATA (Live from Kite API):
   NIFTY 50: ₹{market_data.nifty_price:,.2f} ({market_data.nifty_change_pct:+.2f}%)
   India VIX: {market_data.vix_level:.2f}
   MMI Status: {market_data.mmi_status}

💰 PORTFOLIO OVERVIEW:
   Total Capital: ₹{self.total_capital:,.0f}
   Active Strategies: {len(self.strategies)}
   Total Trades: {len(self.trade_ledger)}

📋 STRATEGY SUMMARY:
"""
        
        total_portfolio_value = 0
        total_cash = 0
        total_invested = 0
        
        for strategy_name, strategy in self.strategies.items():
            try:
                positions = strategy.get_positions()
                cash_balance = strategy.get_cash_balance()
                invested_amount = strategy.get_invested_amount()
                
                total_portfolio_value += cash_balance + invested_amount
                total_cash += cash_balance
                total_invested += invested_amount
                
                report += f"""
   🎯 {strategy_name}:
      Allocation: ₹{self.strategy_allocations[strategy_name]:,.0f}
      Cash: ₹{cash_balance:,.0f}
      Invested: ₹{invested_amount:,.0f}
      Positions: {len([p for p in positions if p.status == "OPEN"])}
      Current Value: ₹{cash_balance + invested_amount:,.0f}
"""
            except Exception as e:
                logger.error(f"Error generating report for {strategy_name}: {e}")
        
        report += f"""
📈 PORTFOLIO TOTALS:
   Total Portfolio Value: ₹{total_portfolio_value:,.0f}
   Total Cash: ₹{total_cash:,.0f}
   Total Invested: ₹{total_invested:,.0f}
   Net P&L: ₹{total_portfolio_value - self.total_capital:+,.0f}

{'='*60}
"""
        
        return report
    
    def save_daily_data(self, market_data: MarketSnapshot):
        """Save daily data to database"""
        try:
            total_portfolio_value = 0
            total_cash = 0
            total_invested = 0
            
            for strategy in self.strategies.values():
                try:
                    total_portfolio_value += strategy.get_cash_balance() + strategy.get_invested_amount()
                    total_cash += strategy.get_cash_balance()
                    total_invested += strategy.get_invested_amount()
                except Exception as e:
                    logger.error(f"Error calculating strategy totals: {e}")
            
            self.conn.execute("""
                INSERT OR REPLACE INTO daily_portfolio
                (date, total_portfolio_value, total_cash, total_invested, strategy_count, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.date.today().isoformat(),
                total_portfolio_value,
                total_cash,
                total_invested,
                len(self.strategies),
                f"NIFTY: {market_data.nifty_price:.0f}, VIX: {market_data.vix_level:.1f}"
            ))
            
            self.conn.commit()
            logger.info("Daily data saved to database")
            
        except Exception as e:
            logger.error(f"Error saving daily data: {e}")
    
    def run_paper_trading_scheduler(self):
        """Run the paper trading scheduler"""
        logger.info("Starting Modular Paper Trading Engine Scheduler...")
        logger.info("📚 LEARNING MODE: No real trades will be executed")
        logger.info(f"💰 Total Capital: ₹{self.total_capital:,.0f}")
        logger.info(f"🎯 Active Strategies: {len(self.strategies)}")
        
        # Schedule daily review at market close
        schedule.every().day.at("15:45").do(self.daily_review)
        
        # Schedule quick updates during market hours
        schedule.every(30).minutes.do(self.quick_market_update)
        
        print("📅 Scheduled Activities:")
        print("   - Daily Review: 15:45 (Market Close)")
        print("   - Market Updates: Every 30 minutes")
        print("\n🚀 Modular Paper Trading Engine is now running...")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Paper Trading Engine stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def quick_market_update(self):
        """Quick market update during trading hours"""
        if not self.is_market_open():
            return
        
        try:
            market_data = self.get_live_market_data()
            if market_data.nifty_price > 0:
                # Log significant changes
                if abs(market_data.nifty_change_pct) > 2:
                    logger.info(f"Market Update - NIFTY: {market_data.nifty_price:.0f} "
                              f"({market_data.nifty_change_pct:+.1f}%), VIX: {market_data.vix_level:.1f}")
        
        except Exception as e:
            logger.error(f"Error in quick update: {e}")

def main():
    """Main function for modular paper trading engine"""
    print("🚀 MODULAR PAPER TRADING ENGINE")
    print("=" * 50)
    print("🎯 Support for Multiple Trading Strategies")
    print("💰 Virtual Portfolio: ₹5,00,000")
    print("⚠️  NO REAL TRADES - SIMULATION ONLY")
    print("📊 Data Source: Live Kite API")
    print("=" * 50)
    
    # Get API credentials
    api_key = input("Enter your Kite API Key (for data only): ").strip()
    access_token = input("Enter your Access Token: ").strip()
    
    if not api_key or not access_token:
        print("❌ API credentials required for live data")
        return
    
    try:
        # Initialize paper trading engine
        print("\n🚀 Initializing Modular Paper Trading Engine...")
        engine = ModularPaperTradingEngine(api_key, access_token)
        
        # Add strategies
        print("📋 Adding strategies...")
        
        # Import and add strategies dynamically
        try:
            from strategies.volatility_arbitrage import VolatilityArbitrageStrategy
            vol_strategy = VolatilityArbitrageStrategy(500000, 38550)
            engine.add_strategy(vol_strategy, 38550)
            print("✅ Added Volatility Arbitrage Strategy")
        except Exception as e:
            print(f"⚠️  Could not add Volatility Arbitrage Strategy: {e}")
        
        try:
            from strategies.equity_momentum import EquityMomentumStrategy
            equity_strategy = EquityMomentumStrategy(500000, 20000)
            engine.add_strategy(equity_strategy, 20000)
            print("✅ Added Equity Momentum Strategy")
        except Exception as e:
            print(f"⚠️  Could not add Equity Momentum Strategy: {e}")
        
        # Run initial review
        print("📊 Performing initial market review...")
        engine.daily_review()
        
        # Start automated monitoring
        print("\n🔄 Starting automated paper trading scheduler...")
        engine.run_paper_trading_scheduler()
        
    except KeyboardInterrupt:
        print("\n👋 Paper Trading Engine stopped by user")
    except Exception as e:
        logger.error(f"Engine error: {e}")
        print(f"❌ Error: {e}")
    finally:
        print("📊 Final performance summary available in database")

if __name__ == "__main__":
    main()
