#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Easy Cloud Deployment Script
Automates the deployment process to various cloud platforms
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_git_status():
    """Check if git is initialized and files are committed."""
    if not os.path.exists('.git'):
        print("📁 Initializing git repository...")
        run_command('git init', 'Git initialization')
        run_command('git add .', 'Adding files to git')
        run_command('git commit -m "Initial commit for cloud deployment"', 'Initial commit')
    else:
        # Check for uncommitted changes
        result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print("📝 Committing recent changes...")
            run_command('git add .', 'Adding changes')
            run_command(f'git commit -m "Update for deployment - {datetime.now().strftime("%Y-%m-%d %H:%M")}"', 'Committing changes')

def deploy_to_railway():
    """Deploy to Railway via GitHub."""
    print("\n🚂 RAILWAY DEPLOYMENT")
    print("=" * 50)
    
    check_git_status()
    
    print("\n📋 Railway Deployment Steps:")
    print("1. 🌐 Go to https://railway.app")
    print("2. 🔐 Sign up/login with GitHub")
    print("3. ➕ Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. 📂 Select your repository")
    print("5. 🚀 Railway will auto-deploy your Flask app")
    print("6. 🔗 Get your app URL from Railway dashboard")
    
    # Check if we have a GitHub remote
    result = subprocess.run('git remote -v', shell=True, capture_output=True, text=True)
    if 'origin' not in result.stdout:
        print("\n⚠️  No GitHub remote found. You need to:")
        print("1. Create a repository on GitHub")
        print("2. Add remote: git remote add origin https://github.com/USERNAME/REPO.git")
        print("3. Push: git push -u origin main")
    else:
        print("\n✅ GitHub remote found. Pushing latest changes...")
        run_command('git push origin main', 'Pushing to GitHub')
        print("🎉 Ready for Railway deployment!")

def deploy_to_heroku():
    """Deploy to Heroku."""
    print("\n🟣 HEROKU DEPLOYMENT")
    print("=" * 50)
    
    # Check if Heroku CLI is installed
    result = subprocess.run('heroku --version', shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Heroku CLI not found. Install it first:")
        print("Mac: brew tap heroku/brew && brew install heroku")
        print("Windows: Download from https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    check_git_status()
    
    # Check if already logged in
    result = subprocess.run('heroku auth:whoami', shell=True, capture_output=True)
    if result.returncode != 0:
        print("🔐 Please login to Heroku:")
        run_command('heroku login', 'Heroku login')
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    if app_name:
        create_cmd = f'heroku create {app_name}'
    else:
        create_cmd = 'heroku create'
    
    if run_command(create_cmd, 'Creating Heroku app'):
        run_command('git push heroku main', 'Deploying to Heroku')
        run_command('heroku open', 'Opening app in browser')

def deploy_to_render():
    """Deploy to Render (manual process)."""
    print("\n🎨 RENDER DEPLOYMENT")
    print("=" * 50)
    
    check_git_status()
    
    print("\n📋 Render Deployment Steps:")
    print("1. 🌐 Go to https://render.com")
    print("2. 🔐 Sign up/login with GitHub")
    print("3. ➕ Click 'New' → 'Web Service'")
    print("4. 📂 Connect your GitHub repository")
    print("5. ⚙️  Use these settings:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python mobile_web_app.py")
    print("6. 🚀 Click 'Create Web Service'")
    print("7. 🔗 Get your app URL from Render dashboard")

def main():
    """Main deployment menu."""
    print("☁️  CLOUD DEPLOYMENT ASSISTANT")
    print("=" * 50)
    print("Deploy your Stock Analysis app to the cloud!")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        print("\n🚀 Choose deployment platform:")
        print("1. 🚂 Railway (Recommended - Free & Easy)")
        print("2. 🟣 Heroku (Classic)")
        print("3. 🎨 Render (Alternative)")
        print("4. 📖 View deployment guide")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            deploy_to_railway()
        elif choice == '2':
            deploy_to_heroku()
        elif choice == '3':
            deploy_to_render()
        elif choice == '4':
            print("\n📖 Opening deployment guide...")
            if os.path.exists('CLOUD_DEPLOYMENT.md'):
                print("📄 Check CLOUD_DEPLOYMENT.md for detailed instructions")
            else:
                print("❌ Deployment guide not found")
        elif choice == '5':
            print("\n👋 Happy deploying!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()