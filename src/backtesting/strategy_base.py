"""
Base strategy class for algorithmic trading strategies.
"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    """Trading signal types."""
    BUY = 1
    SELL = -1
    HOLD = 0

@dataclass
class Signal:
    """Trading signal data structure."""
    timestamp: pd.Timestamp
    symbol: str
    signal_type: SignalType
    price: float
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Position:
    """Position data structure."""
    symbol: str
    quantity: int
    entry_price: float
    entry_date: pd.Timestamp
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    
    def update_price(self, new_price: float):
        """Update current price and unrealized P&L."""
        self.current_price = new_price
        self.unrealized_pnl = (new_price - self.entry_price) * self.quantity

class StrategyBase(ABC):
    """
    Abstract base class for trading strategies.
    
    All trading strategies should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.parameters = kwargs
        self.signals = []
        self.positions = {}
        self.cash = 0.0
        self.portfolio_value = 0.0
        self.data = None
        self.current_date = None
        
        # Performance tracking
        self.trades = []
        self.portfolio_history = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on market data.
        
        Args:
            data: Market data DataFrame
            
        Returns:
            List of Signal objects
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Signal, available_cash: float) -> int:
        """
        Calculate position size for a given signal.
        
        Args:
            signal: Trading signal
            available_cash: Available cash for trading
            
        Returns:
            Number of shares to trade
        """
        pass
    
    def initialize(self, data: pd.DataFrame, initial_cash: float = 100000):
        """Initialize strategy with data and starting capital."""
        self.data = data
        self.cash = initial_cash
        self.portfolio_value = initial_cash
        self.positions = {}
        self.signals = []
        self.trades = []
        self.portfolio_history = []
        
    def update_positions(self, current_prices: Dict[str, float]):
        """Update all positions with current market prices."""
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position.update_price(current_prices[symbol])
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value."""
        self.update_positions(current_prices)
        positions_value = sum(pos.quantity * pos.current_price for pos in self.positions.values())
        return self.cash + positions_value
    
    def execute_signal(self, signal: Signal, commission: float = 0.0):
        """
        Execute a trading signal.
        
        Args:
            signal: Signal to execute
            commission: Commission cost per trade
        """
        if signal.signal_type == SignalType.BUY:
            self._execute_buy(signal, commission)
        elif signal.signal_type == SignalType.SELL:
            self._execute_sell(signal, commission)
    
    def _execute_buy(self, signal: Signal, commission: float):
        """Execute buy order."""
        position_size = self.calculate_position_size(signal, self.cash)
        
        if position_size > 0:
            cost = position_size * signal.price + commission
            
            if cost <= self.cash:
                if signal.symbol in self.positions:
                    # Add to existing position
                    existing_pos = self.positions[signal.symbol]
                    total_quantity = existing_pos.quantity + position_size
                    avg_price = ((existing_pos.quantity * existing_pos.entry_price) + 
                               (position_size * signal.price)) / total_quantity
                    existing_pos.quantity = total_quantity
                    existing_pos.entry_price = avg_price
                else:
                    # Create new position
                    self.positions[signal.symbol] = Position(
                        symbol=signal.symbol,
                        quantity=position_size,
                        entry_price=signal.price,
                        entry_date=signal.timestamp,
                        current_price=signal.price
                    )
                
                self.cash -= cost
                
                # Record trade
                self.trades.append({
                    'timestamp': signal.timestamp,
                    'symbol': signal.symbol,
                    'action': 'BUY',
                    'quantity': position_size,
                    'price': signal.price,
                    'commission': commission,
                    'total_cost': cost
                })
    
    def _execute_sell(self, signal: Signal, commission: float):
        """Execute sell order."""
        if signal.symbol in self.positions:
            position = self.positions[signal.symbol]
            sell_quantity = min(abs(self.calculate_position_size(signal, self.cash)), 
                              position.quantity)
            
            if sell_quantity > 0:
                proceeds = sell_quantity * signal.price - commission
                self.cash += proceeds
                
                # Update position
                position.quantity -= sell_quantity
                
                # Record trade
                self.trades.append({
                    'timestamp': signal.timestamp,
                    'symbol': signal.symbol,
                    'action': 'SELL',
                    'quantity': sell_quantity,
                    'price': signal.price,
                    'commission': commission,
                    'proceeds': proceeds
                })
                
                # Remove position if fully sold
                if position.quantity <= 0:
                    del self.positions[signal.symbol]
    
    def get_current_positions(self) -> Dict[str, Position]:
        """Get current positions."""
        return self.positions.copy()
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        if self.trades:
            return pd.DataFrame(self.trades)
        return pd.DataFrame()
    
    def get_portfolio_history_df(self) -> pd.DataFrame:
        """Get portfolio history as DataFrame."""
        if self.portfolio_history:
            return pd.DataFrame(self.portfolio_history)
        return pd.DataFrame()
    
    def record_portfolio_state(self, timestamp: pd.Timestamp, current_prices: Dict[str, float]):
        """Record current portfolio state for performance tracking."""
        portfolio_value = self.get_portfolio_value(current_prices)
        
        self.portfolio_history.append({
            'timestamp': timestamp,
            'cash': self.cash,
            'positions_value': portfolio_value - self.cash,
            'total_value': portfolio_value,
            'num_positions': len(self.positions)
        })
        
        self.portfolio_value = portfolio_value
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            'name': self.name,
            'parameters': self.parameters,
            'total_trades': len(self.trades),
            'current_positions': len(self.positions),
            'current_cash': self.cash,
            'current_portfolio_value': self.portfolio_value
        }
    
    def reset(self):
        """Reset strategy state."""
        self.signals = []
        self.positions = {}
        self.trades = []
        self.portfolio_history = []
        self.cash = 0.0
        self.portfolio_value = 0.0
        self.current_date = None