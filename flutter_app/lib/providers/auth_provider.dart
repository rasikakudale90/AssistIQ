import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
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
      final uri = Uri.parse('${AppConstants.apiBaseUrl}/auth/login');
      final res = await http.post(
        uri,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {'username': email, 'password': password},
      );

      if (res.statusCode >= 200 && res.statusCode < 300) {
        final data = jsonDecode(res.body);
        await ApiClient.saveTokens(data['access_token'], data['refresh_token']);
        
        final userRes = await ApiClient.get('/auth/me');
        _user = User.fromJson(userRes);
      } else {
        throw Exception('Login failed: ${res.body}');
      }
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
