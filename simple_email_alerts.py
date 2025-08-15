#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Email Alert System for TSLA Analysis
Uses multiple email service options for easy setup
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from data.data_loader import DataLoader
from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

class SimpleEmailAlerts:
    """Simple email alert system with multiple service options."""
    
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """Load email configuration."""
        # Email service selection
        self.email_service = os.getenv('EMAIL_SERVICE', 'outlook')  # outlook, yahoo, gmail
        
        # Email credentials
        self.sender_email = os.getenv('SENDER_EMAIL', 'keeryu@gmail.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', 'keeryu@gmail.com')
        
        # SMTP settings based on service
        self.smtp_settings = {
            'outlook': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True
            },
            'yahoo': {
                'server': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True
            },
            'gmail': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True
            },
            'icloud': {
                'server': 'smtp.mail.me.com',
                'port': 587,
                'use_tls': True
            }
        }
        
        # File logging
        self.log_file = 'tsla_email_alerts.log'
        
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
    
    def generate_email_content(self, analysis):
        """Generate email content."""
        if not analysis:
            return "TSLA Analysis Failed", "Unable to fetch market data. Please check your internet connection."
        
        price = analysis['price']
        score = analysis['score']
        conditions = analysis['conditions']
        
        # Determine action
        if score >= 0.8:
            action = "🟢 STRONG BUY"
            action_color = "#28a745"
        elif score >= 0.6:
            action = "🟡 GOOD SETUP"
            action_color = "#ffc107"
        elif score >= 0.4:
            action = "🟡 WAIT"
            action_color = "#fd7e14"
        else:
            action = "🔴 AVOID"
            action_color = "#dc3545"
        
        # Email subject
        subject = f"TSLA Alert: ${price:.2f} - {action.replace('🟢 ', '').replace('🟡 ', '').replace('🔴 ', '')}"
        
        # HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333; margin-top: 0;">🚗 TSLA Daily Alert</h2>
                <p style="color: #666; margin: 5px 0;">{analysis['timestamp'].strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h3 style="color: {action_color}; margin-top: 0;">{action}</h3>
                    <p style="font-size: 18px; margin: 10px 0;"><strong>Current Price: ${price:.2f}</strong></p>
                    <p style="margin: 5px 0;">Entry Score: <strong>{score:.0%}</strong> ({sum(conditions.values())}/5 conditions met)</p>
                </div>
                
                <div style="background-color: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="color: #333; margin-top: 0;">📊 Technical Conditions</h4>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 8px 0;">🌀 Fibonacci: {'✅ Good' if conditions['fibonacci'] else '❌ Poor'}</li>
                        <li style="margin: 8px 0;">📈 MACD: {'✅ Bullish' if conditions['macd'] else '❌ Bearish'}</li>
                        <li style="margin: 8px 0;">📊 RSI: {'✅ Neutral' if conditions['rsi'] else '❌ Extreme'} ({analysis['rsi']:.0f})</li>
                        <li style="margin: 8px 0;">📊 Volume: {'✅ High' if conditions['volume'] else '❌ Low'} ({analysis['volume_ratio']:.1f}x)</li>
                        <li style="margin: 8px 0;">📈 Trend: {'✅ Bullish' if conditions['trend'] else '❌ Bearish'}</li>
                    </ul>
                </div>
        """
        
        # Add entry levels if waiting
        if score < 0.6 and analysis['fib_levels']:
            html_body += """
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ffc107;">
                    <h4 style="color: #856404; margin-top: 0;">🎯 Better Entry Opportunities</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
            """
            
            for level_name, level_price in analysis['fib_levels'].items():
                if level_price < price:
                    discount = ((price - level_price) / price) * 100
                    html_body += f"<li style='margin: 5px 0;'><strong>${level_price:.2f}</strong> - {level_name} Fibonacci ({discount:.1f}% discount)</li>"
            
            # Add SMA level
            sma_20 = analysis['sma_20']
            if sma_20 < price:
                discount = ((price - sma_20) / price) * 100
                html_body += f"<li style='margin: 5px 0;'><strong>${sma_20:.2f}</strong> - 20-day Average ({discount:.1f}% discount)</li>"
            
            html_body += "</ul></div>"
        
        # Risk management
        html_body += f"""
                <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #dc3545;">
                    <h4 style="color: #721c24; margin-top: 0;">⚠️ Risk Management</h4>
                    <p style="margin: 5px 0;"><strong>Stop Loss:</strong> ${analysis['stop_loss']:.2f} (-8%)</p>
                    <p style="margin: 5px 0;"><strong>Take Profit:</strong> ${analysis['take_profit']:.2f} (+15%)</p>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #17a2b8;">
                    <p style="color: #0c5460; margin: 0;"><strong>💡 Tip:</strong> Set price alerts at key support levels for optimal entry timing!</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                    This analysis is for educational purposes only. Always do your own research before making investment decisions.
                </p>
            </div>
        </body>
        </html>
        """
        
        return subject, html_body
    
    def send_email(self, subject, html_body):
        """Send email using configured service."""
        if not self.sender_email or not self.sender_password:
            print("❌ Email credentials not configured")
            return False
        
        try:
            # Get SMTP settings
            smtp_config = self.smtp_settings.get(self.email_service)
            if not smtp_config:
                print(f"❌ Unknown email service: {self.email_service}")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
                if smtp_config['use_tls']:
                    server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False
    
    def log_to_file(self, subject, content):
        """Log alert to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*50}\n")
                f.write(f"SUBJECT: {subject}\n")
                f.write(f"CONTENT: {content[:200]}...\n")  # First 200 chars
                f.write(f"{'='*50}\n\n")
            return True
        except Exception as e:
            print(f"File logging failed: {e}")
            return False
    
    def send_alerts(self):
        """Run analysis and send email alert."""
        print(f"📧 Running TSLA Email Alert System...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📮 Email Service: {self.email_service.title()}")
        print(f"📬 Sending to: {self.recipient_email}")
        
        # Run analysis
        analysis = self.run_analysis()
        
        if analysis:
            print(f"✓ Loaded TSLA data successfully")
        else:
            print("❌ Failed to load TSLA data")
            return {'email': False, 'file': False}
        
        subject, html_body = self.generate_email_content(analysis)
        
        # Send email
        results = {
            'email': False,
            'file': False
        }
        
        results['email'] = self.send_email(subject, html_body)
        print(f"📧 Email: {'✅ Sent' if results['email'] else '❌ Failed'}")
        
        # Log to file
        results['file'] = self.log_to_file(subject, html_body)
        print(f"📄 File Log: {'✅ Saved' if results['file'] else '❌ Failed'}")
        
        success_count = sum(results.values())
        print(f"\n✅ Alert system completed: {success_count}/2 methods successful")
        
        return results

def main():
    """Main function to run the email alert system."""
    alert_system = SimpleEmailAlerts()
    results = alert_system.send_alerts()
    
    if not any(results.values()):
        print("⚠️  No alerts sent successfully. Check your email configuration.")
    
    return results

if __name__ == "__main__":
    main()