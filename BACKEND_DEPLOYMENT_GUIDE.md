# 🚀 Backend Deployment Guide - FastAPI + ML Model

## 📋 Table of Contents
1. [Preparation](#preparation)
2. [Option 1: Render (Recommended - Free)](#option-1-render-free)
3. [Option 2: Railway (Easy - Free Tier)](#option-2-railway)
4. [Option 3: Google Cloud Run (Scalable)](#option-3-google-cloud-run)
5. [Option 4: Heroku (Simple)](#option-4-heroku)
6. [Update Flutter App](#update-flutter-app)

---

## 📦 Preparation

### Step 1: Create Deployment Files

First, let's create the necessary files for deployment.

#### 1. Create `requirements.txt` (if not exists)

```bash
cd /home/zeiado/DDI-Prediction/Backend
pip freeze > requirements.txt
```

#### 2. Create `Procfile` for some platforms

```bash
echo "web: uvicorn api.main_with_firebase:app --host 0.0.0.0 --port \$PORT" > Procfile
```

#### 3. Create `runtime.txt` (specify Python version)

```bash
echo "python-3.10.12" > runtime.txt
```

#### 4. Update `.gitignore`

Make sure these are in your `.gitignore`:
```
__pycache__/
*.pyc
.env
venv/
*.pkl
*.h5
.DS_Store
firebase-credentials.json
```

---

## 🎯 Option 1: Render (Recommended - Free Tier)

**Why Render?**
- ✅ Free tier available
- ✅ Easy to use
- ✅ Auto-deploys from GitHub
- ✅ Good for ML models
- ✅ 750 hours/month free

### Step-by-Step:

#### 1. Push to GitHub

```bash
cd /home/zeiado/DDI-Prediction
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub
- Authorize Render to access your repositories

#### 3. Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `DDI-Prediction`
3. Configure:
   - **Name:** `ddi-predictor-api`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `Backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main_with_firebase:app --host 0.0.0.0 --port $PORT`

#### 4. Add Environment Variables
In Render dashboard, add:
```
FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase-credentials.json
FIREBASE_PROJECT_ID=deepddi
```

#### 5. Add Firebase Credentials as Secret File
1. In Render dashboard → "Environment"
2. Click "Secret Files"
3. Add file:
   - **Filename:** `/etc/secrets/firebase-credentials.json`
   - **Contents:** Paste your Firebase JSON credentials

#### 6. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Your API will be at: `https://ddi-predictor-api.onrender.com`

#### 7. Test
```bash
curl https://ddi-predictor-api.onrender.com/health
```

---

## 🚂 Option 2: Railway (Easy - Free Tier)

**Why Railway?**
- ✅ $5 free credit/month
- ✅ Very simple setup
- ✅ Great for FastAPI
- ✅ Auto-scaling

### Step-by-Step:

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Login

```bash
railway login
```

#### 3. Initialize Project

```bash
cd /home/zeiado/DDI-Prediction/Backend
railway init
```

#### 4. Add Environment Variables

```bash
railway variables set FIREBASE_PROJECT_ID=deepddi
```

For Firebase credentials:
```bash
railway variables set FIREBASE_CREDENTIALS=$(cat firebase-credentials.json | base64)
```

#### 5. Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api.main_with_firebase:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 6. Deploy

```bash
railway up
```

#### 7. Get URL

```bash
railway domain
```

---

## ☁️ Option 3: Google Cloud Run (Scalable)

**Why Cloud Run?**
- ✅ Pay only for what you use
- ✅ Auto-scaling
- ✅ Integrates with Firebase
- ✅ Free tier: 2M requests/month

### Step-by-Step:

#### 1. Install Google Cloud SDK

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### 2. Create `Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "api.main_with_firebase:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 3. Create `.dockerignore`

```
__pycache__
*.pyc
.env
venv/
.git
.gitignore
```

#### 4. Build and Deploy

```bash
cd /home/zeiado/DDI-Prediction/Backend

# Set project
gcloud config set project deepddi

# Build container
gcloud builds submit --tag gcr.io/deepddi/ddi-api

# Deploy to Cloud Run
gcloud run deploy ddi-api \
  --image gcr.io/deepddi/ddi-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=deepddi
```

#### 5. Get URL

```bash
gcloud run services describe ddi-api --region us-central1 --format 'value(status.url)'
```

---

## 🔴 Option 4: Heroku (Simple but Paid)

**Note:** Heroku no longer has a free tier, but it's very simple to use.

### Step-by-Step:

#### 1. Install Heroku CLI

```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Login

```bash
heroku login
```

#### 3. Create App

```bash
cd /home/zeiado/DDI-Prediction/Backend
heroku create ddi-predictor-api
```

#### 4. Add Buildpack

```bash
heroku buildpacks:set heroku/python
```

#### 5. Set Environment Variables

```bash
heroku config:set FIREBASE_PROJECT_ID=deepddi
heroku config:set FIREBASE_CREDENTIALS="$(cat firebase-credentials.json)"
```

#### 6. Deploy

```bash
git push heroku main
```

#### 7. Open

```bash
heroku open
```

---

## 📱 Update Flutter App

After deployment, update your Flutter app to use the deployed API:

### 1. Update API Base URL

Edit `/home/zeiado/DDI-Prediction/flutter/lib/services/api_service.dart`:

```dart
class ApiService {
  // Change this to your deployed URL
  static const String baseUrl = 'https://your-api-url.onrender.com';
  
  // Or use environment variable
  static String get baseUrl {
    return const String.fromEnvironment(
      'API_URL',
      defaultValue: 'https://your-api-url.onrender.com',
    );
  }
  
  // ... rest of code
}
```

### 2. Test Connection

```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter run
```

---

## 🔧 Troubleshooting

### Issue: Model file too large

**Solution:** Use Git LFS or download model at runtime

```python
# In your main.py
import requests
import os

MODEL_URL = "https://your-storage.com/model.pkl"
MODEL_PATH = "models/model.pkl"

def download_model():
    if not os.path.exists(MODEL_PATH):
        response = requests.get(MODEL_URL)
        with open(MODEL_PATH, 'wb') as f:
            f.write(response.content)

# Call on startup
download_model()
```

### Issue: Firebase credentials not found

**Solution:** Use environment variable

```python
import json
import os
from google.oauth2 import service_account

# Get credentials from environment
creds_json = os.getenv('FIREBASE_CREDENTIALS')
if creds_json:
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
```

### Issue: Port binding error

**Solution:** Use PORT environment variable

```python
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## ✅ Deployment Checklist

- [ ] All dependencies in `requirements.txt`
- [ ] Firebase credentials configured
- [ ] Environment variables set
- [ ] `.gitignore` updated (no secrets in repo)
- [ ] Model files accessible
- [ ] CORS configured for Flutter app
- [ ] Health endpoint working
- [ ] API tested with Postman/curl
- [ ] Flutter app updated with new URL
- [ ] SSL/HTTPS enabled
- [ ] Monitoring set up

---

## 🎯 My Recommendation

**Use Render (Option 1)** because:
1. ✅ Free tier (750 hours/month)
2. ✅ Easy GitHub integration
3. ✅ Good for ML models
4. ✅ Auto-deploys on push
5. ✅ Built-in SSL
6. ✅ Easy to manage

**Quick Start:**
1. Push code to GitHub
2. Connect to Render
3. Add Firebase credentials as secret file
4. Deploy!
5. Update Flutter app URL

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| **Render** | 750 hrs/mo | $7/mo | ML models, Easy setup |
| **Railway** | $5 credit/mo | $5/mo | Quick deployment |
| **Cloud Run** | 2M requests | Pay per use | High traffic, Scaling |
| **Heroku** | None | $7/mo | Enterprise apps |

---

## 🚀 Ready to Deploy?

Choose your platform and follow the steps above!

**Need help?** Let me know which platform you choose and I'll guide you through it!
