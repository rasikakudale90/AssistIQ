import 'package:flutter/material.dart';
import '../core/api_client.dart';
import '../models/insights_model.dart';

class InsightsProvider extends ChangeNotifier {
  OperationalInsightsModel? _insights;
  DashboardStatsModel? _stats;
  bool _isLoading = false;
  String _timeWindow = '30d';

  OperationalInsightsModel? get insights => _insights;
  DashboardStatsModel? get stats => _stats;
  bool get isLoading => _isLoading;
  String get timeWindow => _timeWindow;

  Future<void> fetchDashboardStats() async {
    try {
      final res = await ApiClient.get('/insights/dashboard');
      _stats = DashboardStatsModel.fromJson(res);
      notifyListeners();
    } catch (_) {}
  }

  Future<void> fetchInsights([String? window]) async {
    if (window != null) _timeWindow = window;
    _isLoading = true;
    notifyListeners();

    try {
      final res = await ApiClient.get('/insights', queryParams: {'window': _timeWindow});
      _insights = OperationalInsightsModel.fromJson(res);
    } catch (_) {} finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
