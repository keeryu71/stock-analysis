#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated Stock and Options Analysis
Combines stock analysis with cash-secured put opportunities
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from multi_stock_alerts import MultiStockAlerts
from cash_secured_puts_analyzer import CashSecuredPutAnalyzer
from real_time_options_analyzer import RealTimeOptionsAnalyzer

def main():
    """Run integrated analysis for stocks and put options."""
    print("🚀 INTEGRATED STOCK & OPTIONS ANALYSIS")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. Run stock analysis first
    print("\n📊 PHASE 1: STOCK ANALYSIS")
    print("-" * 40)
    stock_analyzer = MultiStockAlerts()
    stock_results = stock_analyzer.send_alerts()
    
    # 2. Run theoretical put options analysis
    print("\n🎯 PHASE 2: THEORETICAL PUT ANALYSIS (Greeks-Based)")
    print("-" * 40)
    put_analyzer = CashSecuredPutAnalyzer()
    put_analyzer.generate_put_analysis_report()
    
    # 3. Run real-time options analysis
    print("\n💰 PHASE 3: REAL-TIME OPTIONS ANALYSIS")
    print("-" * 40)
    real_time_analyzer = RealTimeOptionsAnalyzer()
    real_time_analyzer.generate_real_time_report()
    
    print("\n" + "="*60)
    print("✅ INTEGRATED ANALYSIS COMPLETE")
    print("="*60)
    print("📊 Stock charts saved in: ./charts/ directory")
    print("📄 Stock alerts logged in: multi_stock_alerts.log")
    print("🎯 Theoretical analysis: Greeks-based optimization")
    print("💰 Real-time analysis: Live market option prices")
    print("💡 Compare both analyses for optimal put selling decisions!")
    
    return stock_results

if __name__ == "__main__":
    main()