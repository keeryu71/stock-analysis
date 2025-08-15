"""
Performance metrics and risk analysis utilities.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class PerformanceAnalyzer:
    """
    Comprehensive performance analysis for trading strategies.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.daily_rf_rate = risk_free_rate / 252
    
    def calculate_returns_metrics(self, portfolio_values: pd.Series) -> Dict[str, float]:
        """
        Calculate comprehensive return metrics.
        
        Args:
            portfolio_values: Series of portfolio values over time
            
        Returns:
            Dictionary of return metrics
        """
        if len(portfolio_values) < 2:
            return {}
        
        # Calculate returns
        returns = portfolio_values.pct_change().dropna()
        
        # Basic return metrics
        total_return = (portfolio_values.iloc[-1] - portfolio_values.iloc[0]) / portfolio_values.iloc[0]
        
        # Annualized metrics
        periods = len(portfolio_values)
        years = periods / 252  # Assuming daily data
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Volatility
        volatility = returns.std() * np.sqrt(252)
        
        # Downside deviation (volatility of negative returns)
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'downside_deviation': downside_deviation,
            'avg_daily_return': returns.mean(),
            'median_daily_return': returns.median(),
            'std_daily_return': returns.std(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
    
    def calculate_risk_metrics(self, portfolio_values: pd.Series) -> Dict[str, float]:
        """
        Calculate risk-adjusted performance metrics.
        
        Args:
            portfolio_values: Series of portfolio values over time
            
        Returns:
            Dictionary of risk metrics
        """
        if len(portfolio_values) < 2:
            return {}
        
        returns = portfolio_values.pct_change().dropna()
        
        # Sharpe Ratio
        excess_returns = returns - self.daily_rf_rate
        sharpe_ratio = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Sortino Ratio (using downside deviation)
        negative_returns = returns[returns < self.daily_rf_rate]
        downside_std = negative_returns.std() if len(negative_returns) > 0 else 0
        sortino_ratio = (excess_returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        # Calmar Ratio (annualized return / max drawdown)
        max_dd = self.calculate_max_drawdown(portfolio_values)
        annualized_return = self.calculate_returns_metrics(portfolio_values)['annualized_return']
        calmar_ratio = annualized_return / abs(max_dd) if max_dd != 0 else 0
        
        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Conditional Value at Risk (CVaR) - Expected Shortfall
        cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else 0
        cvar_99 = returns[returns <= var_99].mean() if len(returns[returns <= var_99]) > 0 else 0
        
        # Maximum Drawdown
        max_drawdown = max_dd
        
        # Drawdown duration
        dd_info = self.calculate_drawdown_periods(portfolio_values)
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'avg_drawdown': dd_info['avg_drawdown'],
            'max_drawdown_duration': dd_info['max_duration'],
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'pain_index': self.calculate_pain_index(portfolio_values)
        }
    
    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if len(portfolio_values) < 2:
            return 0.0
        
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min()
    
    def calculate_drawdown_periods(self, portfolio_values: pd.Series) -> Dict[str, Any]:
        """
        Calculate drawdown periods and statistics.
        
        Returns:
            Dictionary with drawdown period statistics
        """
        if len(portfolio_values) < 2:
            return {'avg_drawdown': 0, 'max_duration': 0, 'drawdown_periods': []}
        
        # Calculate running maximum and drawdown
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        
        # Find drawdown periods
        in_drawdown = drawdown < 0
        drawdown_periods = []
        
        start_idx = None
        for i, is_dd in enumerate(in_drawdown):
            if is_dd and start_idx is None:
                start_idx = i
            elif not is_dd and start_idx is not None:
                # End of drawdown period
                period_dd = drawdown.iloc[start_idx:i]
                drawdown_periods.append({
                    'start': portfolio_values.index[start_idx],
                    'end': portfolio_values.index[i-1],
                    'duration': i - start_idx,
                    'max_drawdown': period_dd.min(),
                    'recovery_time': i - start_idx
                })
                start_idx = None
        
        # Handle case where we end in drawdown
        if start_idx is not None:
            period_dd = drawdown.iloc[start_idx:]
            drawdown_periods.append({
                'start': portfolio_values.index[start_idx],
                'end': portfolio_values.index[-1],
                'duration': len(portfolio_values) - start_idx,
                'max_drawdown': period_dd.min(),
                'recovery_time': None  # Still in drawdown
            })
        
        # Calculate statistics
        if drawdown_periods:
            avg_drawdown = np.mean([dd['max_drawdown'] for dd in drawdown_periods])
            max_duration = max([dd['duration'] for dd in drawdown_periods])
        else:
            avg_drawdown = 0
            max_duration = 0
        
        return {
            'avg_drawdown': avg_drawdown,
            'max_duration': max_duration,
            'drawdown_periods': drawdown_periods,
            'num_drawdown_periods': len(drawdown_periods)
        }
    
    def calculate_pain_index(self, portfolio_values: pd.Series) -> float:
        """
        Calculate Pain Index (average drawdown over the entire period).
        
        Args:
            portfolio_values: Series of portfolio values
            
        Returns:
            Pain Index value
        """
        if len(portfolio_values) < 2:
            return 0.0
        
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak
        return abs(drawdown.mean())
    
    def calculate_trade_metrics(self, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate trade-level performance metrics.
        
        Args:
            trades_df: DataFrame with trade information
            
        Returns:
            Dictionary of trade metrics
        """
        if trades_df.empty:
            return {}
        
        # Separate buy and sell trades
        buy_trades = trades_df[trades_df['action'] == 'BUY']
        sell_trades = trades_df[trades_df['action'] == 'SELL']
        
        # Calculate P&L for round-trip trades
        pnl_trades = self._calculate_round_trip_pnl(trades_df)
        
        if not pnl_trades:
            return {
                'total_trades': len(trades_df),
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades)
            }
        
        pnl_df = pd.DataFrame(pnl_trades)
        
        # Win/Loss statistics
        winning_trades = pnl_df[pnl_df['pnl'] > 0]
        losing_trades = pnl_df[pnl_df['pnl'] < 0]
        
        # Basic trade metrics
        total_pnl = pnl_df['pnl'].sum()
        win_rate = len(winning_trades) / len(pnl_df) if len(pnl_df) > 0 else 0
        
        # Profit factor
        gross_profit = winning_trades['pnl'].sum() if not winning_trades.empty else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if not losing_trades.empty else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Average metrics
        avg_win = winning_trades['pnl'].mean() if not winning_trades.empty else 0
        avg_loss = losing_trades['pnl'].mean() if not losing_trades.empty else 0
        avg_trade = pnl_df['pnl'].mean()
        
        # Expectancy
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        
        # Consecutive wins/losses
        consecutive_stats = self._calculate_consecutive_stats(pnl_df['pnl'])
        
        return {
            'total_trades': len(trades_df),
            'round_trip_trades': len(pnl_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_trade': avg_trade,
            'expectancy': expectancy,
            'largest_win': winning_trades['pnl'].max() if not winning_trades.empty else 0,
            'largest_loss': losing_trades['pnl'].min() if not losing_trades.empty else 0,
            'avg_holding_period': pnl_df['holding_period'].mean() if 'holding_period' in pnl_df.columns else 0,
            **consecutive_stats
        }
    
    def _calculate_round_trip_pnl(self, trades_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate P&L for round-trip trades (buy -> sell pairs)."""
        pnl_trades = []
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
                        holding_period = (trade['timestamp'] - buy_trade['timestamp']).days
                        
                        pnl_trades.append({
                            'symbol': symbol,
                            'pnl': pnl,
                            'return_pct': (trade['price'] - buy_trade['price']) / buy_trade['price'],
                            'holding_period': holding_period,
                            'entry_price': buy_trade['price'],
                            'exit_price': trade['price'],
                            'quantity': buy_trade['quantity']
                        })
                        
                        remaining_quantity -= buy_trade['quantity']
                        positions[symbol].pop(0)
                    else:
                        # Partial fill
                        pnl = (trade['price'] - buy_trade['price']) * remaining_quantity
                        holding_period = (trade['timestamp'] - buy_trade['timestamp']).days
                        
                        pnl_trades.append({
                            'symbol': symbol,
                            'pnl': pnl,
                            'return_pct': (trade['price'] - buy_trade['price']) / buy_trade['price'],
                            'holding_period': holding_period,
                            'entry_price': buy_trade['price'],
                            'exit_price': trade['price'],
                            'quantity': remaining_quantity
                        })
                        
                        buy_trade['quantity'] -= remaining_quantity
                        remaining_quantity = 0
        
        return pnl_trades
    
    def _calculate_consecutive_stats(self, pnl_series: pd.Series) -> Dict[str, int]:
        """Calculate consecutive wins and losses statistics."""
        if pnl_series.empty:
            return {'max_consecutive_wins': 0, 'max_consecutive_losses': 0}
        
        # Convert to win/loss sequence
        win_loss = (pnl_series > 0).astype(int)
        
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        
        for is_win in win_loss:
            if is_win:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
        
        return {
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses
        }
    
    def calculate_benchmark_comparison(
        self, 
        portfolio_values: pd.Series, 
        benchmark_values: pd.Series
    ) -> Dict[str, float]:
        """
        Compare strategy performance against benchmark.
        
        Args:
            portfolio_values: Strategy portfolio values
            benchmark_values: Benchmark values (aligned dates)
            
        Returns:
            Dictionary of comparison metrics
        """
        if len(portfolio_values) != len(benchmark_values) or len(portfolio_values) < 2:
            return {}
        
        # Calculate returns
        portfolio_returns = portfolio_values.pct_change().dropna()
        benchmark_returns = benchmark_values.pct_change().dropna()
        
        # Align returns
        min_length = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns.iloc[-min_length:]
        benchmark_returns = benchmark_returns.iloc[-min_length:]
        
        # Beta calculation
        covariance = portfolio_returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
        
        # Alpha calculation (CAPM)
        portfolio_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        benchmark_return = (benchmark_values.iloc[-1] / benchmark_values.iloc[0]) - 1
        alpha = portfolio_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))
        
        # Correlation
        correlation = portfolio_returns.corr(benchmark_returns)
        
        # Information Ratio
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (excess_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0
        
        # Up/Down capture ratios
        up_market = benchmark_returns > 0
        down_market = benchmark_returns < 0
        
        up_capture = (portfolio_returns[up_market].mean() / benchmark_returns[up_market].mean()) if benchmark_returns[up_market].mean() != 0 else 0
        down_capture = (portfolio_returns[down_market].mean() / benchmark_returns[down_market].mean()) if benchmark_returns[down_market].mean() != 0 else 0
        
        return {
            'alpha': alpha,
            'beta': beta,
            'correlation': correlation,
            'information_ratio': information_ratio,
            'tracking_error': tracking_error,
            'up_capture_ratio': up_capture,
            'down_capture_ratio': down_capture,
            'excess_return': portfolio_return - benchmark_return
        }
    
    def generate_performance_report(
        self, 
        portfolio_values: pd.Series, 
        trades_df: pd.DataFrame = None,
        benchmark_values: pd.Series = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            portfolio_values: Portfolio values over time
            trades_df: Optional trades DataFrame
            benchmark_values: Optional benchmark values for comparison
            
        Returns:
            Complete performance report dictionary
        """
        report = {}
        
        # Return metrics
        report['returns'] = self.calculate_returns_metrics(portfolio_values)
        
        # Risk metrics
        report['risk'] = self.calculate_risk_metrics(portfolio_values)
        
        # Trade metrics
        if trades_df is not None and not trades_df.empty:
            report['trades'] = self.calculate_trade_metrics(trades_df)
        
        # Benchmark comparison
        if benchmark_values is not None:
            report['benchmark'] = self.calculate_benchmark_comparison(portfolio_values, benchmark_values)
        
        # Summary statistics
        report['summary'] = {
            'start_date': portfolio_values.index[0] if hasattr(portfolio_values.index, 'date') else 'N/A',
            'end_date': portfolio_values.index[-1] if hasattr(portfolio_values.index, 'date') else 'N/A',
            'total_periods': len(portfolio_values),
            'initial_value': portfolio_values.iloc[0],
            'final_value': portfolio_values.iloc[-1],
            'peak_value': portfolio_values.max(),
            'trough_value': portfolio_values.min()
        }
        
        return report

# Convenience functions
def quick_performance_summary(portfolio_values: pd.Series) -> pd.DataFrame:
    """Generate a quick performance summary table."""
    analyzer = PerformanceAnalyzer()
    
    returns_metrics = analyzer.calculate_returns_metrics(portfolio_values)
    risk_metrics = analyzer.calculate_risk_metrics(portfolio_values)
    
    summary_data = [
        ['Total Return', f"{returns_metrics.get('total_return', 0):.2%}"],
        ['Annualized Return', f"{returns_metrics.get('annualized_return', 0):.2%}"],
        ['Volatility', f"{returns_metrics.get('volatility', 0):.2%}"],
        ['Sharpe Ratio', f"{risk_metrics.get('sharpe_ratio', 0):.3f}"],
        ['Sortino Ratio', f"{risk_metrics.get('sortino_ratio', 0):.3f}"],
        ['Max Drawdown', f"{risk_metrics.get('max_drawdown', 0):.2%}"],
        ['Calmar Ratio', f"{risk_metrics.get('calmar_ratio', 0):.3f}"],
        ['VaR (95%)', f"{risk_metrics.get('var_95', 0):.2%}"]
    ]
    
    return pd.DataFrame(summary_data, columns=['Metric', 'Value'])