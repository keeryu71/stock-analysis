"""
Moving Average Crossover Trading Strategies.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from src.backtesting.strategy_base import StrategyBase, Signal, SignalType
from src.config import get_strategy_config

class MovingAverageCrossover(StrategyBase):
    """
    Simple Moving Average Crossover Strategy.
    
    Generates buy signals when short MA crosses above long MA,
    and sell signals when short MA crosses below long MA.
    """
    
    def __init__(
        self, 
        short_window: int = 20, 
        long_window: int = 50,
        signal_threshold: float = 0.01,
        position_size_pct: float = 0.1,
        **kwargs
    ):
        super().__init__("MA_Crossover", **kwargs)
        
        self.short_window = short_window
        self.long_window = long_window
        self.signal_threshold = signal_threshold
        self.position_size_pct = position_size_pct
        
        # Store parameters
        self.parameters.update({
            'short_window': short_window,
            'long_window': long_window,
            'signal_threshold': signal_threshold,
            'position_size_pct': position_size_pct
        })
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate trading signals based on MA crossover."""
        signals = []
        
        if len(data) < self.long_window:
            return signals
        
        # Handle multi-symbol data
        if 'symbol' in data.columns:
            symbols = data['symbol'].unique()
            for symbol in symbols:
                symbol_data = data[data['symbol'] == symbol].copy()
                symbol_signals = self._generate_signals_single_asset(symbol_data, symbol)
                signals.extend(symbol_signals)
        else:
            # Single asset data
            signals = self._generate_signals_single_asset(data, 'asset')
        
        return signals
    
    def _generate_signals_single_asset(self, data: pd.DataFrame, symbol: str) -> List[Signal]:
        """Generate signals for a single asset."""
        signals = []
        
        if len(data) < self.long_window:
            return signals
        
        # Calculate moving averages
        data = data.copy()
        data['sma_short'] = data['close'].rolling(window=self.short_window).mean()
        data['sma_long'] = data['close'].rolling(window=self.long_window).mean()
        
        # Calculate crossover signals
        data['ma_diff'] = data['sma_short'] - data['sma_long']
        data['ma_diff_prev'] = data['ma_diff'].shift(1)
        
        # Identify crossovers
        data['bullish_cross'] = (data['ma_diff'] > 0) & (data['ma_diff_prev'] <= 0)
        data['bearish_cross'] = (data['ma_diff'] < 0) & (data['ma_diff_prev'] >= 0)
        
        # Add signal strength based on the magnitude of crossover
        data['signal_strength'] = abs(data['ma_diff']) / data['close']
        
        # Generate signals
        for idx, row in data.iterrows():
            timestamp = idx if hasattr(data.index, 'unique') else row['date']
            
            # Bullish crossover (buy signal)
            if row['bullish_cross'] and row['signal_strength'] >= self.signal_threshold:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    confidence=min(row['signal_strength'] * 10, 1.0),
                    metadata={
                        'short_ma': row['sma_short'],
                        'long_ma': row['sma_long'],
                        'signal_strength': row['signal_strength']
                    }
                ))
            
            # Bearish crossover (sell signal)
            elif row['bearish_cross'] and row['signal_strength'] >= self.signal_threshold:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=row['close'],
                    confidence=min(row['signal_strength'] * 10, 1.0),
                    metadata={
                        'short_ma': row['sma_short'],
                        'long_ma': row['sma_long'],
                        'signal_strength': row['signal_strength']
                    }
                ))
        
        return signals
    
    def calculate_position_size(self, signal: Signal, available_cash: float) -> int:
        """Calculate position size based on available cash and risk management."""
        if signal.signal_type == SignalType.BUY:
            # Calculate position size as percentage of portfolio
            target_value = available_cash * self.position_size_pct
            position_size = int(target_value / signal.price)
            return max(0, position_size)
        
        elif signal.signal_type == SignalType.SELL:
            # For sell signals, sell all shares of the symbol
            if signal.symbol in self.positions:
                return self.positions[signal.symbol].quantity
            return 0
        
        return 0

