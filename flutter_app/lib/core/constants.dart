class AppConstants {
  static String _overrideBaseUrl = '';

  static String get apiBaseUrl {
    if (_overrideBaseUrl.isNotEmpty) return _overrideBaseUrl;
    return const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.122.120.196:8000/api/v1',
    );
  }

  static void setBaseUrl(String url) {
    var clean = url.trim();
    if (clean.endsWith('/')) {
      clean = clean.substring(0, clean.length - 1);
    }
    if (!clean.endsWith('/api/v1')) {
      clean = '$clean/api/v1';
    }
    _overrideBaseUrl = clean;
  }

  static const String demoPassword = 'Password123!@#';

  static const Map<String, String> demoUsers = {
    'Requester': 'requester@assistiq.local',
    'Operator': 'operator@assistiq.local',
    'TeamLead': 'lead@assistiq.local',
    'Manager': 'manager@assistiq.local',
    'Administrator': 'admin@assistiq.local',
  };
}
