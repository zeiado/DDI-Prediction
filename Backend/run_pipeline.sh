#!/bin/bash

# Complete pipeline: Preprocess → Train → Run API

echo "=========================================="
echo "DDI Predictor - Complete Pipeline"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ Virtual environment not found. Run ./setup.sh first${NC}"
    exit 1
fi

# Step 1: Preprocess data
echo -e "\n${YELLOW}Step 1: Preprocessing data...${NC}"
cd src
python data_preprocessing.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Preprocessing failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Preprocessing complete${NC}"

# Step 2: Train model
echo -e "\n${YELLOW}Step 2: Training model...${NC}"
python model_training.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Training failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Training complete${NC}"

# Step 3: Test predictions
echo -e "\n${YELLOW}Step 3: Testing predictions...${NC}"
python predict.py

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Prediction test failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Predictions working${NC}"

# Step 4: Run API
echo -e "\n${YELLOW}Step 4: Starting API server...${NC}"
cd ../api
echo ""
echo "=========================================="
echo -e "${GREEN}API Server Starting${NC}"
echo "=========================================="
echo "API: http://localhost:5000"
echo "Docs: http://localhost:5000/docs"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

python main.py
