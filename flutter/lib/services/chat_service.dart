import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/chat_message.dart';
import '../utils/constants.dart';

/// Service for AI Chat Assistant
class ChatService {
  final String baseUrl;

  ChatService({this.baseUrl = AppConstants.apiBaseUrl});

  /// Generate initial bilingual summary when chat opens
  Future<Map<String, dynamic>> generateSummary({
    String? interactionId,
    Map<String, dynamic>? interactionData,
    String? userId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat/summary'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'interaction_id': interactionId,
          'interaction_data': interactionData,
          'user_id': userId,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'english': data['english'] ?? '',
          'arabic': data['arabic'] ?? '',
          'full_text': data['full_text'] ?? '',
          'timestamp': data['timestamp'] ?? DateTime.now().toIso8601String(),
        };
      } else {
        return {
          'success': false,
          'error': 'Failed to generate summary: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Send a chat message and get AI response
  Future<Map<String, dynamic>> sendMessage({
    String? interactionId,
    Map<String, dynamic>? interactionData,
    required String message,
    String? userId,
    List<ChatMessage>? chatHistory,
  }) async {
    try {
      // Convert chat history to backend format
      final historyJson = chatHistory
          ?.map((msg) => msg.toBackendFormat())
          .toList();

      final response = await http.post(
        Uri.parse('$baseUrl/chat/message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'interaction_id': interactionId,
          'interaction_data': interactionData,
          'message': message,
          'user_id': userId,
          'chat_history': historyJson,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'response': data['response'] ?? '',
          'timestamp': data['timestamp'] ?? DateTime.now().toIso8601String(),
          'language_detected': data['language_detected'],
        };
      } else {
        return {
          'success': false,
          'error': 'Failed to send message: ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }

  /// Check if chat service is available
  Future<bool> isAvailable() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // Check if both Firebase and model are loaded
        return data['firebase_connected'] == true && 
               data['model_loaded'] == true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
