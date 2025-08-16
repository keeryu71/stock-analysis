#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Chart Generator for Stock Analysis
Creates interactive charts with Fibonacci levels, RSI, volume, and technical indicators
"""

import os
import sys

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from matplotlib.figure import Figure

# Disable matplotlib font cache warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Try to import yfinance, fallback to mock data if not available
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance not available, using mock data for charts")

class StockChartGenerator:
    """Generate custom technical analysis charts."""
    
    def __init__(self):
        self.fig_size = (12, 10)
        self.dpi = 100
        
    def fetch_chart_data(self, symbol, period='3mo'):
        """Fetch REAL data for charting using same logic as stock analyzer."""
        if not YFINANCE_AVAILABLE:
            print(f"❌ yfinance not available - cannot generate real chart for {symbol}")
            return None
            
        # Try multiple periods and methods to get real data (same as hybrid analyzer)
        periods_to_try = ['3mo', '6mo', '1y', '2y', '5y']
        
        for period_attempt in periods_to_try:
            try:
                print(f"🔍 Chart: Trying {period_attempt} historical data for {symbol}...")
                ticker = yf.Ticker(symbol)
                print(f"🔍 Chart: Created ticker for {symbol}")
                
                data = ticker.history(period=period_attempt)
                print(f"🔍 Chart: History call completed for {symbol}, got {len(data) if not data.empty else 0} rows")
                
                if not data.empty and len(data) >= 30:  # Need at least 30 days for indicators
                    print(f"✅ Chart: Got {len(data)} days of REAL historical data for {symbol} ({period_attempt})")
                    print(f"✅ Chart: Date range: {data.index[0]} to {data.index[-1]}")
                    print(f"✅ Chart: Latest close: ${data['Close'].iloc[-1]:.2f}")
                    # Calculate technical indicators
                    data = self.calculate_indicators(data)
                    return data
                else:
                    print(f"⚠️ Chart: Insufficient historical data for {symbol} with {period_attempt}: {len(data) if not data.empty else 0} days")
                    if not data.empty:
                        print(f"⚠️ Chart: Data columns: {list(data.columns)}")
                    
            except Exception as e:
                print(f"⚠️ Chart: Failed to get {period_attempt} data for {symbol}: {e}")
                continue
        
        # Try alternative download method (same as hybrid analyzer)
        try:
            print(f"🔄 Chart: Trying alternative download method for {symbol}...")
            # Disable caching to avoid SQLite issues on Railway
            data = yf.download(symbol, period='1y', interval='1d', progress=False,
                             auto_adjust=True, prepost=True, threads=True, proxy=None)
            
            if not data.empty and len(data) >= 30:
                print(f"✅ Chart: Alternative method got {len(data)} days of REAL data for {symbol}")
                # Rename columns to match expected format if needed
                if 'Adj Close' in data.columns:
                    data['Close'] = data['Adj Close']
                # Calculate technical indicators
                data = self.calculate_indicators(data)
                return data
                
        except Exception as e:
            print(f"⚠️ Chart: Alternative method failed for {symbol}: {e}")
            
        # Try with minimal parameters to avoid SQLite issues
        try:
            print(f"🔄 Chart: Trying minimal download for {symbol}...")
            data = yf.download(symbol, period='6mo', auto_adjust=False, progress=False)
            if not data.empty and len(data) >= 20:
                print(f"✅ Chart: Minimal method got {len(data)} days of data for {symbol}")
                data = self.calculate_indicators(data)
                return data
        except Exception as e2:
            print(f"⚠️ Chart: Minimal method also failed for {symbol}: {e2}")
            
        # Try ultra-minimal approach - just symbol and period
        try:
            print(f"🔄 Chart: Trying ultra-minimal download for {symbol}...")
            data = yf.download(symbol, period='3mo')
            if not data.empty and len(data) >= 15:
                print(f"✅ Chart: Ultra-minimal method got {len(data)} days of data for {symbol}")
                data = self.calculate_indicators(data)
                return data
        except Exception as e3:
            print(f"⚠️ Chart: Ultra-minimal method also failed for {symbol}: {e3}")
            
        # Try using Ticker with different periods as last resort
        try:
            print(f"🔄 Chart: Trying ticker with shorter periods for {symbol}...")
            ticker = yf.Ticker(symbol)
            for short_period in ['1mo', '2mo', '3mo']:
                try:
                    data = ticker.history(period=short_period, auto_adjust=False)
                    if not data.empty and len(data) >= 10:
                        print(f"✅ Chart: Short period {short_period} got {len(data)} days for {symbol}")
                        data = self.calculate_indicators(data)
                        return data
                except:
                    continue
        except Exception as e4:
            print(f"⚠️ Chart: Short period method failed for {symbol}: {e4}")
        
        print(f"❌ Chart: Could not get ANY real historical data for {symbol}")
        return None
    
    def get_current_real_price(self, symbol):
        """Get current real price for anchoring mock data."""
        try:
            if not YFINANCE_AVAILABLE:
                return None
                
            ticker = yf.Ticker(symbol)
            
            # Try multiple methods to get current price
            methods = [
                lambda: ticker.history(period='1d')['Close'].iloc[-1],
                lambda: ticker.history(period='2d')['Close'].iloc[-1],
                lambda: ticker.info.get('currentPrice'),
                lambda: ticker.info.get('regularMarketPrice'),
                lambda: ticker.info.get('previousClose')
            ]
            
            for method in methods:
                try:
                    price = method()
                    if price and price > 0:
                        print(f"✅ Got real current price for {symbol}: ${price:.2f}")
                        return float(price)
                except:
                    continue
                    
            print(f"⚠️ Could not get real current price for {symbol}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting current price for {symbol}: {e}")
            return None
    
    def generate_mock_data(self, symbol):
        """Generate mock stock data for demonstration."""
        try:
            # Generate 90 days of mock data
            dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
            
            # Try to get real current price first
            current_real_price = self.get_current_real_price(symbol)
            
            # Realistic base prices for different stocks (fallback if real price not available)
            base_prices = {
                'AAPL': 230.0, 'MSFT': 520.0, 'GOOGL': 204.0, 'AMZN': 231.0, 'NVDA': 180.0,
                'META': 101.0, 'TSLA': 331.0, 'NFLX': 1239.0, 'AMD': 178.0, 'CRM': 242.0,
                'ORCL': 248.0, 'ADBE': 355.0, 'AVGO': 306.0, 'INTC': 25.0, 'QCOM': 158.0,
                'JPM': 290.0, 'BAC': 47.0, 'WFC': 77.0, 'GS': 731.0, 'MS': 145.0,
                'C': 94.0, 'V': 344.0, 'MA': 582.0, 'PYPL': 69.0, 'JNJ': 177.0,
                'PFE': 25.0, 'UNH': 304.0, 'ABBV': 207.0, 'MRK': 84.0, 'TMO': 489.0,
                'ABT': 132.0, 'WMT': 100.0, 'HD': 390.0, 'PG': 154.0, 'KO': 70.0,
                'PEP': 150.0, 'NKE': 77.0, 'MCD': 309.0, 'SBUX': 91.0, 'XOM': 106.0,
                'CVX': 157.0, 'BA': 235.0, 'CAT': 408.0, 'GE': 268.0, 'PLTR': 177.0,
                'HOOD': 114.0, 'COIN': 318.0, 'SOFI': 24.0, 'RIVN': 12.24, 'LCID': 2.0
            }
            
            # Use real current price if available, otherwise use base price
            if current_real_price:
                target_price = current_real_price
                print(f"📊 Using real current price for {symbol}: ${target_price:.2f}")
            else:
                target_price = base_prices.get(symbol, 150.0)
                print(f"📊 Using fallback price for {symbol}: ${target_price:.2f}")
            
            np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
            
            # Generate price series that ends at the target price
            returns = np.random.normal(0.001, 0.02, len(dates) - 1)  # Daily returns for 89 days
            
            # Start from a price that will allow us to reach target_price
            start_price = target_price * (1 + np.random.uniform(-0.15, 0.15))  # Start within 15% of target
            prices = [start_price]
            
            # Generate intermediate prices
            for ret in returns:
                new_price = prices[-1] * (1 + ret)
                prices.append(max(new_price, 0.1))  # Ensure positive prices
            
            # Force the last price to be exactly the target price
            prices[-1] = target_price
            
            print(f"📈 Generated chart data for {symbol}: ${prices[0]:.2f} → ${prices[-1]:.2f}")
            
            # Create OHLC data
            data = pd.DataFrame(index=dates)
            data['Close'] = prices
            data['Open'] = data['Close'].shift(1).fillna(data['Close'].iloc[0])
            data['High'] = data[['Open', 'Close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, len(data)))
            data['Low'] = data[['Open', 'Close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, len(data)))
            data['Volume'] = np.random.randint(1000000, 10000000, len(data))
            
            # Calculate technical indicators
            data = self.calculate_indicators(data)
            return data
            
        except Exception as e:
            print(f"Error generating mock data for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, data):
        """Calculate all technical indicators for charting."""
        # Moving averages
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        data['MACD'] = exp1 - exp2
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # Volume moving average
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        
        return data
    
    def calculate_fibonacci_levels(self, data):
        """Calculate Fibonacci retracement levels."""
        try:
            # Use recent high and low (last 60 days)
            recent_data = data.tail(60)
            high = recent_data['High'].max()
            low = recent_data['Low'].min()
            
            # Find the dates of high and low
            high_date = recent_data[recent_data['High'] == high].index[0]
            low_date = recent_data[recent_data['Low'] == low].index[0]
            
            # Calculate Fibonacci levels
            diff = high - low
            fib_levels = {
                '0%': high,
                '23.6%': high - (diff * 0.236),
                '38.2%': high - (diff * 0.382),
                '50%': high - (diff * 0.500),
                '61.8%': high - (diff * 0.618),
                '78.6%': high - (diff * 0.786),
                '100%': low
            }
            
            return fib_levels, high_date, low_date
            
        except Exception as e:
            print(f"Error calculating Fibonacci levels: {e}")
            return {}, None, None
    
    def create_simple_price_chart(self, symbol, analysis_data=None):
        """Create a simple chart when historical data is not available."""
        try:
            print(f"📊 Creating simple price chart for {symbol}")
            
            # Get current price from analysis data or try to fetch it
            current_price = None
            if analysis_data and analysis_data.get('price'):
                current_price = analysis_data['price']
                print(f"✅ Using price from analysis data: ${current_price:.2f}")
            else:
                current_price = self.get_current_real_price(symbol)
                if not current_price:
                    # Use fallback price
                    base_prices = {
                        'AAPL': 230.0, 'MSFT': 520.0, 'GOOGL': 204.0, 'AMZN': 231.0, 'NVDA': 180.0,
                        'META': 101.0, 'TSLA': 331.0, 'NFLX': 1239.0, 'AMD': 178.0, 'CRM': 242.0,
                        'ORCL': 248.0, 'ADBE': 355.0, 'AVGO': 306.0, 'INTC': 25.0, 'QCOM': 158.0,
                        'JPM': 290.0, 'BAC': 47.0, 'WFC': 77.0, 'GS': 731.0, 'MS': 145.0,
                        'C': 94.0, 'V': 344.0, 'MA': 582.0, 'PYPL': 69.0, 'JNJ': 177.0,
                        'PFE': 25.0, 'UNH': 304.0, 'ABBV': 207.0, 'MRK': 84.0, 'TMO': 489.0,
                        'ABT': 132.0, 'WMT': 100.0, 'HD': 390.0, 'PG': 154.0, 'KO': 70.0,
                        'PEP': 150.0, 'NKE': 77.0, 'MCD': 309.0, 'SBUX': 91.0, 'XOM': 106.0,
                        'CVX': 157.0, 'BA': 235.0, 'CAT': 408.0, 'GE': 268.0, 'PLTR': 177.0,
                        'HOOD': 114.0, 'COIN': 318.0, 'SOFI': 24.0, 'RIVN': 12.24, 'LCID': 2.0
                    }
                    current_price = base_prices.get(symbol, 150.0)
                    print(f"⚠️ Using fallback price for {symbol}: ${current_price:.2f}")
            
            # Create a simple figure
            plt.style.use('default')
            fig, ax = plt.subplots(1, 1, figsize=(10, 6), dpi=self.dpi)
            fig.patch.set_facecolor('white')
            
            # Create a simple price display
            ax.text(0.5, 0.6, f'{symbol}', fontsize=32, weight='bold',
                   ha='center', va='center', transform=ax.transAxes, color='#2196F3')
            ax.text(0.5, 0.4, f'${current_price:.2f}', fontsize=24, weight='bold',
                   ha='center', va='center', transform=ax.transAxes, color='#4CAF50')
            ax.text(0.5, 0.25, 'Current Price', fontsize=14,
                   ha='center', va='center', transform=ax.transAxes, color='#666')
            ax.text(0.5, 0.1, '⚠️ Historical chart data not available', fontsize=12,
                   ha='center', va='center', transform=ax.transAxes, color='#FF9800')
            
            # Add analysis data if available
            if analysis_data:
                info_text = []
                if 'rsi' in analysis_data:
                    info_text.append(f"RSI: {analysis_data['rsi']:.1f}")
                if 'signal' in analysis_data:
                    info_text.append(f"Signal: {analysis_data['signal']}")
                if 'score' in analysis_data:
                    info_text.append(f"Score: {analysis_data['score']*100:.0f}%")
                
                if info_text:
                    ax.text(0.5, 0.85, ' | '.join(info_text), fontsize=12, weight='bold',
                           ha='center', va='center', transform=ax.transAxes, color='#333')
            
            # Remove axes
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=self.dpi, facecolor='white')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close('all')
            
            print(f"✅ Simple chart created for {symbol}")
            return img_base64
            
        except Exception as e:
            print(f"❌ Error creating simple chart for {symbol}: {e}")
            return None
    
    def generate_chart(self, symbol, analysis_data=None):
        """Generate comprehensive technical analysis chart with robust error handling."""
        try:
            print(f"🎨 Starting chart generation for {symbol}")
            
            # Fetch data - REAL DATA ONLY
            data = self.fetch_chart_data(symbol)
            if data is None:
                print(f"⚠️ No real historical data available for {symbol}, creating simple price chart")
                return self.create_simple_price_chart(symbol, analysis_data)
                
            if len(data) < 20:  # Reduced minimum requirement
                print(f"⚠️ Insufficient historical data for {symbol}: {len(data)} days, creating simple price chart")
                return self.create_simple_price_chart(symbol, analysis_data)
            
            print(f"✅ Data fetched for {symbol}: {len(data)} days")
            
            # Determine data source for display
            data_source_text = "Real Market Data" if hasattr(data, '_real_data') else "Simulated Data (Real Price Anchored)"
            
            # Calculate Fibonacci levels
            fib_levels, fib_high_date, fib_low_date = self.calculate_fibonacci_levels(data)
            print(f"✅ Fibonacci levels calculated: {len(fib_levels)} levels")
            
            # Create figure with subplots - use plt instead of Figure for better compatibility
            plt.style.use('default')  # Ensure we have a clean style
            fig, axes = plt.subplots(4, 1, figsize=self.fig_size, dpi=self.dpi)
            fig.patch.set_facecolor('white')
            
            # Unpack axes
            ax1 = axes[0:2]  # Price chart (spans 2 rows)
            ax2 = axes[2]    # RSI
            ax3 = axes[3]    # Volume
            
            # Combine the first two axes for price chart
            ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
            ax2 = plt.subplot2grid((4, 1), (2, 0))
            ax3 = plt.subplot2grid((4, 1), (3, 0))
            
            print(f"✅ Chart layout created for {symbol}")
            
            # Plot data
            dates = data.index
            print(f"✅ Plotting data for {symbol}: {len(dates)} data points")
            
            # Price line
            ax1.plot(dates, data['Close'], color='#2196F3', linewidth=2, label='Close Price')
            
            # Moving averages (with error handling)
            if 'SMA20' in data.columns and not data['SMA20'].isna().all():
                ax1.plot(dates, data['SMA20'], color='#FF9800', linewidth=1.5, label='SMA20', alpha=0.8)
            if 'SMA50' in data.columns and not data['SMA50'].isna().all():
                ax1.plot(dates, data['SMA50'], color='#9C27B0', linewidth=1.5, label='SMA50', alpha=0.8)
            
            # Fibonacci levels
            if fib_levels:
                colors = ['#FF5722', '#FF9800', '#FFC107', '#4CAF50', '#2196F3', '#9C27B0', '#E91E63']
                for i, (level, price) in enumerate(fib_levels.items()):
                    if pd.notna(price) and price > 0:  # Validate price
                        color = colors[i % len(colors)]
                        ax1.axhline(y=price, color=color, linestyle='--', alpha=0.7, linewidth=1)
                        ax1.text(dates[-1], price, f'  {level}: ${price:.2f}',
                                verticalalignment='center', fontsize=8, color=color, weight='bold')
            
            # Entry points from analysis
            if analysis_data and 'top_entries' in analysis_data:
                for entry in analysis_data['top_entries'][:3]:  # Show top 3 entries
                    entry_price = entry.get('price', 0)
                    if entry_price > 0:
                        ax1.axhline(y=entry_price, color='#4CAF50', linestyle='-', alpha=0.8, linewidth=2)
                        ax1.text(dates[len(dates)//4], entry_price, f'  🎯 {entry.get("level", "Entry")}: ${entry_price:.2f}',
                                verticalalignment='bottom', fontsize=9, color='#4CAF50', weight='bold',
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='#4CAF50', alpha=0.2))
            
            ax1.set_title(f'{symbol} - Technical Analysis Chart', fontsize=16, weight='bold', pad=20)
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # RSI subplot
            if 'RSI' in data.columns and not data['RSI'].isna().all():
                ax2.plot(dates, data['RSI'], color='#FF5722', linewidth=2)
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
                ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
                ax2.fill_between(dates, 30, 70, alpha=0.1, color='gray')
                ax2.set_ylabel('RSI', fontsize=10)
                ax2.set_ylim(0, 100)
                ax2.legend(loc='upper right', fontsize=8)
                ax2.grid(True, alpha=0.3)
                
                # Add RSI trend indicator
                if analysis_data and 'rsi' in analysis_data:
                    current_rsi = analysis_data['rsi']
                    rsi_color = '#4CAF50' if current_rsi < 30 else '#FF9800' if current_rsi < 70 else '#F44336'
                    ax2.text(0.02, 0.95, f'Current RSI: {current_rsi:.1f}', transform=ax2.transAxes,
                            fontsize=10, weight='bold', color=rsi_color,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor=rsi_color, alpha=0.2))
            else:
                ax2.text(0.5, 0.5, 'RSI data not available', transform=ax2.transAxes,
                        ha='center', va='center', fontsize=12, color='gray')
                ax2.set_ylabel('RSI', fontsize=10)
            
            # Volume subplot
            if 'Volume' in data.columns and not data['Volume'].isna().all():
                volume_colors = ['#4CAF50' if close >= open_price else '#F44336'
                               for close, open_price in zip(data['Close'], data['Open'])]
                ax3.bar(dates, data['Volume'], color=volume_colors, alpha=0.7, width=0.8)
                
                if 'Volume_MA' in data.columns and not data['Volume_MA'].isna().all():
                    ax3.plot(dates, data['Volume_MA'], color='#2196F3', linewidth=2, label='Volume MA(20)')
                    ax3.legend(loc='upper right', fontsize=8)
                
                ax3.set_ylabel('Volume', fontsize=10)
                ax3.grid(True, alpha=0.3)
                
                # Add volume trend indicator
                if analysis_data and 'volume_ratio' in analysis_data:
                    vol_ratio = analysis_data['volume_ratio']
                    vol_trend = analysis_data.get('volume_trend', 'Unknown')
                    vol_color = '#4CAF50' if vol_ratio >= 1.5 else '#FF9800' if vol_ratio >= 1.0 else '#F44336'
                    ax3.text(0.02, 0.95, f'Volume: {vol_ratio:.1f}x ({vol_trend})', transform=ax3.transAxes,
                            fontsize=10, weight='bold', color=vol_color,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor=vol_color, alpha=0.2))
            else:
                ax3.text(0.5, 0.5, 'Volume data not available', transform=ax3.transAxes,
                        ha='center', va='center', fontsize=12, color='gray')
                ax3.set_ylabel('Volume', fontsize=10)
            
            # Format x-axis for all subplots
            for ax in [ax1, ax2, ax3]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # Add analysis summary box
            if analysis_data:
                score = analysis_data.get('score', 0) * 100
                signal = analysis_data.get('signal', 'WAIT')
                signal_color = '#4CAF50' if signal == 'BUY' else '#FF9800' if signal == 'HOLD' else '#F44336'
                
                summary_text = f"Score: {score:.0f}% | Signal: {signal}"
                fig.text(0.02, 0.98, summary_text, fontsize=14, weight='bold', color=signal_color,
                        bbox=dict(boxstyle='round,pad=0.5', facecolor=signal_color, alpha=0.2))
            
            # Add data source indicator
            fig.text(0.98, 0.02, data_source_text, fontsize=10, ha='right', va='bottom',
                    color='#666', style='italic', transform=fig.transFigure)
            
            # Adjust layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.95, bottom=0.1, hspace=0.3)
            
            print(f"✅ Chart layout completed for {symbol}")
            
            # Convert to base64 string for web display
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=self.dpi, facecolor='white')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close('all')  # Free memory - close all figures
            
            print(f"✅ Chart generated successfully for {symbol}")
            return img_base64
            
        except Exception as e:
            print(f"Error generating chart for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None

def generate_stock_chart(symbol, analysis_data=None):
    """Convenience function to generate a stock chart."""
    generator = StockChartGenerator()
    return generator.generate_chart(symbol, analysis_data)

if __name__ == "__main__":
    # Test the chart generator
    print("Testing chart generator...")
    
    # Test with TSLA
    chart_data = generate_stock_chart('TSLA')
    if chart_data:
        print("✅ Chart generated successfully!")
        print(f"Chart data length: {len(chart_data)} characters")
    else:
        print("❌ Failed to generate chart")