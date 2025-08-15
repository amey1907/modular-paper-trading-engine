from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, date

@dataclass
class StrategyPosition:
    """Base position structure for any strategy"""
    symbol: str
    tradingsymbol: str
    instrument_token: int
    strike: float
    option_type: str  # 'CE', 'PE', 'FUT', 'EQ', etc.
    expiry: str
    quantity: int  # Positive for long, negative for short
    entry_price: float
    entry_date: str
    current_price: float = 0.0
    exit_price: float = 0.0
    exit_date: str = ""
    status: str = "OPEN"
    notes: str = ""

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, name: str, capital: float, allocation: float):
        self.name = name
        self.total_capital = capital
        self.strategy_allocation = allocation
        self.available_cash = allocation
        self.positions: List[StrategyPosition] = []
        self.entry_date = date.today()
        
    @abstractmethod
    def initialize_positions(self, kite_data) -> List[StrategyPosition]:
        """Initialize strategy positions - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def should_rebalance(self, market_data: Dict) -> bool:
        """Check if strategy needs rebalancing - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def rebalance_strategy(self, market_data: Dict, kite_data) -> List[Dict]:
        """Execute rebalancing trades - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_strategy_metrics(self) -> Dict:
        """Get strategy-specific metrics - must be implemented by subclasses"""
        pass
    
    def get_positions(self) -> List[StrategyPosition]:
        """Get current positions"""
        return self.positions
    
    def get_cash_balance(self) -> float:
        """Get available cash for this strategy"""
        return self.available_cash
    
    def get_invested_amount(self) -> float:
        """Calculate total invested amount"""
        total = 0
        for pos in self.positions:
            if pos.status == "OPEN":
                total += abs(pos.quantity) * pos.entry_price
        return total
