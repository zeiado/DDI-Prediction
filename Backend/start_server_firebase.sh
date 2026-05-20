#!/bin/bash

# DDI Predictor - Start Backend Server with Firebase

echo "=========================================="
echo "🚀 Starting DDI Predictor Backend Server"
echo "🔥 With Firebase Integration"
echo "=========================================="

# Navigate to Backend directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first"
    exit 1
fi

# Check if model exists
if [ ! -f "models/deepddi_model.pt" ]; then
    echo "❌ Model file not found!"
    echo "Run preprocessing and training first:"
    echo "  cd src"
    echo "  python data_preprocessing_optimized.py"
    echo "  python model_training.py"
    exit 1
fi

# Check if Firebase credentials exist
if [ ! -f "firebase-credentials.json" ]; then
    echo "⚠️  Warning: firebase-credentials.json not found!"
    echo "Firebase features may not work properly."
    echo "See FIREBASE_SETUP_GUIDE.md for setup instructions."
fi

# Start the API server with Firebase
echo ""
echo "=========================================="
echo "🔥 Backend Server Starting with Firebase..."
echo "=========================================="
echo "📍 API: http://localhost:5000"
echo "📚 Docs: http://localhost:5000/docs"
echo "🔐 Firebase: Enabled"
echo "🛑 Press Ctrl+C to stop"
echo "=========================================="
echo ""

cd api
python main_with_firebase.py
