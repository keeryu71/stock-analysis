#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile Web App for Stock Analysis
Simple web interface that works on phones
"""

import os
import sys
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import threading
import webbrowser
import time

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from stock_config import get_stock_list
from free_extended_hours_fetcher import FreeExtendedHoursAnalyzer
from hybrid_stock_analyzer import HybridStockAnalyzer, HybridOptionsAnalyzer

app = Flask(__name__)

# Mobile-friendly HTML template
MOBILE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Stock Analysis Mobile</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .controls {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #FF9800, #F57C00);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            padding: 20px;
            max-height: 60vh;
            overflow-y: auto;
        }
        
        .stock-card {
            background: #fff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            margin: 10px 0;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .stock-symbol {
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
        }
        
        .stock-price {
            font-size: 16px;
            font-weight: 600;
            color: #4CAF50;
        }
        
        .stock-details {
            font-size: 14px;
            color: #666;
            line-height: 1.4;
        }
        
        .signal {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
            margin: 5px 5px 5px 0;
        }
        
        .signal-buy { background: #d4edda; color: #155724; }
        .signal-hold { background: #fff3cd; color: #856404; }
        .signal-sell { background: #f8d7da; color: #721c24; }
        
        .footer {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            color: #666;
            font-size: 12px;
        }
        
        @media (max-width: 480px) {
            .container {
                margin: 5px;
                border-radius: 10px;
            }
            
            .header h1 {
                font-size: 20px;
            }
            
            .btn {
                padding: 12px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Stock Analysis</h1>
            <p>Real-time analysis on your mobile device</p>
            <p>{{ stock_count }} stocks • Updated {{ timestamp }}</p>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="runStockAnalysis()">
                📈 Stock Analysis
            </button>
            <button class="btn btn-secondary" onclick="runOptionsAnalysis()">
                💰 Options Analysis
            </button>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            <div class="spinner"></div>
            <p>Analyzing markets...</p>
        </div>
        
        <div id="results" class="results"></div>
        
        <div class="footer">
            <p>🔄 Tap refresh to update • 24/7 Data from Free APIs (Yahoo, Finnhub, Alpha Vantage)</p>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
            document.querySelectorAll('.btn').forEach(btn => btn.disabled = true);
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.querySelectorAll('.btn').forEach(btn => btn.disabled = false);
        }
        
        function runStockAnalysis() {
            showLoading();
            fetch('/api/stock-analysis')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    hideLoading();
                    if (data.success) {
                        displayStockResults(data);
                    } else {
                        document.getElementById('results').innerHTML =
                            '<div class="stock-card"><p style="color: red;">❌ API Error: ' + data.error + '</p></div>';
                    }
                })
                .catch(error => {
                    hideLoading();
                    document.getElementById('results').innerHTML =
                        '<div class="stock-card"><p style="color: red;">❌ Network Error: ' + error.message + '</p></div>';
                });
        }
        
        function runOptionsAnalysis() {
            showLoading();
            fetch('/api/options-analysis')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    hideLoading();
                    if (data.success) {
                        displayOptionsResults(data);
                    } else {
                        document.getElementById('results').innerHTML =
                            '<div class="stock-card"><p style="color: red;">❌ API Error: ' + data.error + '</p></div>';
                    }
                })
                .catch(error => {
                    hideLoading();
                    document.getElementById('results').innerHTML =
                        '<div class="stock-card"><p style="color: red;">❌ Network Error: ' + error.message + '</p></div>';
                });
        }
        
        function displayStockResults(data) {
            let html = '<h3 style="margin-bottom: 15px;">📊 Stock Analysis Results</h3>';
            
            if (data.results && data.results.length > 0) {
                // Count data sources
                let robinhoodCount = 0;
                let yahooCount = 0;
                let otherCount = 0;
                
                data.results.forEach(stock => {
                    if (stock.data_source && stock.data_source.startsWith('free_api_')) {
                        robinhoodCount++; // Reuse counter for free APIs
                    } else if (stock.data_source === 'real_price') {
                        yahooCount++;
                    } else {
                        otherCount++;
                    }
                });
                
                // Add data source info
                let statusText = '';
                if (robinhoodCount > 0) {
                    statusText = `🆓 ${robinhoodCount} from Free APIs (24/7)`;
                    if (yahooCount > 0) statusText += `, ${yahooCount} from Yahoo Finance`;
                } else if (yahooCount > 0) {
                    statusText = `📡 ${yahooCount} from Yahoo Finance`;
                } else {
                    statusText = `⚠️ Limited data available`;
                }
                
                html += `<p style="font-size: 12px; color: #4CAF50; margin-bottom: 10px;">${statusText}</p>`;
                
                data.results.forEach(stock => {
                    const signalClass = stock.score >= 0.8 ? 'signal-buy' :
                                       stock.score >= 0.6 ? 'signal-hold' : 'signal-sell';
                    const signalText = stock.score >= 0.8 ? '🚀 STRONG BUY' :
                                      stock.score >= 0.6 ? '⚡ GOOD SETUP' : '⏳ WAIT';
                    
                    // Icon based on data source
                    let dataIcon = '📡';
                    if (stock.data_source && stock.data_source.startsWith('free_api_')) {
                        dataIcon = '🆓';
                    } else if (stock.data_source === 'real_price') {
                        dataIcon = '📡';
                    }
                    
                    // Add market status for Robinhood data
                    let marketStatus = '';
                    if (stock.market_status && stock.market_status !== 'unknown') {
                        const statusEmoji = {
                            'regular_hours': '🟢',
                            'pre_market': '🟡',
                            'after_hours': '🟠',
                            'weekend': '🔴',
                            'closed': '🔴'
                        };
                        marketStatus = ` ${statusEmoji[stock.market_status] || '⚪'}`;
                    }
                    
                    html += `
                        <div class="stock-card">
                            <div class="stock-header">
                                <span class="stock-symbol">${dataIcon} ${stock.symbol}${marketStatus}</span>
                                <span class="stock-price">$${stock.price.toFixed(2)}</span>
                            </div>
                            <div class="signal ${signalClass}">${signalText} (${(stock.score * 100).toFixed(0)}%)</div>
                            <div class="stock-details">
                                RSI: ${stock.rsi.toFixed(0)} •
                                Volume: ${stock.volume_ratio.toFixed(1)}x •
                                ${stock.top_entries.length > 0 ?
                                  `Entry: $${stock.top_entries[0].price.toFixed(2)}` : 'No entry'}
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<div class="stock-card"><p>No stock data available</p></div>';
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        function displayOptionsResults(data) {
            let html = '<h3 style="margin-bottom: 15px;">💰 Options Analysis Results</h3>';
            
            if (data.results && data.results.length > 0) {
                // Count real vs mock options data
                let realCount = 0;
                let mockCount = 0;
                data.results.forEach(stock => {
                    if (stock.data_source === 'real_options') realCount++;
                    else mockCount++;
                });
                
                // Add data source info
                if (realCount > 0 && mockCount > 0) {
                    html += `<p style="font-size: 12px; color: #666; margin-bottom: 10px;">
                        📡 ${realCount} real options, ${mockCount} demo data</p>`;
                } else if (realCount > 0) {
                    html += `<p style="font-size: 12px; color: #4CAF50; margin-bottom: 10px;">
                        📡 All options are real-time</p>`;
                } else {
                    html += `<p style="font-size: 12px; color: #FF9800; margin-bottom: 10px;">
                        📡 Demo options data (market closed)</p>`;
                }
                
                data.results.forEach(stock => {
                    if (stock.put_analysis && stock.put_analysis.length > 0) {
                        const bestPut = stock.put_analysis[0];
                        const qualityStars = '⭐'.repeat(Math.ceil(stock.quality_score * 5));
                        
                        const dataIcon = stock.data_source === 'real_options' ? '📡' : '🎯';
                        
                        html += `
                            <div class="stock-card">
                                <div class="stock-header">
                                    <span class="stock-symbol">${dataIcon} ${stock.symbol}</span>
                                    <span class="stock-price">$${stock.current_price.toFixed(2)}</span>
                                </div>
                                <div class="stock-details">
                                    <strong>Best Put: $${bestPut.strike.toFixed(2)}</strong><br>
                                    Premium: $${bestPut.bid.toFixed(2)} •
                                    Return: ${(bestPut.annualized_return * 100).toFixed(1)}%<br>
                                    Quality: ${qualityStars} •
                                    Days: ${bestPut.days_to_exp}d
                                </div>
                            </div>
                        `;
                    }
                });
            } else {
                html += '<div class="stock-card"><p>No options data available</p></div>';
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        // Auto-refresh every 5 minutes
        setInterval(() => {
            if (document.getElementById('results').innerHTML.trim() !== '') {
                location.reload();
            }
        }, 300000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main mobile interface."""
    stocks = get_stock_list()
    return render_template_string(MOBILE_TEMPLATE, 
                                stock_count=len(stocks),
                                timestamp=datetime.now().strftime('%H:%M'))

