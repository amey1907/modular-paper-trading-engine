#!/usr/bin/env python3
"""
Real-Time Option Chain Data Fetcher using Kite Connect WebSocket
"""

import logging
import sqlite3
import json
from datetime import datetime
import pandas as pd
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('option_chain_websocket.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptionChainWebSocket:
    """
    Real-time Option Chain Data Collector using Kite WebSocket
    """
    
    def __init__(self, api_key, access_token):
        """
        Initialize WebSocket connection and database
        
        :param api_key: Kite API Key
        :param access_token: Kite Access Token
        """
        # Kite Connect initialization
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        
        # WebSocket ticker
        self.kws = KiteTicker(api_key, access_token)
        
        # Database connection
        self.conn = sqlite3.connect('option_chain_realtime.db', check_same_thread=False)
        self.create_tables()
        
        # Instrument tokens to track
        self.instrument_tokens = []
        
        # Bind WebSocket events
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error
        self.kws.on_reconnect = self.on_reconnect
        
        # Tracking variables
        self.tick_count = 0
        self.max_ticks = 1000  # Stop after 1000 ticks
    
    def create_tables(self):
        """
        Create SQLite tables for storing option chain data
        """
        try:
            # Option chain real-time quotes table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS option_quotes (
                    timestamp TEXT,
                    instrument_token INTEGER,
                    tradingsymbol TEXT,
                    exchange TEXT,
                    last_price REAL,
                    last_quantity INTEGER,
                    average_price REAL,
                    volume REAL,
                    buy_quantity INTEGER,
                    sell_quantity INTEGER,
                    open_interest REAL,
                    strike_price REAL,
                    option_type TEXT,
                    expiry TEXT
                )
            ''')
            
            # Option Greeks table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS option_greeks (
                    timestamp TEXT,
                    instrument_token INTEGER,
                    tradingsymbol TEXT,
                    delta REAL,
                    gamma REAL,
                    theta REAL,
                    vega REAL,
                    implied_volatility REAL
                )
            ''')
            
            self.conn.commit()
            logger.info("Option chain database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    def fetch_nifty_options(self, expiry_date):
        """
        Fetch NIFTY option instruments for a specific expiry
        
        :param expiry_date: Expiry date in 'YYYY-MM-DD' format
        :return: List of instrument tokens
        """
        try:
            # Fetch NIFTY 50 instruments
            instruments = self.kite.instruments('NFO')
            
            # Filter for NIFTY options with specific expiry
            nifty_options = [
                instrument for instrument in instruments 
                if (instrument['name'] == 'NIFTY' and 
                    instrument['expiry'] == expiry_date and 
                    instrument['instrument_type'] in ['CE', 'PE'])
            ]
            
            # Extract instrument tokens
            self.instrument_tokens = [
                instrument['instrument_token'] for instrument in nifty_options
            ]
            
            logger.info(f"Found {len(self.instrument_tokens)} NIFTY option instruments")
            return self.instrument_tokens
        
        except Exception as e:
            logger.error(f"Error fetching NIFTY option instruments: {e}")
            return []
    
    def on_ticks(self, ticks):
        """
        Callback for tick data
        
        :param ticks: List of tick data
        """
        try:
            for tick in ticks:
                # Store tick data in SQLite
                self.store_tick_data(tick)
                
                # Increment tick count
                self.tick_count += 1
                
                # Stop after max ticks
                if self.tick_count >= self.max_ticks:
                    self.kws.close()
                    break
        
        except Exception as e:
            logger.error(f"Error processing ticks: {e}")
    
    def store_tick_data(self, tick):
        """
        Store tick data in SQLite database
        
        :param tick: Tick data dictionary
        """
        try:
            # Prepare data for insertion
            timestamp = datetime.now().isoformat()
            
            # Insert quote data
            self.conn.execute('''
                INSERT INTO option_quotes 
                (timestamp, instrument_token, tradingsymbol, exchange, 
                last_price, last_quantity, average_price, volume, 
                buy_quantity, sell_quantity, open_interest)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                tick.get('instrument_token'),
                tick.get('tradingsymbol'),
                tick.get('exchange'),
                tick.get('last_price'),
                tick.get('last_quantity'),
                tick.get('average_price'),
                tick.get('volume'),
                tick.get('buy_quantity'),
                tick.get('sell_quantity'),
                tick.get('open_interest')
            ))
            
            # Commit every 10 ticks to improve performance
            if self.tick_count % 10 == 0:
                self.conn.commit()
        
        except Exception as e:
            logger.error(f"Error storing tick data: {e}")
    
    def on_connect(self, ws):
        """WebSocket connection successful"""
        logger.info("WebSocket connection established")
        
        # Subscribe to instruments
        if self.instrument_tokens:
            ws.subscribe(self.instrument_tokens)
            ws.set_mode(ws.MODE_FULL, self.instrument_tokens)
    
    def on_close(self, ws, code, reason):
        """WebSocket connection closed"""
        logger.info(f"WebSocket connection closed: {reason}")
        
        # Close database connection
        self.conn.commit()
        self.conn.close()
    
    def on_error(self, ws, code, reason):
        """WebSocket error handler"""
        logger.error(f"WebSocket error: {reason}")
    
    def on_reconnect(self, ws, attempts_count):
        """WebSocket reconnection handler"""
        logger.info(f"WebSocket reconnection attempt: {attempts_count}")
    
    def start_websocket(self, expiry_date):
        """
        Start WebSocket connection for option chain
        
        :param expiry_date: Option expiry date in 'YYYY-MM-DD' format
        """
        try:
            # Fetch option instruments
            self.fetch_nifty_options(expiry_date)
            
            # Start WebSocket connection
            self.kws.connect()
        
        except Exception as e:
            logger.error(f"Error starting WebSocket: {e}")
    
    def generate_option_chain_report(self):
        """
        Generate a comprehensive option chain report from stored data
        
        :return: Pandas DataFrame with option chain data
        """
        try:
            # Read stored option quotes
            query = "SELECT * FROM option_quotes ORDER BY timestamp"
            df = pd.read_sql_query(query, self.conn)
            
            # Basic analysis
            summary = df.groupby('tradingsymbol').agg({
                'last_price': ['mean', 'max', 'min'],
                'volume': 'sum',
                'open_interest': 'mean'
            })
            
            # Save summary to CSV
            summary.to_csv('option_chain_summary.csv')
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating option chain report: {e}")
            return pd.DataFrame()

def main():
    """
    Main function to demonstrate option chain WebSocket
    """
    print("🚀 Real-Time Option Chain Data Collector")
    print("=" * 50)
    
    # Use configuration from config.py
    api_key = config.KITE_API_KEY
    access_token = config.KITE_ACCESS_TOKEN
    
    # Set expiry date (modify as needed)
    expiry_date = '2025-08-29'  # Example expiry date
    
    try:
        # Initialize Option Chain WebSocket
        option_chain = OptionChainWebSocket(api_key, access_token)
        
        # Start WebSocket connection
        print(f"📊 Collecting Option Chain Data for Expiry: {expiry_date}")
        option_chain.start_websocket(expiry_date)
        
        # Wait for data collection
        print("🕒 Collecting data... (Press Ctrl+C to stop)")
        
        # Generate report after collection
        print("\n📈 Generating Option Chain Report...")
        report = option_chain.generate_option_chain_report()
        print(report)
        
    except KeyboardInterrupt:
        print("\n👋 Option Chain Data Collection Stopped")
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
