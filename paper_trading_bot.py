
#!/usr/bin/env python3
"""
Paper Trading Bot for Volatility Arbitrage Strategy
Virtual Portfolio Management using LIVE Kite API Data
NO REAL TRADES - SIMULATION ONLY with REAL MARKET PRICES

Virtual Portfolio: ₹5,00,000
Strategy Allocation: ₹38,550 (7.7%)
Duration: 1 Year (365 days)
Data Source: Live Kite API (Read-Only)
Objective: Learning and trade ledger maintenance

Author: Trading Assistant
Version: 2.0 - Paper Trading with Live Data
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
class VirtualPosition:
    """Virtual options position for paper trading"""
    trade_id: str
    symbol: str
    tradingsymbol: str  # Kite format symbol
    instrument_token: int
    strike: float
    option_type: str  # 'CE' or 'PE'
    expiry: str
    quantity: int  # Positive for long, negative for short
    entry_price: float
    entry_date: str
    current_price: float = 0.0
    exit_price: float = 0.0
    exit_date: str = ""
    status: str = "OPEN"  # OPEN, CLOSED, EXPIRED
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    iv: float = 0.0
    pnl: float = 0.0
    notes: str = ""

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
    fees: float  # Simulated brokerage
    cash_impact: float  # Net cash flow
    balance_after: float
    strategy: str = "Volatility Arbitrage"
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
                # Parse CSV response
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
    
    def search_instrument(self, symbol_pattern: str, exchange: str = "NFO") -> Dict:
        """Search for instrument by symbol pattern"""
        if exchange not in self.instruments_cache:
            self.get_instruments(exchange)
        
        df = self.instruments_cache.get(exchange, pd.DataFrame())
        if df.empty:
            return {}
        
        # Search for matching symbols
        matches = df[df['tradingsymbol'].str.contains(symbol_pattern, case=False, na=False)]
        
        if not matches.empty:
            match = matches.iloc[0]
            return {
                'instrument_token': match['instrument_token'],
                'tradingsymbol': match['tradingsymbol'],
                'name': match['name'],
                'strike': match.get('strike', 0),
                'expiry': match.get('expiry', ''),
                'instrument_type': match.get('instrument_type', '')
            }
        return {}
    
    def get_quote(self, instruments: List[str]) -> Dict:
        """Get live quotes for instruments"""
        try:
            # Format instruments for API call
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
    
    def get_historical_data(self, instrument_token: int, from_date: str, 
                           to_date: str, interval: str = "day") -> pd.DataFrame:
        """Get historical data for an instrument"""
        try:
            url = f"{self.base_url}/instruments/historical/{instrument_token}/{interval}"
            params = {
                'from': from_date,
                'to': to_date
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()['data']['candles']
                df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                return df
            else:
                logger.error(f"Failed to get historical data: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()

class PaperTradingBot:
    """Paper Trading Bot with Live Kite Data"""
    
    def __init__(self, api_key: str, access_token: str):
        """Initialize the paper trading environment"""
        
        # Kite Data Connection (Read-Only)
        self.kite = KiteDataFetcher(api_key, access_token)
        
        # Virtual Portfolio Settings
        self.total_virtual_capital = 500000  # ₹5 Lakh
        self.strategy_allocation = 38550     # ₹38,550 for this strategy
        self.available_cash = self.total_virtual_capital
        self.invested_amount = 0
        
        # Strategy Parameters
        self.strategy_start_date = datetime.date.today()
        self.target_duration_days = 365  # 1 year learning period
        self.nifty_entry_level = 24631
        self.vix_entry_level = 12.0
        
        # Virtual Portfolio Tracking
        self.virtual_positions: List[VirtualPosition] = []
        self.trade_ledger: List[VirtualTrade] = []
        self.daily_portfolio_values: List[Dict] = []
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.portfolio_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
        
        # Learning Metrics
        self.learning_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'rolling_executed': 0,
            'adjustments_made': 0,
            'days_active': 0
        }
        
        # Paper Trading Settings
        self.brokerage_per_lot = 20  # ₹20 per lot (simulated)
        self.trade_counter = 1
        
        # Database setup
        self.setup_database()
        
        logger.info("Paper Trading Bot initialized with ₹5,00,000 virtual capital")
        logger.info("Strategy allocation: ₹38,550 (7.7% of portfolio)")
    
    def setup_database(self):
        """Setup SQLite database for paper trading data"""
        self.db_path = Path("paper_trading_portfolio.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Create tables for paper trading
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS virtual_positions (
                trade_id TEXT PRIMARY KEY,
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
                exit_price REAL,
                exit_date TEXT,
                status TEXT,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                iv REAL,
                pnl REAL,
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
                trading_day INTEGER,
                nifty_price REAL,
                vix_level REAL,
                mmi_status TEXT,
                portfolio_value REAL,
                cash_balance REAL,
                invested_amount REAL,
                total_pnl REAL,
                daily_pnl REAL,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                open_positions INTEGER,
                notes TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                lesson_type TEXT,
                description TEXT,
                market_condition TEXT,
                action_taken TEXT,
                outcome TEXT,
                lesson_learned TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("Database initialized for paper trading")
    
    def initialize_paper_strategy(self):
        """Initialize the paper trading strategy positions"""
        logger.info("Setting up initial paper trading positions...")
        
        # Fetch instrument data first
        instruments_df = self.kite.get_instruments("NFO")
        
        # Define the strategy positions
        strategy_positions = [
            # Long March 2026 Straddle (Back Month)
            {
                'symbol': 'NIFTY26MAR24600CE',
                'strike': 24600,
                'option_type': 'CE',
                'expiry': '2026-03-26',
                'quantity': 25,
                'entry_price': 1100,
                'position_type': 'LONG'
            },
            {
                'symbol': 'NIFTY26MAR24600PE',
                'strike': 24600,
                'option_type': 'PE',
                'expiry': '2026-03-26',
                'quantity': 25,
                'entry_price': 980,
                'position_type': 'LONG'
            },
            # Short September 2025 Straddle (Front Month)
            {
                'symbol': 'NIFTY25SEP24600CE',
                'strike': 24600,
                'option_type': 'CE',
                'expiry': '2025-09-26',
                'quantity': -25,
                'entry_price': 350,
                'position_type': 'SHORT'
            },
            {
                'symbol': 'NIFTY25SEP24600PE',
                'strike': 24600,
                'option_type': 'PE',
                'expiry': '2025-09-26',
                'quantity': -25,
                'entry_price': 320,
                'position_type': 'SHORT'
            },
            # Protective Wings
            {
                'symbol': 'NIFTY26MAR26000CE',
                'strike': 26000,
                'option_type': 'CE',
                'expiry': '2026-03-26',
                'quantity': 10,
                'entry_price': 150,
                'position_type': 'LONG'
            },
            {
                'symbol': 'NIFTY26MAR23000PE',
                'strike': 23000,
                'option_type': 'PE',
                'expiry': '2026-03-26',
                'quantity': 10,
                'entry_price': 180,
                'position_type': 'LONG'
            }
        ]
        
        # Create virtual positions
        total_investment = 0
        
        for pos_data in strategy_positions:
            # Search for instrument in Kite data
            search_pattern = f"NIFTY.*{pos_data['strike']}.*{pos_data['option_type']}"
            instrument_info = self.kite.search_instrument(search_pattern)
            
            trade_id = f"PT{self.trade_counter:04d}"
            self.trade_counter += 1
            
            # Create virtual position
            position = VirtualPosition(
                trade_id=trade_id,
                symbol=pos_data['symbol'],
                tradingsymbol=instrument_info.get('tradingsymbol', pos_data['symbol']),
                instrument_token=instrument_info.get('instrument_token', 0),
                strike=pos_data['strike'],
                option_type=pos_data['option_type'],
                expiry=pos_data['expiry'],
                quantity=pos_data['quantity'],
                entry_price=pos_data['entry_price'],
                entry_date=datetime.date.today().isoformat(),
                current_price=pos_data['entry_price'],
                status="OPEN",
                notes=f"Initial {pos_data['position_type']} position"
            )
            
            self.virtual_positions.append(position)
            
            # Calculate investment
            investment = abs(pos_data['quantity']) * pos_data['entry_price']
            if pos_data['quantity'] > 0:  # Long positions require cash outflow
                total_investment += investment
            else:  # Short positions provide cash inflow
                total_investment -= investment
            
            # Create trade ledger entry
            fees = abs(pos_data['quantity']) * self.brokerage_per_lot
            cash_impact = -investment if pos_data['quantity'] > 0 else investment
            cash_impact -= fees  # Always subtract fees
            
            trade = VirtualTrade(
                trade_id=trade_id,
                date=datetime.date.today().isoformat(),
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                action="BUY" if pos_data['quantity'] > 0 else "SELL",
                symbol=pos_data['symbol'],
                tradingsymbol=instrument_info.get('tradingsymbol', pos_data['symbol']),
                quantity=abs(pos_data['quantity']),
                price=pos_data['entry_price'],
                total_value=investment,
                fees=fees,
                cash_impact=cash_impact,
                balance_after=self.available_cash + cash_impact,
                notes=f"Initial strategy position - {pos_data['position_type']}"
            )
            
            self.trade_ledger.append(trade)
            self.available_cash += cash_impact
        
        self.invested_amount = total_investment
        self.learning_stats['total_trades'] = len(strategy_positions)
        
        # Save to database
        self.save_positions_to_db()
        self.save_trades_to_db()
        
        logger.info(f"Initialized {len(strategy_positions)} virtual positions")
        logger.info(f"Net investment: ₹{self.invested_amount:,.0f}")
        logger.info(f"Available cash: ₹{self.available_cash:,.0f}")
    
    def get_live_market_data(self) -> MarketSnapshot:
        """Fetch live market data using Kite API"""
        try:
            # Get NIFTY and VIX quotes
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
            
            # Get MMI status (would need external API or web scraping)
            mmi_status = self.get_mmi_status()
            
            # Calculate trading day
            trading_day = (datetime.date.today() - self.strategy_start_date).days + 1
            
            return MarketSnapshot(
                timestamp=datetime.datetime.now().isoformat(),
                nifty_price=nifty_price,
                vix_level=vix_level,
                mmi_status=mmi_status,
                nifty_change=nifty_change,
                nifty_change_pct=nifty_change_pct,
                market_status="OPEN" if self.is_market_open() else "CLOSED",
                trading_day=trading_day
            )
            
        except Exception as e:
            logger.error(f"Error fetching live market data: {e}")
            return MarketSnapshot("", 0, 0, "Error", 0, 0, "ERROR", 0)
    
    def get_mmi_status(self) -> str:
        """Get MMI status (placeholder - would need web scraping)"""
        # In real implementation, would scrape from Tickertape
        return "Extreme Fear"  # Current known status
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.datetime.now()
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # Check if it's a weekday and within market hours
        is_weekday = now.weekday() < 5
        is_market_hours = market_start <= now <= market_end
        
        return is_weekday and is_market_hours
    
    def update_position_prices(self, market_data: MarketSnapshot):
        """Update current prices for all positions using live Kite data"""
        if not self.virtual_positions:
            return
        
        try:
            # Collect all instrument tokens
            instruments_to_quote = []
            token_to_position = {}
            
            for position in self.virtual_positions:
                if position.status == "OPEN" and position.instrument_token > 0:
                    instrument_key = f"NFO:{position.tradingsymbol}"
                    instruments_to_quote.append(instrument_key)
                    token_to_position[instrument_key] = position
            
            if not instruments_to_quote:
                logger.warning("No instruments to quote")
                return
            
            # Get live quotes
            quotes = self.kite.get_quote(instruments_to_quote)
            
            # Update position prices
            for instrument_key, quote_data in quotes.items():
                if instrument_key in token_to_position:
                    position = token_to_position[instrument_key]
                    old_price = position.current_price
                    position.current_price = quote_data.get('last_price', old_price)
                    
                    # Calculate Greeks
                    greeks = self.calculate_option_greeks(
                        spot=market_data.nifty_price,
                        strike=position.strike,
                        expiry=position.expiry,
                        option_type=position.option_type,
                        volatility=market_data.vix_level/100
                    )
                    
                    position.delta = greeks['delta']
                    position.gamma = greeks['gamma'] 
                    position.theta = greeks['theta']
                    position.vega = greeks['vega']
                    
                    # Calculate P&L
                    position.pnl = (position.current_price - position.entry_price) * position.quantity
            
            logger.info(f"Updated prices for {len(quotes)} positions")
            
        except Exception as e:
            logger.error(f"Error updating position prices: {e}")
    
    def calculate_option_greeks(self, spot: float, strike: float, expiry: str, 
                              option_type: str, risk_free_rate: float = 0.07, 
                              volatility: float = 0.20) -> Dict[str, float]:
        """Calculate Black-Scholes Greeks"""
        try:
            # Parse expiry date
            expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d")
            today = datetime.datetime.now()
            time_to_expiry = (expiry_date - today).days / 365.0
            
            if time_to_expiry <= 0:
                return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
            
            # Black-Scholes calculations
            d1 = (math.log(spot/strike) + (risk_free_rate + 0.5*volatility**2)*time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
            d2 = d1 - volatility * math.sqrt(time_to_expiry)
            
            # Standard normal CDF approximation
            def norm_cdf(x):
                return 0.5 * (1 + math.erf(x / math.sqrt(2)))
            
            def norm_pdf(x):
                return (1/math.sqrt(2*math.pi)) * math.exp(-0.5*x**2)
            
            # Calculate Greeks
            if option_type.upper() == 'CE':
                delta = norm_cdf(d1)
            else:  # PE
                delta = norm_cdf(d1) - 1
            
            gamma = norm_pdf(d1) / (spot * volatility * math.sqrt(time_to_expiry))
            theta = (-spot * norm_pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry)) - 
                    risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * 
                    (norm_cdf(d2) if option_type.upper() == 'CE' else norm_cdf(-d2))) / 365
            vega = spot * norm_pdf(d1) * math.sqrt(time_to_expiry) / 100
            
            return {
                'delta': round(delta, 4),
                'gamma': round(gamma, 6), 
                'theta': round(theta, 2),
                'vega': round(vega, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    def calculate_portfolio_metrics(self) -> Dict:
        """Calculate overall portfolio metrics"""
        total_pnl = 0
        portfolio_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
        
        for position in self.virtual_positions:
            if position.status == "OPEN":
                total_pnl += position.pnl
                portfolio_greeks['delta'] += position.delta * position.quantity
                portfolio_greeks['gamma'] += position.gamma * position.quantity
                portfolio_greeks['theta'] += position.theta * position.quantity
                portfolio_greeks['vega'] += position.vega * position.quantity
        
        portfolio_value = self.available_cash + self.invested_amount + total_pnl
        
        return {
            'total_pnl': total_pnl,
            'portfolio_value': portfolio_value,
            'portfolio_greeks': portfolio_greeks,
            'open_positions': len([p for p in self.virtual_positions if p.status == "OPEN"])
        }
    
    def daily_review(self):
        """Perform comprehensive daily review"""
        logger.info("Starting daily paper trading review...")
        
        try:
            # Get live market data
            market_data = self.get_live_market_data()
            
            if market_data.nifty_price == 0:
                logger.warning("Could not fetch market data, skipping review")
                return
            
            # Update all position prices with live data
            self.update_position_prices(market_data)
            
            # Calculate portfolio metrics
            metrics = self.calculate_portfolio_metrics()
            
            # Update instance variables
            self.total_pnl = metrics['total_pnl']
            self.portfolio_greeks = metrics['portfolio_greeks']
            
            # Generate comprehensive report
            report = self.generate_daily_report(market_data, metrics)
            print(report)
            
            # Save daily data
            self.save_daily_data(market_data, metrics)
            
            # Save updated positions
            self.save_positions_to_db()
            
            # Check for learning opportunities
            self.check_learning_opportunities(market_data)
            
            # Update learning stats
            self.learning_stats['days_active'] = market_data.trading_day
            
            logger.info("Daily review completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily review: {e}")
    
    def generate_daily_report(self, market_data: MarketSnapshot, metrics: Dict) -> str:
        """Generate comprehensive daily report"""
        
        report = f"""
{'='*60}
PAPER TRADING DAILY REPORT - VOLATILITY ARBITRAGE
Date: {datetime.date.today()} | Strategy Day: {market_data.trading_day}/365
{'='*60}

