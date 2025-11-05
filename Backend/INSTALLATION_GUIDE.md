# 🔧 Installation Guide - Python 3.12 Compatible

## ✅ Installation Status

Your setup is now installing with Python 3.12 compatible packages!

## 📦 What's Being Installed

- **PyTorch 2.9.0** (~900MB) - Deep learning framework
- **RDKit 2023.9.1** - Chemistry toolkit for SMILES processing
- **FastAPI** - Modern web framework for API
- **Scikit-learn** - Machine learning utilities
- **Pandas & NumPy** - Data processing
- **Matplotlib & Seaborn** - Visualization

## ⏱️ Installation Time

- **Total time**: ~5-10 minutes (depending on internet speed)
- **PyTorch download**: ~3-5 minutes (900MB)
- **Other packages**: ~2-3 minutes

## 🚀 After Installation Completes

### Step 1: Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python -c "import torch; import rdkit; import fastapi; print('✅ All packages installed successfully!')"
```

### Step 2: Preprocess Data

```bash
cd src
python data_preprocessing.py
```

**Expected output:**
```
Loading drug SMILES data...
Processing drugs: 100%
Loaded XXXX drug entries

Loading drug interactions...
Loaded XXXXX interactions

Processing drug pairs...
Creating fingerprints: 100%

Class distribution:
  None: XXXX (XX.XX%)
  Moderate: XXXX (XX.XX%)
  Severe: XXXX (XX.XX%)

Training set: XXXX samples
Test set: XXXX samples

✅ Preprocessing complete!
```

**Time**: ~5-10 minutes

### Step 3: Train Model

```bash
python model_training.py
```

**Expected output:**
```
Using device: cuda/cpu

Model Architecture:
DeepDDI(...)
Total parameters: 2,234,567

Starting training on cuda/cpu
============================================================

Epoch 1/30
  Train Loss: 0.XXXX | Train Acc: XX.XX%
  Val Loss: 0.XXXX | Val Acc: XX.XX%
  ✅ Best model saved!

...

✅ TRAINING COMPLETE!
Model saved to: ../models/deepddi_model.pt
Final test accuracy: XX.XX%
```

**Time**: ~10-30 minutes (depending on hardware)

### Step 4: Test Predictions

```bash
python predict.py
```

This will run example predictions to verify the model works.

### Step 5: Start API Server

```bash
cd ../api
python main.py
```

**API will be available at:**
- Main API: http://localhost:5000
- Documentation: http://localhost:5000/docs
- Health check: http://localhost:5000/health

## 🧪 Quick Test Commands

After API is running:

```bash
# Test health
curl http://localhost:5000/health

# Test drug search
curl "http://localhost:5000/search-drugs?q=aspirin"

# Test interaction check
curl -X POST http://localhost:5000/check-interaction \
  -H "Content-Type: application/json" \
  -d '{"drug_a": "Warfarin", "drug_b": "Aspirin"}'
```

## 📱 Connect Flutter App

Once API is running, test with your Flutter app:

```bash
cd ../../flutter
flutter run
```

The app is already configured to connect to `http://10.0.2.2:5000` (Android emulator).

## 🐛 Troubleshooting

### Issue: Import errors after installation

```bash
# Reinstall specific package
pip install --force-reinstall rdkit

# Or reinstall all
pip install --force-reinstall -r requirements.txt
```

### Issue: CUDA not available

This is normal if you don't have an NVIDIA GPU. The model will use CPU, which is slower but works fine.

```python
# Check in Python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
# Output: CUDA available: False (on CPU) or True (on GPU)
```

### Issue: Out of memory during training

Edit `src/model_training.py`:

```python
# Line ~XXX - Reduce batch size
train_loader = DataLoader(train_dataset, batch_size=64, ...)  # Was 128
```

### Issue: RDKit import error

```bash
# Try alternative installation
pip uninstall rdkit
pip install rdkit-pypi
```

## 📊 Expected Performance

### With CPU:
- Training: ~20-30 minutes
- Inference: ~100-200ms per prediction

### With GPU (CUDA):
- Training: ~5-10 minutes
- Inference: ~10-50ms per prediction

## 🎯 Next Steps After Installation

1. ✅ Installation complete
2. 📊 Run preprocessing
3. 🧠 Train model
4. 🧪 Test predictions
5. 🚀 Start API server
6. 📱 Connect Flutter app
7. 🎉 Test complete system!

## 💡 Pro Tips

- **Use GPU**: If you have NVIDIA GPU, install CUDA-enabled PyTorch for 5-10x faster training
- **Monitor training**: Watch the training progress - it should show improving accuracy
- **Save checkpoints**: The best model is automatically saved during training
- **Test thoroughly**: Use the sample predictions to verify model quality
- **Check logs**: Training generates visualization plots in `logs/` directory

## 📝 Files Generated During Process

```
Backend/
├── data/                      # After preprocessing
│   ├── X_train.npy           # Training features
│   ├── X_test.npy            # Test features
│   ├── y_train.npy           # Training labels
│   ├── y_test.npy            # Test labels
│   └── preprocessor.pkl      # Preprocessor state
├── models/                    # After training
│   ├── deepddi_model.pt      # Final model
│   ├── deepddi_best.pt       # Best model checkpoint
│   └── model_info.json       # Model metadata
└── logs/                      # After training
    ├── confusion_matrix.png  # Evaluation plot
    └── training_history.png  # Training curves
```

## 🔄 Retraining the Model

If you want to retrain with different parameters:

```bash
# Delete old models
rm -rf models/* data/*

# Run preprocessing again
cd src
python data_preprocessing.py

# Train with new parameters (edit model_training.py first)
python model_training.py
```

## 📚 Additional Resources

- **PyTorch Docs**: https://pytorch.org/docs/
- **RDKit Docs**: https://www.rdkit.org/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Project README**: See `README.md` for full documentation

---

**Installation should complete in ~5-10 minutes. Check terminal for progress!**
