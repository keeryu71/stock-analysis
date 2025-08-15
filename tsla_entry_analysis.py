#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSLA Entry Price Analysis Tool
Identifies optimal entry prices for TSLA using Fibonacci MACD strategy
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from data.data_loader import DataLoader
from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

def analyze_tsla_entry_opportunities():
    """Analyze current TSLA data to find optimal entry prices."""
    
    print("🚗 TESLA (TSLA) ENTRY PRICE ANALYSIS")
    print("=" * 50)
    
    # Load recent TSLA data (extended period for better analysis)
    loader = DataLoader()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year of data
    
    print(f"📊 Loading TSLA data from {start_date} to {end_date}...")
    
    try:
        data = loader.fetch_stock_data(['TSLA'], start_date, end_date)
        tsla_data = data['TSLA']
        
        if tsla_data.empty:
            print("❌ No TSLA data available")
            return
            
        print(f"✅ Loaded {len(tsla_data)} trading days of TSLA data")
        print(f"📈 Current Price: ${tsla_data['close'].iloc[-1]:.2f}")
        print(f"📊 52-Week Range: ${tsla_data['close'].min():.2f} - ${tsla_data['close'].max():.2f}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Create strategy instance
    strategy = FibonacciMACDStrategy(
        fibonacci_period=50,
        macd_fast=12, macd_slow=26, macd_signal=9,
        rsi_period=14, rsi_oversold=30, rsi_overbought=70,
        volume_threshold=1.2,
        min_confidence=0.6
    )
    
    # Calculate all indicators
    print(f"\n🔍 Calculating technical indicators...")
    analyzed_data = strategy._calculate_indicators(tsla_data.copy())
    
    # Get the most recent data point
    latest = analyzed_data.iloc[-1]
    current_price = latest['close']
    
    print(f"\n📊 CURRENT TECHNICAL ANALYSIS:")
    print(f"=" * 40)
    
    # Current indicator values
    print(f"💰 Current Price: ${current_price:.2f}")
    print(f"📈 RSI (14): {latest['rsi']:.1f}")
    print(f"📊 MACD: {latest['macd']:.3f}")
    print(f"📊 MACD Signal: {latest['macd_signal']:.3f}")
    print(f"📊 MACD Histogram: {latest['macd_histogram']:.3f}")
    print(f"📊 Volume Ratio: {latest['volume_ratio']:.2f}x")
    
    # Fibonacci levels
    print(f"\n🌀 FIBONACCI RETRACEMENT LEVELS:")
    print(f"=" * 40)
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    
    for level in fib_levels:
        fib_price = latest[f'fib_{level:.3f}']
        if pd.notna(fib_price):
            distance = ((current_price - fib_price) / fib_price) * 100
            status = "🎯 NEAR" if abs(distance) < 2 else "⬆️ ABOVE" if distance > 0 else "⬇️ BELOW"
            print(f"  {level*100:5.1f}% Level: ${fib_price:7.2f} ({distance:+5.1f}%) {status}")
    
    # Analyze entry conditions
    print(f"\n🎯 ENTRY CONDITION ANALYSIS:")
    print(f"=" * 40)
    
    # Check each condition
    conditions = {}
    
    # 1. Fibonacci condition
    fib_condition = latest['fib_position'] in ['fib_0.382', 'fib_0.500', 'fib_0.618']
    conditions['Fibonacci Support'] = fib_condition
    print(f"🌀 Fibonacci Support: {'✅ YES' if fib_condition else '❌ NO'} (Near {latest['fib_position']})")
    
    # 2. MACD condition
    macd_bullish = latest['macd'] > latest['macd_signal'] and latest['macd_histogram'] > 0
    conditions['MACD Bullish'] = macd_bullish
    print(f"📊 MACD Bullish: {'✅ YES' if macd_bullish else '❌ NO'}")
    
    # 3. RSI condition
    rsi_favorable = 30 < latest['rsi'] < 70
    conditions['RSI Favorable'] = rsi_favorable
    rsi_status = "Oversold" if latest['rsi'] < 30 else "Overbought" if latest['rsi'] > 70 else "Neutral"
    print(f"📈 RSI Favorable: {'✅ YES' if rsi_favorable else '❌ NO'} ({rsi_status})")
    
    # 4. Volume condition
    volume_good = latest['volume_ratio'] > 1.2
    conditions['Volume Confirmation'] = volume_good
    print(f"📊 Volume Confirmation: {'✅ YES' if volume_good else '❌ NO'} ({latest['volume_ratio']:.1f}x avg)")
    
    # 5. Trend condition
    trend_up = latest['close'] > latest['sma_20']
    conditions['Trend Favorable'] = trend_up
    print(f"📈 Trend Favorable: {'✅ YES' if trend_up else '❌ NO'} (Price vs SMA20)")
    
    # Calculate overall score
    score = sum(conditions.values()) / len(conditions)
    
    print(f"\n🎯 OVERALL ENTRY SCORE: {score:.1%} ({sum(conditions.values())}/{len(conditions)} conditions met)")
    
    # Entry recommendation
    print(f"\n💡 ENTRY RECOMMENDATIONS:")
    print(f"=" * 40)
    
    if score >= 0.6:
        print(f"🟢 STRONG BUY SIGNAL - Consider entering at current levels")
        print(f"🎯 Target Entry: ${current_price:.2f} (current price)")
    elif score >= 0.4:
        print(f"🟡 MODERATE SIGNAL - Wait for better setup")
        # Suggest better entry levels
        suggest_entry_levels(analyzed_data, current_price)
    else:
        print(f"🔴 WEAK SIGNAL - Avoid entry, wait for better conditions")
        suggest_entry_levels(analyzed_data, current_price)
    
    # Risk management
    print(f"\n⚠️ RISK MANAGEMENT:")
    print(f"=" * 40)
    stop_loss = current_price * 0.92  # 8% stop loss
    take_profit = current_price * 1.15  # 15% take profit
    print(f"🛑 Stop Loss: ${stop_loss:.2f} (-8%)")
    print(f"🎯 Take Profit: ${take_profit:.2f} (+15%)")
    print(f"💰 Risk/Reward Ratio: 1:1.88")
    
    # Future price targets based on Fibonacci
    print(f"\n🔮 POTENTIAL PRICE TARGETS:")
    print(f"=" * 40)
    
    # Calculate potential targets
    recent_high = analyzed_data['high'].tail(20).max()
    recent_low = analyzed_data['low'].tail(20).min()
    
    print(f"📈 Recent 20-day High: ${recent_high:.2f}")
    print(f"📉 Recent 20-day Low: ${recent_low:.2f}")
    
    # Fibonacci extension levels (potential targets)
    fib_range = recent_high - recent_low
    extensions = [1.272, 1.414, 1.618]
    
    print(f"\n🎯 Fibonacci Extension Targets (if trend continues):")
    for ext in extensions:
        target = recent_high + (fib_range * (ext - 1))
        upside = ((target - current_price) / current_price) * 100
        print(f"  {ext:.3f} Extension: ${target:.2f} (+{upside:.1f}%)")
    
    # Create visualization
    create_tsla_chart(analyzed_data, current_price)
    
    print(f"\n📅 NEXT FEW DAYS STRATEGY:")
    print(f"=" * 40)
    print(f"1. Monitor for Fibonacci level bounces (especially 38.2%, 50%, 61.8%)")
    print(f"2. Wait for MACD bullish crossover if not already present")
    print(f"3. Ensure RSI is not overbought (>70)")
    print(f"4. Look for volume confirmation (>1.2x average)")
    print(f"5. Set alerts at key Fibonacci levels")
    
    return analyzed_data, conditions, score

def suggest_entry_levels(data, current_price):
    """Suggest better entry levels based on technical analysis."""
    latest = data.iloc[-1]
    
    print(f"\n🎯 SUGGESTED ENTRY LEVELS:")
    
    # Fibonacci levels as potential entries
    fib_levels = [0.382, 0.5, 0.618]
    entry_suggestions = []
    
    for level in fib_levels:
        fib_price = latest[f'fib_{level:.3f}']
        if pd.notna(fib_price) and fib_price < current_price:
            discount = ((current_price - fib_price) / current_price) * 100
            entry_suggestions.append((fib_price, f"{level*100:.1f}% Fib Level", discount))
    
    # Support levels
    sma_20 = latest['sma_20']
    if sma_20 < current_price:
        discount = ((current_price - sma_20) / current_price) * 100
        entry_suggestions.append((sma_20, "SMA 20 Support", discount))
    
    # Sort by price (highest first)
    entry_suggestions.sort(reverse=True)
    
    if entry_suggestions:
        print(f"Consider waiting for pullbacks to these levels:")
        for price, level_name, discount in entry_suggestions[:3]:  # Top 3 suggestions
            print(f"  💰 ${price:.2f} - {level_name} ({discount:.1f}% discount)")
    else:
        print(f"  Current price appears to be at or near support levels")

def create_tsla_chart(data, current_price):
    """Create a visualization of TSLA with technical indicators."""
    try:
        # Create the chart
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
        
        # Recent data (last 60 days for clarity)
        recent_data = data.tail(60)
        dates = recent_data.index
        
        # Price chart with Fibonacci levels
        ax1.plot(dates, recent_data['close'], linewidth=2, label='TSLA Price', color='black')
        ax1.plot(dates, recent_data['sma_20'], alpha=0.7, label='SMA 20', color='blue')
        ax1.plot(dates, recent_data['sma_50'], alpha=0.7, label='SMA 50', color='orange')
        
        # Plot Fibonacci levels
        fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        colors = ['lightblue', 'lightgreen', 'yellow', 'orange', 'lightcoral']
        
        for level, color in zip(fib_levels, colors):
            fib_prices = recent_data[f'fib_{level:.3f}']
            ax1.plot(dates, fib_prices, '--', alpha=0.6, color=color, 
                    label=f'Fib {level*100:.1f}%')
        
        # Mark current price
        ax1.axhline(y=current_price, color='red', linestyle='-', linewidth=2, 
                   label=f'Current: ${current_price:.2f}')
        
        ax1.set_title('TSLA Price with Fibonacci Levels')
        ax1.set_ylabel('Price ($)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # MACD
        ax2.plot(dates, recent_data['macd'], label='MACD', color='blue')
        ax2.plot(dates, recent_data['macd_signal'], label='Signal', color='red')
        ax2.bar(dates, recent_data['macd_histogram'], alpha=0.3, label='Histogram')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('MACD')
        ax2.set_ylabel('MACD')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # RSI
        ax3.plot(dates, recent_data['rsi'], label='RSI', color='purple')
        ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought')
        ax3.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold')
        ax3.axhline(y=50, color='gray', linestyle='-', alpha=0.3)
        ax3.set_title('RSI (14)')
        ax3.set_ylabel('RSI')
        ax3.set_xlabel('Date')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig('tsla_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\n📊 Chart saved as 'tsla_analysis.png'")
        plt.show()
        
    except Exception as e:
        print(f"⚠️ Could not create chart: {e}")

if __name__ == "__main__":
    try:
        analyzed_data, conditions, score = analyze_tsla_entry_opportunities()
        
        print(f"\n" + "="*50)
        print(f"📋 SUMMARY FOR TSLA ENTRY ANALYSIS")
        print(f"="*50)
        print(f"📊 Overall Entry Score: {score:.1%}")
        print(f"✅ Conditions Met: {sum(conditions.values())}/{len(conditions)}")
        
        if score >= 0.6:
            print(f"🟢 RECOMMENDATION: STRONG BUY - Consider entering now")
        elif score >= 0.4:
            print(f"🟡 RECOMMENDATION: WAIT - Look for better setup")
        else:
            print(f"🔴 RECOMMENDATION: AVOID - Wait for better conditions")
            
        print(f"\n💡 This analysis is based on technical indicators only.")
        print(f"⚠️  Always consider fundamental analysis and risk management.")
        print(f"📈 Markets can be unpredictable - never risk more than you can afford to lose.")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()