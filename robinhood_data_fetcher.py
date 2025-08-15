#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robinhood Data Fetcher for 24/7 Stock Quotes
Uses unofficial Robinhood API to get extended hours trading data
"""

import requests
import json
from datetime import datetime
import time
from stock_config import get_stock_list

class RobinhoodDataFetcher:
    """Fetches real-time stock data from Robinhood including extended hours."""
    
    def __init__(self):
        self.base_url = "https://robinhood.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_instrument_id(self, symbol):
        """Get Robinhood instrument ID for a stock symbol."""
        try:
            url = f"{self.base_url}/instruments/"
            params = {'symbol': symbol}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    return data['results'][0]['id']
            return None
        except Exception as e:
            print(f"❌ Error getting instrument ID for {symbol}: {e}")
            return None
    
    def get_quote_data(self, symbol):
        """Get real-time quote data from Robinhood."""
        try:
            # Method 1: Direct quote endpoint
            url = f"{self.base_url}/quotes/"
            params = {'symbols': symbol}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    quote = data['results'][0]
                    return self.parse_quote_data(quote, symbol)
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching quote for {symbol}: {e}")
            return None
    
    def parse_quote_data(self, quote, symbol):
        """Parse Robinhood quote data into our format."""
        try:
            # Get the most current price available
            current_price = None
            price_source = "unknown"
            
            # Priority order: extended_hours_last_trade_price, last_trade_price, previous_close
            if quote.get('last_extended_hours_trade_price'):
                current_price = float(quote['last_extended_hours_trade_price'])
                price_source = "extended_hours"
            elif quote.get('last_trade_price'):
                current_price = float(quote['last_trade_price'])
                price_source = "regular_hours"
            elif quote.get('previous_close'):
                current_price = float(quote['previous_close'])
                price_source = "previous_close"
            
            if not current_price:
                return None
            
            # Calculate price change
            previous_close = float(quote.get('previous_close', current_price))
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close) * 100 if previous_close > 0 else 0
            
            # Get trading session info
            trading_halted = quote.get('trading_halted', False)
            has_traded = quote.get('has_traded', True)
            
            # Determine market status
            now = datetime.now()
            market_hours = self.get_market_status(now)
            
            result = {
                'symbol': symbol,
                'price': round(current_price, 2),
                'previous_close': round(previous_close, 2),
                'price_change': round(price_change, 2),
                'price_change_percent': round(price_change_percent, 2),
                'price_source': price_source,
                'market_status': market_hours,
                'trading_halted': trading_halted,
                'has_traded': has_traded,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'robinhood'
            }
            
            print(f"✅ {symbol}: ${current_price:.2f} ({price_source}) {price_change:+.2f} ({price_change_percent:+.1f}%)")
            return result
            
        except Exception as e:
            print(f"❌ Error parsing quote data for {symbol}: {e}")
            return None
    
    def get_market_status(self, current_time):
        """Determine current market status."""
        hour = current_time.hour
        minute = current_time.minute
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # Weekend
        if weekday >= 5:  # Saturday or Sunday
            return "weekend"
        
        # Convert to minutes for easier comparison
        current_minutes = hour * 60 + minute
        
        # Market hours (EST): 9:30 AM - 4:00 PM = 570 - 960 minutes
        # Extended hours: 4:00 AM - 9:30 AM and 4:00 PM - 8:00 PM
        pre_market_start = 4 * 60  # 4:00 AM
        market_open = 9 * 60 + 30  # 9:30 AM
        market_close = 16 * 60     # 4:00 PM
        after_hours_end = 20 * 60  # 8:00 PM
        
        if pre_market_start <= current_minutes < market_open:
            return "pre_market"
        elif market_open <= current_minutes < market_close:
            return "regular_hours"
        elif market_close <= current_minutes < after_hours_end:
            return "after_hours"
        else:
            return "closed"
    
    def get_multiple_quotes(self, symbols):
        """Get quotes for multiple symbols."""
        results = []
        
        # Robinhood allows batch requests
        try:
            symbols_str = ','.join(symbols)
            url = f"{self.base_url}/quotes/"
            params = {'symbols': symbols_str}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for i, quote in enumerate(data.get('results', [])):
                    if i < len(symbols):
                        parsed = self.parse_quote_data(quote, symbols[i])
                        if parsed:
                            results.append(parsed)
            
        except Exception as e:
            print(f"❌ Batch request failed: {e}")
            # Fall back to individual requests
            for symbol in symbols:
                result = self.get_quote_data(symbol)
                if result:
                    results.append(result)
                time.sleep(0.1)  # Rate limiting
        
        return results
    
    def get_all_stock_quotes(self):
        """Get quotes for all configured stocks."""
        print("🚀 Fetching 24/7 stock data from Robinhood...")
        stocks = get_stock_list()
        
        # Process in batches of 10 to avoid rate limits
        all_results = []
        batch_size = 10
        
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            print(f"📊 Processing batch {i//batch_size + 1}: {', '.join(batch)}")
            
            batch_results = self.get_multiple_quotes(batch)
            all_results.extend(batch_results)
            
            # Rate limiting between batches
            if i + batch_size < len(stocks):
                time.sleep(1)
        
        print(f"✅ Robinhood data fetch complete: {len(all_results)} stocks")
        return all_results

class RobinhoodStockAnalyzer:
    """Stock analyzer using Robinhood 24/7 data."""
    
    def __init__(self):
        self.fetcher = RobinhoodDataFetcher()
    
    def calculate_simple_rsi(self, current_price, previous_close):
        """Calculate a simple RSI approximation based on price change."""
        if previous_close <= 0:
            return 50
        
        price_change_percent = ((current_price - previous_close) / previous_close) * 100
        
        # Simple RSI approximation based on price change
        if price_change_percent > 5:
            return 75  # Overbought territory
        elif price_change_percent > 2:
            return 65
        elif price_change_percent > 0:
            return 55
        elif price_change_percent > -2:
            return 45
        elif price_change_percent > -5:
            return 35
        else:
            return 25  # Oversold territory
    
    def analyze_stock_from_robinhood(self, quote_data):
        """Analyze a stock using Robinhood data."""
        try:
            symbol = quote_data['symbol']
            current_price = quote_data['price']
            previous_close = quote_data['previous_close']
            price_change_percent = quote_data['price_change_percent']
            
            # Calculate simple indicators
            rsi = self.calculate_simple_rsi(current_price, previous_close)
            
            # Simple moving average approximations
            sma_20 = previous_close * 0.98  # Approximate 20-day SMA
            sma_50 = previous_close * 0.95  # Approximate 50-day SMA
            
            # Volume ratio (use price volatility as proxy)
            volume_ratio = min(3.0, max(0.5, 1.0 + abs(price_change_percent) / 5))
            
            # Calculate score
            score = 0.5  # Base score
            
            # RSI scoring
            if 30 <= rsi <= 70:
                score += 0.2
            elif rsi < 30:
                score += 0.3  # Oversold
            
            # Price trend scoring
            if current_price > sma_20:
                score += 0.15
            if sma_20 > sma_50:
                score += 0.15
            
            # Momentum scoring
            if price_change_percent > 0:
                score += 0.1
            elif price_change_percent > 2:
                score += 0.15
            
            # Market hours bonus (extended hours trading is often more volatile)
            if quote_data['market_status'] in ['pre_market', 'after_hours']:
                score += 0.05
            
            score = max(0, min(1, score))
            
            result = {
                'symbol': symbol,
                'price': current_price,
                'price_change': quote_data['price_change'],
                'price_change_percent': price_change_percent,
                'rsi': round(rsi, 1),
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'volume_ratio': round(volume_ratio, 1),
                'score': round(score, 2),
                'signal': 'BUY' if score >= 0.8 else 'HOLD' if score >= 0.6 else 'WAIT',
                'top_entries': [{'price': round(sma_20, 2), 'level': 'SMA20'}],
                'market_status': quote_data['market_status'],
                'price_source': quote_data['price_source'],
                'data_source': 'robinhood_24h'
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing {quote_data.get('symbol', 'unknown')}: {e}")
            return None
    
    def run_analysis(self):
        """Run 24/7 stock analysis using Robinhood data."""
        print("🚀 Starting 24/7 Robinhood stock analysis...")
        
        # Get all quotes from Robinhood
        quotes = self.fetcher.get_all_stock_quotes()
        
        if not quotes:
            print("❌ No data received from Robinhood")
            return []
        
        # Analyze each stock
        results = []
        for quote in quotes:
            analysis = self.analyze_stock_from_robinhood(quote)
            if analysis:
                results.append(analysis)
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Robinhood analysis complete: {len(results)} stocks analyzed")
        
        # Show market status summary
        status_counts = {}
        for result in results:
            status = result['market_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"📊 Market status: {dict(status_counts)}")
        
        return results

if __name__ == "__main__":
    # Test the Robinhood data fetcher
    print("Testing Robinhood Data Fetcher...")
    
    # Test single stock
    fetcher = RobinhoodDataFetcher()
    tsla_quote = fetcher.get_quote_data('TSLA')
    if tsla_quote:
        print(f"TSLA Quote: {tsla_quote}")
    
    # Test analyzer
    analyzer = RobinhoodStockAnalyzer()
    results = analyzer.run_analysis()
    print(f"Analysis results: {len(results)} stocks")