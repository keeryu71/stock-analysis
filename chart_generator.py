#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Chart Generator for Stock Analysis
Creates interactive charts with Fibonacci levels, RSI, volume, and technical indicators
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import io
import base64
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web

class StockChartGenerator:
    """Generate custom technical analysis charts."""
    
    def __init__(self):
        self.fig_size = (12, 10)
        self.dpi = 100
        
    def fetch_chart_data(self, symbol, period='3mo'):
        """Fetch data for charting."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
                
            # Calculate technical indicators
            data = self.calculate_indicators(data)
            return data
            
        except Exception as e:
            print(f"Error fetching chart data for {symbol}: {e}")
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
    
    def generate_chart(self, symbol, analysis_data=None):
        """Generate comprehensive technical analysis chart."""
        try:
            # Fetch data
            data = self.fetch_chart_data(symbol)
            if data is None or len(data) < 50:
                return None
            
            # Calculate Fibonacci levels
            fib_levels, fib_high_date, fib_low_date = self.calculate_fibonacci_levels(data)
            
            # Create figure with subplots
            fig = Figure(figsize=self.fig_size, dpi=self.dpi)
            fig.patch.set_facecolor('white')
            
            # Main price chart (60% of height)
            ax1 = fig.add_subplot(4, 1, (1, 2))
            
            # Plot candlestick-style price chart
            dates = data.index
            
            # Price line
            ax1.plot(dates, data['Close'], color='#2196F3', linewidth=2, label='Close Price')
            
            # Moving averages
            ax1.plot(dates, data['SMA20'], color='#FF9800', linewidth=1.5, label='SMA20', alpha=0.8)
            ax1.plot(dates, data['SMA50'], color='#9C27B0', linewidth=1.5, label='SMA50', alpha=0.8)
            
            # Fibonacci levels
            if fib_levels:
                colors = ['#FF5722', '#FF9800', '#FFC107', '#4CAF50', '#2196F3', '#9C27B0', '#E91E63']
                for i, (level, price) in enumerate(fib_levels.items()):
                    color = colors[i % len(colors)]
                    ax1.axhline(y=price, color=color, linestyle='--', alpha=0.7, linewidth=1)
                    ax1.text(dates[-1], price, f'  {level}: ${price:.2f}', 
                            verticalalignment='center', fontsize=8, color=color, weight='bold')
            
            # Entry points from analysis
            if analysis_data and 'top_entries' in analysis_data:
                for entry in analysis_data['top_entries'][:3]:  # Show top 3 entries
                    entry_price = entry['price']
                    ax1.axhline(y=entry_price, color='#4CAF50', linestyle='-', alpha=0.8, linewidth=2)
                    ax1.text(dates[len(dates)//4], entry_price, f'  🎯 {entry["level"]}: ${entry_price:.2f}', 
                            verticalalignment='bottom', fontsize=9, color='#4CAF50', weight='bold',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='#4CAF50', alpha=0.2))
            
            ax1.set_title(f'{symbol} - Technical Analysis Chart', fontsize=16, weight='bold', pad=20)
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            
            # RSI subplot (15% of height)
            ax2 = fig.add_subplot(4, 1, 3)
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
            
            # Volume subplot (15% of height)
            ax3 = fig.add_subplot(4, 1, 4)
            volume_colors = ['#4CAF50' if close >= open_price else '#F44336' 
                           for close, open_price in zip(data['Close'], data['Open'])]
            ax3.bar(dates, data['Volume'], color=volume_colors, alpha=0.7, width=0.8)
            ax3.plot(dates, data['Volume_MA'], color='#2196F3', linewidth=2, label='Volume MA(20)')
            ax3.set_ylabel('Volume', fontsize=10)
            ax3.legend(loc='upper right', fontsize=8)
            ax3.grid(True, alpha=0.3)
            
            # Add volume trend indicator
            if analysis_data and 'volume_ratio' in analysis_data:
                vol_ratio = analysis_data['volume_ratio']
                vol_trend = analysis_data.get('volume_trend', 'Unknown')
                vol_color = '#4CAF50' if vol_ratio >= 1.5 else '#FF9800' if vol_ratio >= 1.0 else '#F44336'
                ax3.text(0.02, 0.95, f'Volume: {vol_ratio:.1f}x ({vol_trend})', transform=ax3.transAxes,
                        fontsize=10, weight='bold', color=vol_color,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=vol_color, alpha=0.2))
            
            # Format x-axis for bottom subplot
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # Add analysis summary box
            if analysis_data:
                score = analysis_data.get('score', 0) * 100
                signal = analysis_data.get('signal', 'WAIT')
                signal_color = '#4CAF50' if signal == 'BUY' else '#FF9800' if signal == 'HOLD' else '#F44336'
                
                summary_text = f"Score: {score:.0f}% | Signal: {signal}"
                fig.text(0.02, 0.98, summary_text, fontsize=14, weight='bold', color=signal_color,
                        bbox=dict(boxstyle='round,pad=0.5', facecolor=signal_color, alpha=0.2))
            
            # Adjust layout
            fig.tight_layout()
            fig.subplots_adjust(top=0.95, bottom=0.1, hspace=0.3)
            
            # Convert to base64 string for web display
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=self.dpi)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            plt.close(fig)  # Free memory
            
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