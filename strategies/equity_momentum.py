from .base_strategy import BaseStrategy, StrategyPosition
from typing import Dict, List
import datetime

class EquityMomentumStrategy(BaseStrategy):
    """Simple Equity Momentum Strategy Example"""
    
    def __init__(self, capital: float, allocation: float):
        super().__init__("Equity Momentum", capital, allocation)
        self.momentum_threshold = 0.02  # 2% momentum threshold
        
    def initialize_positions(self, kite_data) -> List[StrategyPosition]:
        """Initialize equity momentum positions"""
        positions = []
        
        # Example equity positions
        equity_positions = [
            {
                'symbol': 'RELIANCE',
                'tradingsymbol': 'RELIANCE-EQ',
                'strike': 0,
                'option_type': 'EQ',
                'expiry': 'PERPETUAL',
                'quantity': 100,
                'entry_price': 2500,
                'position_type': 'LONG'
            },
            {
                'symbol': 'TCS',
                'tradingsymbol': 'TCS-EQ',
                'strike': 0,
                'option_type': 'EQ',
                'expiry': 'PERPETUAL',
                'quantity': 50,
                'entry_price': 3800,
                'position_type': 'LONG'
            }
        ]
        
        # Create positions
        for pos_data in equity_positions:
            position = StrategyPosition(
                symbol=pos_data['symbol'],
                tradingsymbol=pos_data['tradingsymbol'],
                instrument_token=0,
                strike=pos_data['strike'],
                option_type=pos_data['option_type'],
                expiry=pos_data['expiry'],
                quantity=pos_data['quantity'],
                entry_price=pos_data['entry_price'],
                entry_date=datetime.date.today().isoformat(),
                notes=f"Initial {pos_data['position_type']} position"
            )
            positions.append(position)
            
            # Update cash balance
            investment = abs(pos_data['quantity']) * pos_data['entry_price']
            self.available_cash -= investment
        
        self.positions = positions
        return positions
    
    def should_rebalance(self, market_data: Dict) -> bool:
        """Check if strategy needs rebalancing based on momentum"""
        # Simple momentum check
        return market_data.get('momentum_score', 0) > self.momentum_threshold
    
    def rebalance_strategy(self, market_data: Dict, kite_data) -> List[Dict]:
        """Execute rebalancing trades"""
        trades = []
        
        # Example momentum-based rebalancing
        if market_data.get('momentum_score', 0) > self.momentum_threshold:
            trades.append({
                'action': 'ADD_MOMENTUM',
                'reason': 'Positive momentum detected',
                'positions': []
            })
        
        return trades
    
    def get_strategy_metrics(self) -> Dict:
        """Get strategy-specific metrics"""
        total_value = sum(pos.quantity * pos.current_price for pos in self.positions if pos.status == "OPEN")
        
        return {
            'strategy_type': 'Equity Momentum',
            'total_equity_value': total_value,
            'momentum_threshold': self.momentum_threshold,
            'position_count': len([p for p in self.positions if p.status == "OPEN"])
        }
