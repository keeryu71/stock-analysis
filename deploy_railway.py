#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Deployment Assistant
Automates the Railway deployment process
"""

import os
import subprocess
import sys
import webbrowser
from datetime import datetime

def run_command(command, description, show_output=False):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if show_output:
            result = subprocess.run(command, shell=True, check=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True, result.stdout if hasattr(result, 'stdout') else ""
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
        print(f"❌ {description} failed: {error_msg}")
        return False, error_msg

def check_git_status():
    """Check if git is initialized and set up repository."""
    print("\n📁 PREPARING GIT REPOSITORY")
    print("=" * 40)
    
    if not os.path.exists('.git'):
        print("🆕 Initializing new git repository...")
        success, _ = run_command('git init', 'Git initialization')
        if not success:
            return False
    else:
        print("✅ Git repository already exists")
    
    # Add all files
    success, _ = run_command('git add .', 'Adding files to git')
    if not success:
        return False
    
    # Check if there are changes to commit
    result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        commit_msg = f"Railway deployment - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        success, _ = run_command(f'git commit -m "{commit_msg}"', 'Committing changes')
        if not success:
            return False
    else:
        print("✅ No new changes to commit")
    
    return True

def setup_github_remote():
    """Set up GitHub remote if not exists."""
    print("\n🐙 GITHUB SETUP")
    print("=" * 40)
    
    # Check if remote exists
    result = subprocess.run('git remote -v', shell=True, capture_output=True, text=True)
    if 'origin' in result.stdout:
        print("✅ GitHub remote already configured")
        return True
    
    print("🔗 GitHub remote not found. You need to:")
    print("1. Create a repository on GitHub.com")
    print("2. Make it PUBLIC (required for Railway free tier)")
    print("3. Copy the repository URL")
    
    repo_url = input("\n📝 Enter your GitHub repository URL (https://github.com/username/repo.git): ").strip()
    
    if not repo_url:
        print("❌ No URL provided")
        return False
    
    if not repo_url.startswith('https://github.com/'):
        print("❌ Invalid GitHub URL format")
        return False
    
    success, _ = run_command(f'git remote add origin {repo_url}', 'Adding GitHub remote')
    if not success:
        return False
    
    success, _ = run_command('git branch -M main', 'Setting main branch')
    if not success:
        return False
    
    success, _ = run_command('git push -u origin main', 'Pushing to GitHub', show_output=True)
    return success

def deploy_to_railway():
    """Guide user through Railway deployment."""
    print("\n🚂 RAILWAY DEPLOYMENT")
    print("=" * 40)
    
    print("📋 Follow these steps to deploy to Railway:")
    print()
    print("1. 🌐 Go to https://railway.app")
    print("2. 🔐 Click 'Login with GitHub'")
    print("3. ✅ Authorize Railway to access your repositories")
    print("4. ➕ Click 'Start a New Project'")
    print("5. 📂 Click 'Deploy from GitHub repo'")
    print("6. 🔍 Find and select your repository")
    print("7. 🚀 Click 'Deploy Now'")
    print("8. ⏳ Wait 2-3 minutes for deployment")
    print("9. 🔗 Get your app URL from Railway dashboard")
    
    print("\n🌐 Opening Railway in your browser...")
    webbrowser.open('https://railway.app')
    
    input("\n⏸️  Press Enter after you've completed the Railway deployment...")
    
    app_url = input("📝 Enter your Railway app URL (optional): ").strip()
    
    if app_url:
        print(f"\n🎉 Your app is deployed at: {app_url}")
        print("📱 You can now access your stock analysis from anywhere!")
        
        test_app = input("\n🧪 Open your app in browser to test? (y/n): ").strip().lower()
        if test_app == 'y':
            webbrowser.open(app_url)
    
    return True

def verify_deployment_files():
    """Verify all required deployment files exist."""
    print("\n📋 VERIFYING DEPLOYMENT FILES")
    print("=" * 40)
    
    required_files = {
        'Procfile': 'Railway process configuration',
        'requirements.txt': 'Python dependencies',
        'runtime.txt': 'Python version specification',
        'mobile_web_app.py': 'Main Flask application',
        'stock_config.py': 'Stock configuration'
    }
    
    all_good = True
    for filename, description in required_files.items():
        if os.path.exists(filename):
            print(f"✅ {filename} - {description}")
        else:
            print(f"❌ {filename} - {description} (MISSING)")
            all_good = False
    
    return all_good

def main():
    """Main Railway deployment process."""
    print("🚂 RAILWAY DEPLOYMENT ASSISTANT")
    print("=" * 50)
    print("Deploy your Stock Analysis app to Railway!")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check current directory and provide guidance
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    if not os.path.exists('mobile_web_app.py'):
        print("\n❌ Error: mobile_web_app.py not found")
        print("📁 You need to navigate to the algorithmic-trading-project directory first")
        print("\n🔧 Run this command to navigate to the correct directory:")
        print('cd "/Users/keeryu/Library/Mobile Documents/com~apple~icloud~applecorporate/Documents/Coding/algorithmic-trading-project"')
        print("\n🚀 Then run the deployment script again:")
        print("python3 deploy_railway.py")
        return
    
    # Step 1: Verify deployment files
    if not verify_deployment_files():
        print("\n❌ Missing required files. Please ensure all files are present.")
        return
    
    # Step 2: Set up git
    if not check_git_status():
        print("\n❌ Git setup failed. Please check the errors above.")
        return
    
    # Step 3: Set up GitHub
    if not setup_github_remote():
        print("\n❌ GitHub setup failed. Please check the errors above.")
        return
    
    # Step 4: Deploy to Railway
    if not deploy_to_railway():
        print("\n❌ Railway deployment guidance failed.")
        return
    
    # Success!
    print("\n🎉 DEPLOYMENT COMPLETE!")
    print("=" * 50)
    print("✅ Your stock analysis app is now deployed to Railway!")
    print("📱 Access it from any device with internet connection")
    print("🔄 Future updates: just push to GitHub and Railway auto-deploys")
    print("💰 Cost: ~$0.50/month (covered by Railway's $5 free credit)")
    
    print("\n📖 For detailed instructions, check:")
    print("📄 RAILWAY_DEPLOYMENT.md")
    
    print("\n🎯 Next steps:")
    print("1. Bookmark your Railway URL on your phone")
    print("2. Test the stock analysis and options features")
    print("3. Share with friends (optional)")
    print("4. Enjoy analyzing stocks from anywhere!")

if __name__ == "__main__":
    main()