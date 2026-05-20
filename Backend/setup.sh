#!/bin/bash

# DDI Predictor Backend Setup Script

echo "=========================================="
echo "DDI Predictor Backend Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Error installing dependencies${NC}"
    exit 1
fi

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p data models logs

echo -e "${GREEN}✓ Directories created${NC}"

# Check if data files exist
echo -e "\n${YELLOW}Checking data files...${NC}"
if [ -f "../model_data/drug_info_combined.csv" ] && [ -f "../model_data/db_drug_interactions.csv" ]; then
    echo -e "${GREEN}✓ Data files found${NC}"
else
    echo -e "${RED}✗ Data files not found in ../model_data/${NC}"
    echo "Please ensure the following files exist:"
    echo "  - ../model_data/drug_info_combined.csv"
    echo "  - ../model_data/db_drug_interactions.csv"
fi

echo -e "\n=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Preprocess data: cd src && python data_preprocessing.py"
echo "  3. Train model: python model_training.py"
echo "  4. Run API: cd ../api && python main.py"
echo ""
echo "Or use the quick start script: ./run_pipeline.sh"
echo ""
