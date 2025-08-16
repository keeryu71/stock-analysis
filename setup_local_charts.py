#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script for Local Chart Generation
Helps you set up and run the local chart server for real data charts
"""

import os
import sys
import subprocess
import time
import requests
import threading

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'flask-cors', 'schedule', 'yfinance', 'matplotlib', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All dependencies installed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def test_yfinance():
    """Test if yfinance works locally."""
    print("\n🧪 Testing yfinance locally...")
    
    try:
        import yfinance as yf
        
        # Test with a simple stock
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="5d")
        
        if not data.empty:
            print(f"✅ yfinance works! Got {len(data)} days of AAPL data")
            print(f"   Latest price: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("⚠️ yfinance returned empty data")
            return False
            
    except Exception as e:
        print(f"❌ yfinance test failed: {e}")
        return False

def start_local_server():
    """Start the local chart server."""
    print("\n🚀 Starting local chart server...")
    
    try:
        # Run the local chart server
        process = subprocess.Popen([
            sys.executable, 'local_chart_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give it time to start
        time.sleep(3)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:5001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Local chart server is running!")
                print("🌐 Server URL: http://localhost:5001")
                return process
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def generate_sample_charts():
    """Generate charts for a few sample stocks."""
    print("\n📊 Generating sample charts...")
    
    sample_stocks = ['AAPL', 'MSFT', 'TSLA', 'CRM', 'NVDA']
    
    for stock in sample_stocks:
        try:
            print(f"📈 Generating chart for {stock}...")
            response = requests.post(f"http://localhost:5001/generate/{stock}", timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {stock} chart generated")
            else:
                print(f"⚠️ {stock} chart failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error generating {stock} chart: {e}")
        
        time.sleep(1)  # Small delay between requests

def test_chart_access():
    """Test accessing generated charts."""
    print("\n🧪 Testing chart access...")
    
    try:
        response = requests.get("http://localhost:5001/chart/AAPL", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('chart'):
                print("✅ Chart access works! Charts are ready for the web app.")
                return True
            else:
                print("⚠️ Chart response format issue")
                return False
        else:
            print(f"❌ Chart access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chart access test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🏠 Local Chart Generation Setup")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return False
    
    # Step 2: Test yfinance
    if not test_yfinance():
        print("\n❌ Setup failed: yfinance not working")
        return False
    
    # Step 3: Start server
    server_process = start_local_server()
    if not server_process:
        print("\n❌ Setup failed: Could not start server")
        return False
    
    try:
        # Step 4: Generate sample charts
        generate_sample_charts()
        
        # Step 5: Test chart access
        if test_chart_access():
            print("\n🎉 Setup Complete!")
            print("\n📋 Next Steps:")
            print("1. Keep this terminal open (server is running)")
            print("2. Open your web app: http://localhost:5000")
            print("3. Click on any stock's '📊 Chart' button")
            print("4. Charts will now display real market data!")
            print("\n💡 Tips:")
            print("- Charts update automatically every hour")
            print("- Generate all charts: POST http://localhost:5001/generate/all")
            print("- Check server status: http://localhost:5001/health")
            print("\n⏹️ To stop: Press Ctrl+C")
            
            # Keep the server running
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping local chart server...")
                server_process.terminate()
                
        else:
            print("\n⚠️ Setup completed with warnings")
            
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    main()