# 📱 SMS Alert Setup Instructions

## Quick Setup for +1 (408) 799-5948

I've configured your SMS alert system to send daily TSLA alerts to your phone at 9:00 AM every day.

## 🔧 Twilio Account Setup (Required)

### Step 1: Create Twilio Account
1. Go to [Twilio.com](https://www.twilio.com/try-twilio)
2. Sign up for a free account
3. Verify your phone number (+1 (408) 799-5948)

### Step 2: Get Your Credentials
After signing up, you'll see your dashboard with:
1. **Account SID** (starts with "AC...")
2. **Auth Token** (click the eye icon to reveal)
3. **Trial Phone Number** (starts with "+1...")

### Step 3: Update Configuration
1. Open the `.env` file in your project
2. Replace the placeholder values:
```env
SMS_ALERTS_ENABLED=true
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
RECIPIENT_PHONE=+14087995948
```

## 💰 Twilio Pricing

### Free Trial:
- **$15.50 credit** when you sign up
- **SMS costs**: $0.0075 per message (less than 1 cent!)
- **Daily alerts**: About $2.74 per year (365 messages × $0.0075)
- Your free credit covers **2,066 messages** (5+ years of daily alerts!)

### After Trial:
- Pay-as-you-go: Only pay for messages sent
- No monthly fees for basic SMS
- Extremely affordable for daily alerts

## 🚀 Start Daily Alerts

### Install Dependencies
```bash
cd algorithmic-trading-project
pip install twilio
```

### Option 1: Automated Setup (Recommended)
```bash
./setup_cron.sh
```

### Option 2: Manual Cron Setup
```bash
# Edit crontab
crontab -e

# Add this line for 9:00 AM daily alerts:
0 9 * * * cd /Users/keeryu/Library/Mobile\ Documents/com~apple~icloud~applecorporate/Documents/Coding/algorithmic-trading-project && python3 automated_tsla_alerts.py >> tsla_cron.log 2>&1
```

### Option 3: Python Scheduler
```bash
# Run continuously (keeps terminal open)
python3 schedule_alerts.py
```

## 🧪 Test Your Setup

```bash
# Test the SMS system
python3 automated_tsla_alerts.py
```

You should see:
- 📱 SMS: ✅ Sent
- A text message on your phone at +1 (408) 799-5948

## 📱 What You'll Receive

Every morning at 9:00 AM, you'll get a concise SMS like:

```
⏳ TSLA Alert 08/15
Price: $339.38
Score: 40% - WAIT
Entry: $305.42 (10% off)
Signals: 2/5 (RSI: 70 overbought)
```

### SMS Content Breakdown:
- **🚀/⚡/⏳/🛑**: Action recommendation
- **Price**: Current TSLA stock price
- **Score**: Entry confidence (0-100%)
- **Entry**: Best entry price with discount
- **Signals**: How many technical indicators are positive
- **RSI**: Momentum indicator status

## 🛠️ Troubleshooting

### Common Issues:

**1. "SMS send failed" error**
- Check your Twilio credentials in `.env`
- Verify your phone number is verified in Twilio
- Check internet connection

**2. "Module not found: twilio"**
```bash
pip install twilio
```

**3. "Invalid phone number"**
- Phone numbers must include country code: `+14087995948`
- Verify the number in your Twilio console

**4. "Insufficient funds"**
- Add credit to your Twilio account
- Check your account balance in Twilio console

### Debug Mode:
Add debug prints to see what's happening:
```python
# Edit automated_tsla_alerts.py and add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📱 SMS Features

### Concise Format:
- **160 character limit** consideration
- **Key information only**: Price, action, entry level
- **Emoji indicators** for quick visual scanning
- **Date stamp** for reference

### Smart Content:
- **Entry recommendations** when score is low
- **RSI alerts** for overbought/oversold conditions
- **Signal count** for quick confidence assessment
- **Discount percentages** for entry opportunities

## 🔄 Managing Alerts

### Stop Alerts:
```bash
crontab -e  # Delete the TSLA line
```

### Change Time:
Edit the cron job or `schedule_alerts.py` to change from 9:00 AM

### View Logs:
```bash
tail -f tsla_alerts.log     # Alert logs
tail -f tsla_cron.log      # Cron logs
```

### Check Twilio Usage:
- Log into your Twilio console
- View usage and billing
- Monitor message delivery status

## 🎯 Next Steps

1. **Create Twilio account**: [Twilio.com](https://www.twilio.com/try-twilio)
2. **Get your credentials** (Account SID, Auth Token, Phone Number)
3. **Update `.env` file** with your Twilio credentials
4. **Install Twilio**: `pip install twilio`
5. **Test the system**: `python3 automated_tsla_alerts.py`
6. **Run setup script**: `./setup_cron.sh`
7. **Enjoy daily TSLA alerts on your phone!** 📱

---

**Cost**: Less than $3/year for daily alerts with Twilio's pay-as-you-go pricing!
**Reliability**: Professional SMS delivery with 99.95% uptime
**Convenience**: Get TSLA analysis directly on your phone every morning