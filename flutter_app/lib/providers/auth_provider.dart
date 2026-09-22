import 'package:flutter/material.dart';
import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/user.dart';

class AuthProvider extends ChangeNotifier {
  User? _user;
  bool _isLoading = true;

  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _user != null;

  AuthProvider() {
    initAuth();
  }

  Future<void> initAuth() async {
    _isLoading = true;
    notifyListeners();

    try {
      await ApiClient.getBaseUrl();
      final token = await ApiClient.getToken();
      if (token != null) {
        final res = await ApiClient.get('/auth/me');
        _user = User.fromJson(res);
      }
    } catch (_) {
      await ApiClient.clearTokens();
      _user = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      await ApiClient.getBaseUrl();
      final data = await ApiClient.post('/auth/login', body: {
        'email': email.trim(),
        'password': password.trim(),
      });

      if (data != null && data['access_token'] != null) {
        await ApiClient.saveTokens(data['access_token'], data['refresh_token'] ?? '');
        final userRes = await ApiClient.get('/auth/me');
        _user = User.fromJson(userRes);
      } else {
        throw Exception('Invalid response received from server.');
      }
    } catch (e) {
      final msg = e.toString().replaceAll('Exception: ', '');
      if (msg.contains('SocketException') || msg.contains('TimeoutException') || msg.contains('Connection refused') || msg.contains('Failed host lookup')) {
        throw Exception('Cannot connect to server at ${AppConstants.apiBaseUrl}. Please verify your PC and phone are on the same Wi-Fi network.');
      }
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> signup(String email, String password, String role, String site) async {
    _isLoading = true;
    notifyListeners();

    try {
      await ApiClient.getBaseUrl();
      await ApiClient.post('/auth/signup', body: {
        'email': email.trim(),
        'password': password.trim(),
        'role': role,
        'site': site,
      });

      await login(email, password);
    } catch (e) {
      final msg = e.toString().replaceAll('Exception: ', '');
      if (msg.contains('SocketException') || msg.contains('TimeoutException') || msg.contains('Connection refused')) {
        throw Exception('Cannot connect to server at ${AppConstants.apiBaseUrl}. Please check Wi-Fi connection.');
      }
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> switchDemoRole(String role) async {
    final email = AppConstants.demoUsers[role];
    if (email != null) {
      await login(email, AppConstants.demoPassword);
    }
  }

  Future<void> logout() async {
    await ApiClient.clearTokens();
    _user = null;
    notifyListeners();
  }
}