📊 MARKET DATA (Live from Kite API):
   NIFTY 50: ₹{market_data.nifty_price:,.2f} ({market_data.nifty_change_pct:+.2f}%)
   India VIX: {market_data.vix_level:.2f}
   MMI Status: {market_data.mmi_status}
   Market: {market_data.market_status}

💰 VIRTUAL PORTFOLIO PERFORMANCE:
   Total Capital: ₹{self.total_virtual_capital:,.0f}
   Available Cash: ₹{self.available_cash:,.0f}
   Invested Amount: ₹{self.invested_amount:,.0f}
   Current P&L: ₹{metrics['total_pnl']:+,.0f}
   Portfolio Value: ₹{metrics['portfolio_value']:,.0f}
   Return: {metrics['total_pnl']/self.invested_amount*100:+.2f}%

📈 PORTFOLIO GREEKS:
   Delta: {metrics['portfolio_greeks']['delta']:+.2f}
   Gamma: {metrics['portfolio_greeks']['gamma']:+.4f}
   Theta: ₹{metrics['portfolio_greeks']['theta']:+.0f}/day
   Vega: ₹{metrics['portfolio_greeks']['vega']:+.0f}/point

📋 POSITION SUMMARY ({metrics['open_positions']} Open):
"""
        
        # Add position details
        for i, position in enumerate(self.virtual_positions, 1):
            if position.status == "OPEN":
                pnl_pct = (position.pnl / (abs(position.quantity) * position.entry_price)) * 100
                report += f"""
   {i}. {position.symbol} | {position.quantity:+d} lots
      Entry: ₹{position.entry_price:.0f} | Current: ₹{position.current_price:.0f}
      P&L: ₹{position.pnl:+,.0f} ({pnl_pct:+.1f}%)
      Greeks: Δ{position.delta:+.3f} | Θ₹{position.theta:+.0f} | ν₹{position.vega:+.0f}
