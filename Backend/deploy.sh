#!/bin/bash

echo "🚀 DDI Predictor Backend Deployment Script"
echo "=========================================="
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "✅ requirements.txt found"
echo ""

# Check if Procfile exists
if [ ! -f "Procfile" ]; then
    echo "❌ Procfile not found!"
    exit 1
fi

echo "✅ Procfile found"
echo ""

# Check if Firebase credentials exist
if [ ! -f "firebase-credentials.json" ]; then
    echo "⚠️  Warning: firebase-credentials.json not found"
    echo "   Make sure to add it as a secret in your deployment platform"
fi

echo ""
echo "📦 Deployment files ready!"
echo ""
echo "Choose your deployment platform:"
echo "1. Render (Recommended - Free)"
echo "2. Railway (Easy)"
echo "3. Google Cloud Run (Scalable)"
echo "4. Manual Docker build"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🎨 Deploying to Render..."
        echo "1. Go to https://render.com"
        echo "2. Sign up/Login with GitHub"
        echo "3. Click 'New +' → 'Web Service'"
        echo "4. Connect your repository"
        echo "5. Configure:"
        echo "   - Root Directory: Backend"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: uvicorn api.main_with_firebase:app --host 0.0.0.0 --port \$PORT"
        echo "6. Add Firebase credentials as Secret File"
        echo "7. Deploy!"
        ;;
    2)
        echo ""
        echo "🚂 Deploying to Railway..."
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        railway login
        railway init
        railway up
        ;;
    3)
        echo ""
        echo "☁️  Deploying to Google Cloud Run..."
        if ! command -v gcloud &> /dev/null; then
            echo "❌ Google Cloud SDK not installed"
            echo "Install from: https://cloud.google.com/sdk/docs/install"
            exit 1
        fi
        gcloud builds submit --tag gcr.io/deepddi/ddi-api
        gcloud run deploy ddi-api --image gcr.io/deepddi/ddi-api --platform managed --region us-central1 --allow-unauthenticated
        ;;
    4)
        echo ""
        echo "🐳 Building Docker image..."
        docker build -t ddi-predictor-api .
        echo "✅ Docker image built successfully!"
        echo "Run with: docker run -p 5000:5000 ddi-predictor-api"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment process initiated!"
echo "📖 See BACKEND_DEPLOYMENT_GUIDE.md for detailed instructions"
