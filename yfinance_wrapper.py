#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YFinance Wrapper for Railway Deployment
Handles Railway-specific environment issues and provides robust data fetching
"""

import os
import sys
import warnings
import pandas as pd
from datetime import datetime, timedelta

# Suppress warnings
warnings.filterwarnings('ignore')

# Try to import yfinance with error handling
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    print("✅ yfinance imported successfully")
except ImportError as e:
    YFINANCE_AVAILABLE = False
    print(f"❌ yfinance import failed: {e}")

class RailwayYFinance:
    """Robust yfinance wrapper for Railway deployment."""
    
    def __init__(self):
        self.available = YFINANCE_AVAILABLE
        
    def get_stock_data(self, symbol, period='1y', min_days=20):
        """Get stock data with multiple fallback methods for Railway."""
        if not self.available:
            print(f"❌ yfinance not available for {symbol}")
            return None
            
        print(f"🔍 Fetching data for {symbol} with period {period}")
        
        # Method 1: Standard ticker.history()
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, auto_adjust=False, prepost=False, 
                                actions=False, back_adjust=False, repair=False)
            if not data.empty and len(data) >= min_days:
                print(f"✅ Method 1 success: {len(data)} days for {symbol}")
                return self._clean_data(data)
        except Exception as e:
            print(f"⚠️ Method 1 failed for {symbol}: {e}")
        
        # Method 2: yf.download() with minimal parameters
        try:
            data = yf.download(symbol, period=period, progress=False, 
                             show_errors=False, auto_adjust=False, 
                             prepost=False, threads=False)
            if not data.empty and len(data) >= min_days:
                print(f"✅ Method 2 success: {len(data)} days for {symbol}")
                return self._clean_data(data)
        except Exception as e:
            print(f"⚠️ Method 2 failed for {symbol}: {e}")
        
        # Method 3: Ultra-minimal approach
        try:
            data = yf.download(symbol, period=period)
            if not data.empty and len(data) >= min_days:
                print(f"✅ Method 3 success: {len(data)} days for {symbol}")
                return self._clean_data(data)
        except Exception as e:
            print(f"⚠️ Method 3 failed for {symbol}: {e}")
        
        # Method 4: Try shorter periods
        short_periods = ['6mo', '3mo', '2mo', '1mo']
        for short_period in short_periods:
            try:
                data = yf.download(symbol, period=short_period)
                if not data.empty and len(data) >= max(10, min_days // 2):
                    print(f"✅ Method 4 success: {len(data)} days for {symbol} ({short_period})")
                    return self._clean_data(data)
            except Exception as e:
                print(f"⚠️ Method 4 ({short_period}) failed for {symbol}: {e}")
                continue
        
        print(f"❌ All methods failed for {symbol}")
        return None
    
    def get_current_price(self, symbol):
        """Get current price with multiple fallback methods."""
        if not self.available:
            return None
            
        print(f"🔍 Fetching current price for {symbol}")
        
        # Method 1: Recent history
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                if price > 0:
                    print(f"✅ Current price for {symbol}: ${price:.2f}")
                    return float(price)
        except Exception as e:
            print(f"⚠️ Current price method 1 failed for {symbol}: {e}")
        
        # Method 2: Try 2-day history
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                if price > 0:
                    print(f"✅ Current price for {symbol}: ${price:.2f}")
                    return float(price)
        except Exception as e:
            print(f"⚠️ Current price method 2 failed for {symbol}: {e}")
        
        # Method 3: Try info (might fail on Railway)
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']
            for field in price_fields:
                if field in info and info[field] and info[field] > 0:
                    price = float(info[field])
                    print(f"✅ Current price for {symbol} from {field}: ${price:.2f}")
                    return price
        except Exception as e:
            print(f"⚠️ Current price method 3 failed for {symbol}: {e}")
        
        print(f"❌ Could not get current price for {symbol}")
        return None
    
    def _clean_data(self, data):
        """Clean and standardize the data format."""
        try:
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Handle multi-level columns from yf.download
            if isinstance(data.columns, pd.MultiIndex):
                # Flatten multi-level columns
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
            
            # Ensure all required columns exist
            for col in required_columns:
                if col not in data.columns:
                    if col == 'Volume' and 'Vol' in data.columns:
                        data['Volume'] = data['Vol']
                    elif 'Adj Close' in data.columns and col == 'Close':
                        data['Close'] = data['Adj Close']
                    else:
                        print(f"⚠️ Missing column {col}, using Close price as fallback")
                        data[col] = data['Close']
            
            # Remove any NaN values
            data = data.dropna()
            
            # Ensure positive values
            for col in ['Open', 'High', 'Low', 'Close']:
                data[col] = data[col].abs()
            
            data['Volume'] = data['Volume'].abs()
            
            print(f"✅ Data cleaned: {len(data)} rows, columns: {list(data.columns)}")
            return data
            
        except Exception as e:
            print(f"❌ Error cleaning data: {e}")
            return data

# Global instance
railway_yf = RailwayYFinance()

def get_stock_data(symbol, period='1y', min_days=20):
    """Convenience function to get stock data."""
    return railway_yf.get_stock_data(symbol, period, min_days)

def get_current_price(symbol):
    """Convenience function to get current price."""
    return railway_yf.get_current_price(symbol)

if __name__ == "__main__":
    # Test the wrapper
    print("Testing Railway YFinance Wrapper...")
    
    test_symbols = ['AAPL', 'MSFT', 'CRM']
    for symbol in test_symbols:
        print(f"\n--- Testing {symbol} ---")
        
        # Test current price
        price = get_current_price(symbol)
        print(f"Current price: {price}")
        
        # Test historical data
        data = get_stock_data(symbol, period='3mo', min_days=20)
        if data is not None:
            print(f"Historical data: {len(data)} days")
            print(f"Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("No historical data available")