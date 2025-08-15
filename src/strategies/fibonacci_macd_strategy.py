"""
Advanced Multi-Indicator Strategy combining:
- Fibonacci Retracement Levels
- MACD Bullish Signals
- Volume Analysis
- RSI Levels
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from src.backtesting.strategy_base import StrategyBase, Signal, SignalType
from src.config import get_strategy_config

class FibonacciMACDStrategy(StrategyBase):
    """
    Advanced strategy that identifies optimal entry points using:
    1. Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%)
    2. Bullish MACD crossover signals
    3. Volume analysis (above average volume)
    4. RSI levels (oversold but recovering)
    """
    
    def __init__(
        self,
        fibonacci_period: int = 50,  # Period to calculate Fibonacci levels
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        volume_period: int = 20,  # Period for volume moving average
        volume_threshold: float = 1.2,  # Volume must be 20% above average
        position_size_pct: float = 0.15,
        min_confidence: float = 0.6,
        **kwargs
    ):
        super().__init__("Fibonacci_MACD_Strategy", **kwargs)
        
        self.fibonacci_period = fibonacci_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.volume_period = volume_period
        self.volume_threshold = volume_threshold
        self.position_size_pct = position_size_pct
        self.min_confidence = min_confidence
        
        # Fibonacci retracement levels
        self.fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        
        # Store parameters
        self.parameters.update({
            'fibonacci_period': fibonacci_period,
            'macd_fast': macd_fast,
            'macd_slow': macd_slow,
            'macd_signal': macd_signal,
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'volume_period': volume_period,
            'volume_threshold': volume_threshold,
            'position_size_pct': position_size_pct,
            'min_confidence': min_confidence
        })
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate trading signals based on multi-indicator analysis."""
        signals = []
        
        if len(data) < max(self.fibonacci_period, self.macd_slow + self.macd_signal, self.volume_period):
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
        """Generate signals for a single asset using multi-indicator analysis."""
        signals = []
        
        if len(data) < max(self.fibonacci_period, self.macd_slow + self.macd_signal, self.volume_period):
            return signals
        
        # Calculate all indicators
        data = self._calculate_indicators(data)
        
        # Generate entry signals
        for idx in range(len(data)):
            if idx < max(self.fibonacci_period, self.macd_slow + self.macd_signal, self.volume_period):
                continue
                
            row = data.iloc[idx]
            timestamp = row.name if hasattr(data.index, 'date') else row.get('date', idx)
            
            # Check for buy signal
            buy_signal, confidence, metadata = self._check_buy_conditions(data, idx)
            
            if buy_signal and confidence >= self.min_confidence:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    confidence=confidence,
                    metadata=metadata
                ))
            
            # Check for sell signal (take profit or stop loss)
            sell_signal, sell_confidence, sell_metadata = self._check_sell_conditions(data, idx, symbol)
            
            if sell_signal:
                signals.append(Signal(
                    timestamp=timestamp,
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=row['close'],
                    confidence=sell_confidence,
                    metadata=sell_metadata
                ))
        
        return signals
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        data = data.copy()
        
        # 1. Fibonacci Retracement Levels
        data = self._calculate_fibonacci_levels(data)
        
        # 2. MACD
        data = self._calculate_macd(data)
        
        # 3. RSI
        data = self._calculate_rsi(data)
        
        # 4. Volume Analysis
        data = self._calculate_volume_indicators(data)
        
        # 5. Additional trend indicators
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        
        return data
    
    def _calculate_fibonacci_levels(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Fibonacci retracement levels."""
        data = data.copy()
        
        # Calculate rolling high and low over fibonacci_period
        data['rolling_high'] = data['high'].rolling(window=self.fibonacci_period).max()
        data['rolling_low'] = data['low'].rolling(window=self.fibonacci_period).min()
        
        # Calculate Fibonacci levels
        data['fib_range'] = data['rolling_high'] - data['rolling_low']
        
        for level in self.fib_levels:
            data[f'fib_{level:.3f}'] = data['rolling_high'] - (data['fib_range'] * level)
        
        # Determine current position relative to Fibonacci levels
        data['fib_position'] = self._get_fibonacci_position(data)
        
        return data
    
    def _get_fibonacci_position(self, data: pd.DataFrame) -> pd.Series:
        """Determine which Fibonacci level the current price is near."""
        positions = []
        
        for idx, row in data.iterrows():
            current_price = row['close']
            position = 'none'
            
            # Check proximity to each Fibonacci level (within 1% tolerance)
            tolerance = 0.01
            
            for level in self.fib_levels:
                fib_price = row[f'fib_{level:.3f}']
                if pd.notna(fib_price):
                    if abs(current_price - fib_price) / fib_price <= tolerance:
                        position = f'fib_{level:.3f}'
                        break
            
            positions.append(position)
        
        return pd.Series(positions, index=data.index)
    
    def _calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator."""
        data = data.copy()
        
        # Calculate EMAs
        ema_fast = data['close'].ewm(span=self.macd_fast).mean()
        ema_slow = data['close'].ewm(span=self.macd_slow).mean()
        
        # MACD line
        data['macd'] = ema_fast - ema_slow
        
        # Signal line
        data['macd_signal'] = data['macd'].ewm(span=self.macd_signal).mean()
        
        # Histogram
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # MACD signals
        data['macd_bullish'] = (data['macd'] > data['macd_signal']) & (data['macd'].shift(1) <= data['macd_signal'].shift(1))
        data['macd_bearish'] = (data['macd'] < data['macd_signal']) & (data['macd'].shift(1) >= data['macd_signal'].shift(1))
        
        return data
    
    def _calculate_rsi(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator."""
        data = data.copy()
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI conditions
        data['rsi_oversold'] = data['rsi'] < self.rsi_oversold
        data['rsi_overbought'] = data['rsi'] > self.rsi_overbought
        data['rsi_recovering'] = (data['rsi'] > data['rsi'].shift(1)) & (data['rsi'].shift(1) < self.rsi_oversold)
        
        return data
    
    def _calculate_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators."""
        data = data.copy()
        
        # Volume moving average
        data['volume_ma'] = data['volume'].rolling(window=self.volume_period).mean()
        
        # Volume ratio (current volume vs average)
        data['volume_ratio'] = data['volume'] / data['volume_ma']
        
        # High volume condition
        data['high_volume'] = data['volume_ratio'] > self.volume_threshold
        
        # Volume trend
        data['volume_trend'] = data['volume'].rolling(window=5).mean() > data['volume'].rolling(window=20).mean()
        
        return data
    
    def _check_buy_conditions(self, data: pd.DataFrame, idx: int) -> Tuple[bool, float, Dict[str, Any]]:
        """Check if all buy conditions are met and calculate confidence."""
        row = data.iloc[idx]
        prev_row = data.iloc[idx-1] if idx > 0 else row
        
        conditions = {}
        confidence_factors = []
        
        # 1. Fibonacci Level Check (near support levels)
        fib_condition = row['fib_position'] in ['fib_0.382', 'fib_0.500', 'fib_0.618']
        conditions['fibonacci_support'] = fib_condition
        if fib_condition:
            confidence_factors.append(0.25)
        
        # 2. MACD Bullish Signal
        macd_condition = row['macd_bullish'] and row['macd'] > prev_row['macd']
        conditions['macd_bullish'] = macd_condition
        if macd_condition:
            confidence_factors.append(0.3)
        
        # 3. RSI Conditions (oversold recovery)
        rsi_condition = (row['rsi_recovering'] or 
                        (self.rsi_oversold < row['rsi'] < 50 and row['rsi'] > prev_row['rsi']))
        conditions['rsi_favorable'] = rsi_condition
        if rsi_condition:
            confidence_factors.append(0.25)
        
        # 4. Volume Confirmation
        volume_condition = row['high_volume'] and row['volume_trend']
        conditions['volume_confirmation'] = volume_condition
        if volume_condition:
            confidence_factors.append(0.2)
        
        # 5. Trend Confirmation (price above short-term MA)
        trend_condition = row['close'] > row['sma_20']
        conditions['trend_favorable'] = trend_condition
        if trend_condition:
            confidence_factors.append(0.1)
        
        # Calculate overall confidence
        confidence = sum(confidence_factors)
        
        # Buy signal requires at least 3 out of 5 conditions
        buy_signal = sum(conditions.values()) >= 3
        
        metadata = {
            'conditions': conditions,
            'confidence_breakdown': confidence_factors,
            'fibonacci_level': row['fib_position'],
            'rsi_value': row['rsi'],
            'macd_value': row['macd'],
            'volume_ratio': row['volume_ratio'],
            'price_vs_sma20': (row['close'] - row['sma_20']) / row['sma_20']
        }
        
        return buy_signal, confidence, metadata
    
    def _check_sell_conditions(self, data: pd.DataFrame, idx: int, symbol: str) -> Tuple[bool, float, Dict[str, Any]]:
        """Check for sell conditions (take profit, stop loss, or trend reversal)."""
        row = data.iloc[idx]
        
        # Only sell if we have a position
        if symbol not in self.positions:
            return False, 0.0, {}
        
        position = self.positions[symbol]
        current_price = row['close']
        entry_price = position.entry_price
        
        # Calculate return
        return_pct = (current_price - entry_price) / entry_price
        
        conditions = {}
        
        # 1. Take Profit (15% gain)
        take_profit_condition = return_pct > 0.15
        conditions['take_profit'] = take_profit_condition
        
        # 2. Stop Loss (8% loss)
        stop_loss_condition = return_pct < -0.08
        conditions['stop_loss'] = stop_loss_condition
        
        # 3. RSI Overbought
        rsi_exit_condition = row['rsi'] > self.rsi_overbought
        conditions['rsi_overbought'] = rsi_exit_condition
        
        # 4. MACD Bearish Signal
        macd_exit_condition = row['macd_bearish']
        conditions['macd_bearish'] = macd_exit_condition
        
        # 5. Volume Drying Up
        volume_exit_condition = row['volume_ratio'] < 0.8 and not row['volume_trend']
        conditions['volume_weak'] = volume_exit_condition
        
        # Sell signal logic
        sell_signal = (take_profit_condition or stop_loss_condition or 
                      (rsi_exit_condition and macd_exit_condition))
        
        # Calculate sell confidence
        sell_confidence = 0.8 if (take_profit_condition or stop_loss_condition) else 0.6
        
        metadata = {
            'conditions': conditions,
            'return_pct': return_pct,
            'entry_price': entry_price,
            'current_price': current_price,
            'rsi_value': row['rsi'],
            'macd_value': row['macd'],
            'volume_ratio': row['volume_ratio']
        }
        
        return sell_signal, sell_confidence, metadata
    
    def calculate_position_size(self, signal: Signal, available_cash: float) -> int:
        """Calculate position size based on signal confidence and available cash."""
        if signal.signal_type == SignalType.BUY:
            # Adjust position size based on confidence
            base_size = available_cash * self.position_size_pct
            confidence_multiplier = signal.confidence  # Scale by confidence
            target_value = base_size * confidence_multiplier
            position_size = int(target_value / signal.price)
            return max(0, position_size)
        
        elif signal.signal_type == SignalType.SELL:
            if signal.symbol in self.positions:
                return self.positions[signal.symbol].quantity
            return 0
        
        return 0

# Factory function for easy strategy creation
def create_fibonacci_macd_strategy(**kwargs) -> FibonacciMACDStrategy:
    """
    Factory function to create Fibonacci MACD strategy with custom parameters.
    
    Args:
        **kwargs: Strategy parameters
        
    Returns:
        Configured FibonacciMACDStrategy instance
    """
    return FibonacciMACDStrategy(**kwargs)