"""
        
        # Add learning metrics
        win_rate = (self.learning_stats['winning_trades'] / max(1, self.learning_stats['total_trades'])) * 100
        
        report += f"""
📚 LEARNING PROGRESS:
   Total Virtual Trades: {self.learning_stats['total_trades']}
   Winning Trades: {self.learning_stats['winning_trades']}
   Win Rate: {win_rate:.1f}%
   Largest Win: ₹{self.learning_stats['largest_win']:+,.0f}
   Largest Loss: ₹{self.learning_stats['largest_loss']:+,.0f}
   Rolls Executed: {self.learning_stats['rolling_executed']}
   Adjustments Made: {self.learning_stats['adjustments_made']}

{'='*60}
"""
        
        return report
    
    def save_daily_data(self, market_data: MarketSnapshot, metrics: Dict):
        """Save daily data to database"""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO daily_portfolio
                (date, trading_day, nifty_price, vix_level, mmi_status, 
                 portfolio_value, cash_balance, invested_amount, total_pnl, daily_pnl,
                 delta, gamma, theta, vega, open_positions, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.date.today().isoformat(),
                market_data.trading_day,
                market_data.nifty_price,
                market_data.vix_level,
                market_data.mmi_status,
                metrics['portfolio_value'],
                self.available_cash,
                self.invested_amount,
                metrics['total_pnl'],
                self.daily_pnl,
                metrics['portfolio_greeks']['delta'],
                metrics['portfolio_greeks']['gamma'],
                metrics['portfolio_greeks']['theta'],
                metrics['portfolio_greeks']['vega'],
                metrics['open_positions'],
                f"VIX: {market_data.vix_level:.1f}, NIFTY: {market_data.nifty_change_pct:+.1f}%"
            ))
            
            self.conn.commit()
            logger.info("Daily data saved to database")
            
        except Exception as e:
            logger.error(f"Error saving daily data: {e}")
    
    def save_positions_to_db(self):
        """Save all positions to database"""
        try:
            # Clear existing positions
            self.conn.execute("DELETE FROM virtual_positions")
            
            # Insert current positions
            for position in self.virtual_positions:
                self.conn.execute("""
                    INSERT INTO virtual_positions VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    position.trade_id, position.symbol, position.tradingsymbol,
                    position.instrument_token, position.strike, position.option_type,
                    position.expiry, position.quantity, position.entry_price,
                    position.entry_date, position.current_price, position.exit_price,
                    position.exit_date, position.status, position.delta,
                    position.gamma, position.theta, position.vega, position.iv,
                    position.pnl, position.notes
                ))
            
            self.conn.commit()
            logger.info(f"Saved {len(self.virtual_positions)} positions to database")
            
        except Exception as e:
            logger.error(f"Error saving positions: {e}")
    
    def save_trades_to_db(self):
        """Save all trades to database"""
        try:
            for trade in self.trade_ledger:
                self.conn.execute("""
                    INSERT OR REPLACE INTO trade_ledger VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade.trade_id, trade.date, trade.time, trade.action,
                    trade.symbol, trade.tradingsymbol, trade.quantity,
                    trade.price, trade.total_value, trade.fees, trade.cash_impact,
                    trade.balance_after, trade.strategy, trade.notes
                ))
            
            self.conn.commit()
            logger.info(f"Saved {len(self.trade_ledger)} trades to database")
            
        except Exception as e:
            logger.error(f"Error saving trades: {e}")
    
    def check_learning_opportunities(self, market_data: MarketSnapshot):
        """Identify and log learning opportunities"""
        lessons = []
        
        # VIX movement lessons
        vix_change = market_data.vix_level - self.vix_entry_level
        if abs(vix_change) > 2:
            lessons.append({
                'type': 'Volatility Movement',
                'description': f'VIX moved from {self.vix_entry_level} to {market_data.vix_level:.1f}',
                'lesson': 'Observe how option prices and Greeks change with volatility shifts'
            })
        
        # NIFTY movement lessons
        nifty_change_pct = (market_data.nifty_price - self.nifty_entry_level) / self.nifty_entry_level * 100
        if abs(nifty_change_pct) > 5:
            lessons.append({
                'type': 'Directional Movement',
                'description': f'NIFTY moved {nifty_change_pct:+.1f}% from entry level',
                'lesson': 'Study delta hedging requirements and gamma effects'
            })
        
        # Greeks-based lessons
        portfolio_delta = self.portfolio_greeks['delta']
        if abs(portfolio_delta) > 5:
            lessons.append({
                'type': 'Risk Management',
                'description': f'Portfolio delta at {portfolio_delta:.1f}',
                'lesson': 'Consider delta hedging to maintain market neutrality'
            })
        
        # Log lessons to database
        for lesson in lessons:
            self.conn.execute("""
                INSERT INTO learning_log 
                (date, lesson_type, description, market_condition, action_taken, lesson_learned)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.date.today().isoformat(),
                lesson['type'],
                lesson['description'],
                f"NIFTY: {market_data.nifty_price:.0f}, VIX: {market_data.vix_level:.1f}",
                "Monitoring",
                lesson['lesson']
            ))
        
        if lessons:
            self.conn.commit()
            logger.info(f"Logged {len(lessons)} learning opportunities")
    
    def execute_virtual_trade(self, action: str, symbol: str, quantity: int, 
                             price: float, notes: str = "") -> bool:
        """Execute a virtual trade (for learning purposes)"""
        try:
            trade_id = f"PT{self.trade_counter:04d}"
            self.trade_counter += 1
            
            total_value = abs(quantity) * price
            fees = abs(quantity) * self.brokerage_per_lot
            
            # Calculate cash impact
            if action == "BUY":
                cash_impact = -(total_value + fees)
            else:  # SELL
                cash_impact = total_value - fees
            
            # Check if sufficient funds for buy orders
            if action == "BUY" and abs(cash_impact) > self.available_cash:
                logger.warning(f"Insufficient funds for {symbol} purchase")
                return False
            
            # Create trade record
            trade = VirtualTrade(
                trade_id=trade_id,
                date=datetime.date.today().isoformat(),
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                action=action,
                symbol=symbol,
                tradingsymbol=symbol,  # Simplified
                quantity=abs(quantity),
                price=price,
                total_value=total_value,
                fees=fees,
                cash_impact=cash_impact,
                balance_after=self.available_cash + cash_impact,
                notes=notes
            )
            
            self.trade_ledger.append(trade)
            self.available_cash += cash_impact
            self.learning_stats['total_trades'] += 1
            
            logger.info(f"Executed virtual {action}: {quantity} x {symbol} @ ₹{price}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing virtual trade: {e}")
            return False
    
    def simulate_monthly_roll(self, current_expiry: str, new_expiry: str):
        """Simulate monthly rolling of short positions"""
        logger.info(f"Simulating roll from {current_expiry} to {new_expiry}")
        
        positions_to_roll = [p for p in self.virtual_positions 
                            if p.expiry == current_expiry and p.quantity < 0 and p.status == "OPEN"]
        
        for position in positions_to_roll:
            # Close current position
            close_price = position.current_price * 0.95  # Simulate favorable close
            self.execute_virtual_trade(
                action="BUY",  # Buy back short position
                symbol=position.symbol,
                quantity=abs(position.quantity),
                price=close_price,
                notes=f"Rolling close - {current_expiry}"
            )
            
            # Mark position as closed
            position.status = "CLOSED"
            position.exit_price = close_price
            position.exit_date = datetime.date.today().isoformat()
            
            # Open new position
            new_symbol = position.symbol.replace(current_expiry.replace('-', ''), new_expiry.replace('-', ''))
            new_price = close_price * 1.1  # Simulate new month premium
            
            self.execute_virtual_trade(
                action="SELL",
                symbol=new_symbol,
                quantity=abs(position.quantity),
                price=new_price,
                notes=f"Rolling open - {new_expiry}"
            )
            
            # Create new position
            new_position = VirtualPosition(
                trade_id=f"PT{self.trade_counter:04d}",
                symbol=new_symbol,
                tradingsymbol=new_symbol,
                instrument_token=0,
                strike=position.strike,
                option_type=position.option_type,
                expiry=new_expiry,
                quantity=position.quantity,  # Keep negative for short
                entry_price=new_price,
                entry_date=datetime.date.today().isoformat(),
                current_price=new_price,
                status="OPEN",
                notes=f"Rolled from {current_expiry}"
            )
            
            self.virtual_positions.append(new_position)
            self.learning_stats['rolling_executed'] += 1
            self.trade_counter += 1
        
        logger.info(f"Completed rolling {len(positions_to_roll)} positions")
    
    def generate_performance_chart(self):
        """Generate performance visualization"""
        try:
            # Get historical data
            query = "SELECT date, portfolio_value, total_pnl FROM daily_portfolio ORDER BY date"
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                logger.warning("No data available for chart")
                return
            
            # Create performance chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Portfolio value over time
            ax1.plot(pd.to_datetime(df['date']), df['portfolio_value'], 'b-', linewidth=2)
            ax1.axhline(y=self.total_virtual_capital, color='r', linestyle='--', alpha=0.7, label='Initial Capital')
            ax1.set_title('Portfolio Value Over Time')
            ax1.set_ylabel('Portfolio Value (₹)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # P&L over time
            ax2.plot(pd.to_datetime(df['date']), df['total_pnl'], 'g-', linewidth=2)
            ax2.axhline(y=0, color='k', linestyle='-', alpha=0.5)
            ax2.fill_between(pd.to_datetime(df['date']), df['total_pnl'], 0, 
                           where=(df['total_pnl'] >= 0), color='green', alpha=0.3)
            ax2.fill_between(pd.to_datetime(df['date']), df['total_pnl'], 0, 
                           where=(df['total_pnl'] < 0), color='red', alpha=0.3)
            ax2.set_title('Strategy P&L Over Time')
            ax2.set_ylabel('P&L (₹)')
            ax2.set_xlabel('Date')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'portfolio_performance_{datetime.date.today()}.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("Performance chart generated")
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
    
    def export_learning_report(self):
        """Export comprehensive learning report"""
        try:
            filename = f"paper_trading_report_{datetime.date.today()}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Daily portfolio data
                daily_df = pd.read_sql_query("SELECT * FROM daily_portfolio ORDER BY date", self.conn)
                daily_df.to_excel(writer, sheet_name='Daily_Portfolio', index=False)
                
                # Trade ledger
                trades_df = pd.read_sql_query("SELECT * FROM trade_ledger ORDER BY date, time", self.conn)
                trades_df.to_excel(writer, sheet_name='Trade_Ledger', index=False)
                
                # Current positions
                positions_df = pd.read_sql_query("SELECT * FROM virtual_positions", self.conn)
                positions_df.to_excel(writer, sheet_name='Positions', index=False)
                
                # Learning log
                learning_df = pd.read_sql_query("SELECT * FROM learning_log ORDER BY date", self.conn)
                learning_df.to_excel(writer, sheet_name='Learning_Log', index=False)
                
                # Summary statistics
                summary_data = {
                    'Metric': ['Total Capital', 'Strategy Allocation', 'Current Portfolio Value', 
                              'Total P&L', 'Return %', 'Days Active', 'Total Trades', 'Win Rate %'],
                    'Value': [
                        f"₹{self.total_virtual_capital:,.0f}",
                        f"₹{self.strategy_allocation:,.0f}",
                        f"₹{self.available_cash + self.invested_amount + self.total_pnl:,.0f}",
                        f"₹{self.total_pnl:+,.0f}",
                        f"{self.total_pnl/self.strategy_allocation*100:+.2f}%",
                        str(self.learning_stats['days_active']),
                        str(self.learning_stats['total_trades']),
                        f"{self.learning_stats['winning_trades']/max(1,self.learning_stats['total_trades'])*100:.1f}%"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Learning report exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
    
    def run_paper_trading_scheduler(self):
        """Run the paper trading scheduler"""
        logger.info("Starting Paper Trading Bot Scheduler...")
        logger.info("📚 LEARNING MODE: No real trades will be executed")
        logger.info("💰 Virtual Portfolio: ₹5,00,000")
        logger.info("🎯 Strategy Focus: Volatility Arbitrage")
        
        # Schedule daily review at market close
        schedule.every().day.at("15:45").do(self.daily_review)
        
        # Schedule quick updates during market hours
        schedule.every(30).minutes.do(self.quick_market_update)
        
        # Schedule weekly exports
        schedule.every().friday.at("16:00").do(self.export_learning_report)
        schedule.every().friday.at("16:05").do(self.generate_performance_chart)
        
        # Schedule monthly roll simulation (last Friday of month)
        schedule.every().day.at("16:30").do(self.check_monthly_roll)
        
        print("📅 Scheduled Activities:")
        print("   - Daily Review: 15:45 (Market Close)")
        print("   - Market Updates: Every 30 minutes")
        print("   - Weekly Reports: Friday 16:00")
        print("   - Monthly Rolls: Last Friday of month")
        print("\n🚀 Paper Trading Bot is now running...")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Paper Trading Bot stopped by user")
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
                self.update_position_prices(market_data)
                metrics = self.calculate_portfolio_metrics()
                
                # Log significant changes
                vix_change = abs(market_data.vix_level - self.vix_entry_level)
                nifty_change_pct = abs((market_data.nifty_price - self.nifty_entry_level) / self.nifty_entry_level * 100)
                
                if vix_change > 1 or nifty_change_pct > 2:
                    logger.info(f"Market Update - NIFTY: {market_data.nifty_price:.0f} ({market_data.nifty_change_pct:+.1f}%), "
                               f"VIX: {market_data.vix_level:.1f}, P&L: ₹{metrics['total_pnl']:+,.0f}")
        
        except Exception as e:
            logger.error(f"Error in quick update: {e}")
    
    def check_monthly_roll(self):
        """Check if monthly roll is needed"""
        today = datetime.date.today()
        
        # Check if it's last Friday of month and time for roll
        if today.weekday() == 4:  # Friday
            next_month = today.replace(day=28) + datetime.timedelta(days=4)
            last_day_of_month = next_month - datetime.timedelta(days=next_month.day)
            
            # If today is the last Friday
            if today >= last_day_of_month - datetime.timedelta(days=6):
                current_month = today.strftime("%Y-%m")
                
                # Check if any positions need rolling
                expiring_positions = [p for p in self.virtual_positions 
                                    if p.expiry.startswith(current_month) and p.quantity < 0]
                
                if expiring_positions:
                    next_month_str = (today + datetime.timedelta(days=30)).strftime("%Y-%m")
                    logger.info(f"Initiating monthly roll simulation: {current_month} → {next_month_str}")
                    self.simulate_monthly_roll(current_month + "-26", next_month_str + "-26")

def main():
    """Main function for paper trading bot"""
    print("📚 PAPER TRADING BOT - VOLATILITY ARBITRAGE")
    print("=" * 50)
    print("🎯 Learning Objective: Master options volatility trading")
    print("💰 Virtual Portfolio: ₹5,00,000")
    print("⚠️  NO REAL TRADES - SIMULATION ONLY")
    print("📊 Data Source: Live Kite API")
    print("=" * 50)
    
    # Get API credentials
    api_key = input("Enter your Kite API Key (for data only): ").strip()
    access_token = input("Enter your Access Token: ").strip()
    
    if not api_key or not access_token:
        print("❌ API credentials required for live data")
        print("📝 Note: No trades will be executed - data reading only")
        return
    
    try:
        # Initialize paper trading bot
        print("\n🚀 Initializing Paper Trading Environment...")
        bot = PaperTradingBot(api_key, access_token)
        
        # Set up initial strategy
        print("📋 Setting up volatility arbitrage strategy...")
        bot.initialize_paper_strategy()
        
        # Run initial review
        print("📊 Performing initial market review...")
        bot.daily_review()
        
        # Start automated monitoring
        print("\n🔄 Starting automated paper trading scheduler...")
        bot.run_paper_trading_scheduler()
        
    except KeyboardInterrupt:
        print("\n👋 Paper Trading Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"❌ Error: {e}")
    finally:
        print("📊 Final performance summary available in database")
        print("📈 Check generated reports and charts for learning insights")

if __name__ == "__main__":
    main()