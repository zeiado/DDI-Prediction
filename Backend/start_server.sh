#!/bin/bash

# DDI Predictor - Start Backend Server

echo "=========================================="
echo "🚀 Starting DDI Predictor Backend Server"
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
    echo "⚠️  Warning: Model not found!"
    echo "Run preprocessing and training first:"
    echo "  cd src"
    echo "  python data_preprocessing_optimized.py"
    echo "  python model_training.py"
    exit 1
fi

# Start the API server
echo ""
echo "=========================================="
echo "🔥 Backend Server Starting..."
echo "=========================================="
echo "📍 API: http://localhost:5000"
echo "📚 Docs: http://localhost:5000/docs"
echo "🛑 Press Ctrl+C to stop"
echo "=========================================="
echo ""

cd api
python main.py
