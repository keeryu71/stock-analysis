#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Stock Analyzer for Cloud Deployment
Provides realistic sample data when live data isn't available
"""

import random
from datetime import datetime
from stock_config import get_stock_list

class MockStockAnalyzer:
    """Mock stock analyzer that provides realistic sample data."""
    
    def __init__(self):
        self.stocks = get_stock_list()
        # Set seed for consistent results
        random.seed(42)
    
    def generate_mock_stock_data(self, symbol):
        """Generate realistic mock data for a stock."""
        # Base prices for different stocks
        base_prices = {
            'TSLA': 250.0, 'AMD': 140.0, 'BMNR': 15.0, 'SBET': 8.0, 'MSTR': 180.0,
            'HIMS': 12.0, 'PLTR': 25.0, 'AVGO': 900.0, 'NVDA': 450.0, 'HOOD': 20.0,
            'COIN': 85.0, 'OSCR': 35.0, 'GOOG': 2800.0, 'UNH': 520.0, 'MSFT': 420.0, 'SOFI': 8.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Add some randomness
        price_variation = random.uniform(-0.1, 0.1)  # ±10%
        current_price = base_price * (1 + price_variation)
        
        # Generate other metrics
        rsi = random.uniform(25, 75)
        volume_ratio = random.uniform(0.5, 2.5)
        price_change = random.uniform(-5, 5)
        
        # Calculate score based on RSI and other factors
        score = 0.5  # Base score
        
        if 30 <= rsi <= 70:
            score += 0.2
        elif rsi < 30:
            score += 0.3
        
        if volume_ratio > 1.2:
            score += 0.1
        
        if price_change > 0:
            score += 0.1
        
        # Add some randomness to score
        score += random.uniform(-0.1, 0.1)
        score = max(0, min(1, score))  # Keep between 0 and 1
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'rsi': round(rsi, 1),
            'sma_20': round(current_price * 0.98, 2),
            'sma_50': round(current_price * 0.95, 2),
            'volume_ratio': round(volume_ratio, 1),
            'score': round(score, 2),
            'signal': 'BUY' if score >= 0.8 else 'HOLD' if score >= 0.6 else 'WAIT',
            'top_entries': [{'price': round(current_price * 0.98, 2), 'level': 'SMA20'}]
        }
    
    def analyze_stock(self, symbol):
        """Analyze a single stock with mock data."""
        try:
            print(f"📊 Generating mock data for {symbol}...")
            result = self.generate_mock_stock_data(symbol)
            print(f"✅ {symbol}: ${result['price']}, RSI: {result['rsi']}, Score: {result['score']}")
            return result
        except Exception as e:
            print(f"❌ Error generating mock data for {symbol}: {e}")
            return None
    
    def run_analysis(self):
        """Run analysis on all stocks with mock data."""
        print("🚀 Starting mock stock analysis...")
        results = []
        
        for symbol in self.stocks:
            try:
                result = self.analyze_stock(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"❌ Failed to generate mock data for {symbol}: {e}")
                continue
        
        print(f"✅ Mock analysis complete! Generated {len(results)} results")
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

class MockOptionsAnalyzer:
    """Mock options analyzer that provides realistic sample data."""
    
    def __init__(self):
        self.stocks = get_stock_list()  # Use all 50 stocks
        random.seed(42)
    
    def generate_mock_options_data(self, symbol):
        """Generate realistic mock options data."""
        # More realistic base prices for popular stocks
        base_prices = {
            'AAPL': 230.0, 'MSFT': 520.0, 'GOOGL': 204.0, 'AMZN': 231.0, 'NVDA': 180.0,
            'META': 101.0, 'TSLA': 331.0, 'NFLX': 1239.0, 'AMD': 178.0, 'CRM': 242.0,
            'ORCL': 248.0, 'ADBE': 355.0, 'AVGO': 306.0, 'INTC': 25.0, 'QCOM': 158.0,
            'JPM': 290.0, 'BAC': 47.0, 'WFC': 77.0, 'GS': 731.0, 'MS': 145.0,
            'C': 94.0, 'V': 344.0, 'MA': 582.0, 'PYPL': 69.0, 'JNJ': 177.0,
            'PFE': 25.0, 'UNH': 304.0, 'ABBV': 207.0, 'MRK': 84.0, 'TMO': 489.0,
            'ABT': 132.0, 'WMT': 100.0, 'HD': 390.0, 'PG': 154.0, 'KO': 70.0,
            'PEP': 150.0, 'NKE': 77.0, 'MCD': 309.0, 'SBUX': 91.0, 'XOM': 106.0,
            'CVX': 157.0, 'BA': 235.0, 'CAT': 408.0, 'GE': 268.0, 'PLTR': 177.0,
            'HOOD': 114.0, 'COIN': 318.0, 'SOFI': 24.0, 'RIVN': 12.24, 'LCID': 2.0
        }
        
        base_price = base_prices.get(symbol, 150.0)  # Better default price
        current_price = base_price * (1 + random.uniform(-0.05, 0.05))
        
        # Generate put options at different strikes
        put_analysis = []
        for i in range(3):
            strike_offset = random.uniform(0.85, 0.95)  # 5-15% out of money
            strike = current_price * strike_offset
            
            # Calculate premium based on strike distance
            premium = (current_price - strike) * random.uniform(0.1, 0.3)
            premium = max(0.5, premium)  # Minimum premium
            
            days_to_exp = random.randint(15, 45)
            annualized_return = (premium / strike) * (365 / days_to_exp)
            
            put_analysis.append({
                'strike': round(strike, 2),
                'bid': round(premium * 0.95, 2),
                'ask': round(premium * 1.05, 2),
                'volume': random.randint(10, 500),
                'days_to_exp': days_to_exp,
                'annualized_return': round(annualized_return, 3)
            })
        
        # Sort by annualized return
        put_analysis.sort(key=lambda x: x['annualized_return'], reverse=True)
        
        quality_score = random.uniform(0.6, 0.9)
        
        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'quality_score': round(quality_score, 2),
            'put_analysis': put_analysis,
            'days_to_expiration': put_analysis[0]['days_to_exp'] if put_analysis else 30
        }
    
    def get_basic_options_data(self, symbol):
        """Get mock options data for a symbol."""
        try:
            print(f"💰 Generating mock options data for {symbol}...")
            result = self.generate_mock_options_data(symbol)
            print(f"✅ {symbol}: ${result['current_price']}, {len(result['put_analysis'])} puts")
            return result
        except Exception as e:
            print(f"❌ Error generating mock options data for {symbol}: {e}")
            return None
    
    def run_real_time_analysis(self):
        """Run mock options analysis."""
        print("🚀 Starting mock options analysis...")
        results = []
        
        for symbol in self.stocks:
            try:
                result = self.get_basic_options_data(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"❌ Failed to generate mock options data for {symbol}: {e}")
                continue
        
        print(f"✅ Mock options analysis complete! Generated {len(results)} results")
        return results

if __name__ == "__main__":
    # Test the mock analyzers
    print("Testing Mock Stock Analyzer...")
    stock_analyzer = MockStockAnalyzer()
    stock_results = stock_analyzer.run_analysis()
    print(f"Mock stock results: {len(stock_results)}")
    
    print("\nTesting Mock Options Analyzer...")
    options_analyzer = MockOptionsAnalyzer()
    options_results = options_analyzer.run_real_time_analysis()
    print(f"Mock options results: {len(options_results)}")