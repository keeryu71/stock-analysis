"""
Backtesting engine for algorithmic trading strategies.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from src.backtesting.strategy_base import StrategyBase, Signal, SignalType
from src.config import config

class BacktestEngine:
    """
    Main backtesting engine for running strategy simulations.
    """
    
    def __init__(
        self,
        initial_capital: float = None,
        commission: float = None,
        slippage: float = None
    ):
        self.initial_capital = initial_capital or config.initial_capital
        self.commission = commission or config.commission
        self.slippage = slippage or config.slippage
        
        # Results storage
        self.results = {}
        self.benchmark_data = None
        
    def run_backtest(
        self,
        strategy: StrategyBase,
        data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        benchmark_symbol: str = 'SPY'
    ) -> Dict[str, Any]:
        """
        Run backtest for a single strategy.
        
        Args:
            strategy: Strategy instance to test
            data: Market data DataFrame
            start_date: Start date for backtest
            end_date: End date for backtest
            benchmark_symbol: Benchmark symbol for comparison
            
        Returns:
            Dictionary containing backtest results
        """
        print(f"Running backtest for strategy: {strategy.name}")
        
        # Filter data by date range if specified
        if start_date or end_date:
            data = self._filter_data_by_date(data, start_date, end_date)
        
        if data.empty:
            raise ValueError("No data available for the specified date range")
        
        # Initialize strategy
        strategy.initialize(data, self.initial_capital)
        
        # Get unique dates for iteration
        dates = sorted(data.index.unique()) if hasattr(data.index, 'unique') else sorted(data['date'].unique())
        
        print(f"Backtesting from {dates[0]} to {dates[-1]} ({len(dates)} periods)")
        
        # Run backtest day by day
        for i, current_date in enumerate(dates):
            # Get data up to current date for signal generation
            historical_data = data[data.index <= current_date] if hasattr(data.index, 'unique') else data[data['date'] <= current_date]
            
            # Get current prices for portfolio valuation
            current_data = data[data.index == current_date] if hasattr(data.index, 'unique') else data[data['date'] == current_date]
            current_prices = {}
            
            if not current_data.empty:
                if 'symbol' in current_data.columns:
                    for _, row in current_data.iterrows():
                        current_prices[row['symbol']] = row['close']
                else:
                    # Single asset case
                    current_prices['asset'] = current_data['close'].iloc[0]
            
            # Generate signals
            try:
                signals = strategy.generate_signals(historical_data)
                
                # Execute signals
                for signal in signals:
                    if signal.timestamp == current_date:
                        # Apply slippage to signal price
                        adjusted_price = self._apply_slippage(signal.price, signal.signal_type)
                        signal.price = adjusted_price
                        
                        # Execute the signal
                        strategy.execute_signal(signal, self.commission)
                
            except Exception as e:
                print(f"Warning: Error generating signals for {current_date}: {e}")
                continue
            
            # Record portfolio state
            strategy.record_portfolio_state(current_date, current_prices)
            
            # Progress update
            if i % max(1, len(dates) // 10) == 0:
                progress = (i / len(dates)) * 100
                print(f"Progress: {progress:.1f}% - Portfolio Value: ${strategy.portfolio_value:,.2f}")
        
        # Calculate performance metrics
        results = self._calculate_performance_metrics(strategy, data, benchmark_symbol)
        
        # Store results
        self.results[strategy.name] = results
        
        print(f"✓ Backtest completed for {strategy.name}")
        print(f"  Final Portfolio Value: ${results['final_value']:,.2f}")
        print(f"  Total Return: {results['total_return']:.2%}")
        print(f"  Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"  Max Drawdown: {results['max_drawdown']:.2%}")
        
        return results
    
    def run_multiple_backtests(
        self,
        strategies: List[StrategyBase],
        data: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        benchmark_symbol: str = 'SPY'
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run backtests for multiple strategies.
        
        Args:
            strategies: List of strategy instances
            data: Market data DataFrame
            start_date: Start date for backtest
            end_date: End date for backtest
            benchmark_symbol: Benchmark symbol for comparison
            
        Returns:
            Dictionary with strategy names as keys and results as values
        """
        results = {}
        
        for strategy in strategies:
            try:
                # Reset strategy before each run
                strategy.reset()
                result = self.run_backtest(strategy, data, start_date, end_date, benchmark_symbol)
                results[strategy.name] = result
            except Exception as e:
                print(f"Error running backtest for {strategy.name}: {e}")
                results[strategy.name] = None
        
        return results
    
    def _filter_data_by_date(
        self, 
        data: pd.DataFrame, 
        start_date: Optional[str], 
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """Filter data by date range."""
        filtered_data = data.copy()
        
        if hasattr(data.index, 'unique'):
            # Data has datetime index
            if start_date:
                filtered_data = filtered_data[filtered_data.index >= start_date]
            if end_date:
                filtered_data = filtered_data[filtered_data.index <= end_date]
        else:
            # Data has date column
            if 'date' in data.columns:
                if start_date:
                    filtered_data = filtered_data[filtered_data['date'] >= start_date]
                if end_date:
                    filtered_data = filtered_data[filtered_data['date'] <= end_date]
        
        return filtered_data
    
    def _apply_slippage(self, price: float, signal_type: SignalType) -> float:
        """Apply slippage to trade price."""
        if signal_type == SignalType.BUY:
            return price * (1 + self.slippage)
        elif signal_type == SignalType.SELL:
            return price * (1 - self.slippage)
        return price
    
    def _calculate_performance_metrics(
        self, 
        strategy: StrategyBase, 
        data: pd.DataFrame,
        benchmark_symbol: str
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        portfolio_df = strategy.get_portfolio_history_df()
        trades_df = strategy.get_trades_df()
        
        if portfolio_df.empty:
            return {'error': 'No portfolio history available'}
        
        # Basic metrics
        initial_value = self.initial_capital
        final_value = portfolio_df['total_value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        
        # Calculate returns series
        portfolio_df['returns'] = portfolio_df['total_value'].pct_change().fillna(0)
        
        # Risk metrics
        returns_series = portfolio_df['returns']
        sharpe_ratio = self._calculate_sharpe_ratio(returns_series)
        max_drawdown = self._calculate_max_drawdown(portfolio_df['total_value'])
        volatility = returns_series.std() * np.sqrt(252)  # Annualized
        
        # Trade statistics
        trade_stats = self._calculate_trade_statistics(trades_df)
        
        # Benchmark comparison
        benchmark_metrics = self._calculate_benchmark_metrics(
            portfolio_df, data, benchmark_symbol
        )
        
        return {
            'strategy_name': strategy.name,
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': (1 + total_return) ** (252 / len(portfolio_df)) - 1,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'total_trades': len(trades_df) if not trades_df.empty else 0,
            'portfolio_history': portfolio_df,
            'trades': trades_df,
            'trade_statistics': trade_stats,
            'benchmark_metrics': benchmark_metrics
        }
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio."""
        if returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (config.risk_free_rate / 252)  # Daily risk-free rate
        return (excess_returns.mean() / returns.std()) * np.sqrt(252)
    
    def _calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min()
    
    def _calculate_trade_statistics(self, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trade-level statistics."""
        if trades_df.empty:
            return {}
        
        # Separate buy and sell trades
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        # Calculate P&L for completed trades
        completed_trades = []
        positions = {}
        
        for _, trade in trades_df.iterrows():
            symbol = trade['symbol']
            
            if trade['action'] == 'BUY':
                if symbol not in positions:
                    positions[symbol] = []
                positions[symbol].append({
                    'quantity': trade['quantity'],
                    'price': trade['price'],
                    'timestamp': trade['timestamp']
                })
            
            elif trade['action'] == 'SELL' and symbol in positions:
                remaining_quantity = trade['quantity']
                
                while remaining_quantity > 0 and positions[symbol]:
                    buy_trade = positions[symbol][0]
                    
                    if buy_trade['quantity'] <= remaining_quantity:
                        # Complete the buy trade
                        pnl = (trade['price'] - buy_trade['price']) * buy_trade['quantity']
                        completed_trades.append({
                            'symbol': symbol,
                            'pnl': pnl,
                            'return_pct': (trade['price'] - buy_trade['price']) / buy_trade['price'],
                            'holding_period': (trade['timestamp'] - buy_trade['timestamp']).days
                        })
                        
                        remaining_quantity -= buy_trade['quantity']
                        positions[symbol].pop(0)
                    else:
                        # Partial fill
                        pnl = (trade['price'] - buy_trade['price']) * remaining_quantity
                        completed_trades.append({
                            'symbol': symbol,
                            'pnl': pnl,
                            'return_pct': (trade['price'] - buy_trade['price']) / buy_trade['price'],
                            'holding_period': (trade['timestamp'] - buy_trade['timestamp']).days
                        })
                        
                        buy_trade['quantity'] -= remaining_quantity
                        remaining_quantity = 0
        
        if not completed_trades:
            return {'total_trades': len(trades_df)}
        
        completed_df = pd.DataFrame(completed_trades)
        
        winning_trades = completed_df[completed_df['pnl'] > 0]
        losing_trades = completed_df[completed_df['pnl'] < 0]
        
        return {
            'total_trades': len(trades_df),
            'completed_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(completed_trades) if completed_trades else 0,
            'avg_win': winning_trades['pnl'].mean() if not winning_trades.empty else 0,
            'avg_loss': losing_trades['pnl'].mean() if not losing_trades.empty else 0,
            'profit_factor': abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if not losing_trades.empty and losing_trades['pnl'].sum() != 0 else float('inf'),
            'avg_holding_period': completed_df['holding_period'].mean(),
            'total_pnl': completed_df['pnl'].sum()
        }
    
    def _calculate_benchmark_metrics(
        self, 
        portfolio_df: pd.DataFrame, 
        data: pd.DataFrame, 
        benchmark_symbol: str
    ) -> Dict[str, Any]:
        """Calculate benchmark comparison metrics."""
        try:
            # Get benchmark data
            if 'symbol' in data.columns:
                benchmark_data = data[data['symbol'] == benchmark_symbol]
            else:
                # Assume single asset data is the benchmark
                benchmark_data = data
            
            if benchmark_data.empty:
                return {'error': f'No benchmark data found for {benchmark_symbol}'}
            
            # Align dates
            portfolio_dates = portfolio_df['timestamp']
            benchmark_aligned = []
            
            for date in portfolio_dates:
                if hasattr(benchmark_data.index, 'unique'):
                    benchmark_price = benchmark_data[benchmark_data.index <= date]['close'].iloc[-1] if not benchmark_data[benchmark_data.index <= date].empty else None
                else:
                    benchmark_price = benchmark_data[benchmark_data['date'] <= date]['close'].iloc[-1] if not benchmark_data[benchmark_data['date'] <= date].empty else None
                
                benchmark_aligned.append(benchmark_price)
            
            if not benchmark_aligned or all(p is None for p in benchmark_aligned):
                return {'error': 'Could not align benchmark data'}
            
            # Calculate benchmark returns
            benchmark_prices = pd.Series(benchmark_aligned, index=portfolio_dates)
            benchmark_returns = benchmark_prices.pct_change().fillna(0)
            
            # Calculate metrics
            benchmark_total_return = (benchmark_prices.iloc[-1] - benchmark_prices.iloc[0]) / benchmark_prices.iloc[0]
            
            # Beta calculation
            portfolio_returns = portfolio_df['returns']
            covariance = portfolio_returns.cov(benchmark_returns)
            benchmark_variance = benchmark_returns.var()
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
            
            # Alpha calculation
            portfolio_total_return = (portfolio_df['total_value'].iloc[-1] - portfolio_df['total_value'].iloc[0]) / portfolio_df['total_value'].iloc[0]
            alpha = portfolio_total_return - (config.risk_free_rate + beta * (benchmark_total_return - config.risk_free_rate))
            
            return {
                'benchmark_symbol': benchmark_symbol,
                'benchmark_return': benchmark_total_return,
                'alpha': alpha,
                'beta': beta,
                'correlation': portfolio_returns.corr(benchmark_returns)
            }
            
        except Exception as e:
            return {'error': f'Error calculating benchmark metrics: {str(e)}'}
    
    def get_results_summary(self) -> pd.DataFrame:
        """Get summary of all backtest results."""
        if not self.results:
            return pd.DataFrame()
        
        summary_data = []
        for strategy_name, results in self.results.items():
            if results and 'error' not in results:
                summary_data.append({
                    'Strategy': strategy_name,
                    'Total Return': f"{results['total_return']:.2%}",
                    'Annualized Return': f"{results['annualized_return']:.2%}",
                    'Sharpe Ratio': f"{results['sharpe_ratio']:.3f}",
                    'Max Drawdown': f"{results['max_drawdown']:.2%}",
                    'Volatility': f"{results['volatility']:.2%}",
                    'Total Trades': results['total_trades'],
                    'Final Value': f"${results['final_value']:,.2f}"
                })
        
        return pd.DataFrame(summary_data)