#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated TSLA Daily Alert System
Runs analysis and sends notifications via multiple channels
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import smtplib
import json
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import warnings
warnings.filterwarnings('ignore')

from data.data_loader import DataLoader
from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

class TSLAAlertSystem:
    """Automated TSLA alert system with multiple notification methods."""
    
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """Load configuration from environment or config file."""
        # SMS configuration
        self.sms_enabled = os.getenv('SMS_ALERTS_ENABLED', 'false').lower() == 'true'
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        self.recipient_phone = os.getenv('RECIPIENT_PHONE', '')
        
        # Email configuration (disabled by default)
        self.email_enabled = os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true'
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', '')
        
        # Slack configuration (disabled by default)
        self.slack_enabled = os.getenv('SLACK_ALERTS_ENABLED', 'false').lower() == 'true'
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        # Discord configuration (disabled by default)
        self.discord_enabled = os.getenv('DISCORD_ALERTS_ENABLED', 'false').lower() == 'true'
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')
        
        # File logging always enabled
        self.log_file = 'tsla_alerts.log'
        
    def run_analysis(self):
        """Run TSLA analysis and return results."""
        try:
            # Load TSLA data
            loader = DataLoader()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            data = loader.fetch_stock_data(['TSLA'], start_date, end_date)
            tsla_data = data['TSLA']
            
            if tsla_data.empty:
                return None
            
            # Calculate indicators
            strategy = FibonacciMACDStrategy()
            analyzed_data = strategy._calculate_indicators(tsla_data.copy())
            latest = analyzed_data.iloc[-1]
            current_price = latest['close']
            
            # Evaluate conditions
            conditions = {
                'fibonacci': latest['fib_position'] in ['fib_0.382', 'fib_0.500', 'fib_0.618'],
                'macd': latest['macd'] > latest['macd_signal'],
                'rsi': 30 < latest['rsi'] < 70,
                'volume': latest['volume_ratio'] > 1.0,
                'trend': latest['close'] > latest['sma_20']
            }
            
            score = sum(conditions.values()) / len(conditions)
            
            # Get key levels
            fib_levels = {}
            for level in [0.382, 0.5, 0.618]:
                fib_price = latest[f'fib_{level:.3f}']
                if pd.notna(fib_price):
                    fib_levels[f'{level*100:.1f}%'] = fib_price
            
            return {
                'timestamp': datetime.now(),
                'price': current_price,
                'score': score,
                'conditions': conditions,
                'rsi': latest['rsi'],
                'macd_bullish': latest['macd'] > latest['macd_signal'],
                'volume_ratio': latest['volume_ratio'],
                'fib_levels': fib_levels,
                'sma_20': latest['sma_20'],
                'stop_loss': current_price * 0.92,
                'take_profit': current_price * 1.15
            }
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return None
    
    def generate_alert_message(self, analysis):
        """Generate alert message based on analysis."""
        if not analysis:
            return "❌ TSLA Analysis Failed - Unable to fetch data"
        
        price = analysis['price']
        score = analysis['score']
        conditions = analysis['conditions']
        
        # Determine action
        if score >= 0.8:
            action = "🟢 STRONG BUY"
            emoji = "🚀"
        elif score >= 0.6:
            action = "🟡 GOOD SETUP"
            emoji = "⚡"
        elif score >= 0.4:
            action = "🟡 WAIT"
            emoji = "⏳"
        else:
            action = "🔴 AVOID"
            emoji = "🛑"
        
        # Build message
        message = f"""
{emoji} TSLA DAILY ALERT - {analysis['timestamp'].strftime('%Y-%m-%d %H:%M')}

💰 Current Price: ${price:.2f}
📊 Entry Score: {score:.0%} ({sum(conditions.values())}/5 conditions)
🎯 Action: {action}

📈 Technical Conditions:
  🌀 Fibonacci: {'✅' if conditions['fibonacci'] else '❌'}
  📊 MACD: {'✅' if conditions['macd'] else '❌'} 
  📈 RSI: {'✅' if conditions['rsi'] else '❌'} ({analysis['rsi']:.0f})
  📊 Volume: {'✅' if conditions['volume'] else '❌'} ({analysis['volume_ratio']:.1f}x)
  📈 Trend: {'✅' if conditions['trend'] else '❌'}

🎯 Key Levels:"""
        
        # Add Fibonacci levels
        for level_name, level_price in analysis['fib_levels'].items():
            if level_price < price:
                discount = ((price - level_price) / price) * 100
                message += f"\n  💰 ${level_price:.2f} - {level_name} Fib ({discount:.1f}% discount)"
        
        # Add SMA level
        sma_20 = analysis['sma_20']
        if sma_20 < price:
            discount = ((price - sma_20) / price) * 100
            message += f"\n  💰 ${sma_20:.2f} - SMA 20 ({discount:.1f}% discount)"
        
        message += f"""

⚠️ Risk Management:
  🛑 Stop Loss: ${analysis['stop_loss']:.2f} (-8%)
  🎯 Take Profit: ${analysis['take_profit']:.2f} (+15%)

📱 Set alerts at key support levels for entry opportunities!
"""
    def generate_sms_message(self, analysis):
        """Generate concise SMS message based on analysis."""
        if not analysis:
            return "TSLA Analysis Failed - Unable to fetch data"
        
        price = analysis['price']
        score = analysis['score']
        conditions = analysis['conditions']
        
        # Determine action
        if score >= 0.8:
            action = "STRONG BUY"
            emoji = "🚀"
        elif score >= 0.6:
            action = "GOOD SETUP"
            emoji = "⚡"
        elif score >= 0.4:
            action = "WAIT"
            emoji = "⏳"
        else:
            action = "AVOID"
            emoji = "🛑"
        
        # Build concise SMS message (160 char limit consideration)
        message = f"{emoji} TSLA Alert {analysis['timestamp'].strftime('%m/%d')}\n"
        message += f"Price: ${price:.2f}\n"
        message += f"Score: {score:.0%} - {action}\n"
        
        # Add best entry level if waiting
        if score < 0.6 and analysis['fib_levels']:
            best_level = min(analysis['fib_levels'].values())
            discount = ((price - best_level) / price) * 100
            message += f"Entry: ${best_level:.2f} ({discount:.0f}% off)\n"
        
        # Add key condition summary
        conditions_met = sum(conditions.values())
        message += f"Signals: {conditions_met}/5"
        
        # Add RSI if overbought/oversold
        rsi = analysis['rsi']
        if rsi > 70:
            message += f" (RSI: {rsi:.0f} overbought)"
        elif rsi < 30:
            message += f" (RSI: {rsi:.0f} oversold)"
        
        return message.strip()
    
    def send_sms_alert(self, analysis):
        """Send SMS alert using Twilio."""
        if not self.sms_enabled or not self.twilio_account_sid or not self.recipient_phone:
            return False
        
        try:
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            message_body = self.generate_sms_message(analysis)
            
            message = client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=self.recipient_phone
            )
            
            return True
        except Exception as e:
            print(f"SMS send failed: {e}")
            return False

        
        return message.strip()
    
    def send_email_alert(self, message):
        """Send email alert."""
        if not self.email_enabled or not self.email_user or not self.recipient_email:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.recipient_email
            msg['Subject'] = f"TSLA Daily Alert - {datetime.now().strftime('%Y-%m-%d')}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, self.recipient_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False
    
    def send_slack_alert(self, message):
        """Send Slack alert."""
        if not self.slack_enabled or not self.slack_webhook:
            return False
        
        try:
            payload = {
                "text": f"TSLA Daily Alert",
                "attachments": [{
                    "color": "good",
                    "text": message,
                    "mrkdwn_in": ["text"]
                }]
            }
            
            response = requests.post(self.slack_webhook, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack send failed: {e}")
            return False
    
    def send_discord_alert(self, message):
        """Send Discord alert."""
        if not self.discord_enabled or not self.discord_webhook:
            return False
        
        try:
            payload = {
                "content": f"**TSLA Daily Alert**\n```\n{message}\n```"
            }
            
            response = requests.post(self.discord_webhook, json=payload)
            return response.status_code == 204
        except Exception as e:
            print(f"Discord send failed: {e}")
            return False
    
    def log_to_file(self, message):
        """Log alert to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*50}\n")
                f.write(message)
                f.write(f"\n{'='*50}\n\n")
            return True
        except Exception as e:
            print(f"File logging failed: {e}")
            return False
    
    def send_alerts(self):
        """Run analysis and send alerts via all configured channels."""
        print(f"🚗 Running TSLA Daily Alert System...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run analysis
        analysis = self.run_analysis()
        message = self.generate_alert_message(analysis)
        
        # Send via all channels
        results = {
            'sms': False,
            'email': False,
            'slack': False,
            'discord': False,
            'file': False
        }
        
        if self.sms_enabled:
            results['sms'] = self.send_sms_alert(analysis)
            print(f"📱 SMS: {'✅ Sent' if results['sms'] else '❌ Failed'}")
        
        if self.email_enabled:
            results['email'] = self.send_email_alert(message)
            print(f"📧 Email: {'✅ Sent' if results['email'] else '❌ Failed'}")
        
        if self.slack_enabled:
            results['slack'] = self.send_slack_alert(message)
            print(f"💬 Slack: {'✅ Sent' if results['slack'] else '❌ Failed'}")
        
        if self.discord_enabled:
            results['discord'] = self.send_discord_alert(message)
            print(f"🎮 Discord: {'✅ Sent' if results['discord'] else '❌ Failed'}")
        
        # Always log to file
        results['file'] = self.log_to_file(message)
        print(f"📄 File Log: {'✅ Saved' if results['file'] else '❌ Failed'}")
        
        # Print message to console
        print(f"\n📊 ALERT MESSAGE:")
        print(message)
        
        return results

def main():
    """Main function to run the alert system."""
    alert_system = TSLAAlertSystem()
    results = alert_system.send_alerts()
    
    success_count = sum(results.values())
    total_channels = len([k for k, v in results.items() if k != 'file']) + 1  # +1 for file
    
    print(f"\n✅ Alert system completed: {success_count}/{total_channels} channels successful")
    
    if not any(results.values()):
        print("⚠️  No alerts sent successfully. Check configuration.")
    
    return results

if __name__ == "__main__":
    main()