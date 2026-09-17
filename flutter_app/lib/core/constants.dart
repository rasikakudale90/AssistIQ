class AppConstants {
  // Use http://10.0.2.2:8000 for Android Emulator, http://localhost:8000 for Web/Desktop/iOS
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  static const String demoPassword = 'Password123!@#';

  static const Map<String, String> demoUsers = {
    'Requester': 'requester@assistiq.local',
    'Operator': 'operator@assistiq.local',
    'TeamLead': 'lead@assistiq.local',
    'Manager': 'manager@assistiq.local',
    'Administrator': 'admin@assistiq.local',
  };
}
