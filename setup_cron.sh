#!/bin/bash
# Setup script for TSLA daily alerts using cron (macOS/Linux)

echo "🚀 Setting up TSLA Daily Alert System..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "📁 Project directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHON_PATH"

# Create the cron job command
CRON_COMMAND="0 9 * * * cd $SCRIPT_DIR && $PYTHON_PATH automated_tsla_alerts.py >> tsla_cron.log 2>&1"

echo "⏰ Setting up cron job for 9:00 AM daily..."
echo "📝 Cron command: $CRON_COMMAND"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "📅 TSLA alerts will run daily at 9:00 AM"
    echo "📄 Logs will be saved to: $SCRIPT_DIR/tsla_cron.log"
    echo ""
    echo "📋 Current crontab:"
    crontab -l | grep -E "(tsla|TSLA)" || echo "   (No TSLA jobs found)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

echo ""
echo "🔧 Next steps:"
echo "1. Configure your alert settings in alert_config.env"
echo "2. Copy alert_config.env to .env and add your credentials"
echo "3. Test the system: python3 automated_tsla_alerts.py"
echo "4. Check logs: tail -f tsla_cron.log"
echo ""
echo "🛑 To remove the cron job later:"
echo "   crontab -e  # then delete the TSLA line"