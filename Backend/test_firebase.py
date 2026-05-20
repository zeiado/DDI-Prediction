#!/usr/bin/env python3
"""
Quick Firebase Connection Test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 50)
print("🔥 Testing Firebase Connection")
print("=" * 50)

# Check if credentials file exists
creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
if os.path.exists(creds_path):
    print(f"✅ Credentials file found: {creds_path}")
else:
    print(f"❌ Credentials file NOT found: {creds_path}")
    exit(1)

# Check project ID
project_id = os.getenv('FIREBASE_PROJECT_ID', 'deepddi')
print(f"✅ Project ID: {project_id}")

# Try to initialize Firebase
try:
    from src.firebase_service import FirebaseService
    print("\n🔄 Initializing Firebase...")
    
    fs = FirebaseService()
    print("✅ Firebase service initialized!")
    
    # Test connection
    print("\n🔄 Testing Firestore connection...")
    if fs.test_connection():
        print("✅ Firebase connected successfully!")
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
        print("=" * 50)
    else:
        print("❌ Firebase connection test failed")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
