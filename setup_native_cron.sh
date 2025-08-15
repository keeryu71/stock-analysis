#!/bin/bash
# Setup script for TSLA daily alerts using native macOS notifications

echo "🚀 Setting up TSLA Native Alert System..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "📁 Project directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHON_PATH"

# Create the cron job command for native alerts
CRON_COMMAND="0 9 * * * cd $SCRIPT_DIR && $PYTHON_PATH native_alerts.py >> tsla_native_cron.log 2>&1"

echo "⏰ Setting up cron job for 9:00 AM daily native alerts..."
echo "📝 Cron command: $CRON_COMMAND"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "📅 TSLA native alerts will run daily at 9:00 AM"
    echo "📄 Logs will be saved to: $SCRIPT_DIR/tsla_native_cron.log"
    echo ""
    echo "📋 Current crontab:"
    crontab -l | grep -E "(tsla|TSLA|native)" || echo "   (No TSLA jobs found)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

echo ""
echo "🔧 Next steps:"
echo "1. Test the system: python3 native_alerts.py"
echo "2. Check logs: tail -f tsla_native_cron.log"
echo "3. You'll get macOS notifications + terminal alerts + file logs"
echo ""
echo "🛑 To remove the cron job later:"
echo "   crontab -e  # then delete the TSLA native line"
echo ""
echo "🍎 macOS Notification Features:"
echo "   • Pop-up notifications on your screen"
echo "   • Sound alerts (Glass sound)"
echo "   • No external services required"
echo "   • Works offline"