@app.route('/api/stock-analysis')
def api_stock_analysis():
    """API endpoint for stock analysis."""
    try:
        print("🔍 Starting 24/7 stock analysis...")
        
        # Try free extended hours APIs first
        try:
            free_analyzer = FreeExtendedHoursAnalyzer()
            print("✅ FreeExtendedHoursAnalyzer initialized")
            results = free_analyzer.run_analysis()
            print(f"✅ Free API analysis complete, got {len(results)} results")
            
            # If we got good results from free APIs, use them
            if results and len(results) >= 5:  # At least 5 stocks
                print("🎯 Using free extended hours data")
            else:
                raise Exception("Insufficient free API data")
                
        except Exception as e:
            print(f"⚠️ Free APIs failed ({e}), falling back to Yahoo Finance...")
            analyzer = HybridStockAnalyzer()
            results = analyzer.run_analysis()
            print(f"✅ Yahoo Finance fallback complete, got {len(results)} results")
        
        # Format results for mobile
        mobile_results = []
        for result in results:
            mobile_results.append({
                'symbol': result.get('symbol', 'N/A'),
                'price': result.get('price', 0),
                'score': result.get('score', 0),
                'rsi': result.get('rsi', 0),
                'volume_ratio': result.get('volume_ratio', 0),
                'top_entries': result.get('top_entries', []),
                'data_source': result.get('data_source', 'unknown'),
                'market_status': result.get('market_status', 'unknown'),
                'price_source': result.get('price_source', 'unknown')
            })
        
        print(f"✅ Formatted {len(mobile_results)} results for mobile")
        
        return jsonify({
            'success': True,
            'results': mobile_results,
            'timestamp': datetime.now().isoformat(),
            'count': len(mobile_results)
        })
    
    except Exception as e:
        error_msg = f"Stock analysis error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

