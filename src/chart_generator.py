#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Stock Chart Generator
Creates comprehensive technical analysis charts with Fibonacci, MACD, RSI, and Volume
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from .data.data_loader import DataLoader
from .strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

class StockChartGenerator:
    """Professional stock chart generator with technical indicators."""
    
    def __init__(self, stocks=None):
        # Default stock list (can be overridden)
        self.stocks = stocks or ['TSLA', 'AMD', 'BMNR', 'SBET', 'MSTR', 'HIMS', 'PLTR', 'AVGO', 'NVDA', 'HOOD', 'COIN', 'OSCR', 'GOOG']
        
    def create_stock_chart(self, symbol, data):
        """Create comprehensive technical analysis chart for a stock."""
        try:
            if data.empty:
                print(f"No data available for {symbol}")
                return None
            
            # Calculate technical indicators
            strategy = FibonacciMACDStrategy()
            analyzed_data = strategy._calculate_indicators(data.copy())
            
            # Multi-timeframe Fibonacci analysis for charts
            # Use 1-year data for comprehensive view in charts
            year_high = data['high'].max()
            year_low = data['low'].min()
            fib_range = year_high - year_low
            
            # Calculate 1-year Fibonacci retracement levels for chart display
            fib_levels = {
                '23.6%': year_high - (fib_range * 0.236),
                '38.2%': year_high - (fib_range * 0.382),
                '50.0%': year_high - (fib_range * 0.500),
                '61.8%': year_high - (fib_range * 0.618),
                '78.6%': year_high - (fib_range * 0.786)
            }
            
            # Create figure with subplots
            fig = plt.figure(figsize=(16, 12))
            
            # Define grid layout
            gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1.5], hspace=0.1)
            
            # 1. Main price chart with Fibonacci levels
            ax1 = fig.add_subplot(gs[0])
            
            # Plot candlestick-style price chart
            dates = analyzed_data.index
            
            # Plot price line
            ax1.plot(dates, analyzed_data['close'], linewidth=2, color='#2E86AB', label='Close Price')
            ax1.fill_between(dates, analyzed_data['low'], analyzed_data['high'], 
                           alpha=0.1, color='#2E86AB', label='High-Low Range')
            
            # Plot Fibonacci levels
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            for i, (level_name, level_price) in enumerate(fib_levels.items()):
                ax1.axhline(y=level_price, color=colors[i % len(colors)], 
                           linestyle='--', alpha=0.7, linewidth=1.5, 
                           label=f'Fib {level_name}: ${level_price:.2f}')
            
            # Plot SMA 20
            ax1.plot(dates, analyzed_data['sma_20'], color='orange', 
                    linewidth=1.5, alpha=0.8, label='SMA 20')
            
            # Highlight current price
            current_price = analyzed_data['close'].iloc[-1]
            ax1.scatter(dates[-1], current_price, color='red', s=100, zorder=5, 
                       label=f'Current: ${current_price:.2f}')
            
            ax1.set_title(f'{symbol} - Technical Analysis Chart', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.legend(loc='upper left', fontsize=9)
            ax1.grid(True, alpha=0.3)
            
            # 2. RSI subplot
            ax2 = fig.add_subplot(gs[1], sharex=ax1)
            ax2.plot(dates, analyzed_data['rsi'], color='purple', linewidth=2, label='RSI')
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
            ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
            ax2.fill_between(dates, 30, 70, alpha=0.1, color='gray')
            
            # Highlight current RSI
            current_rsi = analyzed_data['rsi'].iloc[-1]
            ax2.scatter(dates[-1], current_rsi, color='red', s=50, zorder=5)
            
            ax2.set_ylabel('RSI', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left', fontsize=9)
            ax2.grid(True, alpha=0.3)
            
            # 3. MACD subplot
            ax3 = fig.add_subplot(gs[2], sharex=ax1)
            ax3.plot(dates, analyzed_data['macd'], color='blue', linewidth=2, label='MACD')
            ax3.plot(dates, analyzed_data['macd_signal'], color='red', linewidth=2, label='Signal')
            
            # MACD histogram
            macd_hist = analyzed_data['macd'] - analyzed_data['macd_signal']
            colors = ['green' if x >= 0 else 'red' for x in macd_hist]
            ax3.bar(dates, macd_hist, color=colors, alpha=0.3, width=1)
            
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax3.set_ylabel('MACD', fontsize=12)
            ax3.legend(loc='upper left', fontsize=9)
            ax3.grid(True, alpha=0.3)
            
            # 4. Volume subplot
            ax4 = fig.add_subplot(gs[3], sharex=ax1)
            
            # Volume bars with color coding
            volume_colors = []
            for i in range(len(analyzed_data)):
                if i == 0:
                    volume_colors.append('gray')
                else:
                    if analyzed_data['close'].iloc[i] > analyzed_data['close'].iloc[i-1]:
                        volume_colors.append('green')
                    else:
                        volume_colors.append('red')
            
            ax4.bar(dates, analyzed_data['volume'], color=volume_colors, alpha=0.7, width=1)
            
            # Volume moving average
            volume_ma = analyzed_data['volume'].rolling(window=20).mean()
            ax4.plot(dates, volume_ma, color='orange', linewidth=2, label='Volume MA(20)')
            
            ax4.set_ylabel('Volume', fontsize=12)
            ax4.set_xlabel('Date', fontsize=12)
            ax4.legend(loc='upper left', fontsize=9)
            ax4.grid(True, alpha=0.3)
            
            # Format x-axis
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            
            # Remove x-axis labels from upper subplots
            plt.setp(ax1.get_xticklabels(), visible=False)
            plt.setp(ax2.get_xticklabels(), visible=False)
            plt.setp(ax3.get_xticklabels(), visible=False)
            
            # Add analysis summary text box
            latest = analyzed_data.iloc[-1]
            conditions = {
                'fibonacci': any(abs(current_price - fib_price) / current_price <= 0.02 
                               for fib_price in fib_levels.values()),
                'macd': latest['macd'] > latest['macd_signal'],
                'rsi': 30 < latest['rsi'] < 70,
                'volume': latest['volume_ratio'] > 1.0,
                'trend': latest['close'] > latest['sma_20']
            }
            
            score = sum(conditions.values()) / len(conditions)
            
            # Determine action
            if score >= 0.8:
                action = "🚀 STRONG BUY"
                action_color = 'green'
            elif score >= 0.6:
                action = "⚡ GOOD SETUP"
                action_color = 'orange'
            elif score >= 0.4:
                action = "⏳ WAIT"
                action_color = 'gray'
            else:
                action = "🛑 AVOID"
                action_color = 'red'
            
            # Create summary text
            summary_text = f"""
{action} ({score:.0%})

Technical Indicators:
🌀 Fibonacci: {'✅' if conditions['fibonacci'] else '❌'}
📈 MACD: {'✅' if conditions['macd'] else '❌'}
📊 RSI: {'✅' if conditions['rsi'] else '❌'} ({latest['rsi']:.0f})
📊 Volume: {'✅' if conditions['volume'] else '❌'} ({latest['volume_ratio']:.1f}x)
📈 Trend: {'✅' if conditions['trend'] else '❌'}

Current Price: ${current_price:.2f}
1Y High: ${year_high:.2f}
1Y Low: ${year_low:.2f}
"""
            
            # Add text box
            props = dict(boxstyle='round', facecolor=action_color, alpha=0.1)
            ax1.text(0.02, 0.98, summary_text.strip(), transform=ax1.transAxes, 
                    fontsize=10, verticalalignment='top', bbox=props, fontfamily='monospace')
            
            plt.tight_layout()
            
            # Save chart
            chart_filename = f'charts/{symbol}_technical_analysis.png'
            os.makedirs('charts', exist_ok=True)
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Chart saved: {chart_filename}")
            return chart_filename
            
        except Exception as e:
            print(f"❌ Error creating chart for {symbol}: {e}")
            return None
    
    def generate_all_charts(self):
        """Generate charts for all stocks."""
        print("📊 Generating professional technical analysis charts...")
        print(f"📈 Stocks: {', '.join(self.stocks)}")
        
        try:
            # Load 1 year of data for multi-timeframe Fibonacci analysis
            loader = DataLoader()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            all_data = loader.fetch_stock_data(self.stocks, start_date, end_date)
            
            chart_files = []
            for symbol in self.stocks:
                if symbol in all_data:
                    stock_data = all_data[symbol]
                    chart_file = self.create_stock_chart(symbol, stock_data)
                    if chart_file:
                        chart_files.append(chart_file)
                else:
                    print(f"❌ {symbol}: No data available")
            
            print(f"\n✅ Generated {len(chart_files)} charts successfully!")
            print(f"📁 Charts saved in: ./charts/ directory")
            
            return chart_files
            
        except Exception as e:
            print(f"❌ Error generating charts: {e}")
            return []

def main():
    """Main function to generate all stock charts."""
    chart_generator = StockChartGenerator()
    chart_files = chart_generator.generate_all_charts()
    
    if chart_files:
        print(f"\n🎯 Chart files created:")
        for chart_file in chart_files:
            print(f"  📊 {chart_file}")
        print(f"\n💡 Open these PNG files to view detailed technical analysis!")
    else:
        print("⚠️  No charts generated successfully.")
    
    return chart_files

if __name__ == "__main__":
    main()