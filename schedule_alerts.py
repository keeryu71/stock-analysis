#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSLA Alert Scheduler
Runs automated alerts at specified times using schedule library
"""

import schedule
import time
import os
import sys
from datetime import datetime
from automated_tsla_alerts import TSLAAlertSystem

def run_daily_alert():
    """Run the daily TSLA alert."""
    print(f"\n🕘 Scheduled Alert Triggered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        alert_system = TSLAAlertSystem()
        results = alert_system.send_alerts()
        
        success_count = sum(results.values())
        print(f"✅ Alert completed: {success_count} channels successful")
        
    except Exception as e:
        print(f"❌ Alert failed: {e}")

def main():
    """Main scheduler function."""
    print("🚀 TSLA Alert Scheduler Starting...")
    print(f"📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Schedule daily alert at 9:00 AM
    schedule.every().day.at("09:00").do(run_daily_alert)
    
    # Optional: Add additional alert times
    # schedule.every().day.at("15:30").do(run_daily_alert)  # Market close
    # schedule.every().monday.at("08:30").do(run_daily_alert)  # Pre-market Monday
    
    print("⏰ Scheduled daily TSLA alerts at 9:00 AM")
    print("📱 Press Ctrl+C to stop the scheduler")
    print("🔄 Scheduler is running...")
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")

if __name__ == "__main__":
    main()