#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily TSLA Entry Monitor
Quick daily check for TSLA entry opportunities
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from data.data_loader import DataLoader
from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

def daily_tsla_check():
    """Quick daily TSLA entry check."""
    
    print("🚗 DAILY TSLA ENTRY MONITOR")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
    # Load recent TSLA data
    loader = DataLoader()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')  # 6 months
    
    try:
        data = loader.fetch_stock_data(['TSLA'], start_date, end_date)
        tsla_data = data['TSLA']
        
        if tsla_data.empty:
            print("❌ No TSLA data available")
            return
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Calculate indicators
    strategy = FibonacciMACDStrategy()
    analyzed_data = strategy._calculate_indicators(tsla_data.copy())
    latest = analyzed_data.iloc[-1]
    current_price = latest['close']
    
    # Quick status check
    print(f"💰 Current Price: ${current_price:.2f}")
    
    # Check entry conditions
    conditions = []
    
    # Fibonacci
    fib_near = latest['fib_position'] in ['fib_0.382', 'fib_0.500', 'fib_0.618']
    conditions.append(("🌀 Fibonacci", fib_near))
    
    # MACD
    macd_bullish = latest['macd'] > latest['macd_signal']
    conditions.append(("📊 MACD", macd_bullish))
    
    # RSI
    rsi_ok = 30 < latest['rsi'] < 70
    conditions.append(("📈 RSI", rsi_ok))
    
    # Volume
    volume_ok = latest['volume_ratio'] > 1.0
    conditions.append(("📊 Volume", volume_ok))
    
    # Trend
    trend_up = latest['close'] > latest['sma_20']
    conditions.append(("📈 Trend", trend_up))
    
    # Display conditions
    score = sum([cond[1] for cond in conditions]) / len(conditions)
    
    print(f"\n🎯 ENTRY CONDITIONS:")
    for name, status in conditions:
        print(f"  {name}: {'✅' if status else '❌'}")
    
    print(f"\n📊 Overall Score: {score:.0%} ({sum([cond[1] for cond in conditions])}/{len(conditions)})")
    
    # Recommendation
    if score >= 0.8:
        print(f"🟢 STRONG BUY - Excellent entry opportunity!")
        action = "BUY NOW"
    elif score >= 0.6:
        print(f"🟡 GOOD SETUP - Consider entering")
        action = "CONSIDER BUYING"
    elif score >= 0.4:
        print(f"🟡 WAIT - Look for better setup")
        action = "WAIT"
    else:
        print(f"🔴 AVOID - Poor entry conditions")
        action = "AVOID"
    
    # Key levels
    print(f"\n🎯 KEY LEVELS TO WATCH:")
    
    # Fibonacci levels
    fib_levels = [0.382, 0.5, 0.618]
    for level in fib_levels:
        fib_price = latest[f'fib_{level:.3f}']
        if pd.notna(fib_price):
            distance = ((current_price - fib_price) / current_price) * 100
            if abs(distance) < 5:  # Within 5%
                status = "🎯 WATCH" if fib_price < current_price else "🔴 RESISTANCE"
                print(f"  ${fib_price:.2f} - {level*100:.1f}% Fib ({distance:+.1f}%) {status}")
    
    # Support/Resistance
    sma_20 = latest['sma_20']
    sma_distance = ((current_price - sma_20) / current_price) * 100
    print(f"  ${sma_20:.2f} - SMA 20 ({sma_distance:+.1f}%) {'🟢 SUPPORT' if sma_20 < current_price else '🔴 RESISTANCE'}")
    
    # Risk management
    stop_loss = current_price * 0.92
    take_profit = current_price * 1.15
    
    print(f"\n⚠️ RISK MANAGEMENT:")
    print(f"  🛑 Stop Loss: ${stop_loss:.2f} (-8%)")
    print(f"  🎯 Take Profit: ${take_profit:.2f} (+15%)")
    
    # Quick summary
    print(f"\n📋 QUICK SUMMARY:")
    print(f"  Action: {action}")
    print(f"  Current: ${current_price:.2f}")
    print(f"  RSI: {latest['rsi']:.0f}")
    print(f"  MACD: {'Bullish' if macd_bullish else 'Bearish'}")
    
    return {
        'price': current_price,
        'score': score,
        'action': action,
        'rsi': latest['rsi'],
        'macd_bullish': macd_bullish,
        'conditions': conditions
    }

def create_alert_levels():
    """Create price alert levels for TSLA."""
    
    print(f"\n🔔 SUGGESTED PRICE ALERTS:")
    print("=" * 30)
    
    try:
        # Load data
        loader = DataLoader()
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        data = loader.fetch_stock_data(['TSLA'], start_date, end_date)
        tsla_data = data['TSLA']
        
        strategy = FibonacciMACDStrategy()
        analyzed_data = strategy._calculate_indicators(tsla_data.copy())
        latest = analyzed_data.iloc[-1]
        current_price = latest['close']
        
        # Alert levels
        alerts = []
        
        # Fibonacci levels below current price
        fib_levels = [0.382, 0.5, 0.618, 0.786]
        for level in fib_levels:
            fib_price = latest[f'fib_{level:.3f}']
            if pd.notna(fib_price) and fib_price < current_price:
                discount = ((current_price - fib_price) / current_price) * 100
                alerts.append((fib_price, f"{level*100:.1f}% Fib Support", discount))
        
        # Moving averages
        sma_20 = latest['sma_20']
        if sma_20 < current_price:
            discount = ((current_price - sma_20) / current_price) * 100
            alerts.append((sma_20, "SMA 20 Support", discount))
        
        # Sort by price (highest first - closest to current price)
        alerts.sort(reverse=True)
        
        print(f"Set buy alerts at these levels:")
        for price, description, discount in alerts[:4]:  # Top 4 levels
            print(f"  🔔 ${price:.2f} - {description} ({discount:.1f}% below current)")
        
        # Resistance alerts
        print(f"\nSet sell/resistance alerts:")
        recent_high = analyzed_data['high'].tail(20).max()
        if recent_high > current_price:
            upside = ((recent_high - current_price) / current_price) * 100
            print(f"  🔔 ${recent_high:.2f} - Recent High (+{upside:.1f}%)")
        
        take_profit = current_price * 1.15
        print(f"  🔔 ${take_profit:.2f} - Take Profit Target (+15%)")
        
    except Exception as e:
        print(f"❌ Could not create alerts: {e}")

if __name__ == "__main__":
    try:
        # Run daily check
        result = daily_tsla_check()
        
        # Create alert levels
        create_alert_levels()
        
        print(f"\n" + "="*40)
        print(f"✅ Daily TSLA monitor completed!")
        print(f"💡 Run this script daily to track entry opportunities")
        print(f"📱 Set price alerts based on the suggested levels")
        print(f"⚠️  Always combine with fundamental analysis")
        
    except Exception as e:
        print(f"❌ Error in daily monitor: {e}")
        import traceback
        traceback.print_exc()