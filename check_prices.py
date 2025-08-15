import sys
sys.path.append('src')
from data.data_loader import DataLoader
from datetime import datetime, timedelta

loader = DataLoader()
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

print(f"Checking data from {start_date} to {end_date}")
print(f"Current time: {datetime.now()}")

data = loader.fetch_stock_data(['TSLA', 'AVGO'], start_date, end_date)

for symbol in ['TSLA', 'AVGO']:
    if symbol in data:
        df = data[symbol]
        print(f"\n{symbol}:")
        print(f"  Latest date in data: {df.index[-1]}")
        print(f"  Latest price: ${df['close'].iloc[-1]:.2f}")
        print(f"  Data points: {len(df)}")
    else:
        print(f"\n{symbol}: No data found")