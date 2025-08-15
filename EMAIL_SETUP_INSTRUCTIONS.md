# 📧 Gmail Email Alert Setup Instructions

## Quick Setup for keeryu@gmail.com

I've configured your email alert system to send daily TSLA alerts to **keeryu@gmail.com** at 9:00 AM every day.

## 🔐 Gmail App Password Setup (Required)

Since you're using Gmail, you need to create an **App Password** for security:

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **2-Step Verification**
3. Follow the setup process if not already enabled

### Step 2: Generate App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click **App passwords**
3. Select app: **Mail**
4. Select device: **Other (Custom name)**
5. Enter name: **TSLA Alert System**
6. Click **Generate**
7. **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)

### Step 3: Update Configuration
1. Open the `.env` file in your project
2. Replace `your_gmail_app_password_here` with your App Password:
```env
EMAIL_PASSWORD=abcd efgh ijkl mnop
```
3. Save the file

## 🚀 Start Daily Alerts

### Option 1: Automated Setup (Recommended)
```bash
cd algorithmic-trading-project
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
# Test the email system
python3 automated_tsla_alerts.py
```

You should see:
- ✅ Email: ✅ Sent
- A test email in your inbox at keeryu@gmail.com

## 📧 What You'll Receive

Every morning at 9:00 AM, you'll get an email with:

**Subject:** `TSLA Daily Alert - 2024-01-15`

**Content:**
```
🚀 TSLA DAILY ALERT - 2024-01-15 09:00

💰 Current Price: $339.38
📊 Entry Score: 40% (2/5 conditions)
🎯 Action: ⏳ WAIT

📈 Technical Conditions:
  🌀 Fibonacci: ❌
  📊 MACD: ✅ 
  📈 RSI: ❌ (70)
  📊 Volume: ❌ (0.8x)
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

## 🛠️ Troubleshooting

### Email Not Sending?
1. **Check App Password**: Make sure you used the App Password, not your regular Gmail password
2. **Check 2FA**: Ensure 2-factor authentication is enabled
3. **Test Connection**: Run `python3 automated_tsla_alerts.py` and check output

### Common Errors:
- `Authentication failed`: Wrong App Password
- `Connection refused`: Check internet connection
- `Module not found`: Run `pip install schedule requests python-dotenv`

## 📱 Mobile Notifications

To get push notifications on your phone:
1. Enable Gmail notifications in your phone's Gmail app
2. Set up a Gmail filter to mark TSLA alerts as important
3. Configure your phone to notify for important emails

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

---

**Ready to go!** Once you add your Gmail App Password, you'll receive professional TSLA analysis every morning at 9:00 AM.