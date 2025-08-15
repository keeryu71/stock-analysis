"""
Algorithmic Trading Framework

A comprehensive Python framework for developing, backtesting, and analyzing
algorithmic trading strategies.
"""

__version__ = "1.0.0"
__author__ = "Algorithmic Trading Framework"
__email__ = "contact@example.com"

# Import main components for easy access
from .config import config, TradingConfig
from .data.data_loader import DataLoader, load_single_stock, load_multiple_stocks
from .backtesting.engine import BacktestEngine
from .backtesting.strategy_base import StrategyBase, Signal, SignalType
from .utils.metrics import PerformanceAnalyzer, quick_performance_summary

__all__ = [
    'config',
    'TradingConfig',
    'DataLoader',
    'load_single_stock',
    'load_multiple_stocks',
    'BacktestEngine',
    'StrategyBase',
    'Signal',
    'SignalType',
    'PerformanceAnalyzer',
    'quick_performance_summary'
]