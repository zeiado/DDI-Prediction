# Firestore Index Setup

## Issue
You're getting this error in the history screen:
```
[cloud_firestore/failed-precondition] The query requires an index.
```

## Solution

### Step 1: Create the Index

1. **Open Firebase Console:**
   - Go to: https://console.firebase.google.com
   - Select your project: **deepddi**

2. **Navigate to Firestore:**
   - Click on "Firestore Database" in the left menu
   - Click on "Indexes" tab

3. **Create Composite Index:**
   - Click "Create Index" button
   - Or click the link from the error message (it auto-fills the settings)

4. **Index Configuration:**
   ```
   Collection ID: interactions
   
   Fields to index:
   - userId (Ascending)
   - timestamp (Descending)
   
   Query scope: Collection
   ```

5. **Click "Create"**
   - The index will take a few minutes to build
   - You'll see "Building..." status
   - Wait until it shows "Enabled"

### Step 2: Test

Once the index is enabled:
1. Restart your Flutter app
2. Go to History screen
3. It should now load without errors

## Why This is Needed

Firebase requires composite indexes for queries that:
- Filter by one field (userId)
- AND sort by another field (timestamp)

This ensures fast query performance even with millions of records.

## Alternative: Firestore Rules

If you want to avoid creating indexes manually, you can also set up Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /interactions/{interactionId} {
      allow read: if request.auth != null && 
                     resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && 
                       request.resource.data.userId == request.auth.uid;
    }
  }
}
```

But you still need the composite index for the query to work!
