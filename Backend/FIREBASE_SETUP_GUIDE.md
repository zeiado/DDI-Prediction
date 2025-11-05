# 🔥 Firebase Firestore Setup Guide

Complete guide to integrate Firebase Firestore with your DDI Prediction Backend and Flutter App.

---

## 📋 Overview

Firebase Firestore will provide:
- ✅ **User Authentication** - Secure user accounts
- ✅ **Interaction History** - Store user's drug interaction checks
- ✅ **User Profiles** - Store user preferences and data
- ✅ **Real-time Sync** - Automatic sync between devices
- ✅ **Cloud Storage** - Scalable and reliable

---

## 🚀 Part 1: Firebase Console Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `ddi-predictor` (or your choice)
4. Enable Google Analytics (optional)
5. Click **"Create project"**

### Step 2: Enable Firestore Database

1. In Firebase Console, go to **"Build" → "Firestore Database"**
2. Click **"Create database"**
3. Choose **"Start in test mode"** (we'll secure it later)
4. Select location: Choose closest to your users
5. Click **"Enable"**

### Step 3: Enable Authentication

1. Go to **"Build" → "Authentication"**
2. Click **"Get started"**
3. Enable **"Email/Password"** sign-in method
4. Enable **"Anonymous"** sign-in (optional, for guest users)
5. Click **"Save"**

### Step 4: Register Flutter App

1. In Firebase Console, click **"Add app"** → Select **Flutter** icon
2. Follow the FlutterFire CLI setup:

```bash
# Install FlutterFire CLI
dart pub global activate flutterfire_cli

# Login to Firebase
firebase login

# Configure Flutter app
cd /home/zeiado/DDI-Prediction/flutter
flutterfire configure
```

3. Select your Firebase project
4. Select platforms: **Android**, **iOS**, **Web** (as needed)
5. This will create `firebase_options.dart` automatically

### Step 5: Get Service Account Key (for Backend)

1. Go to **Project Settings** (gear icon) → **"Service accounts"**
2. Click **"Generate new private key"**
3. Download the JSON file
4. Save it as: `/home/zeiado/DDI-Prediction/Backend/firebase-credentials.json`
5. **IMPORTANT**: Add to `.gitignore` to keep it private!

---

## 📊 Part 2: Firestore Database Structure

### Collections Schema:

```
ddi-predictor/
├── users/
│   └── {userId}/
│       ├── email: string
│       ├── displayName: string
│       ├── createdAt: timestamp
│       ├── totalChecks: number
│       └── preferences: map
│
├── interactions/
│   └── {interactionId}/
│       ├── userId: string
│       ├── drugA: string
│       ├── drugB: string
│       ├── severity: string
│       ├── riskScore: number
│       ├── description: string
│       ├── mechanism: string
│       ├── recommendations: array
│       ├── probabilities: map
│       ├── timestamp: timestamp
│       └── deviceInfo: map
│
├── drugs/
│   └── {drugId}/
│       ├── name: string
│       ├── genericName: string
│       ├── smiles: string
│       ├── drugClass: string
│       └── description: string
│
└── analytics/
    └── {date}/
        ├── totalChecks: number
        ├── uniqueUsers: number
        ├── topDrugPairs: array
        └── severityDistribution: map
```

### Firestore Security Rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users collection
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Interactions collection
    match /interactions/{interactionId} {
      allow read: if request.auth != null && 
                     resource.data.userId == request.auth.uid;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && 
                               resource.data.userId == request.auth.uid;
    }
    
    // Drugs collection (read-only for all authenticated users)
    match /drugs/{drugId} {
      allow read: if request.auth != null;
      allow write: if false; // Only admins can write (via backend)
    }
    
    // Analytics (read-only for authenticated users)
    match /analytics/{document=**} {
      allow read: if request.auth != null;
      allow write: if false; // Only backend can write
    }
  }
}
```

Apply these rules:
1. Go to **Firestore Database** → **"Rules"** tab
2. Paste the rules above
3. Click **"Publish"**

---

## 🔧 Part 3: Backend Integration

### Install Firebase Admin SDK:

```bash
cd /home/zeiado/DDI-Prediction/Backend
source venv/bin/activate
pip install firebase-admin
```

### Update requirements.txt:

Add to `/home/zeiado/DDI-Prediction/Backend/requirements.txt`:
```
firebase-admin>=6.2.0
```

---

## 📱 Part 4: Flutter App Integration

### Install Firebase packages:

```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter pub add firebase_core
flutter pub add firebase_auth
flutter pub add cloud_firestore
flutter pub add firebase_analytics
```

### Update `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Existing packages...
  provider: ^6.0.5
  http: ^1.1.0
  
  # Firebase packages
  firebase_core: ^2.24.2
  firebase_auth: ^4.15.3
  cloud_firestore: ^4.13.6
  firebase_analytics: ^10.7.4
