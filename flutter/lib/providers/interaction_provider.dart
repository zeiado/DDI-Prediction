import 'dart:collection';

import 'package:flutter/material.dart';
import '../models/interaction_result.dart';
import '../services/api_service.dart';
import '../services/firebase_service.dart';

class InteractionProvider extends ChangeNotifier {
  InteractionResult? _currentResult;
  bool _isLoading = false;
  String? _error;
  bool _isServerOnline = false;

  final List<InteractionResult> _history = [];

  InteractionResult? get currentResult => _currentResult;
  bool get isLoading => _isLoading;
  String? get error => _error;
  UnmodifiableListView<InteractionResult> get history => UnmodifiableListView(_history);
  bool get isServerOnline => _isServerOnline;

  final ApiService _api = ApiService.instance;
  final FirebaseService _firebase = FirebaseService();

  InteractionProvider();

  Future<void> checkServerHealth() async {
    try {
      final online = await _api.checkHealth();
      _isServerOnline = online;
      notifyListeners();
    } catch (_) {
      _isServerOnline = false;
      notifyListeners();
    }
  }

  Future<void> checkInteraction(String drugA, String drugB) async {
    if (drugA.trim().isEmpty || drugB.trim().isEmpty) {
      _error = 'Please enter both drug names.';
      notifyListeners();
      return;
    }
    if (drugA.trim().toLowerCase() == drugB.trim().toLowerCase()) {
      _error = 'Please choose two different drugs.';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _api.checkInteraction(drugA, drugB);
      _currentResult = result;

      // maintain history (most recent first), max 20
      _history.insert(0, result);
      if (_history.length > 20) _history.removeLast();

      // Save to Firebase if user is signed in
      if (_firebase.isSignedIn) {
        try {
          await _firebase.saveInteraction(result);
        } catch (e) {
          print('Failed to save to Firebase: $e');
          // Continue even if Firebase save fails
        }
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  void clearHistory() {
    _history.clear();
    notifyListeners();
  }

  void removeFromHistory(int index) {
    if (index >= 0 && index < _history.length) {
      _history.removeAt(index);
      notifyListeners();
    }
  }
}
