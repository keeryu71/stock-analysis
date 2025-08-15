#!/bin/bash
# Setup script for daily multi-stock alerts

echo "🚀 Setting up Multi-Stock Alert System..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "📁 Project directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHON_PATH"
echo "📈 Stocks: TSLA, AMD, BMNR, SBET, MSTR, HIMS, PLTR, AVGO, NVDA"

# Create the cron job command for multi-stock alerts
CRON_COMMAND="0 9 * * * cd $SCRIPT_DIR && $PYTHON_PATH multi_stock_alerts.py >> multi_stock_cron.log 2>&1"

echo "⏰ Setting up cron job for 9:00 AM daily multi-stock alerts..."
echo "📝 Cron command: $CRON_COMMAND"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "📅 Multi-stock alerts will run daily at 9:00 AM"
    echo "📄 Logs will be saved to: $SCRIPT_DIR/multi_stock_cron.log"
    echo ""
    echo "📋 Current crontab:"
    crontab -l | grep -E "(multi_stock|TSLA)" || echo "   (No stock jobs found)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

echo ""
echo "🎯 What you'll get every morning at 9:00 AM:"
echo "   🍎 macOS notification with top opportunities"
echo "   📊 Analysis of all 9 stocks"
echo "   🎯 Top 2 entry points for each stock"
echo "   📈 Ranked by best opportunities first"
echo ""
echo "🔧 Management commands:"
echo "   Test: python3 multi_stock_alerts.py"
echo "   Logs: tail -f multi_stock_cron.log"
echo "   Stop: crontab -e (delete the multi-stock line)"
echo ""
echo "🛑 To remove the cron job later:"
echo "   crontab -e  # then delete the multi-stock line"