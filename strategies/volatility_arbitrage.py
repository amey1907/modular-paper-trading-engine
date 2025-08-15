from .base_strategy import BaseStrategy, StrategyPosition
from typing import Dict, List
import datetime

class VolatilityArbitrageStrategy(BaseStrategy):
    """Volatility Arbitrage Strategy Implementation"""
    
    def __init__(self, capital: float, allocation: float):
        super().__init__("Volatility Arbitrage", capital, allocation)
        self.nifty_entry_level = 24631
        self.vix_entry_level = 12.0
        
    def initialize_positions(self, kite_data) -> List[StrategyPosition]:
        """Initialize volatility arbitrage positions"""
        positions = []
        
        # Strategy positions
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
        
        # Create positions
        for pos_data in strategy_positions:
            position = StrategyPosition(
                symbol=pos_data['symbol'],
                tradingsymbol=pos_data['symbol'],
                instrument_token=0,  # Will be updated with live data
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
            if pos_data['quantity'] > 0:  # Long positions
                self.available_cash -= investment
            else:  # Short positions
                self.available_cash += investment
        
        self.positions = positions
        return positions
    
    def should_rebalance(self, market_data: Dict) -> bool:
        """Check if strategy needs rebalancing"""
        vix_change = abs(market_data.get('vix', 0) - self.vix_entry_level)
        nifty_change_pct = abs(market_data.get('nifty_change_pct', 0))
        
        # Rebalance if VIX moves significantly or NIFTY moves >5%
        return vix_change > 3 or nifty_change_pct > 5
    
    def rebalance_strategy(self, market_data: Dict, kite_data) -> List[Dict]:
        """Execute rebalancing trades"""
        trades = []
        
        # Example rebalancing logic
        if market_data.get('vix', 0) > self.vix_entry_level + 5:
            # VIX spike - consider adding protective positions
            trades.append({
                'action': 'ADD_PROTECTION',
                'reason': 'VIX spike detected',
                'positions': []
            })
        
        return trades
    
    def get_strategy_metrics(self) -> Dict:
        """Get strategy-specific metrics"""
        total_delta = sum(pos.delta * pos.quantity for pos in self.positions if hasattr(pos, 'delta'))
        total_gamma = sum(pos.gamma * pos.quantity for pos in self.positions if hasattr(pos, 'gamma'))
        total_theta = sum(pos.theta * pos.quantity for pos in self.positions if hasattr(pos, 'theta'))
        total_vega = sum(pos.vega * pos.quantity for pos in self.positions if hasattr(pos, 'vega'))
        
        return {
            'strategy_type': 'Volatility Arbitrage',
            'portfolio_delta': total_delta,
            'portfolio_gamma': total_gamma,
            'portfolio_theta': total_theta,
            'portfolio_vega': total_vega,
            'vix_entry_level': self.vix_entry_level,
            'nifty_entry_level': self.nifty_entry_level
        }
