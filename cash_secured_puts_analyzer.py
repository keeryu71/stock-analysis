#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cash-Secured Put Options Analyzer
Analyzes stocks for optimal cash-secured put selling opportunities
Considers volatility, support levels, premium income, and risk factors
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf
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
from stock_config import get_stock_list, DEFAULT_DAYS_TO_EXPIRATION

class CashSecuredPutAnalyzer:
    """Analyzes stocks for cash-secured put selling opportunities."""
    
    def __init__(self):
        self.stocks = ['TSLA', 'AMD', 'BMNR', 'SBET', 'MSTR', 'HIMS', 'PLTR', 'AVGO', 'NVDA', 'HOOD', 'COIN', 'OSCR', 'GOOG', 'UNH', 'MSFT', 'SOFI']
        self.days_to_expiration = 30  # 1 month
        
    def calculate_implied_volatility_proxy(self, data):
        """Calculate a proxy for implied volatility using historical volatility."""
        # Calculate 30-day historical volatility (annualized)
        returns = data['close'].pct_change().dropna()
        if len(returns) < 30:
            return None
        
        # Use last 30 days for recent volatility
        recent_returns = returns.tail(30)
        daily_vol = recent_returns.std()
        annualized_vol = daily_vol * np.sqrt(252)  # 252 trading days per year
        
        return annualized_vol
    
    def calculate_support_levels(self, data):
        """Calculate key support levels for strike price selection."""
        current_price = data['close'].iloc[-1]
        
        # Multi-timeframe support levels
        timeframes = {
            '30D': 30,
            '60D': 60,
            '90D': 90
        }
        
        support_levels = {}
        
        for timeframe_name, days in timeframes.items():
            timeframe_data = data.tail(min(days, len(data)))
            
            if len(timeframe_data) > 0:
                tf_high = timeframe_data['high'].max()
                tf_low = timeframe_data['low'].min()
                tf_range = tf_high - tf_low
                
                # Fibonacci support levels
                fib_levels = {
                    f'{timeframe_name}_23.6%': tf_high - (tf_range * 0.236),
                    f'{timeframe_name}_38.2%': tf_high - (tf_range * 0.382),
                    f'{timeframe_name}_50.0%': tf_high - (tf_range * 0.500),
                    f'{timeframe_name}_61.8%': tf_high - (tf_range * 0.618)
                }
                
                support_levels.update(fib_levels)
        
        # Add moving averages as support
        if len(data) >= 20:
            support_levels['SMA_20'] = data['close'].rolling(20).mean().iloc[-1]
        if len(data) >= 50:
            support_levels['SMA_50'] = data['close'].rolling(50).mean().iloc[-1]
        
        # Filter support levels that are below current price (valid for puts)
        valid_supports = {k: v for k, v in support_levels.items() 
                         if pd.notna(v) and v < current_price}
        
        return valid_supports
    
    def calculate_option_metrics(self, current_price, strike_price, volatility, days_to_exp=30):
        """Calculate comprehensive option metrics including all Greeks."""
        if volatility is None or volatility <= 0:
            return None
        
        # Risk-free rate (approximate)
        risk_free_rate = 0.05  # 5% assumption
        
        # Time to expiration in years
        time_to_exp = days_to_exp / 365.0
        
        # Avoid division by zero for very short time periods
        if time_to_exp <= 0:
            time_to_exp = 1/365.0  # Minimum 1 day
        
        # Moneyness
        moneyness = strike_price / current_price
        
        # Black-Scholes calculations
        d1 = (np.log(current_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_exp) / (volatility * np.sqrt(time_to_exp))
        d2 = d1 - volatility * np.sqrt(time_to_exp)
        
        from scipy.stats import norm
        
        # Put option price (Black-Scholes)
        put_price = strike_price * np.exp(-risk_free_rate * time_to_exp) * norm.cdf(-d2) - current_price * norm.cdf(-d1)
        
        # === THE GREEKS ===
        
        # Delta: Price sensitivity (-1 to 0 for puts)
        put_delta = -norm.cdf(-d1)
        
        # Gamma: Delta sensitivity (same for calls and puts)
        gamma = norm.pdf(d1) / (current_price * volatility * np.sqrt(time_to_exp))
        
        # Theta: Time decay (negative for long positions)
        theta_daily = -(current_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_exp)) +
                        risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_exp) * norm.cdf(-d2)) / 365
        
        # Vega: Volatility sensitivity
        vega = current_price * norm.pdf(d1) * np.sqrt(time_to_exp) / 100  # Per 1% vol change
        
        # Rho: Interest rate sensitivity
        rho = -strike_price * time_to_exp * np.exp(-risk_free_rate * time_to_exp) * norm.cdf(-d2) / 100
        
        # === ADDITIONAL METRICS ===
        
        # Probability of assignment (ITM at expiration)
        prob_assignment = norm.cdf(-d2)
        
        # Intrinsic value
        intrinsic_value = max(strike_price - current_price, 0)
        
        # Time value
        time_value = max(put_price - intrinsic_value, 0)
        
        # Implied volatility rank (how current vol compares to historical)
        # This would need historical vol data, so we'll approximate
        iv_rank = min(volatility / 0.5, 1.0)  # Assume 50% as "high" volatility
        
        return {
            'theoretical_premium': max(put_price, 0.01),
            'intrinsic_value': intrinsic_value,
            'time_value': time_value,
            'delta': put_delta,
            'gamma': gamma,
            'theta': theta_daily,
            'vega': vega,
            'rho': rho,
            'prob_assignment': prob_assignment,
            'moneyness': moneyness,
            'iv_rank': iv_rank
        }
    
    def analyze_put_opportunity(self, symbol, data):
        """Analyze a stock for cash-secured put opportunities."""
        try:
            if data.empty:
                return None
            
            current_price = data['close'].iloc[-1]
            
            # Calculate technical indicators
            strategy = FibonacciMACDStrategy()
            analyzed_data = strategy._calculate_indicators(data.copy())
            latest = analyzed_data.iloc[-1]
            
            # Calculate volatility
            volatility = self.calculate_implied_volatility_proxy(data)
            if volatility is None:
                return None
            
            # Calculate support levels
            support_levels = self.calculate_support_levels(data)
            
            # Generate strike price candidates
            strike_candidates = []
            
            # 1. Support-based strikes (most important for puts)
            for level_name, support_price in support_levels.items():
                if support_price > 0:
                    discount = ((current_price - support_price) / current_price) * 100
                    if 5 <= discount <= 25:  # 5-25% below current price
                        strike_candidates.append({
                            'strike': support_price,
                            'type': f'Support ({level_name})',
                            'discount': discount
                        })
            
            # 2. Percentage-based strikes
            for pct in [5, 10, 15, 20]:
                strike_price = current_price * (1 - pct/100)
                strike_candidates.append({
                    'strike': strike_price,
                    'type': f'{pct}% OTM',
                    'discount': pct
                })
            
            # Calculate metrics for each strike
            strike_analysis = []
            for candidate in strike_candidates:
                strike = candidate['strike']
                option_metrics = self.calculate_option_metrics(current_price, strike, volatility, self.days_to_expiration)
                
                if option_metrics:
                    # Calculate returns
                    premium = option_metrics['theoretical_premium']
                    cash_required = strike * 100  # 100 shares per contract
                    monthly_return = (premium * 100) / cash_required  # Premium per contract / cash required
                    annualized_return = monthly_return * 12
                    
                    # Greeks-based scoring for put selling
                    greeks_score = self.calculate_greeks_score(option_metrics)
                    
                    strike_analysis.append({
                        'strike': strike,
                        'type': candidate['type'],
                        'discount': candidate['discount'],
                        'premium': premium,
                        'intrinsic_value': option_metrics['intrinsic_value'],
                        'time_value': option_metrics['time_value'],
                        'monthly_return': monthly_return,
                        'annualized_return': annualized_return,
                        'prob_assignment': option_metrics['prob_assignment'],
                        'delta': option_metrics['delta'],
                        'gamma': option_metrics['gamma'],
                        'theta': option_metrics['theta'],
                        'vega': option_metrics['vega'],
                        'rho': option_metrics['rho'],
                        'iv_rank': option_metrics['iv_rank'],
                        'greeks_score': greeks_score,
                        'cash_required': cash_required
                    })
            
            # Sort by combined score: Greeks score (60%) + Annualized return (40%)
            for strike in strike_analysis:
                # Normalize annualized return (cap at 50% for scoring)
                normalized_return = min(strike['annualized_return'], 0.5) / 0.5
                # Combined score
                strike['combined_score'] = (strike['greeks_score'] * 0.6) + (normalized_return * 0.4)
            
            strike_analysis.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Stock quality assessment
            quality_score = self.assess_stock_quality(analyzed_data, volatility)
            
            # Risk assessment
            risk_factors = self.assess_risk_factors(data, analyzed_data, volatility)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'volatility': volatility,
                'quality_score': quality_score,
                'risk_factors': risk_factors,
                'strike_analysis': strike_analysis[:5],  # Top 5 strikes
                'support_levels': support_levels,
                'rsi': latest['rsi'],
                'trend_strength': 1 if latest['close'] > latest['sma_20'] else -1,
                'best_greeks_score': strike_analysis[0]['greeks_score'] if strike_analysis else 0
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def calculate_greeks_score(self, option_metrics):
        """Calculate a score based on Greeks for put selling optimization."""
        score_components = {}
        
        # Delta Score (0-1): For puts, delta is negative. Ideal range: -0.15 to -0.35
        delta = abs(option_metrics['delta'])  # Make positive for scoring
        if 0.15 <= delta <= 0.35:
            score_components['delta'] = 1.0  # Sweet spot
        elif 0.10 <= delta < 0.15 or 0.35 < delta <= 0.45:
            score_components['delta'] = 0.7  # Acceptable
        else:
            score_components['delta'] = 0.3  # Too low or too high
        
        # Theta Score (0-1): Higher theta decay is better for sellers (more positive theta)
        theta = abs(option_metrics['theta'])  # Daily theta decay
        if theta >= 0.05:  # $0.05+ daily decay
            score_components['theta'] = 1.0
        elif theta >= 0.02:
            score_components['theta'] = 0.7
        else:
            score_components['theta'] = 0.4
        
        # Gamma Score (0-1): Lower gamma is better (less delta sensitivity)
        gamma = option_metrics['gamma']
        if gamma <= 0.02:
            score_components['gamma'] = 1.0  # Low gamma = stable delta
        elif gamma <= 0.05:
            score_components['gamma'] = 0.7
        else:
            score_components['gamma'] = 0.3  # High gamma = unstable
        
        # Vega Score (0-1): Lower vega is better (less vol sensitivity)
        vega = abs(option_metrics['vega'])
        if vega <= 0.10:
            score_components['vega'] = 1.0  # Low vol sensitivity
        elif vega <= 0.20:
            score_components['vega'] = 0.7
        else:
            score_components['vega'] = 0.4  # High vol sensitivity
        
        # Time Value Score (0-1): Higher time value is better for sellers
        time_value_ratio = option_metrics['time_value'] / option_metrics['theoretical_premium']
        if time_value_ratio >= 0.8:  # 80%+ time value
            score_components['time_value'] = 1.0
        elif time_value_ratio >= 0.5:
            score_components['time_value'] = 0.7
        else:
            score_components['time_value'] = 0.4
        
        # IV Rank Score (0-1): Higher IV is better for sellers
        iv_rank = option_metrics['iv_rank']
        if iv_rank >= 0.7:
            score_components['iv_rank'] = 1.0  # High IV = good premiums
        elif iv_rank >= 0.4:
            score_components['iv_rank'] = 0.7
        else:
            score_components['iv_rank'] = 0.4  # Low IV = poor premiums
        
        # Weighted Greeks Score
        weights = {
            'delta': 0.25,      # 25% - Most important for put sellers
            'theta': 0.20,      # 20% - Time decay benefit
            'gamma': 0.15,      # 15% - Delta stability
            'vega': 0.15,       # 15% - Volatility risk
            'time_value': 0.15, # 15% - Premium quality
            'iv_rank': 0.10     # 10% - Market environment
        }
        
        total_score = sum(score_components[component] * weight
                         for component, weight in weights.items())
        
        return total_score
    
    def assess_stock_quality(self, analyzed_data, volatility):
        """Assess overall stock quality for put selling."""
        latest = analyzed_data.iloc[-1]
        
        # Quality factors
        factors = {
            'trend_quality': 1 if latest['close'] > latest['sma_20'] else 0,  # Uptrend preferred
            'rsi_favorable': 1 if 30 < latest['rsi'] < 70 else 0,  # Not extreme
            'volatility_reasonable': 1 if 0.2 < volatility < 0.8 else 0,  # 20-80% vol
            'volume_healthy': 1 if latest['volume_ratio'] > 0.8 else 0,  # Decent volume
            'macd_stable': 1 if abs(latest['macd'] - latest['macd_signal']) < 0.5 else 0  # Not extreme divergence
        }
        
        return sum(factors.values()) / len(factors)
    
    def assess_risk_factors(self, data, analyzed_data, volatility):
        """Assess risk factors for put selling."""
        latest = analyzed_data.iloc[-1]
        current_price = latest['close']
        
        risk_factors = []
        
        # High volatility risk
        if volatility > 0.6:
            risk_factors.append(f"High volatility ({volatility:.1%})")
        
        # Downtrend risk
        if latest['close'] < latest['sma_20']:
            risk_factors.append("Below 20-day SMA (downtrend)")
        
        # Oversold risk (might continue falling)
        if latest['rsi'] < 30:
            risk_factors.append(f"Oversold RSI ({latest['rsi']:.0f})")
        
        # Low volume risk
        if latest['volume_ratio'] < 0.5:
            risk_factors.append("Low volume")
        
        # Recent large decline
        week_ago_price = data['close'].iloc[-5] if len(data) >= 5 else current_price
        week_decline = ((week_ago_price - current_price) / week_ago_price) * 100
        if week_decline > 10:
            risk_factors.append(f"Recent decline ({week_decline:.1f}%)")
        
        return risk_factors
    
    def run_analysis(self):
        """Analyze all stocks for put selling opportunities."""
        print(f"🎯 Analyzing {len(self.stocks)} stocks for cash-secured put opportunities...")
        print(f"📅 Target expiration: ~{self.days_to_expiration} days")
        
        try:
            # Load 6 months of data for comprehensive analysis
            loader = DataLoader()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            all_data = loader.fetch_stock_data(self.stocks, start_date, end_date)
            
            results = []
            for symbol in self.stocks:
                if symbol in all_data:
                    stock_data = all_data[symbol]
                    analysis = self.analyze_put_opportunity(symbol, stock_data)
                    if analysis:
                        results.append(analysis)
                        print(f"✓ {symbol}: ${analysis['current_price']:.2f} (Vol: {analysis['volatility']:.1%})")
                    else:
                        print(f"❌ {symbol}: Analysis failed")
                else:
                    print(f"❌ {symbol}: No data available")
            
            return results
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return []
    
    def create_summary_table(self, results):
        """Create a summary table of put selling opportunities."""
        if not results:
            return "No results available"
        
        # Sort by quality score and best combined score (includes Greeks)
        sorted_results = sorted(results, key=lambda x: (x['quality_score'],
                                                       x['strike_analysis'][0]['combined_score'] if x['strike_analysis'] else 0),
                               reverse=True)
        
        table_data = []
        for stock in sorted_results:
            best_strike = stock['strike_analysis'][0] if stock['strike_analysis'] else None
            
            if best_strike:
                # Risk level
                risk_count = len(stock['risk_factors'])
                risk_level = "🟢 Low" if risk_count <= 1 else "🟡 Med" if risk_count <= 2 else "🔴 High"
                
                # Quality rating
                quality = stock['quality_score']
                quality_rating = "⭐⭐⭐⭐⭐" if quality >= 0.8 else "⭐⭐⭐⭐" if quality >= 0.6 else "⭐⭐⭐" if quality >= 0.4 else "⭐⭐"
                
                row = [
                    stock['symbol'],
                    f"${stock['current_price']:.2f}",
                    f"{stock['volatility']:.1%}",
                    f"${best_strike['strike']:.2f}",
                    f"{best_strike['discount']:.1f}%",
                    f"${best_strike['premium']:.2f}",
                    f"{best_strike['delta']:.2f}",
                    f"${best_strike['theta']:.3f}",
                    f"{best_strike['annualized_return']:.1%}",
                    f"{best_strike['prob_assignment']:.1%}",
                    risk_level,
                    quality_rating
                ]
                table_data.append(row)
        
        headers = [
            "Symbol", "Price", "Vol", "Best Strike", "Discount",
            "Premium", "Delta", "Theta", "Ann. Return", "Assign %", "Risk", "Quality"
        ]
        
        return tabulate(
            table_data,
            headers=headers,
            tablefmt="simple",
            colalign=("center", "right", "center", "right", "center", "right", "center", "center", "center", "center", "center", "center")
        )
    
    def create_detailed_analysis(self, stock_analysis):
        """Create detailed analysis for a specific stock."""
        symbol = stock_analysis['symbol']
        print(f"\n{'='*60}")
        print(f"📊 DETAILED PUT ANALYSIS: {symbol}")
        print(f"{'='*60}")
        print(f"Current Price: ${stock_analysis['current_price']:.2f}")
        print(f"Volatility: {stock_analysis['volatility']:.1%}")
        print(f"Quality Score: {stock_analysis['quality_score']:.1%}")
        print(f"RSI: {stock_analysis['rsi']:.0f}")
        print(f"Trend: {'📈 Up' if stock_analysis['trend_strength'] > 0 else '📉 Down'}")
        
        # Risk factors
        if stock_analysis['risk_factors']:
            print(f"\n⚠️  Risk Factors:")
            for risk in stock_analysis['risk_factors']:
                print(f"  • {risk}")
        else:
            print(f"\n✅ No major risk factors identified")
        
        # Support levels
        print(f"\n🎯 Key Support Levels:")
        for level_name, price in list(stock_analysis['support_levels'].items())[:5]:
            discount = ((stock_analysis['current_price'] - price) / stock_analysis['current_price']) * 100
            print(f"  • {level_name}: ${price:.2f} ({discount:.1f}% below)")
        
        # Strike analysis with Greeks
        print(f"\n💰 TOP PUT STRIKE RECOMMENDATIONS:")
        strike_table = []
        for i, strike in enumerate(stock_analysis['strike_analysis'][:3], 1):
            strike_table.append([
                f"#{i}",
                f"${strike['strike']:.2f}",
                strike['type'],
                f"{strike['discount']:.1f}%",
                f"${strike['premium']:.2f}",
                f"{strike['delta']:.2f}",
                f"${strike['theta']:.3f}",
                f"{strike['gamma']:.3f}",
                f"{strike['vega']:.2f}",
                f"{strike['annualized_return']:.1%}",
                f"{strike['prob_assignment']:.1%}",
                f"{strike['greeks_score']:.1%}"
            ])
        
        strike_headers = ["Rank", "Strike", "Type", "Discount", "Premium", "Delta", "Theta", "Gamma", "Vega", "Annual", "Assign%", "Greeks"]
        print(tabulate(strike_table, headers=strike_headers, tablefmt="simple"))
        
        # Greeks explanation
        print(f"\n📊 GREEKS ANALYSIS (Best Strike):")
        best_strike = stock_analysis['strike_analysis'][0]
        print(f"  • Delta: {best_strike['delta']:.2f} (Price sensitivity - ideal: -0.15 to -0.35)")
        print(f"  • Theta: ${best_strike['theta']:.3f} (Daily time decay - higher is better for sellers)")
        print(f"  • Gamma: {best_strike['gamma']:.3f} (Delta stability - lower is better)")
        print(f"  • Vega: {best_strike['vega']:.2f} (Volatility sensitivity - lower is better)")
        print(f"  • Greeks Score: {best_strike['greeks_score']:.1%} (Combined Greeks rating)")
        
        # Recommendation
        best_strike = stock_analysis['strike_analysis'][0]
        quality = stock_analysis['quality_score']
        risk_count = len(stock_analysis['risk_factors'])
        
        print(f"\n🎯 RECOMMENDATION:")
        if quality >= 0.6 and risk_count <= 2 and best_strike['annualized_return'] >= 0.15:
            print(f"✅ EXCELLENT PUT CANDIDATE")
            print(f"   Sell ${best_strike['strike']:.2f} puts for ~${best_strike['premium']:.2f} premium")
            print(f"   Target return: {best_strike['annualized_return']:.1%} annualized")
        elif quality >= 0.4 and risk_count <= 3:
            print(f"⚡ GOOD PUT CANDIDATE")
            print(f"   Consider ${best_strike['strike']:.2f} puts with caution")
        else:
            print(f"⚠️  PROCEED WITH CAUTION")
            print(f"   High risk or low quality - consider smaller position")
    
    def generate_put_analysis_report(self):
        """Generate comprehensive put selling analysis report."""
        print(f"🎯 CASH-SECURED PUT ANALYSIS REPORT")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Target Expiration: ~{self.days_to_expiration} days")
        
        results = self.run_analysis()
        
        if not results:
            print("❌ No analysis results available")
            return
        
        print(f"\n📊 SUMMARY TABLE - PUT SELLING OPPORTUNITIES:")
        summary_table = self.create_summary_table(results)
        print(summary_table)
        
        # Show top 3 detailed analyses
        top_3 = sorted(results, key=lambda x: (x['quality_score'], 
                                              x['strike_analysis'][0]['annualized_return'] if x['strike_analysis'] else 0), 
                      reverse=True)[:3]
        
        for stock_analysis in top_3:
            self.create_detailed_analysis(stock_analysis)
        
        # Overall market assessment
        print(f"\n{'='*60}")
        print(f"📈 MARKET ASSESSMENT")
        print(f"{'='*60}")
        
        avg_vol = np.mean([r['volatility'] for r in results])
        high_quality = len([r for r in results if r['quality_score'] >= 0.6])
        low_risk = len([r for r in results if len(r['risk_factors']) <= 2])
        
        print(f"Average Volatility: {avg_vol:.1%}")
        print(f"High Quality Stocks: {high_quality}/{len(results)}")
        print(f"Low Risk Stocks: {low_risk}/{len(results)}")
        
        if avg_vol > 0.5:
            print(f"⚠️  High volatility environment - consider smaller positions")
        elif avg_vol < 0.3:
            print(f"📉 Low volatility environment - premiums may be limited")
        else:
            print(f"✅ Moderate volatility - good environment for put selling")

def main():
    """Main function to run cash-secured put analysis."""
    analyzer = CashSecuredPutAnalyzer()
    analyzer.generate_put_analysis_report()

if __name__ == "__main__":
    # Install required package if not available
    try:
        from scipy.stats import norm
    except ImportError:
        print("Installing required scipy package...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])
        from scipy.stats import norm
    
    main()