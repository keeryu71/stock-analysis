#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Options Analyzer
Fetches actual option prices and analyzes cash-secured put opportunities
Uses real market data instead of theoretical pricing
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

class RealTimeOptionsAnalyzer:
    """Analyzes real-time option prices for cash-secured put opportunities."""
    
    def __init__(self):
        self.stocks = ['TSLA', 'AMD', 'BMNR', 'SBET', 'MSTR', 'HIMS', 'PLTR', 'AVGO', 'NVDA', 'HOOD', 'COIN', 'OSCR', 'GOOG', 'UNH', 'MSFT', 'SOFI']
        self.target_days = 30  # Target ~30 days to expiration
        
    def get_option_chain(self, symbol):
        """Fetch real option chain data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            if not expirations:
                print(f"❌ No options data available for {symbol}")
                return None, None
            
            # Find expiration closest to target days (around 30 days)
            target_date = datetime.now() + timedelta(days=self.target_days)
            
            best_expiration = None
            min_diff = float('inf')
            
            for exp_str in expirations:
                exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
                days_diff = abs((exp_date - datetime.now()).days - self.target_days)
                if days_diff < min_diff:
                    min_diff = days_diff
                    best_expiration = exp_str
            
            if not best_expiration:
                return None, None
            
            # Get option chain for best expiration
            option_chain = ticker.option_chain(best_expiration)
            puts = option_chain.puts
            
            # Calculate actual days to expiration
            exp_date = datetime.strptime(best_expiration, '%Y-%m-%d')
            days_to_exp = (exp_date - datetime.now()).days
            
            return puts, days_to_exp
            
        except Exception as e:
            print(f"❌ Error fetching options for {symbol}: {e}")
            return None, None
    
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
    
    def analyze_real_puts(self, symbol, stock_data, puts_data, days_to_exp):
        """Analyze real put options for a stock."""
        try:
            if stock_data.empty or puts_data is None or puts_data.empty:
                return None
            
            current_price = stock_data['close'].iloc[-1]
            
            # Calculate technical indicators
            strategy = FibonacciMACDStrategy()
            analyzed_data = strategy._calculate_indicators(stock_data.copy())
            latest = analyzed_data.iloc[-1]
            
            # Calculate support levels
            support_levels = self.calculate_support_levels(stock_data)
            
            # Filter puts that are reasonable for cash-secured puts
            # Focus on OTM puts (strike < current price) with decent volume/open interest
            filtered_puts = puts_data[
                (puts_data['strike'] < current_price) &  # OTM puts only
                (puts_data['strike'] > current_price * 0.75) &  # Not too far OTM
                (puts_data['bid'] > 0.05) &  # Minimum bid price
                (puts_data['volume'] > 0)  # Some trading volume
            ].copy()
            
            if filtered_puts.empty:
                # If no volume, relax volume requirement but keep other filters
                filtered_puts = puts_data[
                    (puts_data['strike'] < current_price) &
                    (puts_data['strike'] > current_price * 0.75) &
                    (puts_data['bid'] > 0.05)
                ].copy()
            
            if filtered_puts.empty:
                return None
            
            # Analyze each put option
            put_analysis = []
            for _, put_row in filtered_puts.iterrows():
                strike = put_row['strike']
                bid = put_row['bid']
                ask = put_row['ask']
                mid_price = (bid + ask) / 2 if ask > bid else bid
                
                # Skip if spread is too wide (>50% of mid price)
                if ask > 0 and bid > 0:
                    spread = ask - bid
                    if spread / mid_price > 0.5:
                        continue
                
                # Calculate metrics
                discount = ((current_price - strike) / current_price) * 100
                cash_required = strike * 100  # 100 shares per contract
                premium_income = bid * 100  # Use bid price (what you'll actually receive)
                monthly_return = premium_income / cash_required
                annualized_return = monthly_return * (365 / days_to_exp)
                
                # Determine strike type (support-based or percentage-based)
                strike_type = "Percentage OTM"
                closest_support = None
                min_support_diff = float('inf')
                
                for support_name, support_price in support_levels.items():
                    diff = abs(strike - support_price)
                    if diff < min_support_diff and diff < (current_price * 0.02):  # Within 2%
                        min_support_diff = diff
                        closest_support = support_name
                        strike_type = f"Near {support_name}"
                
                # Calculate implied volatility proxy
                time_to_exp = days_to_exp / 365.0
                if time_to_exp > 0:
                    # Simple IV approximation using put-call parity concepts
                    intrinsic = max(strike - current_price, 0)
                    time_value = mid_price - intrinsic
                    iv_proxy = (time_value / current_price) / np.sqrt(time_to_exp) if time_value > 0 else 0
                else:
                    iv_proxy = 0
                
                put_analysis.append({
                    'strike': strike,
                    'type': strike_type,
                    'discount': discount,
                    'bid': bid,
                    'ask': ask,
                    'mid_price': mid_price,
                    'premium_income': premium_income,
                    'monthly_return': monthly_return,
                    'annualized_return': annualized_return,
                    'cash_required': cash_required,
                    'volume': put_row.get('volume', 0),
                    'open_interest': put_row.get('openInterest', 0),
                    'iv_proxy': iv_proxy,
                    'days_to_exp': days_to_exp,
                    'bid_ask_spread': ask - bid if ask > bid else 0,
                    'spread_pct': ((ask - bid) / mid_price * 100) if mid_price > 0 else 0
                })
            
            if not put_analysis:
                return None
            
            # Sort by annualized return, but consider liquidity
            for put in put_analysis:
                # Liquidity score (0-1)
                volume_score = min(put['volume'] / 50, 1.0) if put['volume'] > 0 else 0
                oi_score = min(put['open_interest'] / 100, 1.0) if put['open_interest'] > 0 else 0
                spread_score = max(0, 1 - (put['spread_pct'] / 20))  # Penalize wide spreads
                
                liquidity_score = (volume_score * 0.4 + oi_score * 0.4 + spread_score * 0.2)
                
                # Combined score: Return (70%) + Liquidity (30%)
                return_score = min(put['annualized_return'], 1.0)  # Cap at 100%
                put['combined_score'] = (return_score * 0.7) + (liquidity_score * 0.3)
            
            put_analysis.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Stock quality assessment
            quality_score = self.assess_stock_quality(analyzed_data)
            risk_factors = self.assess_risk_factors(stock_data, analyzed_data)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'quality_score': quality_score,
                'risk_factors': risk_factors,
                'put_analysis': put_analysis[:5],  # Top 5 puts
                'support_levels': support_levels,
                'rsi': latest['rsi'],
                'trend_strength': 1 if latest['close'] > latest['sma_20'] else -1,
                'days_to_expiration': days_to_exp
            }
            
        except Exception as e:
            print(f"Error analyzing puts for {symbol}: {e}")
            return None
    
    def assess_stock_quality(self, analyzed_data):
        """Assess overall stock quality for put selling."""
        latest = analyzed_data.iloc[-1]
        
        # Quality factors
        factors = {
            'trend_quality': 1 if latest['close'] > latest['sma_20'] else 0,
            'rsi_favorable': 1 if 30 < latest['rsi'] < 70 else 0,
            'volume_healthy': 1 if latest['volume_ratio'] > 0.8 else 0,
            'macd_stable': 1 if abs(latest['macd'] - latest['macd_signal']) < 0.5 else 0
        }
        
        return sum(factors.values()) / len(factors)
    
    def assess_risk_factors(self, data, analyzed_data):
        """Assess risk factors for put selling."""
        latest = analyzed_data.iloc[-1]
        current_price = latest['close']
        
        risk_factors = []
        
        # Downtrend risk
        if latest['close'] < latest['sma_20']:
            risk_factors.append("Below 20-day SMA (downtrend)")
        
        # Oversold risk
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
    
    def run_real_time_analysis(self):
        """Run real-time options analysis for all stocks."""
        print(f"🎯 REAL-TIME OPTIONS ANALYSIS")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Analyzing {len(self.stocks)} stocks with live option data...")
        
        # Load stock data
        loader = DataLoader()
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        try:
            all_stock_data = loader.fetch_stock_data(self.stocks, start_date, end_date)
        except Exception as e:
            print(f"❌ Error loading stock data: {e}")
            return []
        
        results = []
        
        for symbol in self.stocks:
            print(f"\n🔍 Analyzing {symbol}...")
            
            if symbol not in all_stock_data:
                print(f"❌ {symbol}: No stock data available")
                continue
            
            stock_data = all_stock_data[symbol]
            
            # Get real option data
            puts_data, days_to_exp = self.get_option_chain(symbol)
            
            if puts_data is None:
                print(f"❌ {symbol}: No options data available")
                continue
            
            # Analyze the options
            analysis = self.analyze_real_puts(symbol, stock_data, puts_data, days_to_exp)
            
            if analysis:
                results.append(analysis)
                best_put = analysis['put_analysis'][0] if analysis['put_analysis'] else None
                if best_put:
                    print(f"✅ {symbol}: ${analysis['current_price']:.2f} | Best Put: ${best_put['strike']:.2f} @ ${best_put['bid']:.2f} ({best_put['annualized_return']:.1%})")
                else:
                    print(f"⚠️  {symbol}: No suitable puts found")
            else:
                print(f"❌ {symbol}: Analysis failed")
        
        return results
    
    def create_real_time_summary(self, results):
        """Create summary table with real option prices."""
        if not results:
            return "No results available"
        
        # Sort by quality score and best return
        sorted_results = sorted(results, key=lambda x: (x['quality_score'], 
                                                       x['put_analysis'][0]['combined_score'] if x['put_analysis'] else 0), 
                               reverse=True)
        
        table_data = []
        for stock in sorted_results:
            best_put = stock['put_analysis'][0] if stock['put_analysis'] else None
            
            if best_put:
                # Risk level
                risk_count = len(stock['risk_factors'])
                risk_level = "🟢 Low" if risk_count <= 1 else "🟡 Med" if risk_count <= 2 else "🔴 High"
                
                # Quality rating
                quality = stock['quality_score']
                quality_rating = "⭐⭐⭐⭐⭐" if quality >= 0.8 else "⭐⭐⭐⭐" if quality >= 0.6 else "⭐⭐⭐" if quality >= 0.4 else "⭐⭐"
                
                # Liquidity indicator
                volume = best_put['volume']
                oi = best_put['open_interest']
                liquidity = "🟢 Good" if volume >= 20 and oi >= 50 else "🟡 Fair" if volume >= 5 or oi >= 20 else "🔴 Poor"
                
                row = [
                    stock['symbol'],
                    f"${stock['current_price']:.2f}",
                    f"${best_put['strike']:.2f}",
                    f"{best_put['discount']:.1f}%",
                    f"${best_put['bid']:.2f}",
                    f"${best_put['ask']:.2f}",
                    f"{best_put['annualized_return']:.1%}",
                    f"{best_put['days_to_exp']}d",
                    f"{volume}",
                    liquidity,
                    risk_level,
                    quality_rating
                ]
                table_data.append(row)
        
        headers = [
            "Symbol", "Stock Price", "Strike", "Discount", "Bid", "Ask", 
            "Ann. Return", "DTE", "Volume", "Liquidity", "Risk", "Quality"
        ]
        
        return tabulate(
            table_data,
            headers=headers,
            tablefmt="simple",
            colalign=("center", "right", "right", "center", "right", "right", "center", "center", "center", "center", "center", "center")
        )
    
    def generate_real_time_report(self):
        """Generate comprehensive real-time options report."""
        results = self.run_real_time_analysis()
        
        if not results:
            print("❌ No real-time options data available")
            return
        
        print(f"\n📊 REAL-TIME PUT OPTIONS SUMMARY:")
        summary_table = self.create_real_time_summary(results)
        print(summary_table)
        
        # Show detailed analysis for top 3
        print(f"\n🎯 TOP 3 REAL-TIME OPPORTUNITIES:")
        top_3 = sorted(results, key=lambda x: (x['quality_score'], 
                                              x['put_analysis'][0]['combined_score'] if x['put_analysis'] else 0), 
                      reverse=True)[:3]
        
        for i, stock in enumerate(top_3, 1):
            print(f"\n{'='*50}")
            print(f"#{i} {stock['symbol']} - REAL-TIME PUT ANALYSIS")
            print(f"{'='*50}")
            print(f"Stock Price: ${stock['current_price']:.2f}")
            print(f"Quality Score: {stock['quality_score']:.1%}")
            print(f"Days to Expiration: {stock['days_to_expiration']}")
            
            if stock['risk_factors']:
                print(f"⚠️  Risk Factors: {', '.join(stock['risk_factors'])}")
            
            print(f"\n💰 TOP PUT OPTIONS:")
            put_table = []
            for j, put in enumerate(stock['put_analysis'][:3], 1):
                put_table.append([
                    f"#{j}",
                    f"${put['strike']:.2f}",
                    f"${put['bid']:.2f}",
                    f"${put['ask']:.2f}",
                    f"{put['discount']:.1f}%",
                    f"{put['annualized_return']:.1%}",
                    f"{put['volume']}",
                    f"{put['open_interest']}",
                    f"${put['cash_required']:,.0f}"
                ])
            
            put_headers = ["Rank", "Strike", "Bid", "Ask", "Discount", "Annual", "Volume", "OI", "Cash Req"]
            print(tabulate(put_table, headers=put_headers, tablefmt="simple"))
        
        print(f"\n💡 REAL-TIME TRADING NOTES:")
        print(f"• Prices shown are LIVE market data from Yahoo Finance")
        print(f"• Use BID prices for premium calculations (what you'll receive)")
        print(f"• Check volume and open interest for liquidity")
        print(f"• Wide bid-ask spreads indicate poor liquidity")
        print(f"• Consider market hours - options may have stale prices after hours")

def main():
    """Main function to run real-time options analysis."""
    analyzer = RealTimeOptionsAnalyzer()
    analyzer.generate_real_time_report()

if __name__ == "__main__":
    main()