#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify the algorithmic trading framework works correctly.
"""

import sys
import os
sys.path.append('src')

print("Testing Algorithmic Trading Framework")
print("=" * 50)

try:
    # Import our modules
    print("Importing modules...")
    from data.data_loader import DataLoader
    from backtesting.engine import BacktestEngine
    from strategies.moving_average import MovingAverageCrossover
    from utils.metrics import quick_performance_summary
    from config import config
    
    print("All modules imported successfully!")
    
    # Test data loading
    print("\nLoading market data...")
    loader = DataLoader()
    
    # Load a small dataset for quick testing
    symbols = ['AAPL']
    start_date = '2022-01-01'
    end_date = '2023-12-31'
    
    print(f"Fetching {symbols[0]} data from {start_date} to {end_date}...")
    data = loader.fetch_stock_data(symbols, start_date, end_date)
    
    if symbols[0] in data and not data[symbols[0]].empty:
        stock_data = data[symbols[0]]
        print("Data loaded successfully!")
        print(f"Records: {len(stock_data)}")
        print(f"Date range: {stock_data.index[0].strftime('%Y-%m-%d')} to {stock_data.index[-1].strftime('%Y-%m-%d')}")
        print(f"Price range: ${stock_data['close'].min():.2f} - ${stock_data['close'].max():.2f}")
    else:
        print("Failed to load data")
        sys.exit(1)
    
    # Test strategy creation
    print("\nCreating trading strategy...")
    strategy = MovingAverageCrossover(
        short_window=20,
        long_window=50,
        position_size_pct=0.1
    )
    print(f"Strategy created: {strategy.name}")
    print(f"Parameters: {strategy.parameters}")
    
    # Test backtesting engine
    print("\nRunning backtest...")
    engine = BacktestEngine(
        initial_capital=config.initial_capital,
        commission=config.commission,
        slippage=config.slippage
    )
    
    print(f"Initial capital: ${config.initial_capital:,.2f}")
    print(f"Commission: {config.commission:.3%}")
    print(f"Slippage: {config.slippage:.3%}")
    
    # Run the backtest
    results = engine.run_backtest(strategy, stock_data)
    
    if results:
        print("Backtest completed successfully!")
        
        # Display key results
        print("\nBacktest Results:")
        print(f"Final Portfolio Value: ${results['final_value']:,.2f}")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Annualized Return: {results['annualized_return']:.2%}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"Maximum Drawdown: {results['max_drawdown']:.2%}")
        print(f"Volatility: {results['volatility']:.2%}")
        print(f"Total Trades: {results['total_trades']}")
        
        # Test performance metrics
        print("\nTesting performance metrics...")
        if 'portfolio_history' in results:
            portfolio_values = results['portfolio_history']['total_value']
            summary = quick_performance_summary(portfolio_values)
            print("Performance metrics calculated successfully!")
            print("\nPerformance Summary:")
            print(summary.to_string(index=False))
        
        # Calculate buy-and-hold comparison
        print("\nBuy & Hold Comparison:")
        initial_price = stock_data['close'].iloc[0]
        final_price = stock_data['close'].iloc[-1]
        buy_hold_return = (final_price / initial_price) - 1
        
        print(f"Buy & Hold Return: {buy_hold_return:.2%}")
        print(f"Strategy Return: {results['total_return']:.2%}")
        outperformance = results['total_return'] - buy_hold_return
        print(f"Outperformance: {outperformance:.2%}")
        
        if outperformance > 0:
            print("Strategy outperformed buy & hold!")
        else:
            print("Strategy underperformed buy & hold")
        
        print("\nFramework test completed successfully!")
        print("\nNext steps:")
        print("1. Open notebooks/01_strategy_development.ipynb for detailed analysis")
        print("2. Try notebooks/02_strategy_optimization.ipynb for parameter tuning")
        print("3. Modify strategies in src/strategies/ to test new approaches")
        print("4. Check README.md for comprehensive documentation")
        
    else:
        print("Backtest failed")
        sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    print("Install dependencies with: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"Error during testing: {e}")
    print("Check the error details above and ensure all dependencies are installed")
    sys.exit(1)

print("\nAll tests passed! The framework is ready to use.")