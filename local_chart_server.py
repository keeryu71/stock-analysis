#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Chart Generation Server
Generates charts locally with real yfinance data and serves them to the web app
"""

import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import schedule

# Import our existing chart generator
from chart_generator import StockChartGenerator
from hybrid_stock_analyzer import HybridStockAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for web app access

class LocalChartService:
    """Local chart generation service that runs on your computer."""
    
    def __init__(self):
        self.chart_generator = StockChartGenerator()
        self.stock_analyzer = HybridStockAnalyzer()
        self.charts_dir = "generated_charts"
        self.chart_cache = {}
        self.last_update = None
        
        # Create charts directory
        os.makedirs(self.charts_dir, exist_ok=True)
        
        print("🏠 Local Chart Service initialized")
    
    def generate_chart_for_symbol(self, symbol):
        """Generate chart for a specific symbol."""
        try:
            print(f"📊 Generating local chart for {symbol}...")
            
            # Get analysis data
            analysis_data = self.stock_analyzer.analyze_stock(symbol)
            if not analysis_data:
                print(f"⚠️ No analysis data for {symbol}")
                return None
            
            # Generate chart
            chart_base64 = self.chart_generator.generate_chart(symbol, analysis_data)
            if chart_base64:
                # Save to cache
                self.chart_cache[symbol] = {
                    'chart': chart_base64,
                    'analysis': analysis_data,
                    'timestamp': datetime.now().isoformat(),
                    'generated_locally': True
                }
                
                # Save to file for persistence
                chart_file = os.path.join(self.charts_dir, f"{symbol}_chart.json")
                with open(chart_file, 'w') as f:
                    json.dump(self.chart_cache[symbol], f)
                
                print(f"✅ Chart generated and cached for {symbol}")
                return self.chart_cache[symbol]
            else:
                print(f"❌ Failed to generate chart for {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating chart for {symbol}: {e}")
            return None
    
    def generate_top_charts(self):
        """Generate charts for top 10 stocks and top 10 options setups."""
        print("🚀 Starting intelligent chart generation for top setups...")
        
        # Get top 10 stock setups
        print("📈 Analyzing top stock setups...")
        stock_results = self.stock_analyzer.run_analysis()
        top_stocks = [result['symbol'] for result in stock_results[:10]]
        
        # Get top 10 options setups
        print("💰 Analyzing top options setups...")
        from hybrid_stock_analyzer import HybridOptionsAnalyzer
        options_analyzer = HybridOptionsAnalyzer()
        options_results = options_analyzer.run_real_time_analysis()
        top_options = [result['symbol'] for result in options_results[:10]]
        
        # Combine and deduplicate
        priority_symbols = list(dict.fromkeys(top_stocks + top_options))  # Preserves order, removes duplicates
        
        print(f"🎯 Priority symbols identified: {len(priority_symbols)} unique stocks")
        print(f"   Top stocks: {', '.join(top_stocks)}")
        print(f"   Top options: {', '.join(top_options)}")
        
        success_count = 0
        
        for i, symbol in enumerate(priority_symbols, 1):
            print(f"📊 [{i}/{len(priority_symbols)}] Processing priority stock {symbol}...")
            
            result = self.generate_chart_for_symbol(symbol)
            if result:
                success_count += 1
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.5)
        
        self.last_update = datetime.now()
        print(f"✅ Priority chart generation complete: {success_count}/{len(priority_symbols)} charts generated")
        
        return {
            'success': True,
            'generated': success_count,
            'total': len(priority_symbols),
            'priority_symbols': priority_symbols,
            'top_stocks': top_stocks,
            'top_options': top_options,
            'timestamp': self.last_update.isoformat()
        }
    
    def generate_all_charts(self):
        """Generate charts for all stocks (fallback method)."""
        print("🚀 Starting bulk chart generation for all stocks...")
        
        stocks = self.stock_analyzer.stocks
        success_count = 0
        
        for i, symbol in enumerate(stocks, 1):
            print(f"📊 [{i}/{len(stocks)}] Processing {symbol}...")
            
            result = self.generate_chart_for_symbol(symbol)
            if result:
                success_count += 1
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.5)
        
        self.last_update = datetime.now()
        print(f"✅ Bulk generation complete: {success_count}/{len(stocks)} charts generated")
        
        return {
            'success': True,
            'generated': success_count,
            'total': len(stocks),
            'timestamp': self.last_update.isoformat()
        }
    
    def load_cached_charts(self):
        """Load previously generated charts from disk."""
        print("📂 Loading cached charts...")
        
        if not os.path.exists(self.charts_dir):
            return
        
        loaded_count = 0
        for filename in os.listdir(self.charts_dir):
            if filename.endswith('_chart.json'):
                symbol = filename.replace('_chart.json', '')
                try:
                    chart_file = os.path.join(self.charts_dir, filename)
                    with open(chart_file, 'r') as f:
                        self.chart_cache[symbol] = json.load(f)
                    loaded_count += 1
                except Exception as e:
                    print(f"⚠️ Error loading cached chart for {symbol}: {e}")
        
        print(f"✅ Loaded {loaded_count} cached charts")
    
    def get_chart_data(self, symbol):
        """Get chart data for a symbol."""
        # Check cache first
        if symbol in self.chart_cache:
            cached_data = self.chart_cache[symbol]
            # Check if cache is recent (within 1 hour)
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=1):
                print(f"📋 Returning cached chart for {symbol}")
                return cached_data
        
        # Generate new chart
        print(f"🔄 Generating fresh chart for {symbol}")
        return self.generate_chart_for_symbol(symbol)

# Global service instance
chart_service = LocalChartService()

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Local Chart Generator',
        'cached_charts': len(chart_service.chart_cache),
        'last_update': chart_service.last_update.isoformat() if chart_service.last_update else None
    })

@app.route('/chart/<symbol>')
def get_chart(symbol):
    """Get chart for a specific symbol."""
    symbol = symbol.upper()
    
    chart_data = chart_service.get_chart_data(symbol)
    if chart_data:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'chart': chart_data['chart'],
            'analysis': chart_data['analysis'],
            'timestamp': chart_data['timestamp'],
            'source': 'local_generation'
        })
    else:
        return jsonify({
            'success': False,
            'symbol': symbol,
            'error': 'Could not generate chart'
        }), 404

@app.route('/charts/bulk')
def get_all_charts():
    """Get all cached charts."""
    return jsonify({
        'success': True,
        'charts': chart_service.chart_cache,
        'count': len(chart_service.chart_cache),
        'last_update': chart_service.last_update.isoformat() if chart_service.last_update else None
    })

@app.route('/generate/all', methods=['POST'])
def generate_all_charts():
    """Generate charts for all symbols."""
    result = chart_service.generate_all_charts()
    return jsonify(result)

@app.route('/generate/<symbol>', methods=['POST'])
def generate_chart(symbol):
    """Generate chart for a specific symbol."""
    symbol = symbol.upper()
    
    chart_data = chart_service.generate_chart_for_symbol(symbol)
    if chart_data:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'message': f'Chart generated for {symbol}',
            'timestamp': chart_data['timestamp']
        })
    else:
        return jsonify({
            'success': False,
            'symbol': symbol,
            'error': 'Failed to generate chart'
        }), 500

def schedule_updates():
    """Schedule automatic chart updates."""
    # Update charts every hour during market hours
    schedule.every().hour.do(chart_service.generate_all_charts)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    print("🏠 Starting Local Chart Generation Server...")
    
    # Load cached charts on startup
    chart_service.load_cached_charts()
    
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=schedule_updates, daemon=True)
    scheduler_thread.start()
    
    print("🌐 Local Chart Server running on http://localhost:5001")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /chart/<symbol> - Get chart for symbol")
    print("  GET  /charts/bulk - Get all charts")
    print("  POST /generate/all - Generate all charts")
    print("  POST /generate/<symbol> - Generate chart for symbol")
    print("\n💡 Usage:")
    print("  1. Run this server locally: python local_chart_server.py")
    print("  2. Generate charts: POST http://localhost:5001/generate/all")
    print("  3. Update your web app to fetch from: http://localhost:5001/chart/<symbol>")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=False)