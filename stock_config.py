#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centralized Stock Configuration
Single source of truth for all stock lists across analysis systems
"""

# TOP 50 POPULAR STOCKS - MASTER LIST
STOCK_LIST = [
    # Mega Cap Tech (FAANG+)
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google/Alphabet
    'AMZN',   # Amazon
    'NVDA',   # NVIDIA
    'META',   # Meta (Facebook)
    'TSLA',   # Tesla
    
    # Large Cap Tech
    'NFLX',   # Netflix
    'AMD',    # Advanced Micro Devices
    'CRM',    # Salesforce
    'ORCL',   # Oracle
    'ADBE',   # Adobe
    'AVGO',   # Broadcom
    'INTC',   # Intel
    'QCOM',   # Qualcomm
    
    # Financial Services
    'JPM',    # JPMorgan Chase
    'BAC',    # Bank of America
    'WFC',    # Wells Fargo
    'GS',     # Goldman Sachs
    'MS',     # Morgan Stanley
    'C',      # Citigroup
    'V',      # Visa
    'MA',     # Mastercard
    'PYPL',   # PayPal
    
    # Healthcare & Pharma
    'JNJ',    # Johnson & Johnson
    'PFE',    # Pfizer
    'UNH',    # UnitedHealth Group
    'ABBV',   # AbbVie
    'MRK',    # Merck
    'TMO',    # Thermo Fisher Scientific
    'ABT',    # Abbott Laboratories
    
    # Consumer & Retail
    'WMT',    # Walmart
    'HD',     # Home Depot
    'PG',     # Procter & Gamble
    'KO',     # Coca-Cola
    'PEP',    # PepsiCo
    'NKE',    # Nike
    'MCD',    # McDonald's
    'SBUX',   # Starbucks
    
    # Energy & Industrials
    'XOM',    # Exxon Mobil
    'CVX',    # Chevron
    'BA',     # Boeing
    'CAT',    # Caterpillar
    'GE',     # General Electric
    
    # Growth & Popular Stocks
    'PLTR',   # Palantir
    'HOOD',   # Robinhood
    'COIN',   # Coinbase
    'SOFI',   # SoFi Technologies
    'RIVN',   # Rivian
    'LCID'    # Lucid Motors
]

# Configuration settings
DEFAULT_DAYS_TO_EXPIRATION = 30  # Target days for options analysis
LOG_FILE_NAME = 'multi_stock_alerts.log'

def get_stock_list():
    """Get the current stock list."""
    return STOCK_LIST.copy()

def add_stock(symbol):
    """Add a stock to the list and save to file."""
    symbol = symbol.upper()
    if symbol not in STOCK_LIST:
        STOCK_LIST.append(symbol)
        _save_stock_list()
        print(f"✅ Added {symbol} to stock list")
    else:
        print(f"⚠️  {symbol} already in stock list")

def remove_stock(symbol):
    """Remove a stock from the list and save to file."""
    symbol = symbol.upper()
    if symbol in STOCK_LIST:
        STOCK_LIST.remove(symbol)
        _save_stock_list()
        print(f"❌ Removed {symbol} from stock list")
    else:
        print(f"⚠️  {symbol} not found in stock list")

def _save_stock_list():
    """Save the current stock list to the file."""
    import os
    
    # Read the current file
    current_file = __file__
    with open(current_file, 'r') as f:
        lines = f.readlines()
    
    # Find the STOCK_LIST section and replace it
    new_lines = []
    in_stock_list = False
    indent = "    "
    
    for line in lines:
        if line.strip().startswith('STOCK_LIST = ['):
            # Start of stock list
            new_lines.append('STOCK_LIST = [\n')
            for stock in STOCK_LIST:
                # Add comment for known stocks
                comments = {
                    'TSLA': 'Tesla',
                    'AMD': 'Advanced Micro Devices',
                    'BMNR': 'Biomerica',
                    'SBET': 'SharpLink Gaming',
                    'MSTR': 'MicroStrategy',
                    'HIMS': 'Hims & Hers Health',
                    'PLTR': 'Palantir',
                    'AVGO': 'Broadcom',
                    'NVDA': 'NVIDIA',
                    'HOOD': 'Robinhood',
                    'COIN': 'Coinbase',
                    'OSCR': 'Oscar Health',
                    'GOOG': 'Google/Alphabet',
                    'UNH': 'UnitedHealth Group',
                    'MSFT': 'Microsoft',
                    'SOFI': 'SoFi Technologies'
                }
                comment = comments.get(stock, stock)
                new_lines.append(f"{indent}'{stock}',   # {comment}\n")
            new_lines.append(']\n')
            in_stock_list = True
        elif in_stock_list and line.strip() == ']':
            # End of stock list - already added above
            in_stock_list = False
        elif not in_stock_list:
            # Outside stock list, keep original line
            new_lines.append(line)
        # Skip lines inside the old stock list
    
    # Write the updated file
    with open(current_file, 'w') as f:
        f.writelines(new_lines)

def print_stock_list():
    """Print the current stock list."""
    print(f"📊 Current Stock List ({len(STOCK_LIST)} stocks):")
    for i, stock in enumerate(STOCK_LIST, 1):
        print(f"  {i:2d}. {stock}")

if __name__ == "__main__":
    print_stock_list()