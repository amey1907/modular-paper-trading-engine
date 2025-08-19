#!/usr/bin/env python3
"""
Comprehensive Historical Data Retrieval Script
"""

from kiteconnect import KiteConnect
import config
from datetime import datetime, timedelta
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_historical_data(instrument_token, 
                        from_date=None, 
                        to_date=None, 
                        interval='day'):
    """
    Retrieve historical data for a given instrument
    
    :param instrument_token: Kite instrument token
    :param from_date: Start date (default: 30 days ago)
    :param to_date: End date (default: today)
    :param interval: Data interval (day, minute, 5minute, etc.)
    :return: DataFrame with historical data
    """
    try:
        # Initialize Kite Connect
        kite = KiteConnect(api_key=config.KITE_API_KEY)
        kite.set_access_token(config.KITE_ACCESS_TOKEN)
        
        # Set default dates if not provided
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if to_date is None:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch historical data
        historical_data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
        
        # Convert to DataFrame with error handling
        if historical_data:
            # Determine the correct column names based on the first data point
            first_data_point = historical_data[0]
            
            # Dynamically determine column names
            if len(first_data_point) == 7:
                columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'oi']
            elif len(first_data_point) == 6:
                columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            else:
                logger.error(f"Unexpected data format: {len(first_data_point)} columns")
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(historical_data, columns=columns)
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
        else:
            logger.warning("No historical data retrieved")
            return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Error retrieving historical data: {e}")
        return pd.DataFrame()

def main():
    """
    Main function to demonstrate historical data retrieval
    """
    # Define instruments to retrieve (tokens from Zerodha)
    instruments = {
        'NIFTY 50': 256265,     # NIFTY 50 Index
        'INDIA VIX': 260105,    # India VIX
        'NIFTY BANK': 260009,   # NIFTY Bank Index
    }
    
    print("🔍 Retrieving Historical Market Data")
    print("=" * 50)
    
    # Retrieve and display data for each instrument
    for name, token in instruments.items():
        print(f"\n📊 Retrieving data for {name} (Token: {token}):")
        
        # Retrieve daily data
        daily_data = get_historical_data(token, interval='day')
        
        if not daily_data.empty:
            print(f"  ✅ Retrieved {len(daily_data)} daily data points")
            print("\n  Last 5 Days Summary:")
            print(daily_data.tail())
            
            # Optional: Save to CSV
            csv_filename = f"{name.replace(' ', '_').lower()}_historical_data.csv"
            daily_data.to_csv(csv_filename)
            print(f"  💾 Data saved to {csv_filename}")
        else:
            print(f"  ❌ No data retrieved for {name}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
