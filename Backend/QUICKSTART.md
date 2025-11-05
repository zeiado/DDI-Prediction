# 🚀 Quick Start Guide

Get your DDI Predictor backend up and running in minutes!

## ⚡ Fast Track (Automated)

```bash
# 1. Run setup
./setup.sh

# 2. Run complete pipeline (preprocess + train + API)
./run_pipeline.sh
```

That's it! The API will be running at http://localhost:5000

## 📝 Step-by-Step (Manual)

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Preprocess Data

```bash
cd src
python data_preprocessing.py
```

**Expected output:**
- `../data/X_train.npy`
- `../data/X_test.npy`
- `../data/y_train.npy`
- `../data/y_test.npy`
- `../data/preprocessor.pkl`

### 3. Train Model

```bash
python model_training.py
```

**Expected output:**
- `../models/deepddi_model.pt`
- `../models/deepddi_best.pt`
- `../models/model_info.json`
- `../logs/confusion_matrix.png`
- `../logs/training_history.png`

**Training time:** ~10-30 minutes (depending on hardware)

### 4. Test Predictions

```bash
python predict.py
```

This will run example predictions to verify everything works.

### 5. Start API Server

```bash
cd ../api
python main.py
```

Or use uvicorn:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload
```

## 🧪 Test the API

### Browser

Open http://localhost:5000/docs for interactive API documentation

### Command Line

```bash
# Health check
curl http://localhost:5000/health

# Search drugs
curl "http://localhost:5000/search-drugs?q=aspirin"

# Check interaction
curl -X POST http://localhost:5000/check-interaction \
  -H "Content-Type: application/json" \
  -d '{"drug_a": "Warfarin", "drug_b": "Aspirin"}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:5000/check-interaction",
    json={"drug_a": "Warfarin", "drug_b": "Aspirin"}
)

print(response.json())
```

## 🐳 Docker (Alternative)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📱 Connect Flutter App

Update `flutter/lib/utils/constants.dart`:

```dart
// Android Emulator
static const String baseUrl = 'http://10.0.2.2:5000';

// iOS Simulator  
static const String baseUrl = 'http://localhost:5000';

// Physical Device (replace with your IP)
static const String baseUrl = 'http://192.168.1.XXX:5000';
```

## ✅ Verification Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Data files exist in `../model_data/`
- [ ] Preprocessing completed without errors
- [ ] Model trained and saved
- [ ] Prediction test successful
- [ ] API server running
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Can search for drugs
- [ ] Can check interactions

## 🐛 Common Issues

### Issue: "Module not found"

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Data files not found"

```bash
# Check if files exist
ls -la ../model_data/

# Files should be:
# - drug_info_combined.csv
# - db_drug_interactions.csv
```

### Issue: "CUDA out of memory"

Edit `src/model_training.py`:
```python
# Reduce batch size
train_loader = DataLoader(train_dataset, batch_size=64, ...)
```

### Issue: "Port 5000 already in use"

```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
uvicorn api.main:app --port 8000
```

## 📊 Expected Performance

- **Preprocessing**: 5-10 minutes
- **Training**: 10-30 minutes
- **Inference**: <100ms per prediction
- **Model Accuracy**: ~90-92%

## 🎯 Next Steps

1. ✅ Backend running
2. 📱 Test with Flutter app
3. 🔧 Fine-tune model parameters
4. 🚀 Deploy to production server
5. 📈 Monitor performance

## 💡 Tips

- Use GPU for faster training (if available)
- Keep model files backed up
- Monitor API logs for errors
- Test with various drug combinations
- Update drug database regularly

## 📚 Resources

- Full documentation: `README.md`
- API docs: http://localhost:5000/docs
- Model architecture: See `src/model_training.py`
- Data preprocessing: See `src/data_preprocessing.py`

---

**Need help?** Check the main README.md or open an issue!
