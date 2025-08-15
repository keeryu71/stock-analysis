#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock List Management Utility
Easy way to add/remove stocks from the centralized configuration
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from stock_config import get_stock_list, add_stock, remove_stock, print_stock_list

def main():
    """Interactive stock management utility."""
    print("🎯 STOCK LIST MANAGEMENT UTILITY")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. View current stock list")
        print("2. Add a stock")
        print("3. Remove a stock")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print_stock_list()
            
        elif choice == '2':
            symbol = input("Enter stock symbol to add: ").strip().upper()
            if symbol:
                add_stock(symbol)
                print(f"\n✅ Updated! All analysis systems will now include {symbol}")
            else:
                print("❌ Invalid symbol")
                
        elif choice == '3':
            symbol = input("Enter stock symbol to remove: ").strip().upper()
            if symbol:
                remove_stock(symbol)
                print(f"\n✅ Updated! All analysis systems will no longer include {symbol}")
            else:
                print("❌ Invalid symbol")
                
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()