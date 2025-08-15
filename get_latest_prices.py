import sys
sys.path.append('src')
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def get_latest_prices(symbols):
    """Get the most recent available prices for stocks."""
    print(f"🔍 Fetching latest prices at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            
            # Method 1: Try to get today's data with extended end date
            end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            
            # Get historical data
            hist = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if not hist.empty:
                latest_date = hist.index[-1]
                latest_price = hist['Close'].iloc[-1]
                
                # Check if we have today's data
                today = datetime.now().date()
                latest_date_only = latest_date.date()
                
                print(f"📊 {symbol}:")
                print(f"   Latest Date: {latest_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   Latest Price: ${latest_price:.2f}")
                print(f"   Is Today's Data: {'✅ YES' if latest_date_only == today else '❌ NO'}")
                
                # Try to get more recent data using info() method
                try:
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    if current_price and current_price != latest_price:
                        print(f"   Real-time Price: ${current_price:.2f} (from ticker.info)")
                        results[symbol] = {
                            'historical_price': latest_price,
                            'historical_date': latest_date,
                            'current_price': current_price,
                            'has_today_data': latest_date_only == today
                        }
                    else:
                        results[symbol] = {
                            'historical_price': latest_price,
                            'historical_date': latest_date,
                            'current_price': latest_price,
                            'has_today_data': latest_date_only == today
                        }
                except:
                    results[symbol] = {
                        'historical_price': latest_price,
                        'historical_date': latest_date,
                        'current_price': latest_price,
                        'has_today_data': latest_date_only == today
                    }
                
                print(f"   Data Points: {len(hist)}")
                print()
            else:
                print(f"❌ {symbol}: No data available")
                print()
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            print()
    
    return results

if __name__ == "__main__":
    # Test with a few symbols
    symbols = ['TSLA', 'AVGO', 'NVDA', 'AMD']
    
    print("🚀 LATEST STOCK PRICE CHECKER")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Market Status: {'After Hours' if datetime.now().hour >= 13 else 'Pre-Market'} (PST)")
    print()
    
    results = get_latest_prices(symbols)
    
    # Summary
    print("📈 SUMMARY:")
    print("=" * 60)
    today_count = sum(1 for r in results.values() if r.get('has_today_data', False))
    print(f"Stocks with today's data: {today_count}/{len(results)}")
    
    for symbol, data in results.items():
        status = "📅 TODAY" if data.get('has_today_data', False) else "📆 YESTERDAY"
        print(f"{symbol}: ${data['current_price']:.2f} {status}")