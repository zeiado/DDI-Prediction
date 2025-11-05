# 🚀 How to Run Your DDI Predictor System

## ⚡ Quick Start (2 Steps)

### Step 1: Start Backend Server

Open a terminal and run:

```bash
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

**Expected output:**
```
========================================
🚀 Starting DDI Predictor Backend Server
========================================
✅ Virtual environment activated

========================================
🔥 Backend Server Starting...
========================================
📍 API: http://localhost:5000
📚 Docs: http://localhost:5000/docs
🛑 Press Ctrl+C to stop
========================================

✅ Model loaded successfully
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:5000
```

**Keep this terminal open!** The server must stay running.

---

### Step 2: Run Flutter App

Open a **NEW terminal** (keep the first one running!) and run:

```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter run
```

**That's it!** Your app should now connect to the backend.

---

## 🔍 Troubleshooting

### Problem: "Server offline" message in app

**Solution:** Make sure the backend server is running!

```bash
# Check if server is running
curl http://localhost:5000/health

# Expected response:
# {"status":"ok","online":true,"model_loaded":true,...}
```

If you get an error, start the server:
```bash
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

---

### Problem: "Model not found" error

**Solution:** Train the model first:

```bash
cd /home/zeiado/DDI-Prediction/Backend/src
source ../venv/bin/activate
python data_preprocessing_optimized.py
python model_training.py
```

---

### Problem: "Virtual environment not found"

**Solution:** Run setup first:

```bash
cd /home/zeiado/DDI-Prediction/Backend
./setup.sh
```

---

### Problem: Port 5000 already in use

**Solution:** Kill the process using port 5000:

```bash
# Find process
lsof -ti:5000

# Kill it
kill -9 $(lsof -ti:5000)

# Or use a different port (edit api/main.py)
```

---

## 📱 Testing the Connection

### 1. Test Backend Health:

```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "ok",
  "online": true,
  "model_loaded": true,
  "timestamp": "2025-11-03T19:13:02Z",
  "version": "1.0.0"
}
```

### 2. Test Drug Search:

```bash
curl "http://localhost:5000/search-drugs?q=war"
```

Should return:
```json
{
  "success": true,
  "results": ["Warfarin"],
  "count": 1
}
```

### 3. Test Interaction Check:

```bash
curl -X POST http://localhost:5000/check-interaction \
  -H "Content-Type: application/json" \
  -d '{"drug_a": "Warfarin", "drug_b": "Ibuprofen"}'
```

Should return interaction prediction with severity, risk score, etc.

---

## 🎯 Complete Workflow

### First Time Setup:

```bash
# 1. Setup backend
cd /home/zeiado/DDI-Prediction/Backend
./setup.sh

# 2. Preprocess data
cd src
python data_preprocessing_optimized.py

# 3. Train model
python model_training.py
```

### Every Time You Want to Use the App:

**Terminal 1 (Backend):**
```bash
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

**Terminal 2 (Flutter):**
```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter run
```

---

## 🔄 Alternative: Manual Start

If the script doesn't work, start manually:

### Backend:
```bash
cd /home/zeiado/DDI-Prediction/Backend
source venv/bin/activate
cd api
python main.py
```

### Flutter:
```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter run
```

---

## 📊 What Each Component Does

```
┌─────────────────────────────────────────┐
│  Flutter App (Mobile UI)                │
│  - Beautiful interface                  │
│  - Drug search                          │
│  - Results display                      │
│  - History management                   │
└──────────────┬──────────────────────────┘
               │ HTTP Requests
               ↓
┌─────────────────────────────────────────┐
│  FastAPI Backend (Port 5000)            │
│  - Receives requests                    │
│  - Loads drug data                      │
│  - Runs AI model                        │
│  - Returns predictions                  │
└──────────────┬──────────────────────────┘
               │ Uses
               ↓
┌─────────────────────────────────────────┐
│  DeepDDI Model (93.84% accuracy)        │
│  - Neural network                       │
│  - Trained on 42K interactions          │
│  - Predicts severity                    │
└─────────────────────────────────────────┘
```

---

## ✅ Success Checklist

Before running the app, make sure:

- [ ] Backend setup completed (`./setup.sh`)
- [ ] Data preprocessed (X_train.npy exists in Backend/data/)
- [ ] Model trained (deepddi_model.pt exists in Backend/models/)
- [ ] Backend server is running (Terminal 1)
- [ ] Flutter app is running (Terminal 2)
- [ ] Health check returns OK (`curl http://localhost:5000/health`)

---

## 💡 Pro Tips

1. **Keep backend terminal open** - Don't close it while using the app

2. **Check server logs** - Backend terminal shows all requests

3. **Use API docs** - Visit http://localhost:5000/docs for interactive testing

4. **Test API first** - Use curl to verify backend before running Flutter

5. **Hot reload works** - Make Flutter changes without restarting backend

---

## 🎉 You're Ready!

Your complete system:
- ✅ AI Model: 93.84% accuracy
- ✅ Backend API: FastAPI on port 5000
- ✅ Flutter App: Beautiful mobile UI
- ✅ 4,286 drugs in database

**Just run the two commands and enjoy your app!** 🚀

---

## 📞 Need Help?

If something doesn't work:

1. Check backend terminal for errors
2. Check Flutter terminal for errors
3. Test backend with curl commands
4. Verify model files exist
5. Check port 5000 is not in use

**Common issue:** "Server offline" = Backend not running → Start it!
