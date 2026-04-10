class AppConfig {
  static const String appName = 'AIMOR';
  static const String appVersion = '1.0.0';

  // API Configuration
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  static const String apiVersion = '/api/v1';
  static const String apiBaseUrl = '$baseUrl$apiVersion';

  // Timeouts
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;

  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userKey = 'user_data';
  static const String themeKey = 'theme_mode';
  static const String onboardingKey = 'onboarding_done';

  // ML Configuration
  static const double similarityThreshold = 0.7;

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
}
