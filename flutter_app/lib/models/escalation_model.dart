class EscalationEventModel {
  final String id;
  final String caseId;
  final String triggerType;
  final String reason;
  final String notifiedRole;
  final String? acknowledgedById;
  final String? acknowledgedAt;
  final String createdAt;
  final String? caseRef;
  final String? caseTitle;

  EscalationEventModel({
    required this.id,
    required this.caseId,
    required this.triggerType,
    required this.reason,
    required this.notifiedRole,
    this.acknowledgedById,
    this.acknowledgedAt,
    required this.createdAt,
    this.caseRef,
    this.caseTitle,
  });

  factory EscalationEventModel.fromJson(Map<String, dynamic> json) {
    return EscalationEventModel(
      id: json['id'] as String,
      caseId: json['case_id'] as String,
      triggerType: json['trigger_type'] as String? ?? 'SLA_BREACH',
      reason: json['reason'] as String? ?? '',
      notifiedRole: json['notified_role'] as String? ?? 'Manager',
      acknowledgedById: json['acknowledged_by_id'] as String?,
      acknowledgedAt: json['acknowledged_at'] as String?,
      createdAt: json['created_at'] as String,
      caseRef: json['case_ref'] as String?,
      caseTitle: json['case_title'] as String?,
    );
  }
}