@app.route('/api/options-analysis')
def api_options_analysis():
    """API endpoint for options analysis."""
    try:
        print("🔍 Starting hybrid options analysis...")
        analyzer = HybridOptionsAnalyzer()
        print("✅ HybridOptionsAnalyzer initialized")
        
        results = analyzer.run_real_time_analysis()
        print(f"✅ Hybrid options analysis complete, got {len(results)} results")
        
        # Format results for mobile
        mobile_results = []
        for result in results:
            mobile_results.append({
                'symbol': result.get('symbol', 'N/A'),
                'current_price': result.get('current_price', 0),
                'quality_score': result.get('quality_score', 0),
                'put_analysis': result.get('put_analysis', []),
                'days_to_expiration': result.get('days_to_expiration', 0)
            })
        
        print(f"✅ Formatted {len(mobile_results)} options results for mobile")
        
        return jsonify({
            'success': True,
            'results': mobile_results,
            'timestamp': datetime.now().isoformat(),
            'count': len(mobile_results)
        })
    
    except Exception as e:
        error_msg = f"Options analysis error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'details': traceback.format_exc()
        }), 500

@app.route('/api/test')
def api_test():
    """Simple test endpoint to verify API is working."""
    try:
        stocks = get_stock_list()
        return jsonify({
            'success': True,
            'message': 'API is working!',
            'stock_count': len(stocks),
            'stocks': stocks[:5],  # First 5 stocks
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-stock')
def api_test_stock():
    """Test the simplified stock analyzer directly."""
    try:
        from simple_stock_analyzer import SimpleStockAnalyzer
        analyzer = SimpleStockAnalyzer()
        
        # Test with just TSLA
        result = analyzer.analyze_stock('TSLA')
        
        return jsonify({
            'success': True,
            'message': 'Stock analyzer test',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/test-options')
def api_test_options():
    """Test the simplified options analyzer directly."""
    try:
        from simple_stock_analyzer import SimpleOptionsAnalyzer
        analyzer = SimpleOptionsAnalyzer()
        
        # Test with just TSLA
        result = analyzer.get_basic_options_data('TSLA')
        
        return jsonify({
            'success': True,
            'message': 'Options analyzer test',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/test-mock')
def api_test_mock():
    """Test the mock analyzers directly."""
    try:
        from mock_stock_analyzer import MockStockAnalyzer, MockOptionsAnalyzer
        
        # Test mock stock analyzer
        stock_analyzer = MockStockAnalyzer()
        stock_result = stock_analyzer.analyze_stock('TSLA')
        
        # Test mock options analyzer
        options_analyzer = MockOptionsAnalyzer()
        options_result = options_analyzer.get_basic_options_data('TSLA')
        
        return jsonify({
            'success': True,
            'message': 'Mock analyzers test',
            'stock_result': stock_result,
            'options_result': options_result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/test-hybrid')
def api_test_hybrid():
    """Test the hybrid analyzers directly."""
    try:
        from hybrid_stock_analyzer import HybridStockAnalyzer, HybridOptionsAnalyzer
        
        # Test hybrid stock analyzer
        stock_analyzer = HybridStockAnalyzer()
        stock_result = stock_analyzer.analyze_stock('TSLA')
        
        # Test hybrid options analyzer
        options_analyzer = HybridOptionsAnalyzer()
        options_result = options_analyzer.get_real_options_data('TSLA')
        
        return jsonify({
            'success': True,
            'message': 'Hybrid analyzers test (real prices + calculated indicators)',
            'stock_result': stock_result,
            'options_result': options_result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/test-free-apis')
def api_test_free_apis():
    """Test the free extended hours APIs directly."""
    try:
        from free_extended_hours_fetcher import FreeExtendedHoursAnalyzer, FreeExtendedHoursDataFetcher
        
        # Test free data fetcher
        fetcher = FreeExtendedHoursDataFetcher()
        quote_result = fetcher.get_best_quote('TSLA')
        
        # Test free analyzer
        analyzer = FreeExtendedHoursAnalyzer()
        if quote_result:
            analysis_result = analyzer.analyze_stock_from_quote(quote_result)
        else:
            analysis_result = None
        
        return jsonify({
            'success': True,
            'message': 'Free extended hours APIs test',
            'quote_result': quote_result,
            'analysis_result': analysis_result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

def open_browser():
    """Open browser after a short delay."""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def main():
    """Run the mobile web app."""
    # Get port from environment (for cloud deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Mobile Stock Analysis App...")
    
    # Only open browser if running locally
    if os.environ.get('PORT') is None:
        print("📱 Opening in your default browser...")
        print("🌐 Access from phone: http://[YOUR_COMPUTER_IP]:5000")
        print("💡 To stop: Press Ctrl+C")
        # Open browser in a separate thread
        threading.Thread(target=open_browser, daemon=True).start()
    else:
        print("☁️ Running in cloud mode...")
        print(f"🌐 Port: {port}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()