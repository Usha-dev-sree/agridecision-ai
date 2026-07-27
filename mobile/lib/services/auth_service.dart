import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String _tokenKey = 'auth_token';
  static const String _roleKey = 'user_role';
  static const String _userNameKey = 'user_name';

  Future<bool> login(String phoneNumber, String password, {bool offlineMode = false}) async {
    final prefs = await SharedPreferences.getInstance();
    
    if (offlineMode) {
      // Simulate local login cache validation
      await prefs.setString(_tokenKey, 'offline_token');
      await prefs.setString(_roleKey, 'FARMER');
      await prefs.setString(_userNameKey, 'Offline Farmer Session');
      return true;
    }

    // In a real network setting, this calls user-service auth endpoint.
    // For demo/production-fallback purposes:
    if (phoneNumber == '9190000000' || phoneNumber == '9000000000') {
      await prefs.setString(_tokenKey, 'simulated_jwt_token_key');
      await prefs.setString(_roleKey, phoneNumber == '9190000000' ? 'AGRONOMIST' : 'FARMER');
      await prefs.setString(_userNameKey, phoneNumber == '9190000000' ? 'Dr. Sarah Smith' : 'Rajesh Kumar');
      return true;
    }
    return false;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_roleKey);
    await prefs.remove(_userNameKey);
  }

  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey(_tokenKey);
  }

  Future<String?> getRole() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_roleKey);
  }

  Future<String?> getUserName() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_userNameKey);
  }
}
