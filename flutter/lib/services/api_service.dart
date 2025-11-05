import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;
import '../models/interaction_result.dart';
import '../utils/constants.dart';

class ApiService {
  ApiService._privateConstructor();

  static final ApiService _instance = ApiService._privateConstructor();

  static ApiService get instance => _instance;

  final http.Client _client = http.Client();

  Future<InteractionResult> checkInteraction(String drugA, String drugB) async {
    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.checkInteractionEndpoint}');
    try {
      final body = jsonEncode({'drug_a': drugA, 'drug_b': drugB});
      final resp = await _client
          .post(uri, headers: {'Content-Type': 'application/json'}, body: body)
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final json = jsonDecode(resp.body) as Map<String, dynamic>;
        return InteractionResult.fromJson(json);
      } else {
        throw Exception('Server error: ${resp.statusCode}');
      }
    } on TimeoutException catch (_) {
      throw Exception('Request timed out. Please try again.');
    } catch (e) {
      throw Exception('Failed to check interaction: ${e.toString()}');
    }
  }

  Future<List<String>> searchDrugs(String query) async {
    if (query.trim().length < 2) return [];
    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.searchDrugsEndpoint}?q=${Uri.encodeQueryComponent(query)}');
    try {
      final resp = await _client.get(uri).timeout(const Duration(seconds: 5));
      if (resp.statusCode == 200) {
        final json = jsonDecode(resp.body) as Map<String, dynamic>;
        final results = (json['results'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];
        return results;
      } else {
        throw Exception('Search error: ${resp.statusCode}');
      }
    } on TimeoutException catch (_) {
      throw Exception('Search timed out.');
    } catch (e) {
      throw Exception('Failed to search drugs: ${e.toString()}');
    }
  }

  Future<bool> checkHealth() async {
    final uri = Uri.parse('${AppConstants.baseUrl}${AppConstants.healthEndpoint}');
    try {
      final resp = await _client.get(uri).timeout(const Duration(seconds: 3));
      if (resp.statusCode == 200) {
        final json = jsonDecode(resp.body);
        if (json is Map<String, dynamic>) {
          return json['status'] == 'ok' || json['online'] == true || json['success'] == true;
        }
        return true;
      }
      return false;
    } on TimeoutException catch (_) {
      return false;
    } catch (_) {
      return false;
    }
  }
}
