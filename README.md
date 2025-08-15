# Modular Paper Trading Engine

A flexible paper trading system that supports multiple trading strategies with live Zerodha Kite data.

## 🎯 Features

- **Modular Strategy System**: Easy to add new trading strategies
- **Live Market Data**: Real-time NIFTY and VIX data from Kite API
- **Paper Trading**: No real money involved - perfect for learning
- **Multiple Strategies**: Run multiple strategies simultaneously
- **Automated Monitoring**: Daily reviews and market updates
- **Database Storage**: SQLite database for tracking performance
- **Comprehensive Reporting**: Daily reports and performance metrics

## 🏗️ Architecture

```
paper_trading_engine.py          # Main engine
├── strategies/                  # Strategy implementations
│   ├── __init__.py
│   ├── base_strategy.py        # Abstract base class
│   ├── volatility_arbitrage.py # Volatility arbitrage strategy
│   ├── equity_momentum.py      # Equity momentum strategy
│   └── simple_demo.py          # Simple demo strategy
└── modular_paper_trading.db    # SQLite database
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install pandas numpy requests schedule matplotlib seaborn openpyxl
```

### 2. Get Kite API Credentials
- Sign up for Zerodha developer account
- Get API Key and Access Token
- **Note**: Only read-only access needed for data

### 3. Run the Engine
```bash
python3 paper_trading_engine.py
```

## 📊 Available Strategies

### 1. Volatility Arbitrage Strategy
- **Allocation**: ₹38,550
- **Positions**: Calendar straddle with protective wings
- **Objective**: Profit from volatility term structure

### 2. Equity Momentum Strategy  
- **Allocation**: ₹20,000
- **Positions**: Long equity positions
- **Objective**: Capture momentum in large-cap stocks

### 3. Simple Demo Strategy
- **Allocation**: Configurable
- **Positions**: Basic equity positions
- **Objective**: Learning and testing

## 🛠️ Adding New Strategies

### Step 1: Create Strategy Class
```python
from strategies.base_strategy import BaseStrategy, StrategyPosition

class MyNewStrategy(BaseStrategy):
    def __init__(self, capital: float, allocation: float):
        super().__init__("My New Strategy", capital, allocation)
    
    def initialize_positions(self, kite_data) -> List[StrategyPosition]:
        # Define your positions here
        pass
    
    def should_rebalance(self, market_data: Dict) -> bool:
        # Define rebalancing logic
        pass
    
    def rebalance_strategy(self, market_data: Dict, kite_data) -> List[Dict]:
        # Define rebalancing trades
        pass
    
    def get_strategy_metrics(self) -> Dict:
        # Return strategy-specific metrics
        pass
```

### Step 2: Add to Engine
```python
# In main() function
from strategies.my_new_strategy import MyNewStrategy

my_strategy = MyNewStrategy(500000, 25000)
engine.add_strategy(my_strategy, 25000)
```

## 📈 Strategy Interface

All strategies must implement these methods:

- **`initialize_positions(kite_data)`**: Set up initial positions
- **`should_rebalance(market_data)`**: Check if rebalancing needed
- **`rebalance_strategy(market_data, kite_data)`**: Execute rebalancing
- **`get_strategy_metrics()`**: Return strategy metrics

## 🔧 Configuration

### Portfolio Settings
- **Total Capital**: ₹5,00,000
- **Strategy Allocations**: Configurable per strategy
- **Brokerage**: ₹20 per lot (simulated)

### Market Data
- **NIFTY 50**: Live prices from Kite
- **India VIX**: Volatility index
- **Update Frequency**: Every 30 minutes during market hours

## 📅 Scheduled Activities

- **Daily Review**: 15:45 (Market Close)
- **Market Updates**: Every 30 minutes during trading hours
- **Database Updates**: Real-time position tracking

## 🗄️ Database Schema

### Tables
- **`strategies`**: Strategy metadata and allocations
- **`strategy_positions`**: Current positions for each strategy
- **`trade_ledger`**: All executed trades
- **`daily_portfolio`**: Daily portfolio snapshots

## 📊 Reports and Analytics

- **Daily Reports**: Console output with portfolio summary
- **Performance Charts**: Matplotlib-generated charts
- **Excel Exports**: Comprehensive data export
- **Learning Log**: Track trading lessons and insights

## ⚠️ Important Notes

- **NO REAL TRADES**: This is purely for learning and simulation
- **Read-Only API**: Kite API used only for market data
- **Virtual Portfolio**: All positions and P&L are simulated
- **Learning Focus**: Designed for strategy testing and education

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all strategy files are in `strategies/` folder
2. **API Errors**: Check Kite API credentials and internet connection
3. **Database Errors**: Check file permissions for SQLite database

### Logs
- Check `paper_trading.log` for detailed error information
- Console output shows real-time status

## 🔮 Future Enhancements

- **Risk Management**: Position sizing and stop-loss logic
- **Backtesting**: Historical strategy performance analysis
- **Machine Learning**: AI-powered strategy optimization
- **Web Interface**: Dashboard for strategy monitoring
- **Multi-Exchange**: Support for other exchanges

## 📚 Learning Resources

- **Options Trading**: Understanding volatility arbitrage
- **Portfolio Management**: Multi-strategy allocation
- **Risk Management**: Position sizing and hedging
- **Market Analysis**: Technical and fundamental analysis

## 🤝 Contributing

Feel free to:
- Add new strategies
- Improve existing strategies
- Enhance the engine
- Report bugs and issues

## 📄 License

This project is for educational purposes. Use at your own risk.

---

**Happy Paper Trading! 📈**
