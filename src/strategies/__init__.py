"""
Trading strategy implementations.
"""

from .moving_average import (
    MovingAverageCrossover,
    ExponentialMovingAverageCrossover,
    TripleMovingAverageCrossover,
    create_ma_strategy
)

from .fibonacci_macd_strategy import (
    FibonacciMACDStrategy,
    create_fibonacci_macd_strategy
)

__all__ = [
    'MovingAverageCrossover',
    'ExponentialMovingAverageCrossover',
    'TripleMovingAverageCrossover',
    'create_ma_strategy',
    'FibonacciMACDStrategy',
    'create_fibonacci_macd_strategy'
]