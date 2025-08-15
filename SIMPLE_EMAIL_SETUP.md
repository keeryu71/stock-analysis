# 📧 Simple Email Alert Setup Guide

## Quick Setup for keeryu@gmail.com

I've created a simple email alert system that sends beautiful HTML emails with your TSLA analysis every day at 9:00 AM.

## 🚀 Super Easy Setup

### Step 1: Update Your Password
1. Open the [`.env`](algorithmic-trading-project/.env) file
2. Replace `your_password_here` with your Gmail password:
```env
SENDER_PASSWORD=your_actual_gmail_password
```

### Step 2: Enable "Less Secure Apps" (Gmail)
Since we're not using App Passwords, you need to allow less secure apps:

**Option A: Use Gmail's "Less Secure Apps" (Easiest)**
1. Go to [Google Account Settings](https://myaccount.google.com/security)
2. Turn ON "Less secure app access" (if available)

**Option B: Use a Different Email Service (Recommended)**
If Gmail doesn't allow less secure apps, switch to Outlook or Yahoo:

**For Outlook/Hotmail:**
```env
EMAIL_SERVICE=outlook
SENDER_EMAIL=your_email@outlook.com
SENDER_PASSWORD=your_outlook_password
```

**For Yahoo:**
```env
EMAIL_SERVICE=yahoo
SENDER_EMAIL=your_email@yahoo.com
SENDER_PASSWORD=your_yahoo_password
```

### Step 3: Start Daily Alerts
```bash
cd algorithmic-trading-project
./setup_email_cron.sh
```

## 🧪 Test Your Setup

```bash
# Test the email system
python3 simple_email_alerts.py
```

You should see:
- ✅ Email: ✅ Sent
- A beautiful HTML email in your inbox!

## 📧 What You'll Receive

Every morning at 9:00 AM, you'll get a professional HTML email like this:

### Email Subject:
`TSLA Alert: $339.38 - WAIT`

### Email Content:
- **🚗 TSLA Daily Alert** header with date/time
- **Current Price** and **Action Recommendation** (color-coded)
- **Entry Score** with confidence percentage
- **📊 Technical Conditions** checklist:
  - 🌀 Fibonacci levels
  - 📈 MACD momentum
  - 📊 RSI indicator
  - 📊 Volume analysis
  - 📈 Trend direction
- **🎯 Better Entry Opportunities** (when waiting is recommended)
- **⚠️ Risk Management** with stop-loss and take-profit levels
- **💡 Trading Tips**

## 🎨 Email Features

### Beautiful HTML Design:
- **Color-coded alerts** (Green=Buy, Yellow=Wait, Red=Avoid)
- **Professional formatting** with boxes and sections
- **Easy-to-read layout** optimized for mobile and desktop
- **Emoji indicators** for quick visual scanning

### Smart Content:
- **Entry recommendations** with discount percentages
- **Risk management** calculations
- **Technical analysis** summary
- **Actionable insights** for trading decisions

## 🛠️ Troubleshooting

### Common Issues:

**1. "Authentication failed"**
- Check your email password in `.env`
- Try switching to Outlook or Yahoo (easier than Gmail)
- Make sure "Less secure apps" is enabled for Gmail

**2. "Connection refused"**
- Check internet connection
- Verify email service settings
- Try a different email provider

**3. Email not received**
- Check spam/junk folder
- Verify recipient email address
- Test with a different email service

### Switch Email Services:
If Gmail doesn't work, try these alternatives:

**Outlook (Recommended):**
```env
EMAIL_SERVICE=outlook
SENDER_EMAIL=your_email@outlook.com
SENDER_PASSWORD=your_password
```

**Yahoo:**
```env
EMAIL_SERVICE=yahoo
SENDER_EMAIL=your_email@yahoo.com
SENDER_PASSWORD=your_password
```

**iCloud:**
```env
EMAIL_SERVICE=icloud
SENDER_EMAIL=your_email@icloud.com
SENDER_PASSWORD=your_password
```

## 🔄 Managing Alerts

### Stop Alerts:
```bash
crontab -e  # Delete the TSLA email line
```

### Change Time:
Edit the cron job to change from 9:00 AM

### View Logs:
```bash
tail -f tsla_email_alerts.log    # Alert logs
tail -f tsla_email_cron.log     # Cron logs
```

### Test Different Times:
```bash
# Run manually anytime
python3 simple_email_alerts.py
```

## 📱 Mobile-Friendly

The HTML emails are optimized for:
- **iPhone Mail app**
- **Gmail mobile app**
- **Outlook mobile app**
- **Desktop email clients**

## 🎯 Next Steps

1. **Update your password** in the `.env` file
2. **Enable less secure apps** (Gmail) or **switch to Outlook**
3. **Test the system**: `python3 simple_email_alerts.py`
4. **Start daily alerts**: `./setup_email_cron.sh`
5. **Check your inbox** for beautiful TSLA analysis emails!

---

**No external services required!** Just your email credentials and you're ready to receive professional TSLA analysis every morning.

**Backup option:** If email doesn't work, you can always use the native macOS notifications with `python3 native_alerts.py`