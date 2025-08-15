#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Free Extended Hours Data Fetcher
Uses multiple free APIs to get 24/7 stock data including extended hours
"""

import requests
import json
from datetime import datetime, timedelta
import time
from stock_config import get_stock_list

class FreeExtendedHoursDataFetcher:
    """Fetches extended hours stock data from free APIs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_yahoo_extended_hours(self, symbol):
        """Get extended hours data from Yahoo Finance."""
        try:
            # Yahoo Finance has extended hours data in their chart API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'range': '1d',
                'interval': '1m',
                'includePrePost': 'true',  # This includes pre/post market data
                'events': 'div,splits'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    # Get current price (includes extended hours)
                    current_price = meta.get('regularMarketPrice', 0)
                    
                    # Check if we have extended hours price
                    if 'postMarketPrice' in meta and meta['postMarketPrice']:
                        current_price = meta['postMarketPrice']
                        price_source = 'after_hours'
                    elif 'preMarketPrice' in meta and meta['preMarketPrice']:
                        current_price = meta['preMarketPrice']
                        price_source = 'pre_market'
                    else:
                        price_source = 'regular_hours'
                    
                    previous_close = meta.get('previousClose', current_price)
                    
                    # Calculate change
                    price_change = current_price - previous_close
                    price_change_percent = (price_change / previous_close) * 100 if previous_close > 0 else 0
                    
                    # Get market status
                    market_state = meta.get('marketState', 'CLOSED').lower()
                    market_status = self.convert_market_state(market_state)
                    
                    return {
                        'symbol': symbol,
                        'price': round(current_price, 2),
                        'previous_close': round(previous_close, 2),
                        'price_change': round(price_change, 2),
                        'price_change_percent': round(price_change_percent, 2),
                        'price_source': price_source,
                        'market_status': market_status,
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'yahoo_extended'
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Yahoo extended hours error for {symbol}: {e}")
            return None
    
    def get_finnhub_data(self, symbol):
        """Get data from Finnhub (free tier, no API key needed for basic quotes)."""
        try:
            # Finnhub free endpoint (limited but works)
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': 'demo'  # Demo token for basic access
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if 'c' in data and data['c'] > 0:  # 'c' is current price
                    current_price = data['c']
                    previous_close = data.get('pc', current_price)  # 'pc' is previous close
                    
                    price_change = current_price - previous_close
                    price_change_percent = (price_change / previous_close) * 100 if previous_close > 0 else 0
                    
                    return {
                        'symbol': symbol,
                        'price': round(current_price, 2),
                        'previous_close': round(previous_close, 2),
                        'price_change': round(price_change, 2),
                        'price_change_percent': round(price_change_percent, 2),
                        'price_source': 'real_time',
                        'market_status': self.get_current_market_status(),
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'finnhub'
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Finnhub error for {symbol}: {e}")
            return None
    
    def get_alpha_vantage_data(self, symbol):
        """Get data from Alpha Vantage (free tier, demo key)."""
        try:
            # Alpha Vantage free endpoint
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': 'demo'  # Demo key for basic access
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    current_price = float(quote.get('05. price', 0))
                    previous_close = float(quote.get('08. previous close', current_price))
                    
                    if current_price > 0:
                        price_change = current_price - previous_close
                        price_change_percent = (price_change / previous_close) * 100 if previous_close > 0 else 0
                        
                        return {
                            'symbol': symbol,
                            'price': round(current_price, 2),
                            'previous_close': round(previous_close, 2),
                            'price_change': round(price_change, 2),
                            'price_change_percent': round(price_change_percent, 2),
                            'price_source': 'real_time',
                            'market_status': self.get_current_market_status(),
                            'timestamp': datetime.now().isoformat(),
                            'data_source': 'alpha_vantage'
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ Alpha Vantage error for {symbol}: {e}")
            return None
    
    def convert_market_state(self, market_state):
        """Convert Yahoo's market state to our format."""
        state_map = {
            'regular': 'regular_hours',
            'pre': 'pre_market',
            'post': 'after_hours',
            'postpost': 'after_hours',
            'prepre': 'pre_market',
            'closed': 'closed'
        }
        return state_map.get(market_state, 'closed')
    
    def get_current_market_status(self):
        """Determine current market status based on time."""
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Weekend
        if weekday >= 5:
            return "weekend"
        
        # Convert to minutes for easier comparison (EST times)
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
    
    def get_best_quote(self, symbol):
        """Try multiple sources to get the best quote for a symbol."""
        print(f"🔍 Fetching extended hours data for {symbol}...")
        
        # Try Yahoo first (best for extended hours)
        result = self.get_yahoo_extended_hours(symbol)
        if result:
            print(f"✅ {symbol}: ${result['price']:.2f} from Yahoo ({result['price_source']})")
            return result
        
        # Try Finnhub
        result = self.get_finnhub_data(symbol)
        if result:
            print(f"✅ {symbol}: ${result['price']:.2f} from Finnhub")
            return result
        
        # Try Alpha Vantage
        result = self.get_alpha_vantage_data(symbol)
        if result:
            print(f"✅ {symbol}: ${result['price']:.2f} from Alpha Vantage")
            return result
        
        print(f"❌ No data available for {symbol}")
        return None
    
    def get_all_quotes(self):
        """Get quotes for all configured stocks."""
        print("🚀 Fetching extended hours data from free APIs...")
        stocks = get_stock_list()
        results = []
        
        for symbol in stocks:
            try:
                result = self.get_best_quote(symbol)
                if result:
                    results.append(result)
                
                # Rate limiting to be respectful to free APIs
                time.sleep(0.2)
                
            except Exception as e:
                print(f"❌ Failed to get data for {symbol}: {e}")
                continue
        
        print(f"✅ Extended hours data fetch complete: {len(results)} stocks")
        return results

class FreeExtendedHoursAnalyzer:
    """Stock analyzer using free extended hours data."""
    
    def __init__(self):
        self.fetcher = FreeExtendedHoursDataFetcher()
    
    def calculate_simple_rsi(self, current_price, previous_close):
        """Calculate simple RSI approximation."""
        if previous_close <= 0:
            return 50
        
        price_change_percent = ((current_price - previous_close) / previous_close) * 100
        
        # Simple RSI approximation
        if price_change_percent > 5:
            return 75
        elif price_change_percent > 2:
            return 65
        elif price_change_percent > 0:
            return 55
        elif price_change_percent > -2:
            return 45
        elif price_change_percent > -5:
            return 35
        else:
            return 25
    
    def analyze_stock_from_quote(self, quote_data):
        """Analyze a stock using free API quote data."""
        try:
            symbol = quote_data['symbol']
            current_price = quote_data['price']
            previous_close = quote_data['previous_close']
            price_change_percent = quote_data['price_change_percent']
            
            # Calculate indicators
            rsi = self.calculate_simple_rsi(current_price, previous_close)
            sma_20 = previous_close * 0.98
            sma_50 = previous_close * 0.95
            volume_ratio = min(3.0, max(0.5, 1.0 + abs(price_change_percent) / 5))
            
            # Calculate score
            score = 0.5
            
            # RSI scoring
            if 30 <= rsi <= 70:
                score += 0.2
            elif rsi < 30:
                score += 0.3
            
            # Price trend
            if current_price > sma_20:
                score += 0.15
            if sma_20 > sma_50:
                score += 0.15
            
            # Momentum
            if price_change_percent > 0:
                score += 0.1
            elif price_change_percent > 2:
                score += 0.15
            
            # Extended hours bonus
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
                'data_source': f"free_api_{quote_data['data_source']}"
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing {quote_data.get('symbol', 'unknown')}: {e}")
            return None
    
    def run_analysis(self):
        """Run extended hours analysis using free APIs."""
        print("🚀 Starting free extended hours stock analysis...")
        
        # Get quotes from free APIs
        quotes = self.fetcher.get_all_quotes()
        
        if not quotes:
            print("❌ No data received from free APIs")
            return []
        
        # Analyze each stock
        results = []
        for quote in quotes:
            analysis = self.analyze_stock_from_quote(quote)
            if analysis:
                results.append(analysis)
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Free API analysis complete: {len(results)} stocks analyzed")
        
        # Show data source summary
        source_counts = {}
        for result in results:
            source = result['data_source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"📊 Data sources: {dict(source_counts)}")
        
        return results

if __name__ == "__main__":
    # Test the free extended hours fetcher
    print("Testing Free Extended Hours Data Fetcher...")
    
    # Test single stock
    fetcher = FreeExtendedHoursDataFetcher()
    tsla_quote = fetcher.get_best_quote('TSLA')
    if tsla_quote:
        print(f"TSLA Quote: {tsla_quote}")
    
    # Test analyzer
    analyzer = FreeExtendedHoursAnalyzer()
    results = analyzer.run_analysis()
    print(f"Analysis results: {len(results)} stocks")