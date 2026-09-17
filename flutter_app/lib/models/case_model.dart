class SLAInfo {
  final String id;
  final String priority;
  final String responseDeadline;
  final String resolveDeadline;
  final String? firstResponseAt;
  final String? resolvedAt;
  final bool responseBreached;
  final bool resolveBreached;
  final int? minutesToResponseDeadline;
  final int? minutesToResolveDeadline;

  SLAInfo({
    required this.id,
    required this.priority,
    required this.responseDeadline,
    required this.resolveDeadline,
    this.firstResponseAt,
    this.resolvedAt,
    required this.responseBreached,
    required this.resolveBreached,
    this.minutesToResponseDeadline,
    this.minutesToResolveDeadline,
  });

  factory SLAInfo.fromJson(Map<String, dynamic> json) {
    return SLAInfo(
      id: json['id'] as String,
      priority: json['priority'] as String,
      responseDeadline: json['response_deadline'] as String,
      resolveDeadline: json['resolve_deadline'] as String,
      firstResponseAt: json['first_response_at'] as String?,
      resolvedAt: json['resolved_at'] as String?,
      responseBreached: json['response_breached'] as bool? ?? false,
      resolveBreached: json['resolve_breached'] as bool? ?? false,
      minutesToResponseDeadline: json['minutes_to_response_deadline'] as int?,
      minutesToResolveDeadline: json['minutes_to_resolve_deadline'] as int?,
    );
  }
}

class CaseModel {
  final String id;
  final String referenceNumber;
  final String title;
  final String description;
  final String caseType;
  final String category;
  final String priority;
  final String status;
  final String requesterId;
  final String? requesterEmail;
  final String? assignedOperatorId;
  final String? assignedTeamId;
  final String? site;
  final int version;
  final String createdAt;
  final String updatedAt;
  final SLAInfo? sla;

  CaseModel({
    required this.id,
    required this.referenceNumber,
    required this.title,
    required this.description,
    required this.caseType,
    required this.category,
    required this.priority,
    required this.status,
    required this.requesterId,
    this.requesterEmail,
    this.assignedOperatorId,
    this.assignedTeamId,
    this.site,
    required this.version,
    required this.createdAt,
    required this.updatedAt,
    this.sla,
  });

  factory CaseModel.fromJson(Map<String, dynamic> json) {
    return CaseModel(
      id: json['id'] as String,
      referenceNumber: json['reference_number'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      caseType: json['case_type'] as String? ?? 'Incident',
      category: json['category'] as String? ?? 'General',
      priority: json['priority'] as String? ?? 'P3',
      status: json['status'] as String? ?? 'New',
      requesterId: json['requester_id'] as String,
      requesterEmail: json['requester_email'] as String?,
      assignedOperatorId: json['assigned_operator_id'] as String?,
      assignedTeamId: json['assigned_team_id'] as String?,
      site: json['site'] as String?,
      version: json['version'] as int? ?? 1,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
      sla: json['sla'] != null ? SLAInfo.fromJson(json['sla']) : null,
    );
  }
}
