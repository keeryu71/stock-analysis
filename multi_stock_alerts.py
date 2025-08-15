#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Stock Alert System
Analyzes multiple stocks and shows top 2 entry opportunities
"""

import os
import pandas as pd
import numpy as np
import subprocess
from datetime import datetime, timedelta
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')

# Add the current directory to Python path
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.data.data_loader import DataLoader
from src.strategies.fibonacci_macd_strategy import FibonacciMACDStrategy
from src.chart_generator import StockChartGenerator
from stock_config import get_stock_list, LOG_FILE_NAME

class MultiStockAlerts:
    """Multi-stock alert system using native macOS notifications."""
    
    def __init__(self):
        self.stocks = get_stock_list()
        self.log_file = LOG_FILE_NAME
        
    def analyze_stock(self, symbol, data):
        """Analyze a single stock and return results."""
        try:
            if data.empty:
                return None
            
            # Multi-timeframe Fibonacci analysis: 60-day, 180-day, and 1-year
            timeframes = {
                '60D': 60,
                '180D': 180,
                '1Y': 365
            }
            
            all_fib_levels = {}
            
            for timeframe_name, days in timeframes.items():
                # Get data for this timeframe
                timeframe_data = data.tail(min(days, len(data)))
                
                if len(timeframe_data) > 0:
                    tf_high = timeframe_data['high'].max()
                    tf_low = timeframe_data['low'].min()
                    tf_range = tf_high - tf_low
                    
                    # Calculate Fibonacci levels for this timeframe
                    timeframe_fibs = {
                        f'{timeframe_name}_23.6%': tf_high - (tf_range * 0.236),
                        f'{timeframe_name}_38.2%': tf_high - (tf_range * 0.382),
                        f'{timeframe_name}_50.0%': tf_high - (tf_range * 0.500),
                        f'{timeframe_name}_61.8%': tf_high - (tf_range * 0.618),
                        f'{timeframe_name}_78.6%': tf_high - (tf_range * 0.786)
                    }
                    
                    all_fib_levels.update(timeframe_fibs)
            
            # Calculate indicators
            strategy = FibonacciMACDStrategy()
            analyzed_data = strategy._calculate_indicators(data.copy())
            latest = analyzed_data.iloc[-1]
            current_price = latest['close']
            
            # Check if current price is near ANY multi-timeframe Fibonacci support level (within 2%)
            near_fib = False
            active_fib_level = None
            
            for level_name, fib_price in all_fib_levels.items():
                # Only trigger when price is ABOVE Fibonacci level (acting as support)
                if fib_price < current_price and abs(current_price - fib_price) / current_price <= 0.02:
                    near_fib = True
                    active_fib_level = level_name
                    break
            
            # Evaluate conditions (using stable Fibonacci check)
            conditions = {
                'fibonacci': near_fib,
                'macd': latest['macd'] > latest['macd_signal'],
                'rsi': 35 < latest['rsi'] < 75,
                'volume': latest['volume_ratio'] > 1.0,
                'trend': latest['close'] > latest['sma_20']
            }
            
            # Weighted scoring system (based on indicator reliability)
            weights = {
                'macd': 0.25,      # 25% - Most reliable for trend/momentum
                'volume': 0.25,    # 25% - Critical institutional confirmation
                'trend': 0.20,     # 20% - Fundamental direction
                'rsi': 0.15,       # 15% - Good timing, but can stay extreme
                'fibonacci': 0.15  # 15% - Psychological levels
            }
            
            # Calculate weighted score
            score = sum(conditions[indicator] * weight for indicator, weight in weights.items())
            
            # Get key levels (first two entry points using 50-day Fibonacci levels)
            entry_levels = []
            
            # Add multi-timeframe Fibonacci levels that are below current price
            for level_name, fib_price in all_fib_levels.items():
                if fib_price < current_price:
                    discount = ((current_price - fib_price) / current_price) * 100
                    entry_levels.append({
                        'price': fib_price,
                        'type': level_name,
                        'discount': discount
                    })
            
            # Add SMA 20 if it's a good entry
            sma_20 = latest['sma_20']
            if pd.notna(sma_20) and sma_20 < current_price:
                discount = ((current_price - sma_20) / current_price) * 100
                entry_levels.append({
                    'price': sma_20,
                    'type': 'SMA 20',
                    'discount': discount
                })
            
            # Sort by price (highest price first - closest to current price) and take top 2
            entry_levels.sort(key=lambda x: x['price'], reverse=True)
            top_entries = entry_levels[:2]
            
            return {
                'symbol': symbol,
                'price': current_price,
                'score': score,
                'conditions': conditions,
                'rsi': latest['rsi'],
                'volume_ratio': latest['volume_ratio'],
                'top_entries': top_entries,
                'active_fib_level': active_fib_level,
                'stop_loss': current_price * 0.92,
                'take_profit': current_price * 1.15
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def run_analysis(self):
        """Analyze all stocks and return results."""
        print(f"📊 Analyzing {len(self.stocks)} stocks...")
        
        try:
            # Load 1 year of data for multi-timeframe Fibonacci calculations
            loader = DataLoader()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            all_data = loader.fetch_stock_data(self.stocks, start_date, end_date)
            
            results = []
            for symbol in self.stocks:
                if symbol in all_data:
                    stock_data = all_data[symbol]
                    analysis = self.analyze_stock(symbol, stock_data)
                    if analysis:
                        results.append(analysis)
                        print(f"✓ {symbol}: ${analysis['price']:.2f} ({analysis['score']:.0%})")
                    else:
                        print(f"❌ {symbol}: Analysis failed")
                else:
                    print(f"❌ {symbol}: No data available")
            
            return results
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return []
    
    def generate_summary_notification(self, results):
        """Generate summary notification for all stocks."""
        if not results:
            return "Stock Analysis Failed", "Unable to fetch market data"
        
        # Sort by score (best opportunities first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Count actions
        strong_buys = [r for r in results if r['score'] >= 0.8]
        good_setups = [r for r in results if 0.6 <= r['score'] < 0.8]
        waits = [r for r in results if 0.4 <= r['score'] < 0.6]
        avoids = [r for r in results if r['score'] < 0.4]
        
        # Create title
        if strong_buys:
            title = f"🚀 {len(strong_buys)} STRONG BUY Signals!"
        elif good_setups:
            title = f"⚡ {len(good_setups)} Good Setups Available"
        else:
            title = f"📊 Market Analysis: {len(waits)} Waiting"
        
        # Create message with top opportunities
        message_parts = []
        
        # Show top 3 opportunities
        top_stocks = results[:3]
        for stock in top_stocks:
            action_emoji = "🚀" if stock['score'] >= 0.8 else "⚡" if stock['score'] >= 0.6 else "⏳" if stock['score'] >= 0.4 else "🛑"
            
            stock_info = f"{action_emoji} {stock['symbol']}: ${stock['price']:.2f} ({stock['score']:.0%})"
            
            # Add best entry if available
            if stock['top_entries'] and stock['score'] < 0.6:
                best_entry = stock['top_entries'][0]
                stock_info += f" → ${best_entry['price']:.2f} ({best_entry['discount']:.0f}% off)"
            
            message_parts.append(stock_info)
        
        # Add summary
        if len(results) > 3:
            remaining = len(results) - 3
            message_parts.append(f"+ {remaining} more stocks analyzed")
        
        message = " • ".join(message_parts)
        
        return title, message
    
    def generate_detailed_notification(self, stock):
        """Generate detailed notification for a single stock."""
        action_emoji = "🚀" if stock['score'] >= 0.8 else "⚡" if stock['score'] >= 0.6 else "⏳" if stock['score'] >= 0.4 else "🛑"
        action_text = "STRONG BUY" if stock['score'] >= 0.8 else "GOOD SETUP" if stock['score'] >= 0.6 else "WAIT" if stock['score'] >= 0.4 else "AVOID"
        
        title = f"{action_emoji} {stock['symbol']}: ${stock['price']:.2f} - {action_text}"
        
        # Show which indicators are met
        conditions = stock['conditions']
        indicators = []
        indicators.append(f"🌀Fib: {'✅' if conditions['fibonacci'] else '❌'}")
        indicators.append(f"📈MACD: {'✅' if conditions['macd'] else '❌'}")
        indicators.append(f"📊RSI: {'✅' if conditions['rsi'] else '❌'}")
        indicators.append(f"📊Vol: {'✅' if conditions['volume'] else '❌'}")
        indicators.append(f"📈Trend: {'✅' if conditions['trend'] else '❌'}")
        
        message_parts = [
            f"Score: {stock['score']:.0%} ({sum(conditions.values())}/5)",
            " ".join(indicators)
        ]
        
        # Add top 2 entry points
        if stock['top_entries']:
            entry_text = []
            for i, entry in enumerate(stock['top_entries'][:2], 1):
                entry_text.append(f"Entry {i}: ${entry['price']:.2f} ({entry['discount']:.0f}% off)")
            message_parts.extend(entry_text)
        
        # Add RSI and volume details
        rsi = stock['rsi']
        vol_ratio = stock['volume_ratio']
        details = []
        if rsi > 70:
            details.append(f"RSI: {rsi:.0f} (Overbought)")
        elif rsi < 30:
            details.append(f"RSI: {rsi:.0f} (Oversold)")
        else:
            details.append(f"RSI: {rsi:.0f}")
            
        if vol_ratio > 1.2:
            details.append(f"Volume: {vol_ratio:.1f}x (High)")
        elif vol_ratio < 0.8:
            details.append(f"Volume: {vol_ratio:.1f}x (Low)")
        else:
            details.append(f"Volume: {vol_ratio:.1f}x")
            
        if details:
            message_parts.append(" • ".join(details))
        
        message = " • ".join(message_parts)
        
        return title, message
    
    def send_macos_notification(self, title, message):
        """Send macOS native notification."""
        try:
            # Use osascript to send notification
            script = f'''
            display notification "{message}" with title "{title}" sound name "Glass"
            '''
            
            subprocess.run(['osascript', '-e', script], check=True)
            return True
        except Exception as e:
            print(f"macOS notification failed: {e}")
            return False
    
    def create_summary_table(self, results):
        """Create a formatted table summary of all stock analyses."""
        if not results:
            return "No results available"

        # Sort results by score
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Prepare table data
        table_data = []
        for stock in sorted_results:
            conditions = stock['conditions']
            best_entry = stock['top_entries'][0] if stock['top_entries'] else {'price': None, 'discount': None}
            
            # Create status emojis
            status_emojis = {
                'fibonacci': '✅' if conditions['fibonacci'] else '❌',
                'macd': '✅' if conditions['macd'] else '❌',
                'rsi': '✅' if conditions['rsi'] else '❌',
                'volume': '✅' if conditions['volume'] else '❌',
                'trend': '✅' if conditions['trend'] else '❌'
            }
            
            # Determine recommendation (without emojis)
            if stock['score'] >= 0.8:
                recommendation = "STRONG BUY"
            elif stock['score'] >= 0.6:
                recommendation = "GOOD"
            elif stock['score'] >= 0.4:
                recommendation = "WAIT"
            else:
                recommendation = "AVOID"
            
            # Get the second entry point if available
            second_entry = stock['top_entries'][1] if len(stock['top_entries']) > 1 else {'price': None, 'discount': None}
            
            fib_status = status_emojis['fibonacci']
            macd_status = status_emojis['macd']
            rsi_status = status_emojis['rsi']
            vol_status = status_emojis['volume']
            trend_status = status_emojis['trend']

            row = [
                f"{stock['symbol']}",
                f"${stock['price']:.2f}",
                f"{stock['score']:.0%}",
                recommendation,
                f"${best_entry['price']:.2f}" if best_entry['price'] else "N/A",
                f"${second_entry['price']:.2f}" if second_entry['price'] else "N/A",
                fib_status,
                macd_status,
                rsi_status,
                vol_status,
                trend_status
            ]
            table_data.append(row)
        
        # Define headers
        headers = [
            "Symbol", "Price", "Score", "Signal",
            "Entry1", "Entry2", "Fib", "MACD",
            "RSI", "Vol", "Trend"
        ]
        
        # Generate table with specific alignment and widths
        colalign = ("center", "right", "center", "center", "right", "right", "center", "center", "center", "center", "center")
        
        table = tabulate(
            table_data,
            headers=headers,
            tablefmt="simple",
            colalign=colalign,
            maxcolwidths=[8, 10, 6, 10, 10, 10, 6, 6, 6, 6, 6]
        )
        
        return table

    def send_terminal_notification(self, title, message):
        """Send terminal notification with visual alert."""
        try:
            # Terminal bell
            print('\a')  # Bell sound
            
            # Visual notification in terminal
            print("\n" + "="*100)
            print(f"🔔 {title}")
            print("="*100)
            print(f"📊 {message}")
            print("="*100)
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*100)
            
            return True
        except Exception as e:
            print(f"Terminal notification failed: {e}")
            return False
    
    def log_to_file(self, results):
        """Log analysis results to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n")
                
                for stock in results:
                    f.write(f"{stock['symbol']}: ${stock['price']:.2f} ({stock['score']:.0%})\n")
                    if stock['top_entries']:
                        for i, entry in enumerate(stock['top_entries'][:2], 1):
                            f.write(f"  Entry {i}: ${entry['price']:.2f} ({entry['discount']:.1f}% discount)\n")
                    f.write(f"  RSI: {stock['rsi']:.0f}, Volume: {stock['volume_ratio']:.1f}x\n")
                    f.write("\n")
                
                f.write(f"{'='*60}\n\n")
            return True
        except Exception as e:
            print(f"File logging failed: {e}")
            return False
    
    def send_alerts(self):
        """Run analysis and send alerts."""
        print(f"🚗 Running Multi-Stock Alert System...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Stocks: {', '.join(self.stocks)}")
        
        # Run analysis
        results = self.run_analysis()
        
        if not results:
            print("❌ No stock data available")
            return {'summary': False, 'terminal': False, 'file': False, 'charts': False}
        
        print(f"✓ Successfully analyzed {len(results)} stocks")
        
        # Generate professional charts
        print(f"\n📊 Generating professional technical analysis charts...")
        chart_generator = StockChartGenerator(stocks=self.stocks)
        chart_files = chart_generator.generate_all_charts()
        
        # Generate summary notification
        summary_title, summary_message = self.generate_summary_notification(results)
        
        # Send notifications
        alert_results = {
            'summary': False,
            'terminal': False,
            'file': False,
            'charts': False
        }
        
        # Summary notification
        alert_results['summary'] = self.send_macos_notification(summary_title, summary_message)
        print(f"🍎 Summary Notification: {'✅ Sent' if alert_results['summary'] else '❌ Failed'}")
        
        # Display summary table
        print("\n📊 STOCK ANALYSIS SUMMARY TABLE:")
        summary_table = self.create_summary_table(results)
        print(summary_table)
        print("\n")
        
        # Terminal notification with detailed view
        print("📊 DETAILED ANALYSIS:")
        for stock in sorted(results, key=lambda x: x['score'], reverse=True):
            detail_title, detail_message = self.generate_detailed_notification(stock)
            print(f"  {detail_title}")
            print(f"    {detail_message}")
        
        alert_results['terminal'] = True
        print(f"💻 Terminal Display: ✅ Shown")
        
        # File logging
        alert_results['file'] = self.log_to_file(results)
        print(f"📄 File Log: {'✅ Saved' if alert_results['file'] else '❌ Failed'}")
        
        # Chart generation
        alert_results['charts'] = len(chart_files) > 0
        print(f"📊 Technical Charts: {'✅ Generated' if alert_results['charts'] else '❌ Failed'} ({len(chart_files)} charts)")
        
        if chart_files:
            print(f"📁 Charts saved in: ./charts/ directory")
            print(f"💡 Open PNG files to view detailed technical analysis!")
        
        success_count = sum(alert_results.values())
        print(f"\n✅ Alert system completed: {success_count}/4 methods successful")
        
        return alert_results

def main():
    """Main function to run the multi-stock alert system."""
    alert_system = MultiStockAlerts()
    results = alert_system.send_alerts()
    
    if not any(results.values()):
        print("⚠️  No alerts sent successfully.")
    
    return results

if __name__ == "__main__":
    main()