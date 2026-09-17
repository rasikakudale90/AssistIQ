class DashboardStatsModel {
  final int activeCases;
  final int unassignedCases;
  final int breachedCases;
  final int criticalP1Cases;
  final int totalCases;

  DashboardStatsModel({
    required this.activeCases,
    required this.unassignedCases,
    required this.breachedCases,
    required this.criticalP1Cases,
    required this.totalCases,
  });

  factory DashboardStatsModel.fromJson(Map<String, dynamic> json) {
    return DashboardStatsModel(
      activeCases: json['active_cases'] as int? ?? 0,
      unassignedCases: json['unassigned_cases'] as int? ?? 0,
      breachedCases: json['breached_cases'] as int? ?? 0,
      criticalP1Cases: json['critical_p1_cases'] as int? ?? 0,
      totalCases: json['total_cases'] as int? ?? 0,
    );
  }
}

class TeamMetricModel {
  final String teamId;
  final String teamName;
  final int assignedCount;
  final int resolvedCount;
  final int breachCount;
  final double avgResolutionMinutes;

  TeamMetricModel({
    required this.teamId,
    required this.teamName,
    required this.assignedCount,
    required this.resolvedCount,
    required this.breachCount,
    required this.avgResolutionMinutes,
  });

  factory TeamMetricModel.fromJson(Map<String, dynamic> json) {
    return TeamMetricModel(
      teamId: json['team_id'] as String,
      teamName: json['team_name'] as String,
      assignedCount: json['assigned_count'] as int? ?? 0,
      resolvedCount: json['resolved_count'] as int? ?? 0,
      breachCount: json['breach_count'] as int? ?? 0,
      avgResolutionMinutes: (json['avg_resolution_minutes'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class OperationalInsightsModel {
  final String timeWindow;
  final int totalCases;
  final int resolvedCases;
  final int reopenedCases;
  final int breachedCases;
  final double reopenRatePercent;
  final double avgResolutionMinutes;
  final double slaComplianceRatePercent;
  final String? aiNarrative;
  final List<TeamMetricModel> teamMetrics;

  OperationalInsightsModel({
    required this.timeWindow,
    required this.totalCases,
    required this.resolvedCases,
    required this.reopenedCases,
    required this.breachedCases,
    required this.reopenRatePercent,
    required this.avgResolutionMinutes,
    required this.slaComplianceRatePercent,
    this.aiNarrative,
    this.teamMetrics = const [],
  });

  factory OperationalInsightsModel.fromJson(Map<String, dynamic> json) {
    var rawTeams = json['team_metrics'] as List<dynamic>? ?? [];
    return OperationalInsightsModel(
      timeWindow: json['time_window'] as String? ?? '30d',
      totalCases: json['total_cases'] as int? ?? 0,
      resolvedCases: json['resolved_cases'] as int? ?? 0,
      reopenedCases: json['reopened_cases'] as int? ?? 0,
      breachedCases: json['breached_cases'] as int? ?? 0,
      reopenRatePercent: (json['reopen_rate_percent'] as num?)?.toDouble() ?? 0.0,
      avgResolutionMinutes: (json['avg_resolution_minutes'] as num?)?.toDouble() ?? 0.0,
      slaComplianceRatePercent: (json['sla_compliance_rate_percent'] as num?)?.toDouble() ?? 0.0,
      aiNarrative: json['ai_narrative'] as String?,
      teamMetrics: rawTeams.map((t) => TeamMetricModel.fromJson(t)).toList(),
    );
  }
}
