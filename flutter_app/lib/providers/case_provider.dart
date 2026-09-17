import 'package:flutter/material.dart';
import '../core/api_client.dart';
import '../models/case_model.dart';
import '../models/triage_model.dart';
import '../models/message_model.dart';

class CaseProvider extends ChangeNotifier {
  List<CaseModel> _cases = [];
  CaseModel? _selectedCase;
  bool _isLoading = false;
  String _filter = 'ALL';
  String _searchQuery = '';

  List<CaseModel> get cases => _cases;
  CaseModel? get selectedCase => _selectedCase;
  bool get isLoading => _isLoading;
  String get filter => _filter;
  String get searchQuery => _searchQuery;

  List<CaseModel> get filteredCases {
    return _cases.where((c) {
      final matchesSearch = c.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          c.referenceNumber.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          c.category.toLowerCase().contains(_searchQuery.toLowerCase());

      if (!matchesSearch) return false;

      if (_filter == 'ACTIVE') {
        return !['Resolved', 'Closed', 'Cancelled'].contains(c.status);
      }
      if (_filter == 'BREACHED') {
        return (c.sla?.responseBreached ?? false) || (c.sla?.resolveBreached ?? false);
      }
      if (_filter == 'UNASSIGNED') {
        return c.assignedOperatorId == null && !['Resolved', 'Closed', 'Cancelled'].contains(c.status);
      }
      return true;
    }).toList();
  }

  void setFilter(String f) {
    _filter = f;
    notifyListeners();
  }

  void setSearchQuery(String q) {
    _searchQuery = q;
    notifyListeners();
  }

  void selectCase(CaseModel c) {
    _selectedCase = c;
    notifyListeners();
  }

  Future<void> fetchCases() async {
    _isLoading = true;
    notifyListeners();

    try {
      final res = await ApiClient.get('/cases');
      if (res is List) {
        _cases = res.map((json) => CaseModel.fromJson(json)).toList();
        if (_cases.isNotEmpty && _selectedCase == null) {
          _selectedCase = _cases.first;
        } else if (_selectedCase != null) {
          final found = _cases.where((c) => c.id == _selectedCase!.id);
          if (found.isNotEmpty) _selectedCase = found.first;
        }
      }
    } catch (_) {
      // Ignored
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<CaseModel> createCase({
    required String title,
    required String description,
    String caseType = 'Incident',
    String category = 'Hardware',
    String priority = 'P3',
    String site = 'Main Facility',
  }) async {
    final res = await ApiClient.post('/cases', body: {
      'title': title,
      'description': description,
      'case_type': caseType,
      'category': category,
      'priority': priority,
      'site': site,
    });
    final newCase = CaseModel.fromJson(res);
    await fetchCases();
    _selectedCase = newCase;
    notifyListeners();
    return newCase;
  }

  Future<void> updateStatus(String caseId, String status, int version) async {
    final res = await ApiClient.patch('/cases/$caseId/status', body: {
      'status': status,
      'expected_version': version,
    });
    final updated = CaseModel.fromJson(res);
    _selectedCase = updated;
    await fetchCases();
  }

  Future<void> updatePriority(String caseId, String priority, int version) async {
    final res = await ApiClient.patch('/cases/$caseId/priority', body: {
      'priority': priority,
      'expected_version': version,
    });
    final updated = CaseModel.fromJson(res);
    _selectedCase = updated;
    await fetchCases();
  }

  Future<AITriageResultModel?> getTriage(String caseId) async {
    try {
      final res = await ApiClient.get('/cases/$caseId/triage');
      return AITriageResultModel.fromJson(res);
    } catch (_) {
      return null;
    }
  }

  Future<CaseSummaryModel?> getSummary(String caseId) async {
    try {
      final res = await ApiClient.get('/cases/$caseId/summary');
      return CaseSummaryModel.fromJson(res);
    } catch (_) {
      return null;
    }
  }

  Future<List<MessageModel>> getMessages(String caseId) async {
    try {
      final res = await ApiClient.get('/cases/$caseId/messages');
      if (res is List) {
        return res.map((m) => MessageModel.fromJson(m)).toList();
      }
    } catch (_) {}
    return [];
  }

  Future<void> postMessage(String caseId, String body, String visibility) async {
    await ApiClient.post('/cases/$caseId/messages', body: {
      'body': body,
      'visibility': visibility,
    });
  }
}