```

---

## 🔐 Part 5: Environment Variables

### Create `.env` file:

```bash
# Backend/.env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=ddi-predictor
FIREBASE_DATABASE_URL=https://ddi-predictor.firebaseio.com
```

### Add to `.gitignore`:

```
# Backend/.gitignore
firebase-credentials.json
.env
venv/
__pycache__/
*.pyc
```

---

## 📝 Part 6: Testing Firebase Connection

### Test Backend Connection:

```bash
cd /home/zeiado/DDI-Prediction/Backend/src
python test_firebase.py
```

Expected output:
```
✅ Firebase initialized successfully
✅ Firestore connection established
✅ Test document created
✅ Test document read
✅ Firebase is working!
```

### Test Flutter Connection:

```bash
cd /home/zeiado/DDI-Prediction/flutter
flutter run
```

Check logs for:
```
✅ Firebase initialized
✅ Firestore connected
```

---

## 🎯 Part 7: Usage Examples

### Backend - Save Interaction:

```python
from firebase_service import FirebaseService

firebase = FirebaseService()

# Save interaction result
interaction_data = {
    'userId': 'user123',
    'drugA': 'Warfarin',
    'drugB': 'Ibuprofen',
    'severity': 'Moderate',
    'riskScore': 9.99,
    'timestamp': datetime.now()
}

firebase.save_interaction(interaction_data)
```

### Flutter - Fetch History:

```dart
// Get user's interaction history
Stream<List<InteractionResult>> getHistory(String userId) {
  return FirebaseFirestore.instance
    .collection('interactions')
    .where('userId', isEqualTo: userId)
    .orderBy('timestamp', descending: true)
    .limit(50)
    .snapshots()
    .map((snapshot) => snapshot.docs
        .map((doc) => InteractionResult.fromFirestore(doc))
        .toList());
}
```

---

## 🔒 Part 8: Security Best Practices

1. **Never commit credentials**:
   - Add `firebase-credentials.json` to `.gitignore`
   - Use environment variables

2. **Use Firestore Security Rules**:
   - Restrict read/write access
   - Validate data before writing

3. **Enable App Check** (optional):
   - Prevents abuse from unauthorized clients
   - Go to Firebase Console → App Check

4. **Set up billing alerts**:
   - Firebase Console → Usage and billing
   - Set budget alerts

5. **Monitor usage**:
   - Check Firebase Console regularly
   - Review authentication logs

---

## 📊 Part 9: Data Migration

### Populate Firestore with Drug Data:

```bash
cd /home/zeiado/DDI-Prediction/Backend/src
python migrate_drugs_to_firestore.py
```

This will:
- Read drugs from CSV
- Upload to Firestore `drugs` collection
- Create searchable indexes

---

## 🚀 Part 10: Deployment Checklist

Before going to production:

- [ ] Switch Firestore to **production mode**
- [ ] Update security rules (remove test mode)
- [ ] Enable **App Check**
- [ ] Set up **billing alerts**
- [ ] Configure **backup** (Firestore automatic backups)
- [ ] Test authentication flow
- [ ] Test data sync
- [ ] Monitor error logs
- [ ] Set up **Cloud Functions** (optional, for triggers)

---

## 💡 Pro Tips

1. **Use Firestore Indexes**:
   - Firebase will prompt you to create indexes
   - Follow the links in error messages

2. **Batch Operations**:
   - Use batch writes for multiple documents
   - More efficient than individual writes

3. **Offline Support**:
   - Firestore has built-in offline support
   - Data syncs automatically when online

4. **Cost Optimization**:
   - Use queries wisely (each read costs)
   - Implement pagination
   - Cache frequently accessed data

5. **Real-time Listeners**:
   - Use streams for live updates
   - Unsubscribe when not needed

---

## 🐛 Troubleshooting

### Issue: "Permission denied" errors

**Solution**: Check Firestore security rules and ensure user is authenticated

### Issue: "Firebase not initialized"

**Solution**: Make sure `Firebase.initializeApp()` is called before any Firebase operations

### Issue: "Service account key not found"

**Solution**: Verify `firebase-credentials.json` path is correct

### Issue: "Quota exceeded"

**Solution**: Check Firebase Console → Usage, upgrade plan if needed

---

## 📚 Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [FlutterFire Documentation](https://firebase.flutter.dev/)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)

---

**Next: Run the setup scripts to integrate Firebase with your system!**
