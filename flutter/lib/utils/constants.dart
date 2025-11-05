import 'package:flutter/material.dart';

class AppConstants {
  static const String baseUrl = 'http://192.168.1.9:5000';
  static const String checkInteractionEndpoint = '/check-interaction';
  static const String searchDrugsEndpoint = '/search-drugs';
  static const String healthEndpoint = '/health';

  // Severity Colors - More vibrant and modern
  static const Color lowColor = Color(0xFF10B981); // Emerald green
  static const Color moderateColor = Color(0xFFF59E0B); // Amber
  static const Color highColor = Color(0xFFEF4444); // Red
  static const Color unknownColor = Color(0xFF6B7280); // Gray

  // UI constants
  static const double padding = 16.0;
  static const double radius = 12.0;
  static const double elevation = 2.0;

  // Animation durations
  static const Duration shortAnimation = Duration(milliseconds: 300);
  static const Duration mediumAnimation = Duration(milliseconds: 600);
  static const Duration longAnimation = Duration(milliseconds: 1500);

  // Error messages
  static const String networkError = 'Network error. Please check your connection.';
  static const String serverOffline = 'Server seems offline.';

  static Color getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'low':
        return lowColor;
      case 'moderate':
        return moderateColor;
      case 'high':
        return highColor;
      default:
        return unknownColor;
    }
  }
}
