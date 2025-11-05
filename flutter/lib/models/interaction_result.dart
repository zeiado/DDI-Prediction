import 'dart:convert';

class InteractionResult {
  final bool success;
  final String drugPair;
  final bool interactionExists;
  final String severity;
  final double riskScore;
  final String description;
  final String mechanism;
  final List<String> recommendations;
  final List<String> sources;
  final String timestamp;
  final String? interactionId;

  InteractionResult({
    required this.success,
    required this.drugPair,
    required this.interactionExists,
    required this.severity,
    required this.riskScore,
    required this.description,
    required this.mechanism,
    required this.recommendations,
    required this.sources,
    required this.timestamp,
    this.interactionId,
  });

  factory InteractionResult.fromJson(Map<String, dynamic> json) {
    return InteractionResult(
      success: json['success'] == true,
      drugPair: json['drug_pair'] ?? '',
      interactionExists: json['interaction_exists'] == true,
      severity: (json['severity'] as String?) ?? 'Unknown',
      riskScore: (json['risk_score'] is num) ? (json['risk_score'] as num).toDouble() : 0.0,
      description: json['description'] ?? '',
      mechanism: json['mechanism'] ?? '',
      recommendations: (json['recommendations'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      sources: (json['sources'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      timestamp: json['timestamp'] ?? '',
      interactionId: json['interaction_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'drug_pair': drugPair,
      'interaction_exists': interactionExists,
      'severity': severity,
      'risk_score': riskScore,
      'description': description,
      'mechanism': mechanism,
      'recommendations': recommendations,
      'sources': sources,
      'timestamp': timestamp,
      'interaction_id': interactionId,
    };
  }

  @override
  String toString() => jsonEncode(toJson());
}
