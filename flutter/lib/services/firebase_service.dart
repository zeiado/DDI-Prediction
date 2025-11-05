import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/interaction_result.dart';

class FirebaseService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  // ==================== Authentication ====================

  /// Get current user
  User? get currentUser => _auth.currentUser;

  /// Check if user is signed in
  bool get isSignedIn => _auth.currentUser != null;

  /// Sign in with email and password
  Future<UserCredential> signIn(String email, String password) async {
    try {
      return await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
    } catch (e) {
      throw Exception('Sign in failed: $e');
    }
  }

  /// Sign up with email and password
  Future<UserCredential> signUp(String email, String password) async {
    try {
      final credential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Create user document in Firestore
      await _firestore.collection('users').doc(credential.user!.uid).set({
        'email': email,
        'displayName': email.split('@')[0],
        'createdAt': FieldValue.serverTimestamp(),
        'totalChecks': 0,
        'preferences': {
          'notifications': true,
          'theme': 'light',
        },
      });

      return credential;
    } catch (e) {
      throw Exception('Sign up failed: $e');
    }
  }

  /// Sign out
  Future<void> signOut() async {
    await _auth.signOut();
  }

  /// Sign in anonymously
  Future<UserCredential> signInAnonymously() async {
    return await _auth.signInAnonymously();
  }

  // ==================== User Data ====================

  /// Get user data
  Future<Map<String, dynamic>?> getUserData(String userId) async {
    try {
      final doc = await _firestore.collection('users').doc(userId).get();
      if (doc.exists) {
        return doc.data();
      }
      return null;
    } catch (e) {
      print('Error getting user data: $e');
      return null;
    }
  }

  /// Update user data
  Future<void> updateUserData(String userId, Map<String, dynamic> data) async {
    await _firestore.collection('users').doc(userId).update(data);
  }

  /// Increment total checks
  Future<void> incrementTotalChecks(String userId) async {
    await _firestore.collection('users').doc(userId).update({
      'totalChecks': FieldValue.increment(1),
    });
  }

  // ==================== Interaction History ====================

  /// Save interaction to Firestore
  Future<String> saveInteraction(InteractionResult result) async {
    try {
      final userId = currentUser?.uid;
      if (userId == null) {
        throw Exception('User not signed in');
      }

      final docRef = await _firestore.collection('interactions').add({
        'userId': userId,
        'drugPair': result.drugPair,
        'severity': result.severity,
        'riskScore': result.riskScore,
        'description': result.description,
        'mechanism': result.mechanism,
        'recommendations': result.recommendations,
        'sources': result.sources,
        'timestamp': FieldValue.serverTimestamp(),
      });

      // Increment user's total checks
      await incrementTotalChecks(userId);

      return docRef.id;
    } catch (e) {
      throw Exception('Failed to save interaction: $e');
    }
  }

  /// Get user's interaction history as stream
  Stream<List<InteractionResult>> getInteractionHistoryStream({int limit = 50}) {
    final userId = currentUser?.uid;
    if (userId == null) {
      return Stream.value([]);
    }

    return _firestore
        .collection('interactions')
        .where('userId', isEqualTo: userId)
        .orderBy('timestamp', descending: true)
        .limit(limit)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        final data = doc.data();
        return InteractionResult(
          success: true,
          drugPair: data['drugPair'] ?? '',
          interactionExists: data['severity'] != 'None',
          severity: data['severity'] ?? 'Unknown',
          riskScore: (data['riskScore'] ?? 0).toDouble(),
          description: data['description'] ?? '',
          mechanism: data['mechanism'] ?? '',
          recommendations: List<String>.from(data['recommendations'] ?? []),
          sources: List<String>.from(data['sources'] ?? []),
          timestamp: (data['timestamp'] as Timestamp?)?.toDate().toString() ??
              DateTime.now().toString(),
        );
      }).toList();
    });
  }

  /// Get user's interaction history (one-time fetch)
  Future<List<InteractionResult>> getInteractionHistory({int limit = 50}) async {
    final userId = currentUser?.uid;
    if (userId == null) {
      return [];
    }

    try {
      final snapshot = await _firestore
          .collection('interactions')
          .where('userId', isEqualTo: userId)
          .orderBy('timestamp', descending: true)
          .limit(limit)
          .get();

      return snapshot.docs.map((doc) {
        final data = doc.data();
        return InteractionResult(
          success: true,
          drugPair: data['drugPair'] ?? '',
          interactionExists: data['severity'] != 'None',
          severity: data['severity'] ?? 'Unknown',
          riskScore: (data['riskScore'] ?? 0).toDouble(),
          description: data['description'] ?? '',
          mechanism: data['mechanism'] ?? '',
          recommendations: List<String>.from(data['recommendations'] ?? []),
          sources: List<String>.from(data['sources'] ?? []),
          timestamp: (data['timestamp'] as Timestamp?)?.toDate().toString() ??
              DateTime.now().toString(),
        );
      }).toList();
    } catch (e) {
      print('Error getting history: $e');
      return [];
    }
  }

  /// Delete a specific interaction
  Future<void> deleteInteraction(String interactionId) async {
    await _firestore.collection('interactions').doc(interactionId).delete();
  }

  /// Clear all user's interactions
  Future<int> clearHistory() async {
    final userId = currentUser?.uid;
    if (userId == null) {
      return 0;
    }

    try {
      final snapshot = await _firestore
          .collection('interactions')
          .where('userId', isEqualTo: userId)
          .get();

      final batch = _firestore.batch();
      for (var doc in snapshot.docs) {
        batch.delete(doc.reference);
      }
      await batch.commit();

      // Reset total checks
      await _firestore.collection('users').doc(userId).update({
        'totalChecks': 0,
      });

      return snapshot.docs.length;
    } catch (e) {
      print('Error clearing history: $e');
      return 0;
    }
  }

  // ==================== Statistics ====================

  /// Get user statistics
  Future<Map<String, int>> getUserStats() async {
    final userId = currentUser?.uid;
    if (userId == null) {
      return {'totalChecks': 0, 'interactions': 0, 'safe': 0};
    }

    try {
      final userData = await getUserData(userId);
      final totalChecks = userData?['totalChecks'] ?? 0;

      final snapshot = await _firestore
          .collection('interactions')
          .where('userId', isEqualTo: userId)
          .get();

      int interactions = 0;
      int safe = 0;

      for (var doc in snapshot.docs) {
        final severity = doc.data()['severity'];
        if (severity == 'High' || severity == 'Moderate') {
          interactions++;
        } else {
          safe++;
        }
      }

      return {
        'totalChecks': totalChecks,
        'interactions': interactions,
        'safe': safe,
      };
    } catch (e) {
      print('Error getting stats: $e');
      return {'totalChecks': 0, 'interactions': 0, 'safe': 0};
    }
  }
}
