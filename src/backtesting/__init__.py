"""
Backtesting engine and strategy framework.
"""

from .engine import BacktestEngine
from .strategy_base import StrategyBase, Signal, SignalType, Position

__all__ = ['BacktestEngine', 'StrategyBase', 'Signal', 'SignalType', 'Position']