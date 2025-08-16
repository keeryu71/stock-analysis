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
from chart_generator import generate_stock_chart

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
                🏆 Find Top 10 Best Setups
            </button>
            <button class="btn btn-secondary" onclick="runOptionsAnalysis()">
                💰 Top 10 Best Options Setups
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
            let html = '<h3 style="margin-bottom: 15px;">🏆 Top 10 Best Stock Setups</h3>';
            
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
                
                // Add analysis info
                let statusText = `🔍 Analyzed top 50 popular stocks, showing ${data.results.length} best setups`;
                if (robinhoodCount > 0) {
                    statusText += ` • 🆓 ${robinhoodCount} from Free APIs (24/7)`;
                    if (yahooCount > 0) statusText += `, ${yahooCount} from Yahoo Finance`;
                } else if (yahooCount > 0) {
                    statusText += ` • 📡 ${yahooCount} from Yahoo Finance`;
                }
                
                html += `<p style="font-size: 12px; color: #4CAF50; margin-bottom: 10px;">${statusText}</p>`;
                
                data.results.forEach(stock => {
                    const signalClass = stock.score >= 0.8 ? 'signal-buy' :
                                       stock.score >= 0.6 ? 'signal-hold' : 'signal-sell';
                    const signalText = stock.score >= 0.8 ? '🚀 STRONG BUY' :
                                      stock.score >= 0.6 ? '⚡ GOOD SETUP' : '⏳ WAIT';
                    
                    // Icon based on data source
                    let dataIcon = '🆓';
                    if (stock.data_source && stock.data_source.startsWith('free_api_')) {
                        dataIcon = '🆓';
                    } else if (stock.data_source === 'real_price') {
                        dataIcon = '📡';
                    }
                    
                    // RSI-based color indicator (more useful than market status)
                    let rsiIndicator = '';
                    if (stock.rsi !== undefined) {
                        if (stock.rsi < 20) {
                            rsiIndicator = ' 🔴'; // Very oversold - extreme
                        } else if (stock.rsi < 30) {
                            rsiIndicator = ' 🟠'; // Oversold - potential buy opportunity
                        } else if (stock.rsi <= 50) {
                            rsiIndicator = ' 🟢'; // Healthy range - good
                        } else if (stock.rsi <= 70) {
                            rsiIndicator = ' 🟡'; // Slightly overbought - caution
                        } else if (stock.rsi <= 80) {
                            rsiIndicator = ' 🟠'; // Overbought - warning
                        } else {
                            rsiIndicator = ' 🔴'; // Very overbought - avoid
                        }
                    } else {
                        rsiIndicator = ' ⚪'; // No RSI data
                    }
                    
                    // RSI trend emoji - match the circle indicator logic
                    let rsiEmoji = '⚪'; // Default
                    if (stock.rsi !== undefined) {
                        if (stock.rsi < 20) {
                            rsiEmoji = '🔴'; // Very oversold - extreme
                        } else if (stock.rsi < 30) {
                            rsiEmoji = '🟠'; // Oversold - potential buy opportunity
                        } else if (stock.rsi <= 50) {
                            rsiEmoji = '🟢'; // Healthy range - good
                        } else if (stock.rsi <= 70) {
                            rsiEmoji = '🟡'; // Slightly overbought - caution
                        } else if (stock.rsi <= 80) {
                            rsiEmoji = '🟠'; // Overbought - warning
                        } else {
                            rsiEmoji = '🔴'; // Very overbought - avoid
                        }
                    }
                    
                    // Volume trend emoji
                    const volumeEmoji = stock.volume_trend === 'Strong' ? '🔥' :
                                       stock.volume_trend === 'Above Average' ? '📈' :
                                       stock.volume_trend === 'Average' ? '➡️' : '📉';
                    
                    // Build Fibonacci levels display
                    let fibDisplay = '';
                    if (stock.fibonacci_levels && Object.keys(stock.fibonacci_levels).length > 0) {
                        const fibKeys = ['23.6', '38.2', '50.0', '61.8', '78.6'];
                        fibDisplay = fibKeys.map(key =>
                            stock.fibonacci_levels[key] ?
                            `${key}%: $${stock.fibonacci_levels[key].toFixed(2)}` : ''
                        ).filter(x => x).join(' • ');
                    }
                    
                    // Build entry points display
                    let entryDisplay = '';
                    if (stock.top_entries && stock.top_entries.length > 0) {
                        entryDisplay = stock.top_entries.slice(0, 2).map(entry =>
                            `${entry.level}: $${entry.price.toFixed(2)} (${entry.timeframe})`
                        ).join('<br>');
                    }
                    
                    html += `
                        <div class="stock-card">
                            <div class="stock-header">
                                <span class="stock-symbol">
                                    ${dataIcon} ${stock.symbol}${rsiIndicator}
                                    <a href="/chart/${stock.symbol}"
                                       style="margin-left: 8px; text-decoration: none;
                                              background: #4CAF50; color: white; padding: 4px 8px;
                                              border-radius: 4px; font-size: 12px;">📊 Chart</a>
                                </span>
                                <span class="stock-price">$${stock.price.toFixed(2)}</span>
                            </div>
                            <div class="signal ${signalClass}">${signalText} (${(stock.score * 100).toFixed(0)}%)</div>
                            
                            <div class="stock-details" style="margin-top: 10px;">
                                <strong>📈 Technical Analysis:</strong><br>
                                ${rsiEmoji} RSI: ${stock.rsi.toFixed(0)} (${stock.rsi_trend}) •
                                ${volumeEmoji} Volume: ${stock.volume_ratio.toFixed(1)}x (${stock.volume_trend})<br>
                                📊 SMA20: $${stock.sma_20.toFixed(2)} • SMA50: $${stock.sma_50.toFixed(2)}<br>
                                
                                ${fibDisplay ? `<strong>🌀 Fibonacci Levels:</strong><br>${fibDisplay}<br>` : ''}
                                
                                ${entryDisplay ? `<strong>🎯 Optimal Entry Points:</strong><br>${entryDisplay}<br>` : ''}
                                
                                <div style="margin-top: 8px; text-align: center;">
                                    <a href="/chart/${stock.symbol}"
                                       style="display: inline-block; background: linear-gradient(45deg, #2196F3, #21CBF3);
                                              color: white; padding: 8px 16px; border-radius: 8px;
                                              text-decoration: none; font-weight: 600; font-size: 14px;">
                                        📊 View Custom Chart
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<div class="stock-card"><p>No good setups found in top 50 stocks. Market conditions may not be favorable for trading right now.</p></div>';
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        function displayOptionsResults(data) {
            let html = '<h3 style="margin-bottom: 15px;">💰 Top 10 Best Options Setups</h3>';
            
            // Check if market is closed
            if (data.message && data.market_status) {
                const statusEmoji = {
                    'weekend': '🔴',
                    'closed': '🔴',
                    'regular_hours': '🟢',
                    'pre_market': '🟡',
                    'after_hours': '🟠'
                };
                
                html += `<div class="stock-card">
                    <p style="text-align: center; color: #666;">
                        ${statusEmoji[data.market_status] || '⚪'} ${data.message}
                    </p>
                    <p style="text-align: center; font-size: 12px; color: #999; margin-top: 10px;">
                        Options trading is only available during market hours
                    </p>
                </div>`;
                
                document.getElementById('results').innerHTML = html;
                return;
            }
            
            if (data.results && data.results.length > 0) {
                // Count data sources
                let realCount = 0;
                let calculatedCount = 0;
                let mockCount = 0;
                
                data.results.forEach(stock => {
                    if (stock.data_source === 'recent_options_data') {
                        realCount++;
                    } else if (stock.data_source === 'calculated_options') {
                        calculatedCount++;
                    } else {
                        mockCount++;
                    }
                });
                
                // Add analysis info
                let statusText = `🔍 Analyzed top 50 popular stocks, showing ${data.results.length} best options setups`;
                if (realCount > 0) {
                    statusText += ` • 📡 ${realCount} real options`;
                    if (calculatedCount > 0) statusText += `, ${calculatedCount} calculated`;
                    if (mockCount > 0) statusText += `, ${mockCount} demo`;
                } else if (calculatedCount > 0) {
                    statusText += ` • 🎯 ${calculatedCount} calculated options`;
                    if (mockCount > 0) statusText += `, ${mockCount} demo`;
                } else if (mockCount > 0) {
                    statusText += ` • 🎯 ${mockCount} demo options`;
                }
                
                html += `<p style="font-size: 12px; color: #4CAF50; margin-bottom: 10px;">${statusText}</p>`;
                
                data.results.forEach((stock, index) => {
                    if (stock.put_analysis && stock.put_analysis.length > 0) {
                        const bestPut = stock.put_analysis[0];
                        const qualityStars = '⭐'.repeat(Math.ceil(stock.quality_score * 5));
                        const rankingScore = stock.ranking_score ? (stock.ranking_score * 100).toFixed(0) : 'N/A';
                        
                        // Data source icon
                        let dataIcon = '🎯';
                        if (stock.data_source === 'recent_options_data') {
                            dataIcon = '📡';
                        } else if (stock.data_source === 'calculated_options') {
                            dataIcon = '🎯';
                        }
                        
                        // Quality indicator based on ranking score
                        let qualityIndicator = '';
                        if (stock.ranking_score >= 0.8) {
                            qualityIndicator = '🟢'; // Excellent
                        } else if (stock.ranking_score >= 0.6) {
                            qualityIndicator = '🟡'; // Good
                        } else if (stock.ranking_score >= 0.4) {
                            qualityIndicator = '🟠'; // Fair
                        } else {
                            qualityIndicator = '🔴'; // Poor
                        }
                        
                        // Calculate potential profit
                        const premium = bestPut.last_price || bestPut.bid;
                        const annualReturn = (bestPut.annualized_return * 100).toFixed(1);
                        const daysReturn = ((bestPut.annualized_return * bestPut.days_to_exp / 365) * 100).toFixed(1);
                        
                        html += `
                            <div class="stock-card">
                                <div class="stock-header">
                                    <span class="stock-symbol">
                                        ${dataIcon} #${index + 1} ${stock.symbol}${qualityIndicator}
                                    </span>
                                    <span class="stock-price">$${stock.current_price.toFixed(2)}</span>
                                </div>
                                <div class="signal signal-buy">🚀 QUALITY SCORE: ${rankingScore}%</div>
                                
                                <div class="stock-details" style="margin-top: 10px;">
                                    <strong>💰 Best Put Option:</strong><br>
                                    Strike: $${bestPut.strike.toFixed(2)} • Premium: $${premium.toFixed(2)}<br>
                                    📈 Returns: ${daysReturn}% (${bestPut.days_to_exp}d) • ${annualReturn}% annual<br>
                                    📊 Volume: ${bestPut.volume || 'N/A'} • Quality: ${qualityStars}<br>
                                    
                                    <strong>🎯 Strategy:</strong><br>
                                    Cash-secured put at $${bestPut.strike.toFixed(2)} strike<br>
                                    Collect $${premium.toFixed(2)} premium per contract<br>
                                    
                                    <div style="margin-top: 8px; text-align: center;">
                                        <a href="/chart/${stock.symbol}"
                                           style="display: inline-block; background: linear-gradient(45deg, #FF9800, #F57C00);
                                                  color: white; padding: 8px 16px; border-radius: 8px;
                                                  text-decoration: none; font-weight: 600; font-size: 14px;">
                                            📊 View Options Chart
                                        </a>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                });
            } else {
                html += '<div class="stock-card"><p>No good options setups found in top 50 stocks. Market conditions may not be favorable for options trading right now.</p></div>';
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

# Chart page template
CHART_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 {{ symbol }} - Technical Analysis Chart</title>
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
        
        .back-btn {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            display: inline-block;
        }
        
        .back-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .chart-container {
            padding: 20px;
            text-align: center;
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            text-align: center;
            padding: 40px;
            color: #F44336;
        }
        
        .chart-info {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            font-size: 14px;
            color: #666;
            text-align: center;
        }
        
        @media (max-width: 480px) {
            .container {
                margin: 5px;
                border-radius: 10px;
            }
            
            .header h1 {
                font-size: 20px;
            }
            
            .back-btn {
                top: 15px;
                left: 15px;
                padding: 8px 12px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="javascript:history.back()" class="back-btn">← Back</a>
            <h1>📊 {{ symbol }} Chart</h1>
            <p>Technical Analysis with Fibonacci, RSI, Volume & Entry Points</p>
        </div>
        
        <div id="loading" class="loading">
            <div class="spinner"></div>
            <p>Generating custom chart...</p>
        </div>
        
        <div id="chart-container" class="chart-container" style="display: none;">
            <img id="chart-image" class="chart-image" alt="{{ symbol }} Technical Analysis Chart">
        </div>
        
        <div id="error" class="error" style="display: none;">
            <h3>❌ Chart Generation Failed</h3>
            <p id="error-message">Unable to generate chart. Please try again.</p>
        </div>
        
        <div class="chart-info">
            <p>📈 Custom chart with Fibonacci levels, RSI, volume analysis, and optimal entry points</p>
            <p>🔄 Chart updates with latest market data</p>
        </div>
    </div>

    <script>
        function loadChart() {
            fetch('/api/chart/{{ symbol }}')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        const chartImage = document.getElementById('chart-image');
                        chartImage.src = 'data:image/png;base64,' + data.chart_data;
                        document.getElementById('chart-container').style.display = 'block';
                    } else {
                        document.getElementById('error-message').textContent = data.error || 'Unknown error';
                        document.getElementById('error').style.display = 'block';
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error-message').textContent = 'Network error: ' + error.message;
                    document.getElementById('error').style.display = 'block';
                });
        }
        
        // Load chart when page loads
        window.onload = loadChart;
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
        
        # Format results for mobile with enhanced data
        mobile_results = []
        for result in results:
            mobile_results.append({
                'symbol': result.get('symbol', 'N/A'),
                'price': result.get('price', 0),
                'score': result.get('score', 0),
                'rsi': result.get('rsi', 0),
                'rsi_trend': result.get('rsi_trend', 'Unknown'),
                'volume_ratio': result.get('volume_ratio', 0),
                'volume_trend': result.get('volume_trend', 'Unknown'),
                'sma_20': result.get('sma_20', 0),
                'sma_50': result.get('sma_50', 0),
                'fibonacci_levels': result.get('fibonacci_levels', {}),
                'fibonacci_level': result.get('fibonacci_level', 'unknown'),
                'fibonacci_score': result.get('fibonacci_score', 0),
                'macd_line': result.get('macd_line', 0),
                'macd_signal': result.get('macd_signal', 'neutral'),
                'macd_score': result.get('macd_score', 0),
                'top_entries': result.get('top_entries', []),
                'chart_url': result.get('chart_url', f"https://finance.yahoo.com/chart/{result.get('symbol', 'TSLA')}"),
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
        print("🔍 Starting 24/7 options analysis using closing prices...")
        
        # Get market status for informational purposes only
        from free_extended_hours_fetcher import FreeExtendedHoursDataFetcher
        fetcher = FreeExtendedHoursDataFetcher()
        market_status = fetcher.get_current_market_status()
        
        print(f"📊 Market status: {market_status} - proceeding with options analysis using most recent closing data")
        analyzer = HybridOptionsAnalyzer()
        print("✅ HybridOptionsAnalyzer initialized")
        
        results = analyzer.run_real_time_analysis()
        print(f"✅ Options analysis complete, got {len(results)} results")
        
        # Format results for mobile with enhanced data
        mobile_results = []
        for result in results:
            mobile_results.append({
                'symbol': result.get('symbol', 'N/A'),
                'current_price': result.get('current_price', 0),
                'quality_score': result.get('quality_score', 0),
                'ranking_score': result.get('ranking_score', 0),
                'put_analysis': result.get('put_analysis', []),
                'days_to_expiration': result.get('days_to_expiration', 0),
                'data_source': result.get('data_source', 'unknown')
            })
        
        print(f"✅ Formatted {len(mobile_results)} options results for mobile")
        
        return jsonify({
            'success': True,
            'results': mobile_results,
            'market_status': market_status,
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

@app.route('/api/chart/<symbol>')
def api_get_chart(symbol):
    """Generate custom technical analysis chart for a stock."""
    try:
        print(f"🎨 Generating custom chart for {symbol}...")
        
        # Get analysis data for the stock
        try:
            free_analyzer = FreeExtendedHoursAnalyzer()
            results = free_analyzer.run_analysis()
            
            # Find the specific stock's analysis
            analysis_data = None
            for result in results:
                if result.get('symbol') == symbol.upper():
                    analysis_data = result
                    break
                    
        except Exception as e:
            print(f"⚠️ Could not get analysis data for {symbol}: {e}")
            analysis_data = None
        
        # Generate the chart
        chart_base64 = generate_stock_chart(symbol.upper(), analysis_data)
        
        if chart_base64:
            print(f"✅ Chart generated successfully for {symbol}")
            return jsonify({
                'success': True,
                'symbol': symbol.upper(),
                'chart_data': chart_base64,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"❌ Failed to generate chart for {symbol}")
            return jsonify({
                'success': False,
                'error': f'Could not generate chart for {symbol}',
                'symbol': symbol.upper()
            }), 500
            
    except Exception as e:
        error_msg = f"Chart generation error for {symbol}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'symbol': symbol.upper(),
            'details': traceback.format_exc()
        }), 500

@app.route('/chart/<symbol>')
def chart_page(symbol):
    """Display custom chart page for a stock."""
    return render_template_string(CHART_TEMPLATE, symbol=symbol.upper())

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