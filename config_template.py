#!/usr/bin/env python3
"""
Configuration Template for Modular Paper Trading Engine
Copy this file to config.py and fill in your actual values
"""

# =============================================================================
# KITE API CONFIGURATION
# =============================================================================
KITE_API_KEY = "your_kite_api_key_here"
KITE_ACCESS_TOKEN = "your_kite_access_token_here"

# =============================================================================
# PORTFOLIO CONFIGURATION
# =============================================================================
TOTAL_CAPITAL = 500000  # Total virtual portfolio capital in ₹
BROKERAGE_PER_LOT = 20  # Simulated brokerage per lot in ₹

# =============================================================================
# STRATEGY ALLOCATIONS
# =============================================================================
STRATEGY_ALLOCATIONS = {
    "Volatility Arbitrage": 38550,    # ₹38,550 (7.7%)
    "Equity Momentum": 20000,         # ₹20,000 (4%)
    "Simple Demo": 15000,             # ₹15,000 (3%)
    # Add more strategies here with their allocations
}

# =============================================================================
# MARKET DATA CONFIGURATION
# =============================================================================
MARKET_UPDATE_INTERVAL = 30  # Minutes between market updates
DAILY_REVIEW_TIME = "15:45"  # Time for daily review (24-hour format)
WEEKLY_REPORT_TIME = "16:00"  # Time for weekly reports (Friday)

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_NAME = "modular_paper_trading.db"
LOG_FILE = "paper_trading.log"

# =============================================================================
# TRADING HOURS (IST)
# =============================================================================
MARKET_START_HOUR = 9
MARKET_START_MINUTE = 15
MARKET_END_HOUR = 15
MARKET_END_MINUTE = 30

# =============================================================================
# RISK MANAGEMENT
# =============================================================================
MAX_STRATEGY_ALLOCATION = 0.20  # Maximum 20% per strategy
MAX_DAILY_LOSS = 0.05           # Maximum 5% daily loss
POSITION_SIZE_LIMIT = 0.10      # Maximum 10% in single position

# =============================================================================
# NOTIFICATION SETTINGS
# =============================================================================
ENABLE_EMAIL_NOTIFICATIONS = False
ENABLE_SMS_NOTIFICATIONS = False
ENABLE_CONSOLE_NOTIFICATIONS = True

# =============================================================================
# REPORTING CONFIGURATION
# =============================================================================
GENERATE_PERFORMANCE_CHARTS = True
EXPORT_EXCEL_REPORTS = True
SAVE_DAILY_SNAPSHOTS = True

# =============================================================================
# DEBUG AND DEVELOPMENT
# =============================================================================
DEBUG_MODE = False
VERBOSE_LOGGING = True
SIMULATE_MARKET_DATA = False  # Use simulated data instead of live API

# =============================================================================
# STRATEGY-SPECIFIC CONFIGURATIONS
# =============================================================================

# Volatility Arbitrage Strategy
VOLATILITY_STRATEGY = {
    "nifty_entry_level": 24631,
    "vix_entry_level": 12.0,
    "rebalance_threshold": 0.05,  # 5% change triggers rebalancing
    "protective_wings": True,
    "max_vega_exposure": 1000,
}

# Equity Momentum Strategy
EQUITY_MOMENTUM_STRATEGY = {
    "momentum_threshold": 0.02,  # 2% momentum threshold
    "rebalance_frequency": "weekly",
    "max_equity_allocation": 0.15,  # 15% max in equity
}

# =============================================================================
# EXAMPLE USAGE
# =============================================================================
"""
# In your main script:
from config import *

# Use configuration values
api_key = KITE_API_KEY
total_capital = TOTAL_CAPITAL

# Access strategy-specific configs
vix_threshold = VOLATILITY_STRATEGY["vix_entry_level"]
momentum_threshold = EQUITY_MOMENTUM_STRATEGY["momentum_threshold"]
"""

# =============================================================================
# SECURITY NOTES
# =============================================================================
"""
IMPORTANT: 
1. Never commit config.py with real API keys
2. Keep config_template.py in version control
3. Add config.py to .gitignore
4. Use environment variables for production
5. Rotate API keys regularly
"""
