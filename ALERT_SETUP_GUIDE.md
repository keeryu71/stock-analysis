# 🚨 TSLA Daily Alert System Setup Guide

## Overview
This automated system runs TSLA analysis every day at 9:00 AM and sends you alerts via multiple channels (email, Slack, Discord, and file logging).

## 📋 Quick Setup

### 1. Install Required Dependencies
```bash
cd algorithmic-trading-project
pip install schedule requests python-dotenv
```

### 2. Configure Alert Settings
```bash
# Copy the configuration template
cp alert_config.env .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### 3. Choose Your Setup Method

#### Option A: Automated Cron Setup (Recommended for macOS/Linux)
```bash
# Run the automated setup script
./setup_cron.sh
```

#### Option B: Manual Cron Setup
```bash
# Edit your crontab
crontab -e

# Add this line for 9:00 AM daily alerts:
0 9 * * * cd /path/to/algorithmic-trading-project && python3 automated_tsla_alerts.py >> tsla_cron.log 2>&1
```

#### Option C: Python Scheduler (Cross-platform)
```bash
# Run the Python scheduler (keeps running)
python3 schedule_alerts.py
```

## 🔧 Configuration Options

### Email Alerts
Set these in your `.env` file:
```env
EMAIL_ALERTS_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password  # Use App Password for Gmail
RECIPIENT_EMAIL=your_email@gmail.com
```

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate an App Password: Google Account → Security → App passwords
3. Use the App Password (not your regular password)

### Slack Alerts
1. Create a Slack webhook: https://api.slack.com/messaging/webhooks
2. Configure in `.env`:
```env
SLACK_ALERTS_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Discord Alerts
1. Create a Discord webhook in your server settings
2. Configure in `.env`:
```env
DISCORD_ALERTS_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
```

## 🧪 Testing

### Test the Alert System
```bash
# Run a single alert to test configuration
python3 automated_tsla_alerts.py
```

### Test the Scheduler
```bash
# Run the scheduler for testing (Ctrl+C to stop)
python3 schedule_alerts.py
```

## 📊 Alert Content

Your daily alerts will include:

### 📈 Technical Analysis
- **Current TSLA Price**: Real-time stock price
- **Entry Score**: 0-100% confidence rating based on 5 indicators
- **Action Recommendation**: STRONG BUY / GOOD SETUP / WAIT / AVOID

### 🎯 Key Levels
- **Fibonacci Support Levels**: Optimal entry prices with discount percentages
- **SMA 20**: Moving average support level
- **Risk Management**: Automatic stop-loss (-8%) and take-profit (+15%) levels

### 📊 Technical Conditions
- ✅/❌ **Fibonacci**: At key retracement levels (38.2%, 50%, 61.8%)
- ✅/❌ **MACD**: Bullish momentum signal
- ✅/❌ **RSI**: Not overbought/oversold (30-70 range)
- ✅/❌ **Volume**: Above average institutional activity
- ✅/❌ **Trend**: Above 20-day moving average

## 📱 Sample Alert

```
🚀 TSLA DAILY ALERT - 2024-01-15 09:00

💰 Current Price: $339.38
📊 Entry Score: 40% (2/5 conditions)
🎯 Action: ⏳ WAIT

📈 Technical Conditions:
  🌀 Fibonacci: ❌
  📊 MACD: ✅ 
  📈 RSI: ❌ (70)
  📊 Volume: ❌ (0.75x)
  📈 Trend: ✅

🎯 Key Levels:
  💰 $325.33 - 38.2% Fib (4.1% discount)
  💰 $315.38 - 50.0% Fib (7.1% discount)
  💰 $305.42 - 61.8% Fib (10.0% discount)

⚠️ Risk Management:
  🛑 Stop Loss: $312.23 (-8%)
  🎯 Take Profit: $390.29 (+15%)

📱 Set alerts at key support levels for entry opportunities!
```

## 🔄 Management Commands

### View Logs
```bash
# View alert logs
tail -f tsla_alerts.log

# View cron logs
tail -f tsla_cron.log
```

### Check Cron Jobs
```bash
# List current cron jobs
crontab -l

# Edit cron jobs
crontab -e
```

### Stop Alerts
```bash
# Remove cron job
crontab -e  # Delete the TSLA line

# Stop Python scheduler
# Press Ctrl+C in the terminal running schedule_alerts.py
```

## 🛠️ Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Install missing dependencies
pip install schedule requests python-dotenv yfinance pandas numpy matplotlib
```

**2. Email not sending**
- Check Gmail App Password (not regular password)
- Verify SMTP settings
- Check firewall/antivirus blocking SMTP

**3. Cron job not running**
```bash
# Check cron service is running
sudo launchctl list | grep cron  # macOS
systemctl status cron           # Linux

# Check cron logs
tail -f /var/log/cron.log       # Linux
tail -f tsla_cron.log          # Our logs
```

**4. Data fetch errors**
- Check internet connection
- Yahoo Finance API might be temporarily down
- Try running manually: `python3 automated_tsla_alerts.py`

### Debug Mode
Add debug prints to see what's happening:
```python
# Edit automated_tsla_alerts.py and add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📅 Customization

### Change Alert Time
Edit the cron job or `schedule_alerts.py`:
```python
# For 8:30 AM
schedule.every().day.at("08:30").do(run_daily_alert)

# For market close (3:30 PM)
schedule.every().day.at("15:30").do(run_daily_alert)
```

### Add Weekend Alerts
```python
# Monday pre-market
schedule.every().monday.at("08:30").do(run_daily_alert)
```

### Multiple Stocks
Modify `automated_tsla_alerts.py` to analyze other stocks by changing the ticker symbol.

## 🎯 Next Steps

1. **Set up your preferred notification method** (email, Slack, or Discord)
2. **Run the setup script**: `./setup_cron.sh`
3. **Test the system**: `python3 automated_tsla_alerts.py`
4. **Monitor logs**: `tail -f tsla_alerts.log`
5. **Enjoy automated TSLA analysis every morning at 9 AM!** 🚀

---

**Need help?** Check the logs first, then review this guide. The system is designed to be robust and will log all activities for troubleshooting.