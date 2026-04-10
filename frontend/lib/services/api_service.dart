import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

class ApiService {
  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(milliseconds: AppConfig.connectTimeout),
      receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeout),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: AppConfig.tokenKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          _storage.delete(key: AppConfig.tokenKey);
        }
        handler.next(error);
      },
    ));
  }

  // Auth
  Future<Response> login(String email, String password) async {
    return await _dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
  }

  Future<Response> register(Map<String, dynamic> data) async {
    return await _dio.post('/auth/register', data: data);
  }

  Future<Response> getProfile() async {
    return await _dio.get('/auth/me');
  }

  Future<Response> updateProfile(Map<String, dynamic> data) async {
    return await _dio.put('/auth/me', data: data);
  }

  Future<Response> changePassword(
      String oldPassword, String newPassword) async {
    return await _dio.post('/auth/change-password', data: {
      'old_password': oldPassword,
      'new_password': newPassword,
    });
  }

  Future<Response> logout() async {
    return await _dio.post('/auth/logout');
  }

  // Lost Items
  Future<Response> getLostItems({int page = 1, int limit = 20}) async {
    return await _dio.get('/lost-items/', queryParameters: {
      'page': page,
      'limit': limit,
    });
  }

  Future<Response> getMyLostItems() async {
    return await _dio.get('/lost-items/my');
  }

  Future<Response> getLostItem(String id) async {
    return await _dio.get('/lost-items/$id');
  }

  Future<Response> createLostItem(FormData data) async {
    return await _dio.post('/lost-items/', data: data);
  }

  Future<Response> updateLostItem(String id, FormData data) async {
    return await _dio.put('/lost-items/$id', data: data);
  }

  Future<Response> deleteLostItem(String id) async {
    return await _dio.delete('/lost-items/$id');
  }

  Future<Response> markLostItemReturned(String id) async {
    return await _dio.post('/lost-items/$id/mark-returned');
  }

  // Found Items
  Future<Response> getFoundItems({int page = 1, int limit = 20}) async {
    return await _dio.get('/found-items/', queryParameters: {
      'page': page,
      'limit': limit,
    });
  }

  Future<Response> getMyFoundItems() async {
    return await _dio.get('/found-items/my');
  }

  Future<Response> getFoundItem(String id) async {
    return await _dio.get('/found-items/$id');
  }

  Future<Response> createFoundItem(FormData data) async {
    return await _dio.post('/found-items/', data: data);
  }

  Future<Response> updateFoundItem(String id, FormData data) async {
    return await _dio.put('/found-items/$id', data: data);
  }

  Future<Response> deleteFoundItem(String id) async {
    return await _dio.delete('/found-items/$id');
  }

  Future<Response> markFoundItemReturned(String id) async {
    return await _dio.post('/found-items/$id/mark-returned');
  }

  // Search
  Future<Response> searchByImage(FormData data) async {
    return await _dio.post('/search/image', data: data);
  }

  Future<Response> searchByText(String query) async {
    return await _dio
        .post('/search/text', queryParameters: {'query_text': query});
  }

  Future<Response> searchNearby(double lat, double lng,
      {double radius = 1000}) async {
    return await _dio.get('/search/nearby', queryParameters: {
      'latitude': lat,
      'longitude': lng,
      'radius': radius,
    });
  }

  Future<Response> getMatches(String itemId) async {
    return await _dio.get('/search/matches/$itemId');
  }

  Future<Response> getCategories() async {
    return await _dio.get('/search/categories');
  }

  // Claims
  Future<Response> createClaim(Map<String, dynamic> data) async {
    return await _dio.post('/claims/', data: data);
  }

  Future<Response> getMyClaims() async {
    return await _dio.get('/claims/my-claims');
  }

  Future<Response> getIncomingClaims() async {
    return await _dio.get('/claims/incoming');
  }

  Future<Response> acceptClaim(String claimId) async {
    return await _dio.put('/claims/$claimId/accept');
  }

  Future<Response> rejectClaim(String claimId) async {
    return await _dio.put('/claims/$claimId/reject');
  }

  // Notifications
  Future<Response> getNotifications({bool unreadOnly = false}) async {
    return await _dio.get('/notifications/', queryParameters: {
      'unread_only': unreadOnly,
    });
  }

  Future<Response> markNotificationRead(String id) async {
    return await _dio.put('/notifications/$id/read');
  }

  Future<Response> markAllNotificationsRead() async {
    return await _dio.put('/notifications/read-all');
  }

  Future<Response> getUnreadCount() async {
    return await _dio.get('/notifications/unread-count');
  }
}
