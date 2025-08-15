#!/bin/bash
# Setup script for TSLA daily email alerts

echo "📧 Setting up TSLA Email Alert System..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "📁 Project directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHON_PATH"

# Create the cron job command for email alerts
CRON_COMMAND="0 9 * * * cd $SCRIPT_DIR && $PYTHON_PATH simple_email_alerts.py >> tsla_email_cron.log 2>&1"

echo "⏰ Setting up cron job for 9:00 AM daily email alerts..."
echo "📝 Cron command: $CRON_COMMAND"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "📅 TSLA email alerts will run daily at 9:00 AM"
    echo "📄 Logs will be saved to: $SCRIPT_DIR/tsla_email_cron.log"
    echo ""
    echo "📋 Current crontab:"
    crontab -l | grep -E "(tsla|TSLA|email)" || echo "   (No TSLA jobs found)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

echo ""
echo "🔧 Next steps:"
echo "1. Update your password in .env file"
echo "2. Test the system: python3 simple_email_alerts.py"
echo "3. Check logs: tail -f tsla_email_cron.log"
echo ""
echo "📧 Email Features:"
echo "   • Beautiful HTML formatted emails"
echo "   • Professional technical analysis"
echo "   • Risk management recommendations"
echo "   • Entry level suggestions"
echo ""
echo "🛑 To remove the cron job later:"
echo "   crontab -e  # then delete the TSLA email line"