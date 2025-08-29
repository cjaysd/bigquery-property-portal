# Launch to Render via GitHub - Complete Step-by-Step Guide

## Overview
This guide will walk you through deploying your Google BigQuery Property Analysis application to Render (a cloud hosting platform) using GitHub (code repository). No prior experience required!

## What We're Doing
1. Creating a GitHub account and repository
2. Uploading your code to GitHub
3. Creating a Render account
4. Connecting GitHub to Render
5. Deploying your application
6. Setting up environment variables
7. Testing your live application

---

## Phase 1: GitHub Setup (30 minutes)

### Step 1.1: Create GitHub Account
1. Go to https://github.com
2. Click "Sign up" (top right corner)
3. Enter:
   - Your email address
   - Create a password
   - Choose a username (e.g., "yourname-airbnb")
4. Verify your email by clicking the link GitHub sends you

### Step 1.2: Install GitHub Desktop (Easier for Beginners)
1. Go to https://desktop.github.com
2. Download GitHub Desktop for Mac
3. Open the downloaded file and drag to Applications
4. Launch GitHub Desktop
5. Sign in with your new GitHub account

### Step 1.3: Create Your First Repository
1. In GitHub Desktop, click "Create a New Repository on your Hard Drive"
2. Name: `bigquery-property-portal`
3. Description: "Property analysis portal with BigQuery integration"
4. Local Path: Choose where to save (leave default is fine)
5. Initialize with README: Check this box
6. Git Ignore: Select "Python"
7. License: Select "MIT License"
8. Click "Create Repository"

### Step 1.4: Copy Your Project Files
1. Open Finder
2. Navigate to `/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery`
3. Select ALL files EXCEPT:
   - Any files starting with `.` (like `.env` if present)
   - `__pycache__` folder
   - Any `.pyc` files
   - Any personal/sensitive data files
4. Copy these files
5. Navigate to the new repository folder GitHub Desktop created
6. Paste all files there

### Step 1.5: Review and Remove Sensitive Data
**CRITICAL**: Check these files for sensitive information:
1. Open each Python file and look for:
   - API keys (especially ClickUp: `pk_120213011_5ZNEENWOLLDGUG3C5EA40CE41C5O91XB`)
   - Passwords
   - Personal addresses
   - Private URLs
2. If found, we'll need to replace them with environment variables (covered in Phase 4)

### Step 1.6: First Commit
1. Return to GitHub Desktop
2. You'll see all your files listed as changes
3. In bottom left, write commit message: "Initial commit - Property portal application"
4. Click "Commit to main"
5. Click "Publish repository" (top toolbar)
6. Make sure "Keep this code private" is UNCHECKED (Render free tier needs public repos)
7. Click "Publish Repository"

---

## Phase 2: Prepare Application for Deployment (20 minutes)

### Step 2.1: Create requirements.txt
Create a new file called `requirements.txt` with ALL Python packages:

```txt
Flask==2.3.2
flask-cors==4.0.0
google-cloud-bigquery==3.11.4
google-cloud-bigquery-storage==2.22.0
pandas==2.0.3
pandas-gbq==0.19.2
pyarrow==12.0.1
requests==2.31.0
python-dotenv==1.0.0
playwright==1.40.0
selenium==4.15.2
webdriver-manager==4.0.1
gunicorn==21.2.0
```

### Step 2.2: Create Render Configuration
Create a new file called `render.yaml`:

```yaml
services:
  - type: web
    name: property-portal
    runtime: python
    buildCommand: "pip install -r requirements.txt && playwright install chromium"
    startCommand: "gunicorn app:app --bind 0.0.0.0:$PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 10000
      - key: CLICKUP_API_TOKEN
        sync: false
      - key: GOOGLE_APPLICATION_CREDENTIALS_JSON
        sync: false
```

### Step 2.3: Modify app.py for Production
We need to update `app.py` to handle environment variables:

1. At the top of `app.py`, add:
```python
import os
from dotenv import load_dotenv
import json
import tempfile

load_dotenv()

# Get ClickUp API token from environment
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN', 'your-default-token-here')

# Handle Google credentials
google_creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
if google_creds_json:
    # Create temporary file for credentials
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(google_creds_json)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
```

2. Replace hardcoded API token in HTML files:
   - Search for `pk_120213011_5ZNEENWOLLDGUG3C5EA40CE41C5O91XB`
   - We'll need to pass this from the Flask backend instead

### Step 2.4: Create .env.example
Create a file called `.env.example`:

```env
CLICKUP_API_TOKEN=your_clickup_api_token_here
GOOGLE_APPLICATION_CREDENTIALS_JSON=your_google_credentials_json_here
```

### Step 2.5: Update .gitignore
Create or update `.gitignore`:

```
*.pyc
__pycache__/
.env
.DS_Store
*.log
venv/
env/
.idea/
.vscode/
node_modules/
dist/
build/
*.egg-info/
```

