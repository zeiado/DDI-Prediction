"""
Firebase Firestore Service for DDI Predictor Backend
Handles all Firebase operations including user management and data storage
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseService:
    """Firebase Firestore service for DDI Predictor"""
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize Firebase Admin SDK
        
        Args:
            credentials_path: Path to Firebase service account JSON file
        """
        if credentials_path is None:
            credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', '../firebase-credentials.json')
        
        # Initialize Firebase Admin SDK (only once)
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing Firebase: {e}")
                raise
        
        # Get Firestore client
        self.db = firestore.client()
        print("✅ Firestore client connected")
    
    # ==================== User Management ====================
    
    def create_user(self, email: str, password: str, display_name: str = None) -> Dict:
        """
        Create a new user in Firebase Authentication and Firestore
        
        Args:
            email: User email
            password: User password
            display_name: Optional display name
            
        Returns:
            User data dictionary
        """
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            # Create user document in Firestore
            user_data = {
                'email': email,
                'displayName': display_name or email.split('@')[0],
                'createdAt': firestore.SERVER_TIMESTAMP,
                'totalChecks': 0,
                'preferences': {
                    'notifications': True,
                    'theme': 'light'
                }
            }
            
            self.db.collection('users').document(user.uid).set(user_data)
            
            print(f"✅ User created: {email}")
            return {'uid': user.uid, **user_data}
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user data from Firestore
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            User data dictionary or None
        """
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return {'uid': user_id, **doc.to_dict()}
            return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    def update_user(self, user_id: str, data: Dict) -> bool:
        """
        Update user data in Firestore
        
        Args:
            user_id: Firebase user ID
            data: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        try:
            self.db.collection('users').document(user_id).update(data)
            print(f"✅ User updated: {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    # ==================== Interaction Management ====================
    
    def save_interaction(self, interaction_data: Dict) -> str:
        """
        Save drug interaction result to Firestore
        
        Args:
            interaction_data: Dictionary containing interaction details
            
        Returns:
            Document ID of saved interaction
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in interaction_data:
                interaction_data['timestamp'] = firestore.SERVER_TIMESTAMP
            
            # Save to Firestore
            doc_ref = self.db.collection('interactions').add(interaction_data)
            doc_id = doc_ref[1].id
            
            # Update user's total checks count
            if 'userId' in interaction_data:
                user_ref = self.db.collection('users').document(interaction_data['userId'])
                user_ref.update({
                    'totalChecks': firestore.Increment(1)
                })
            
            print(f"✅ Interaction saved: {doc_id}")
            return doc_id
            
        except Exception as e:
            print(f"❌ Error saving interaction: {e}")
            raise
    
    def get_user_interactions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get user's interaction history
        
        Args:
            user_id: Firebase user ID
            limit: Maximum number of interactions to return
            
        Returns:
            List of interaction dictionaries
        """
        try:
            docs = (self.db.collection('interactions')
                   .where('userId', '==', user_id)
                   .order_by('timestamp', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            interactions = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                interactions.append(data)
            
            return interactions
            
        except Exception as e:
            print(f"❌ Error getting interactions: {e}")
            return []
    
    def delete_interaction(self, interaction_id: str, user_id: str) -> bool:
        """
        Delete an interaction (with user verification)
        
        Args:
            interaction_id: Interaction document ID
            user_id: User ID (for verification)
            
        Returns:
            True if successful
        """
        try:
            doc_ref = self.db.collection('interactions').document(interaction_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            # Verify ownership
            if doc.to_dict().get('userId') != user_id:
                print("❌ User doesn't own this interaction")
                return False
            
            doc_ref.delete()
            print(f"✅ Interaction deleted: {interaction_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting interaction: {e}")
            return False
    
    def clear_user_history(self, user_id: str) -> int:
        """
        Clear all interactions for a user
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            Number of interactions deleted
        """
        try:
            docs = (self.db.collection('interactions')
                   .where('userId', '==', user_id)
                   .stream())
            
            count = 0
            batch = self.db.batch()
            
            for doc in docs:
                batch.delete(doc.reference)
                count += 1
            
            batch.commit()
            
            # Reset user's total checks
            self.db.collection('users').document(user_id).update({
                'totalChecks': 0
            })
            
            print(f"✅ Cleared {count} interactions for user {user_id}")
            return count
            
        except Exception as e:
            print(f"❌ Error clearing history: {e}")
            return 0
    
    # ==================== Drug Management ====================
    
    def add_drug(self, drug_data: Dict) -> str:
        """
        Add a drug to Firestore
        
        Args:
            drug_data: Dictionary containing drug information
            
        Returns:
            Document ID
        """
        try:
            doc_ref = self.db.collection('drugs').add(drug_data)
            doc_id = doc_ref[1].id
            print(f"✅ Drug added: {drug_data.get('name')}")
            return doc_id
        except Exception as e:
            print(f"❌ Error adding drug: {e}")
            raise
    
    def get_drug(self, drug_name: str) -> Optional[Dict]:
        """
        Get drug information by name
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Drug data dictionary or None
        """
        try:
            docs = (self.db.collection('drugs')
                   .where('name', '==', drug_name)
                   .limit(1)
                   .stream())
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting drug: {e}")
            return None
    
    def search_drugs(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for drugs by name (prefix search)
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching drugs
        """
        try:
            # Firestore doesn't support full-text search natively
            # This is a simple prefix search
            query_upper = query.upper()
            
            docs = (self.db.collection('drugs')
                   .where('name', '>=', query)
                   .where('name', '<=', query + '\uf8ff')
                   .limit(limit)
                   .stream())
            
            drugs = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                drugs.append(data)
            
            return drugs
            
        except Exception as e:
            print(f"❌ Error searching drugs: {e}")
            return []
    
    # ==================== Analytics ====================
    
    def save_analytics(self, date: str, analytics_data: Dict) -> bool:
        """
        Save daily analytics data
        
        Args:
            date: Date string (YYYY-MM-DD)
            analytics_data: Analytics dictionary
            
        Returns:
            True if successful
        """
        try:
            self.db.collection('analytics').document(date).set(
                analytics_data,
                merge=True
            )
            print(f"✅ Analytics saved for {date}")
            return True
        except Exception as e:
            print(f"❌ Error saving analytics: {e}")
            return False
    
    def get_analytics(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get analytics data for date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of analytics dictionaries
        """
        try:
            docs = (self.db.collection('analytics')
                   .where(firestore.FieldPath.document_id(), '>=', start_date)
                   .where(firestore.FieldPath.document_id(), '<=', end_date)
                   .stream())
            
            analytics = []
            for doc in docs:
                data = doc.to_dict()
                data['date'] = doc.id
                analytics.append(data)
            
            return analytics
            
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return []
    
    # ==================== Utility Methods ====================
    
    def test_connection(self) -> bool:
        """
        Test Firestore connection
        
        Returns:
            True if connection is working
        """
        try:
            # Try to read from a collection
            test_ref = self.db.collection('_test').document('connection')
            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
            
            doc = test_ref.get()
            if doc.exists:
                test_ref.delete()
                print("✅ Firestore connection test successful")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Firestore connection test failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("Firebase Service Test")
    print("="*60)
    
    try:
        # Initialize service
        firebase = FirebaseService()
        
        # Test connection
        if firebase.test_connection():
            print("\n✅ Firebase service is working correctly!")
        else:
            print("\n❌ Firebase service test failed")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. firebase-credentials.json exists")
        print("2. Firebase project is set up")
        print("3. Firestore is enabled")
