# 🔧 Troubleshooting "Server Offline" Issue

## ✅ Step 1: Restart Backend with Fixed Code

The error handler has been fixed. Restart your backend:

```bash
# Stop the current server (Press Ctrl+C in the backend terminal)

# Then restart it
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

---

## ✅ Step 2: Verify Backend is Running

Test the backend with curl:

```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "ok",
  "online": true,
  "model_loaded": true,
  "timestamp": "2025-11-03T19:27:00Z",
  "version": "1.0.0"
}
```

If this works, your backend is running correctly!

---

## ✅ Step 3: Check Your Device Type

### Are you using Android Emulator or Physical Device?

**To check, look at your `flutter run` output:**

```
Connected device:
- sdk gphone64 arm64 (mobile) • emulator-5554 • android-arm64 • Android 13 (API 33)
  ↑ This is an EMULATOR

- SM-G991B (mobile) • RFCR123ABC • android-arm64 • Android 13 (API 33)
  ↑ This is a PHYSICAL DEVICE
```

---

## 🔧 Step 4: Configure Based on Device Type

### Option A: Android Emulator (Default - Should Work)

Your Flutter app is already configured for emulator:

**File:** `flutter/lib/utils/constants.dart`
```dart
static const String baseUrl = 'http://10.0.2.2:5000';  // ✅ Correct for emulator
```

**No changes needed!**

---

### Option B: Physical Android Device

If you're using a **physical device**, you need to change the URL:

1. **Find your computer's IP address:**

```bash
# On Linux
hostname -I | awk '{print $1}'

# Or
ip addr show | grep "inet " | grep -v 127.0.0.1
```

Example output: `192.168.1.100`

2. **Update Flutter constants:**

Edit `flutter/lib/utils/constants.dart`:

```dart
// Change this line:
static const String baseUrl = 'http://10.0.2.2:5000';

// To your computer's IP:
static const String baseUrl = 'http://192.168.1.100:5000';  // Use YOUR IP
```

3. **Make sure phone and computer are on same WiFi network!**

4. **Hot restart Flutter app:**
   - Press `r` in the Flutter terminal
   - Or press `R` for full restart

---

### Option C: iOS Simulator

Edit `flutter/lib/utils/constants.dart`:

```dart
static const String baseUrl = 'http://localhost:5000';
```

---

### Option D: Web Browser

Edit `flutter/lib/utils/constants.dart`:

```dart
static const String baseUrl = 'http://localhost:5000';
```

---

## 🧪 Step 5: Test Connection from Flutter

### Method 1: Check Server Status in App

1. Open the app
2. Look at the home screen
3. Check the server status indicator (should be green/online)

### Method 2: Test from Device Terminal (Android)

```bash
# If using emulator
adb shell "curl http://10.0.2.2:5000/health"

# If using physical device (replace with your IP)
adb shell "curl http://192.168.1.100:5000/health"
```

---

## 🔍 Common Issues & Solutions

### Issue 1: "Connection refused"

**Cause:** Backend not running or wrong IP

**Solution:**
```bash
# Check backend is running
curl http://localhost:5000/health

# If not running, start it
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

---

### Issue 2: "Network unreachable" (Physical Device)

**Cause:** Phone and computer on different networks

**Solution:**
1. Connect both to same WiFi
2. Disable mobile data on phone
3. Check firewall isn't blocking port 5000:

```bash
# Allow port 5000 through firewall
sudo ufw allow 5000
```

---

### Issue 3: Backend shows errors

**Cause:** Code errors or missing dependencies

**Solution:**
```bash
# Restart backend with fixed code
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

---

### Issue 4: "Server offline" but backend is running

**Cause:** Wrong URL in Flutter app

**Solution:**

**For Emulator:**
```dart
static const String baseUrl = 'http://10.0.2.2:5000';
```

**For Physical Device:**
```dart
static const String baseUrl = 'http://YOUR_COMPUTER_IP:5000';
```

Then hot restart: Press `R` in Flutter terminal

---

## ✅ Complete Checklist

Before running the app, verify:

- [ ] Backend is running (`./start_server.sh`)
- [ ] Backend health check works (`curl http://localhost:5000/health`)
- [ ] Correct URL in `constants.dart` based on device type
- [ ] Phone and computer on same WiFi (if physical device)
- [ ] Port 5000 not blocked by firewall
- [ ] Flutter app restarted after URL change

---

## 🎯 Quick Fix Commands

### Restart Everything:

**Terminal 1 (Backend):**
```bash
cd /home/zeiado/DDI-Prediction/Backend
./start_server.sh
```

**Terminal 2 (Flutter):**
```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter run
# Then press 'R' to hot restart
```

---

## 📊 Verify Connection Flow

```
1. Backend Running?
   ↓ YES
2. curl http://localhost:5000/health works?
   ↓ YES
3. Using Emulator or Physical Device?
   ↓ Emulator: Use 10.0.2.2:5000
   ↓ Physical: Use YOUR_IP:5000
4. Updated constants.dart?
   ↓ YES
5. Hot restarted Flutter (Press R)?
   ↓ YES
6. ✅ Should work now!
```

---

## 🆘 Still Not Working?

### Debug Steps:

1. **Check backend logs:**
   - Look at Terminal 1 (backend)
   - Should show: `INFO: Uvicorn running on http://0.0.0.0:5000`
   - Should NOT show errors

2. **Check Flutter logs:**
   - Look at Terminal 2 (Flutter)
   - Look for network errors
   - Look for connection refused messages

3. **Test API manually:**
   ```bash
   # From computer
   curl http://localhost:5000/health
   
   # From emulator
   adb shell "curl http://10.0.2.2:5000/health"
   ```

4. **Check firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 5000
   ```

5. **Check if port is in use:**
   ```bash
   lsof -i:5000
   ```

---

## 💡 Pro Tips

1. **Always start backend first**, then Flutter

2. **Keep backend terminal open** - Don't close it

3. **Use hot restart (R)** after changing constants.dart

4. **Check backend logs** for incoming requests

5. **Test with curl first** before testing with app

---

## ✅ Success Indicators

You'll know it's working when:

- ✅ Backend shows: `INFO: Uvicorn running on http://0.0.0.0:5000`
- ✅ curl health check returns JSON
- ✅ App shows "Server Online" (green indicator)
- ✅ Can search for drugs
- ✅ Can check interactions
- ✅ Backend logs show incoming requests

---

## 🎉 Once It Works

Your app will:
- ✅ Show server status as online
- ✅ Search 4,286 drugs
- ✅ Get AI predictions (93.84% accuracy)
- ✅ Display beautiful results
- ✅ Save history locally

**You're almost there! Follow the steps above.** 🚀