### Step 2.6: Commit Changes
1. In GitHub Desktop, review all changes
2. Commit message: "Add deployment configuration for Render"
3. Click "Commit to main"
4. Click "Push origin" (top toolbar)

---

## Phase 3: Render Account Setup (15 minutes)

### Step 3.1: Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest option):
   - Click "Sign up with GitHub"
   - Authorize Render to access your GitHub
4. Verify your email if requested

### Step 3.2: Connect GitHub Repository
1. In Render Dashboard, click "New +"
2. Select "Web Service"
3. Connect to GitHub repository:
   - You'll see your repositories listed
   - Select `bigquery-property-portal`
   - Click "Connect"

### Step 3.3: Configure Service
1. Name: `property-portal` (or whatever you prefer)
2. Region: Select closest to you (Oregon is default)
3. Branch: `main`
4. Runtime: `Python 3`
5. Build Command: `pip install -r requirements.txt && playwright install chromium`
6. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
7. Instance Type: Select "Free" ($0/month)

---

## Phase 4: Environment Variables Setup (15 minutes)

### Step 4.1: Get Your ClickUp API Token
1. Your current token: `pk_120213011_5ZNEENWOLLDGUG3C5EA40CE41C5O91XB`
2. In Render, scroll to "Environment Variables"
3. Add:
   - Key: `CLICKUP_API_TOKEN`
   - Value: `pk_120213011_5ZNEENWOLLDGUG3C5EA40CE41C5O91XB`

### Step 4.2: Get Google Cloud Credentials
1. Find your Google credentials JSON file (usually in your project or home directory)
2. Open the file and copy ALL contents
3. In Render, add:
   - Key: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - Value: Paste the entire JSON content

### Step 4.3: Add Python Version
1. Add:
   - Key: `PYTHON_VERSION`
   - Value: `3.11.0`

### Step 4.4: Deploy
1. Scroll to bottom
2. Click "Create Web Service"
3. Wait for deployment (5-10 minutes first time)

---

## Phase 5: Testing and Troubleshooting (10 minutes)

### Step 5.1: Access Your Application
1. Once deployed, Render provides a URL like: `https://property-portal.onrender.com`
2. Test your endpoints:
   - Main page: `https://property-portal.onrender.com/copyJIC?taskId=868fd6tdt`
   - Dashboard: `https://property-portal.onrender.com/dashboard`

### Step 5.2: View Logs
1. In Render Dashboard, click on your service
2. Click "Logs" tab
3. Look for any errors

### Step 5.3: Common Issues and Fixes

**Issue: "ModuleNotFoundError"**
- Solution: Add missing module to requirements.txt, commit, push

**Issue: "Port binding error"**
- Solution: Make sure using `$PORT` environment variable

**Issue: "Google credentials error"**
- Solution: Check GOOGLE_APPLICATION_CREDENTIALS_JSON is properly set

**Issue: "ClickUp API error"**
- Solution: Verify CLICKUP_API_TOKEN is set correctly

---

## Phase 6: Ongoing Maintenance

### Making Updates
1. Make changes locally
2. In GitHub Desktop:
   - Review changes
   - Commit with descriptive message
   - Push to GitHub
3. Render automatically redeploys (takes 2-3 minutes)

### Monitoring
1. Check Render dashboard for:
   - Service status (should be "Live")
   - Recent deploys
   - Error logs
   - Usage metrics

### Free Tier Limitations
- Your app may sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month free (plenty for one app)
- Public repository required

---

## Security Checklist Before Deployment

### Must Remove/Replace:
- [ ] ClickUp API token in HTML files
- [ ] Any hardcoded addresses
- [ ] Test task IDs in code
- [ ] Any personal information
- [ ] Debug mode in Flask (set to False)

### Must Add:
- [ ] Environment variables for all sensitive data
- [ ] Proper error handling
- [ ] Rate limiting for API calls
- [ ] Input validation

---

## Quick Command Reference

### GitHub Desktop:
- Commit: Save changes locally
- Push: Send changes to GitHub
- Pull: Get latest changes from GitHub

### Render:
- Manual Deploy: "Deploy" button in dashboard
- View Logs: "Logs" tab in service
- Environment Variables: "Environment" tab
- Restart: "Restart Service" button

---

## Estimated Timeline
1. GitHub Setup: 30 minutes
2. Code Preparation: 20 minutes
3. Render Setup: 15 minutes
4. Environment Variables: 15 minutes
5. Testing: 10 minutes
**Total: ~1.5 hours**

---

## Next Steps After Deployment
1. Share your Render URL with team
2. Set up custom domain (optional, ~$20/year)
3. Enable auto-scaling when ready ($7/month per instance)
4. Set up monitoring alerts
5. Create staging environment for testing

---

## Need Help?
- GitHub Support: https://support.github.com
- Render Support: https://render.com/docs
- Community Forum: https://community.render.com

Remember: Take it step by step. Each phase builds on the previous one. If you get stuck, the logs will usually tell you what's wrong!