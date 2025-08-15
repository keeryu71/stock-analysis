#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the advanced Fibonacci MACD Strategy.
"""

import sys
import os
sys.path.append('src')

print("Testing Advanced Fibonacci MACD Strategy")
print("=" * 50)

try:
    # Import required modules
    print("Importing modules...")
    from data.data_loader import DataLoader
    from backtesting.engine import BacktestEngine
    from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy
    from utils.metrics import quick_performance_summary
    from config import config
    
    print("All modules imported successfully!")
    
    # Load data for testing
    print("\nLoading market data...")
    loader = DataLoader()
    
    # Use a longer period for better Fibonacci analysis
    symbols = ['AAPL']
    start_date = '2020-01-01'
    end_date = '2023-12-31'
    
    print(f"Fetching {symbols[0]} data from {start_date} to {end_date}...")
    data = loader.fetch_stock_data(symbols, start_date, end_date)
    
    if symbols[0] in data and not data[symbols[0]].empty:
        stock_data = data[symbols[0]]
        print(f"Data loaded successfully!")
        print(f"Records: {len(stock_data)}")
        print(f"Date range: {stock_data.index[0].strftime('%Y-%m-%d')} to {stock_data.index[-1].strftime('%Y-%m-%d')}")
        print(f"Price range: ${stock_data['close'].min():.2f} - ${stock_data['close'].max():.2f}")
    else:
        print("Failed to load data")
        sys.exit(1)
    
    # Create the advanced strategy
    print("\nCreating Fibonacci MACD Strategy...")
    strategy = FibonacciMACDStrategy(
        fibonacci_period=50,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        rsi_period=14,
        rsi_oversold=30,
        rsi_overbought=70,
        volume_period=20,
        volume_threshold=1.2,
        position_size_pct=0.15,
        min_confidence=0.6
    )
    
    print(f"Strategy created: {strategy.name}")
    print(f"Key parameters:")
    print(f"  Fibonacci Period: {strategy.fibonacci_period}")
    print(f"  MACD: {strategy.macd_fast}/{strategy.macd_slow}/{strategy.macd_signal}")
    print(f"  RSI Period: {strategy.rsi_period}")
    print(f"  Volume Threshold: {strategy.volume_threshold}x")
    print(f"  Min Confidence: {strategy.min_confidence}")
    
    # Run backtest
    print("\nRunning advanced backtest...")
    engine = BacktestEngine(
        initial_capital=config.initial_capital,
        commission=config.commission,
        slippage=config.slippage
    )
    
    print(f"Initial capital: ${config.initial_capital:,.2f}")
    print(f"Commission: {config.commission:.3%}")
    print(f"Slippage: {config.slippage:.3%}")
    
    # Execute backtest
    results = engine.run_backtest(strategy, stock_data)
    
    if results:
        print("\nBacktest completed successfully!")
        
        # Display comprehensive results
        print("\n" + "="*60)
        print("FIBONACCI MACD STRATEGY RESULTS")
        print("="*60)
        
        print(f"\nPERFORMANCE METRICS:")
        print(f"  Final Portfolio Value: ${results['final_value']:,.2f}")
        print(f"  Total Return: {results['total_return']:.2%}")
        print(f"  Annualized Return: {results['annualized_return']:.2%}")
        print(f"  Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"  Maximum Drawdown: {results['max_drawdown']:.2%}")
        print(f"  Volatility: {results['volatility']:.2%}")
        
        print(f"\nTRADING ACTIVITY:")
        print(f"  Total Trades: {results['total_trades']}")
        
        # Analyze trades if any were made
        if 'trades' in results and not results['trades'].empty:
            trades_df = results['trades']
            buy_trades = trades_df[trades_df['action'] == 'BUY']
            sell_trades = trades_df[trades_df['action'] == 'SELL']
            
            print(f"  Buy Orders: {len(buy_trades)}")
            print(f"  Sell Orders: {len(sell_trades)}")
            
            if not buy_trades.empty:
                print(f"  Average Buy Price: ${buy_trades['price'].mean():.2f}")
                print(f"  Average Position Size: {buy_trades['quantity'].mean():.0f} shares")
            
            if not sell_trades.empty:
                print(f"  Average Sell Price: ${sell_trades['price'].mean():.2f}")
            
            print(f"\nFIRST FEW TRADES:")
            print(trades_df.head(10)[['timestamp', 'action', 'quantity', 'price', 'total_cost']].to_string(index=False))
        
        # Calculate buy-and-hold comparison
        print(f"\nBENCHMARK COMPARISON:")
        initial_price = stock_data['close'].iloc[0]
        final_price = stock_data['close'].iloc[-1]
        buy_hold_return = (final_price / initial_price) - 1
        
        print(f"  Buy & Hold Return: {buy_hold_return:.2%}")
        print(f"  Strategy Return: {results['total_return']:.2%}")
        outperformance = results['total_return'] - buy_hold_return
        print(f"  Outperformance: {outperformance:.2%}")
        
        if outperformance > 0:
            print("  🏆 Strategy OUTPERFORMED buy & hold!")
        else:
            print("  📉 Strategy underperformed buy & hold")
        
        # Performance summary
        if 'portfolio_history' in results:
            portfolio_values = results['portfolio_history']['total_value']
            summary = quick_performance_summary(portfolio_values)
            print(f"\nDETAILED PERFORMANCE SUMMARY:")
            print(summary.to_string(index=False))
        
        print(f"\n" + "="*60)
        print("STRATEGY ANALYSIS COMPLETE")
        print("="*60)
        
        print(f"\nKEY INSIGHTS:")
        print(f"  • This strategy combines 5 technical indicators for high-confidence signals")
        print(f"  • Fibonacci levels help identify optimal support/resistance entry points")
        print(f"  • MACD confirms trend direction and momentum")
        print(f"  • RSI prevents buying at overbought levels")
        print(f"  • Volume analysis ensures institutional participation")
        print(f"  • Multi-factor approach reduces false signals")
        
        print(f"\nNEXT STEPS:")
        print(f"  1. Analyze individual trade signals and their metadata")
        print(f"  2. Optimize parameters using the optimization notebook")
        print(f"  3. Test on different stocks and time periods")
        print(f"  4. Consider adding stop-loss and take-profit refinements")
        
    else:
        print("Backtest failed")
        sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed")
    sys.exit(1)

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\nAdvanced strategy test completed successfully! 🚀")