class ExponentialMovingAverageCrossover(StrategyBase):
    """
    Exponential Moving Average Crossover Strategy.
    
    Similar to SMA crossover but uses exponential moving averages
    which are more responsive to recent price changes.
    """
    
    def __init__(
        self, 
        short_span: int = 12, 
        long_span: int = 26,
        signal_threshold: float = 0.01,
        position_size_pct: float = 0.1,
        **kwargs
    ):
        super().__init__("EMA_Crossover", **kwargs)
        
        self.short_span = short_span
        self.long_span = long_span
        self.signal_threshold = signal_threshold
        self.position_size_pct = position_size_pct
        
        self.parameters.update({
            'short_span': short_span,
            'long_span': long_span,
            'signal_threshold': signal_threshold,
            'position_size_pct': position_size_pct
        })
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate trading signals based on EMA crossover."""
        signals = []
        
        if len(data) < self.long_span * 2:  # Need more data for EMA
            return signals
        
        # Handle multi-symbol data
        if 'symbol' in data.columns:
            symbols = data['symbol'].unique()
            for symbol in symbols:
                symbol_data = data[data['symbol'] == symbol].copy()
                symbol_signals = self._generate_signals_single_asset(symbol_data, symbol)
                signals.extend(symbol_signals)
        else:
            signals = self._generate_signals_single_asset(data, 'asset')
        
        return signals
    
    def _generate_signals_single_asset(self, data: pd.DataFrame, symbol: str) -> List[Signal]:
        """Generate EMA crossover signals for a single asset."""
        signals = []
        
        if len(data) < self.long_span * 2:
            return signals
        
        # Calculate exponential moving averages
        data = data.copy()
        data['ema_short'] = data['close'].ewm(span=self.short_span).mean()
        data['ema_long'] = data['close'].ewm(span=self.long_span).mean()
        
        # Calculate crossover signals
        data['ema_diff'] = data['ema_short'] - data['ema_long']
        data['ema_diff_prev'] = data['ema_diff'].shift(1)
        
        # Identify crossovers
        data['bullish_cross'] = (data['ema_diff'] > 0) & (data['ema_diff_prev'] <= 0)
        data['bearish_cross'] = (data['ema_diff'] < 0) & (data['ema_diff_prev'] >= 0)
        
        # Signal strength
        data['signal_strength'] = abs(data['ema_diff']) / data['close']
        
        # Generate signals
        for idx, row in data.iterrows():
            timestamp = idx if hasattr(data.index, 'unique') else row['date']
            
            if row['bullish_cross'] and row['signal_strength'] >= self.signal_threshold:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    confidence=min(row['signal_strength'] * 10, 1.0),
                    metadata={
                        'short_ema': row['ema_short'],
                        'long_ema': row['ema_long'],
                        'signal_strength': row['signal_strength']
                    }
                ))
            
            elif row['bearish_cross'] and row['signal_strength'] >= self.signal_threshold:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=row['close'],
                    confidence=min(row['signal_strength'] * 10, 1.0),
                    metadata={
                        'short_ema': row['ema_short'],
                        'long_ema': row['ema_long'],
                        'signal_strength': row['signal_strength']
                    }
                ))
        
        return signals
    
    def calculate_position_size(self, signal: Signal, available_cash: float) -> int:
        """Calculate position size for EMA strategy."""
        if signal.signal_type == SignalType.BUY:
            target_value = available_cash * self.position_size_pct
            position_size = int(target_value / signal.price)
            return max(0, position_size)
        
        elif signal.signal_type == SignalType.SELL:
            if signal.symbol in self.positions:
                return self.positions[signal.symbol].quantity
            return 0
        
        return 0

class TripleMovingAverageCrossover(StrategyBase):
    """
    Triple Moving Average Crossover Strategy.
    
    Uses three moving averages (fast, medium, slow) for more robust signals.
    Generates buy signals when fast > medium > slow and all are trending up.
    """
    
    def __init__(
        self, 
        fast_window: int = 10,
        medium_window: int = 20, 
        slow_window: int = 50,
        trend_threshold: float = 0.005,
        position_size_pct: float = 0.15,
        **kwargs
    ):
        super().__init__("Triple_MA_Crossover", **kwargs)
        
        self.fast_window = fast_window
        self.medium_window = medium_window
        self.slow_window = slow_window
        self.trend_threshold = trend_threshold
        self.position_size_pct = position_size_pct
        
        self.parameters.update({
            'fast_window': fast_window,
            'medium_window': medium_window,
            'slow_window': slow_window,
            'trend_threshold': trend_threshold,
            'position_size_pct': position_size_pct
        })
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate signals based on triple MA alignment."""
        signals = []
        
        if len(data) < self.slow_window + 5:
            return signals
        
        if 'symbol' in data.columns:
            symbols = data['symbol'].unique()
            for symbol in symbols:
                symbol_data = data[data['symbol'] == symbol].copy()
                symbol_signals = self._generate_signals_single_asset(symbol_data, symbol)
                signals.extend(symbol_signals)
        else:
            signals = self._generate_signals_single_asset(data, 'asset')
        
        return signals
    
    def _generate_signals_single_asset(self, data: pd.DataFrame, symbol: str) -> List[Signal]:
        """Generate triple MA signals for a single asset."""
        signals = []
        
        if len(data) < self.slow_window + 5:
            return signals
        
        # Calculate moving averages
        data = data.copy()
        data['ma_fast'] = data['close'].rolling(window=self.fast_window).mean()
        data['ma_medium'] = data['close'].rolling(window=self.medium_window).mean()
        data['ma_slow'] = data['close'].rolling(window=self.slow_window).mean()
        
        # Calculate MA trends
        data['ma_fast_trend'] = data['ma_fast'].pct_change(5)
        data['ma_medium_trend'] = data['ma_medium'].pct_change(5)
        data['ma_slow_trend'] = data['ma_slow'].pct_change(5)
        
        # Bullish alignment: fast > medium > slow and all trending up
        data['bullish_alignment'] = (
            (data['ma_fast'] > data['ma_medium']) &
            (data['ma_medium'] > data['ma_slow']) &
            (data['ma_fast_trend'] > self.trend_threshold) &
            (data['ma_medium_trend'] > self.trend_threshold) &
            (data['ma_slow_trend'] > self.trend_threshold)
        )
        
        # Bearish alignment: fast < medium < slow or strong downtrend
        data['bearish_alignment'] = (
            (data['ma_fast'] < data['ma_medium']) &
            (data['ma_medium'] < data['ma_slow']) &
            (data['ma_fast_trend'] < -self.trend_threshold)
        )
        
        # Track previous state to identify new signals
        data['bullish_prev'] = data['bullish_alignment'].shift(1)
        data['bearish_prev'] = data['bearish_alignment'].shift(1)
        
        # Generate signals on alignment changes
        for idx, row in data.iterrows():
            timestamp = idx if hasattr(data.index, 'unique') else row['date']
            
            # New bullish alignment
            if row['bullish_alignment'] and not row['bullish_prev']:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    confidence=0.8,  # High confidence for triple confirmation
                    metadata={
                        'ma_fast': row['ma_fast'],
                        'ma_medium': row['ma_medium'],
                        'ma_slow': row['ma_slow'],
                        'fast_trend': row['ma_fast_trend'],
                        'medium_trend': row['ma_medium_trend'],
                        'slow_trend': row['ma_slow_trend']
                    }
                ))
            
            # New bearish alignment
            elif row['bearish_alignment'] and not row['bearish_prev']:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=row['close'],
                    confidence=0.8,
                    metadata={
                        'ma_fast': row['ma_fast'],
                        'ma_medium': row['ma_medium'],
                        'ma_slow': row['ma_slow'],
                        'fast_trend': row['ma_fast_trend'],
                        'medium_trend': row['ma_medium_trend'],
                        'slow_trend': row['ma_slow_trend']
                    }
                ))
        
        return signals
    
    def calculate_position_size(self, signal: Signal, available_cash: float) -> int:
        """Calculate position size for triple MA strategy."""
        if signal.signal_type == SignalType.BUY:
            # Larger position size due to higher confidence
            target_value = available_cash * self.position_size_pct
            position_size = int(target_value / signal.price)
            return max(0, position_size)
        
        elif signal.signal_type == SignalType.SELL:
            if signal.symbol in self.positions:
                return self.positions[signal.symbol].quantity
            return 0
        
        return 0

# Factory function to create MA strategies with default configs
def create_ma_strategy(strategy_type: str = 'simple', **kwargs) -> StrategyBase:
    """
    Factory function to create moving average strategies.
    
    Args:
        strategy_type: Type of MA strategy ('simple', 'exponential', 'triple')
        **kwargs: Strategy-specific parameters
        
    Returns:
        Configured strategy instance
    """
    if strategy_type.lower() == 'simple':
        config = get_strategy_config('moving_average')
        config.update(kwargs)
        return MovingAverageCrossover(**config)
    
    elif strategy_type.lower() == 'exponential':
        return ExponentialMovingAverageCrossover(**kwargs)
    
    elif strategy_type.lower() == 'triple':
        return TripleMovingAverageCrossover(**kwargs)
    
    else:
        raise ValueError(f"Unknown MA strategy type: {strategy_type}")