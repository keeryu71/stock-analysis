"""
Configuration management for algorithmic trading system.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class TradingConfig:
    """Configuration class for trading parameters."""
    
    # Portfolio Settings
    initial_capital: float = 100000.0
    commission: float = 0.001  # 0.1% commission
    slippage: float = 0.0005   # 0.05% slippage
    
    # Risk Management
    max_position_size: float = 0.1  # 10% of portfolio per position
    stop_loss_pct: float = 0.02     # 2% stop loss
    take_profit_pct: float = 0.06   # 6% take profit
    max_drawdown: float = 0.15      # 15% maximum drawdown
    
    # Data Settings
    default_timeframe: str = '1d'
    lookback_period: int = 252  # Trading days for analysis
    
    # API Keys (loaded from environment variables)
    alpha_vantage_key: str = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    polygon_key: str = os.getenv('POLYGON_API_KEY', '')
    
    # Backtesting Settings
    benchmark_symbol: str = 'SPY'
    risk_free_rate: float = 0.02  # 2% annual risk-free rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'initial_capital': self.initial_capital,
            'commission': self.commission,
            'slippage': self.slippage,
            'max_position_size': self.max_position_size,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'max_drawdown': self.max_drawdown,
            'default_timeframe': self.default_timeframe,
            'lookback_period': self.lookback_period,
            'benchmark_symbol': self.benchmark_symbol,
            'risk_free_rate': self.risk_free_rate
        }

# Global configuration instance
config = TradingConfig()

# Strategy-specific configurations
STRATEGY_CONFIGS = {
    'moving_average': {
        'short_window': 20,
        'long_window': 50,
        'signal_threshold': 0.01
    },
    'momentum': {
        'lookback_period': 20,
        'momentum_threshold': 0.02,
        'rebalance_frequency': 5
    },
    'mean_reversion': {
        'lookback_period': 20,
        'z_score_threshold': 2.0,
        'holding_period': 5
    },
    'rsi': {
        'period': 14,
        'oversold_threshold': 30,
        'overbought_threshold': 70
    },
    'bollinger_bands': {
        'period': 20,
        'std_dev': 2.0,
        'signal_threshold': 0.01
    }
}

def get_strategy_config(strategy_name: str) -> Dict[str, Any]:
    """Get configuration for a specific strategy."""
    return STRATEGY_CONFIGS.get(strategy_name, {})

def update_config(**kwargs) -> None:
    """Update global configuration parameters."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")