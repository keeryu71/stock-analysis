#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Stock Analyzer for Cloud Deployment
Focuses on basic analysis that works reliably in cloud environments
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_config import get_stock_list

class SimpleStockAnalyzer:
    """Simplified stock analyzer for cloud deployment."""
    
    def __init__(self):
        self.stocks = get_stock_list()
    
    def get_stock_data(self, symbol, period="1mo"):
        """Get basic stock data."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            return data
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI."""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50
        except:
            return 50
    
    def calculate_sma(self, prices, window=20):
        """Calculate Simple Moving Average."""
        try:
            return prices.rolling(window=window).mean().iloc[-1]
        except:
            return prices.iloc[-1] if not prices.empty else 0
    
    def analyze_stock(self, symbol):
        """Analyze a single stock."""
        try:
            print(f"📊 Analyzing {symbol}...")
            
            # Get stock data
            data = self.get_stock_data(symbol)
            if data is None or data.empty:
                print(f"❌ No data for {symbol}")
                return None
            
            # Current price
            current_price = data['Close'].iloc[-1]
            
            # Calculate indicators
            rsi = self.calculate_rsi(data['Close'])
            sma_20 = self.calculate_sma(data['Close'], 20)
            sma_50 = self.calculate_sma(data['Close'], 50)
            
            # Volume analysis
            avg_volume = data['Volume'].mean()
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Price change
            price_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            
            # Simple scoring
            score = 0.5  # Base score
            
            # RSI scoring
            if 30 <= rsi <= 70:
                score += 0.2
            elif rsi < 30:
                score += 0.3  # Oversold - potential buy
            
            # Trend scoring
            if current_price > sma_20:
                score += 0.15
            if sma_20 > sma_50:
                score += 0.15
            
            # Volume scoring
            if volume_ratio > 1.2:
                score += 0.1
            
            print(f"✅ {symbol}: ${current_price:.2f}, RSI: {rsi:.1f}, Score: {score:.2f}")
            
            return {
                'symbol': symbol,
                'price': current_price,
                'price_change': price_change,
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'volume_ratio': volume_ratio,
                'score': score,
                'signal': 'BUY' if score >= 0.8 else 'HOLD' if score >= 0.6 else 'WAIT',
                'top_entries': [{'price': sma_20, 'level': 'SMA20'}] if sma_20 > 0 else []
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def run_analysis(self):
        """Run analysis on all stocks."""
        print("🚀 Starting simplified stock analysis...")
        results = []
        
        for symbol in self.stocks:
            try:
                result = self.analyze_stock(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"❌ Failed to analyze {symbol}: {e}")
                continue
        
        print(f"✅ Analysis complete! Found {len(results)} valid results")
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

class SimpleOptionsAnalyzer:
    """Simplified options analyzer for cloud deployment."""
    
    def __init__(self):
        self.stocks = get_stock_list()[:5]  # Limit to first 5 stocks for options
    
    def get_basic_options_data(self, symbol):
        """Get basic options information."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current price
            info = ticker.info
            current_price = info.get('currentPrice', 0)
            if current_price == 0:
                hist = ticker.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            # Get options dates
            options_dates = ticker.options
            if not options_dates:
                return None
            
            # Use first available expiration
            exp_date = options_dates[0]
            options_chain = ticker.option_chain(exp_date)
            
            if options_chain.puts.empty:
                return None
            
            # Filter puts near the money
            puts = options_chain.puts
            puts = puts[puts['strike'] <= current_price * 1.1]  # Within 10% of current price
            puts = puts[puts['strike'] >= current_price * 0.8]   # Not too far out of money
            
            if puts.empty:
                return None
            
            # Calculate days to expiration
            exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
            days_to_exp = (exp_datetime - datetime.now()).days
            
            # Simple analysis of best puts
            puts['mid_price'] = (puts['bid'] + puts['ask']) / 2
            puts['return_rate'] = puts['mid_price'] / puts['strike']
            puts['annualized_return'] = puts['return_rate'] * (365 / max(days_to_exp, 1))
            
            # Filter for liquid options
            puts = puts[puts['volume'] > 0]
            puts = puts[puts['bid'] > 0.05]  # Minimum bid
            
            if puts.empty:
                return None
            
            # Sort by annualized return
            puts = puts.sort_values('annualized_return', ascending=False)
            
            # Format results
            put_analysis = []
            for _, put in puts.head(3).iterrows():
                put_analysis.append({
                    'strike': put['strike'],
                    'bid': put['bid'],
                    'ask': put['ask'],
                    'volume': put['volume'],
                    'days_to_exp': days_to_exp,
                    'annualized_return': put['annualized_return']
                })
            
            # Simple quality score
            quality_score = min(0.9, len(put_analysis) * 0.3)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'quality_score': quality_score,
                'put_analysis': put_analysis,
                'days_to_expiration': days_to_exp
            }
            
        except Exception as e:
            print(f"❌ Options error for {symbol}: {e}")
            return None
    
    def run_real_time_analysis(self):
        """Run simplified options analysis."""
        print("🚀 Starting simplified options analysis...")
        results = []
        
        for symbol in self.stocks:
            try:
                result = self.get_basic_options_data(symbol)
                if result:
                    results.append(result)
                    print(f"✅ {symbol}: Found {len(result['put_analysis'])} put options")
            except Exception as e:
                print(f"❌ Failed options analysis for {symbol}: {e}")
                continue
        
        print(f"✅ Options analysis complete! Found {len(results)} results")
        return results

if __name__ == "__main__":
    # Test the analyzers
    print("Testing Simple Stock Analyzer...")
    stock_analyzer = SimpleStockAnalyzer()
    stock_results = stock_analyzer.run_analysis()
    print(f"Stock results: {len(stock_results)}")
    
    print("\nTesting Simple Options Analyzer...")
    options_analyzer = SimpleOptionsAnalyzer()
    options_results = options_analyzer.run_real_time_analysis()
    print(f"Options results: {len(options_results)}")