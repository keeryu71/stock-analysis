"""
Data loading and processing utilities for financial data.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """Class for loading and processing financial data."""
    
    def __init__(self):
        self.cache = {}
    
    def fetch_stock_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch stock data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Data interval ('1d', '1h', '5m', etc.)
            
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Extend end_date by 1 day to ensure we get today's data
                from datetime import datetime, timedelta
                if end_date == datetime.now().strftime('%Y-%m-%d'):
                    extended_end = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                else:
                    extended_end = end_date
                
                df = ticker.history(
                    start=start_date,
                    end=extended_end,
                    interval=interval
                )
                
                if not df.empty:
                    # Clean and standardize column names
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                    df.index.name = 'date'
                    
                    # Add symbol column
                    df['symbol'] = symbol
                    
                    # Calculate additional features
                    df = self._add_technical_features(df)
                    
                    data[symbol] = df
                    print(f"✓ Loaded {len(df)} records for {symbol}")
                else:
                    print(f"✗ No data found for {symbol}")
                    
            except Exception as e:
                print(f"✗ Error loading {symbol}: {str(e)}")
                
        return data
    
    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the DataFrame."""
        # Returns
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Moving averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # Volatility
        df['volatility_20'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'])
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
        bb_std_dev = df['close'].rolling(window=bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std_dev * bb_std)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_sp500_symbols(self, limit: Optional[int] = None) -> List[str]:
        """Get S&P 500 symbols."""
        try:
            # Get S&P 500 list from Wikipedia
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            symbols = sp500_table['Symbol'].tolist()
            
            # Clean symbols (remove dots)
            symbols = [symbol.replace('.', '-') for symbol in symbols]
            
            if limit:
                symbols = symbols[:limit]
                
            return symbols
        except Exception as e:
            print(f"Error fetching S&P 500 symbols: {e}")
            # Return a default list of popular stocks
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V']
    
    def create_universe(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        min_price: float = 5.0,
        min_volume: int = 100000
    ) -> pd.DataFrame:
        """
        Create a trading universe with filtering criteria.
        
        Args:
            symbols: List of symbols to consider
            start_date: Start date for data
            end_date: End date for data
            min_price: Minimum average price filter
            min_volume: Minimum average volume filter
            
        Returns:
            Combined DataFrame with all symbols
        """
        data = self.fetch_stock_data(symbols, start_date, end_date)
        
        # Filter based on criteria
        filtered_data = {}
        for symbol, df in data.items():
            avg_price = df['close'].mean()
            avg_volume = df['volume'].mean()
            
            if avg_price >= min_price and avg_volume >= min_volume:
                filtered_data[symbol] = df
                print(f"✓ {symbol} included (Price: ${avg_price:.2f}, Volume: {avg_volume:,.0f})")
            else:
                print(f"✗ {symbol} filtered out (Price: ${avg_price:.2f}, Volume: {avg_volume:,.0f})")
        
        # Combine all data
        if filtered_data:
            combined_df = pd.concat(filtered_data.values(), ignore_index=False)
            combined_df = combined_df.sort_values(['date', 'symbol'])
            return combined_df
        else:
            return pd.DataFrame()
    
    def get_benchmark_data(self, start_date: str, end_date: str, symbol: str = 'SPY') -> pd.DataFrame:
        """Get benchmark data for comparison."""
        data = self.fetch_stock_data([symbol], start_date, end_date)
        return data.get(symbol, pd.DataFrame())
    
    def resample_data(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Resample data to different frequency.
        
        Args:
            df: Input DataFrame
            freq: Target frequency ('D', 'W', 'M', etc.)
            
        Returns:
            Resampled DataFrame
        """
        # Group by symbol if multiple symbols present
        if 'symbol' in df.columns:
            resampled_data = []
            for symbol in df['symbol'].unique():
                symbol_data = df[df['symbol'] == symbol].copy()
                symbol_data = symbol_data.set_index('date') if 'date' in symbol_data.columns else symbol_data
                
                resampled = symbol_data.resample(freq).agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
                
                resampled['symbol'] = symbol
                resampled_data.append(resampled)
            
            return pd.concat(resampled_data)
        else:
            df = df.set_index('date') if 'date' in df.columns else df
            return df.resample(freq).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()

# Convenience functions
def load_single_stock(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Load data for a single stock."""
    loader = DataLoader()
    data = loader.fetch_stock_data([symbol], start_date, end_date)
    return data.get(symbol, pd.DataFrame())

def load_multiple_stocks(symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """Load data for multiple stocks."""
    loader = DataLoader()
    return loader.fetch_stock_data(symbols, start_date, end_date)