from .base_strategy import BaseStrategy, StrategyPosition
from typing import Dict, List
import datetime

class SimpleDemoStrategy(BaseStrategy):
    """Simple Demo Strategy - Easy to understand and modify"""
    
    def __init__(self, capital: float, allocation: float):
        super().__init__("Simple Demo", capital, allocation)
        self.target_return = 0.15  # 15% target return
        
    def initialize_positions(self, kite_data) -> List[StrategyPosition]:
        """Initialize simple demo positions"""
        positions = []
        
        # Simple long-only equity positions
        demo_positions = [
            {
                'symbol': 'INFY',
                'tradingsymbol': 'INFY-EQ',
                'strike': 0,
                'option_type': 'EQ',
                'expiry': 'PERPETUAL',
                'quantity': 200,
                'entry_price': 1500,
                'position_type': 'LONG'
            },
            {
                'symbol': 'HDFC',
                'tradingsymbol': 'HDFC-EQ',
                'strike': 0,
                'option_type': 'EQ',
                'expiry': 'PERPETUAL',
                'quantity': 100,
                'entry_price': 1800,
                'position_type': 'LONG'
            }
        ]
        
        # Create positions
        for pos_data in demo_positions:
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
        """Check if strategy needs rebalancing"""
        # Simple rebalancing logic
        return market_data.get('market_volatility', 0) > 0.3
    
    def rebalance_strategy(self, market_data: Dict, kite_data) -> List[Dict]:
        """Execute rebalancing trades"""
        trades = []
        
        # Simple rebalancing example
        if market_data.get('market_volatility', 0) > 0.3:
            trades.append({
                'action': 'REDUCE_RISK',
                'reason': 'High volatility detected',
                'positions': []
            })
        
        return trades
    
    def get_strategy_metrics(self) -> Dict:
        """Get strategy-specific metrics"""
        total_value = sum(pos.quantity * pos.current_price for pos in self.positions if pos.status == "OPEN")
        
        return {
            'strategy_type': 'Simple Demo',
            'total_equity_value': total_value,
            'target_return': self.target_return,
            'position_count': len([p for p in self.positions if p.status == "OPEN"])
        }
