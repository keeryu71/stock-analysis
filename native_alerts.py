#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Native macOS Alert System for TSLA Analysis
Uses built-in macOS notifications - no external services required
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import subprocess
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from data.data_loader import DataLoader
from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

class NativeTSLAAlerts:
    """Native macOS alert system using built-in notifications."""
    
    def __init__(self):
        self.log_file = 'tsla_alerts.log'
        
    def run_analysis(self):
        """Run TSLA analysis and return results."""
        try:
            # Load TSLA data
            loader = DataLoader()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            data = loader.fetch_stock_data(['TSLA'], start_date, end_date)
            tsla_data = data['TSLA']
            
            if tsla_data.empty:
                return None
            
            # Calculate indicators
            strategy = FibonacciMACDStrategy()
            analyzed_data = strategy._calculate_indicators(tsla_data.copy())
            latest = analyzed_data.iloc[-1]
            current_price = latest['close']
            
            # Evaluate conditions
            conditions = {
                'fibonacci': latest['fib_position'] in ['fib_0.382', 'fib_0.500', 'fib_0.618'],
                'macd': latest['macd'] > latest['macd_signal'],
                'rsi': 30 < latest['rsi'] < 70,
                'volume': latest['volume_ratio'] > 1.0,
                'trend': latest['close'] > latest['sma_20']
            }
            
            score = sum(conditions.values()) / len(conditions)
            
            # Get key levels
            fib_levels = {}
            for level in [0.382, 0.5, 0.618]:
                fib_price = latest[f'fib_{level:.3f}']
                if pd.notna(fib_price):
                    fib_levels[f'{level*100:.1f}%'] = fib_price
            
            return {
                'timestamp': datetime.now(),
                'price': current_price,
                'score': score,
                'conditions': conditions,
                'rsi': latest['rsi'],
                'macd_bullish': latest['macd'] > latest['macd_signal'],
                'volume_ratio': latest['volume_ratio'],
                'fib_levels': fib_levels,
                'sma_20': latest['sma_20'],
                'stop_loss': current_price * 0.92,
                'take_profit': current_price * 1.15
            }
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return None
    
    def generate_notification_message(self, analysis):
        """Generate notification message."""
        if not analysis:
            return "TSLA Analysis Failed", "Unable to fetch data"
        
        price = analysis['price']
        score = analysis['score']
        conditions = analysis['conditions']
        
        # Determine action
        if score >= 0.8:
            action = "STRONG BUY 🚀"
        elif score >= 0.6:
            action = "GOOD SETUP ⚡"
        elif score >= 0.4:
            action = "WAIT ⏳"
        else:
            action = "AVOID 🛑"
        
        # Create title and message
        title = f"TSLA Alert: ${price:.2f} - {action}"
        
        message_parts = [
            f"Entry Score: {score:.0%} ({sum(conditions.values())}/5 signals)",
        ]
        
        # Add best entry level if waiting
        if score < 0.6 and analysis['fib_levels']:
            best_level = min(analysis['fib_levels'].values())
            discount = ((price - best_level) / price) * 100
            message_parts.append(f"Best Entry: ${best_level:.2f} ({discount:.0f}% discount)")
        
        # Add RSI status
        rsi = analysis['rsi']
        if rsi > 70:
            message_parts.append(f"RSI: {rsi:.0f} (Overbought)")
        elif rsi < 30:
            message_parts.append(f"RSI: {rsi:.0f} (Oversold)")
        else:
            message_parts.append(f"RSI: {rsi:.0f} (Neutral)")
        
        # Add volume status
        vol_ratio = analysis['volume_ratio']
        if vol_ratio > 1.2:
            message_parts.append(f"Volume: {vol_ratio:.1f}x (High)")
        elif vol_ratio < 0.8:
            message_parts.append(f"Volume: {vol_ratio:.1f}x (Low)")
        
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
    
    def send_terminal_notification(self, title, message):
        """Send terminal bell notification with visual alert."""
        try:
            # Terminal bell
            print('\a')  # Bell sound
            
            # Visual notification in terminal
            print("\n" + "="*60)
            print(f"🔔 {title}")
            print("="*60)
            print(f"📊 {message}")
            print("="*60)
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60 + "\n")
            
            return True
        except Exception as e:
            print(f"Terminal notification failed: {e}")
            return False
    
    def log_to_file(self, title, message):
        """Log alert to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*50}\n")
                f.write(f"TITLE: {title}\n")
                f.write(f"MESSAGE: {message}\n")
                f.write(f"{'='*50}\n\n")
            return True
        except Exception as e:
            print(f"File logging failed: {e}")
            return False
    
    def send_alerts(self):
        """Run analysis and send native alerts."""
        print(f"🚗 Running TSLA Native Alert System...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run analysis
        analysis = self.run_analysis()
        
        if analysis:
            print(f"✓ Loaded TSLA data successfully")
        else:
            print("❌ Failed to load TSLA data")
            return {'macos': False, 'terminal': False, 'file': False}
        
        title, message = self.generate_notification_message(analysis)
        
        # Send via all methods
        results = {
            'macos': False,
            'terminal': False,
            'file': False
        }
        
        # macOS notification
        results['macos'] = self.send_macos_notification(title, message)
        print(f"🍎 macOS Notification: {'✅ Sent' if results['macos'] else '❌ Failed'}")
        
        # Terminal notification (always works)
        results['terminal'] = self.send_terminal_notification(title, message)
        print(f"💻 Terminal Alert: {'✅ Sent' if results['terminal'] else '❌ Failed'}")
        
        # File logging
        results['file'] = self.log_to_file(title, message)
        print(f"📄 File Log: {'✅ Saved' if results['file'] else '❌ Failed'}")
        
        success_count = sum(results.values())
        print(f"\n✅ Alert system completed: {success_count}/3 methods successful")
        
        return results

def main():
    """Main function to run the native alert system."""
    alert_system = NativeTSLAAlerts()
    results = alert_system.send_alerts()
    
    if not any(results.values()):
        print("⚠️  No alerts sent successfully.")
    
    return results

if __name__ == "__main__":
    main()