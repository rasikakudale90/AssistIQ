class AITriageResultModel {
  final String id;
  final String predictedCategory;
  final String predictedPriority;
  final double confidenceScore;
  final List<String> supportingFactors;
  final List<String> missingInfoQuestions;

  AITriageResultModel({
    required this.id,
    required this.predictedCategory,
    required this.predictedPriority,
    required this.confidenceScore,
    required this.supportingFactors,
    required this.missingInfoQuestions,
  });

  factory AITriageResultModel.fromJson(Map<String, dynamic> json) {
    return AITriageResultModel(
      id: json['id'] as String,
      predictedCategory: json['predicted_category'] as String? ?? 'General',
      predictedPriority: json['predicted_priority'] as String? ?? 'P3',
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0.8,
      supportingFactors: (json['supporting_factors'] as List<dynamic>? ?? []).map((e) => e.toString()).toList(),
      missingInfoQuestions: (json['missing_info_questions'] as List<dynamic>? ?? []).map((e) => e.toString()).toList(),
    );
  }
}

class CaseSummaryModel {
  final String id;
  final String whatWasReported;
  final String whatHappenedSince;
  final String whatIsConfirmed;
  final String whatRemainsUnresolved;

  CaseSummaryModel({
    required this.id,
    required this.whatWasReported,
    required this.whatHappenedSince,
    required this.whatIsConfirmed,
    required this.whatRemainsUnresolved,
  });

  factory CaseSummaryModel.fromJson(Map<String, dynamic> json) {
    return CaseSummaryModel(
      id: json['id'] as String,
      whatWasReported: json['what_was_reported'] as String? ?? '',
      whatHappenedSince: json['what_happened_since'] as String? ?? '',
      whatIsConfirmed: json['what_is_confirmed'] as String? ?? '',
      whatRemainsUnresolved: json['what_remains_unresolved'] as String? ?? '',
    );
  }
}
