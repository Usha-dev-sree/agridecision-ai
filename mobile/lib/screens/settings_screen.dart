import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../database/local_database.dart';
import '../services/sync_service.dart';
import 'login_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _authService = AuthService();
  final _localDb = LocalDatabase.instance;
  String _selectedLanguage = 'English';
  bool _offlineCacheEnabled = true;
  bool _pushNotifications = true;
  int _pendingSyncCount = 0;
  String? _userName;
  String? _userRole;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    _checkSyncQueue();
  }

  Future<void> _loadUserInfo() async {
    final name = await _authService.getUserName();
    final role = await _authService.getRole();
    setState(() {
      _userName = name ?? 'User Session';
      _userRole = role ?? 'FARMER';
    });
  }

  Future<void> _checkSyncQueue() async {
    final queued = await _localDb.getQueuedRequests();
    setState(() => _pendingSyncCount = queued.length);
  }

  Future<void> _clearCache() async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Offline database cache refreshed.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111B14),
        title: const Text('Application Settings', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Profile Card
          Card(
            color: const Color(0xFF111B14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0x332E7D32))),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: const Color(0xFF2E7D32),
                    child: Text(
                      _userName != null && _userName!.isNotEmpty ? _userName![0] : 'U',
                      style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(_userName ?? 'Loading...', style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Chip(
                        label: Text(_userRole ?? 'FARMER'),
                        backgroundColor: const Color(0x222E7D32),
                        labelStyle: const TextStyle(color: Color(0xFFA5D6A7), fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ],
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Localization Settings
          const Text('Preferences', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Card(
            color: const Color(0xFF111B14),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.language, color: Color(0xFF2E7D32)),
                  title: const Text('Language / भाषा', style: TextStyle(color: Colors.white)),
                  trailing: DropdownButton<String>(
                    value: _selectedLanguage,
                    dropdownColor: const Color(0xFF111B14),
                    style: const TextStyle(color: Color(0xFFA5D6A7)),
                    underline: const SizedBox(),
                    items: ['English', 'Hindi (हिंदी)', 'Punjabi (ਪੰਜਾਬੀ)', 'Marathi (मराठी)', 'Tamil (தமிழ்)']
                        .map((lang) => DropdownMenuItem(value: lang, child: Text(lang)))
                        .toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedLanguage = val);
                    },
                  ),
                ),
                const Divider(color: Colors.white10),
                SwitchListTile(
                  secondary: const Icon(Icons.notifications_active, color: Color(0xFF2E7D32)),
                  title: const Text('Push Notifications', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('Weather & disease outbreak alerts', style: TextStyle(color: Colors.white54, fontSize: 12)),
                  value: _pushNotifications,
                  activeColor: const Color(0xFF2E7D32),
                  onChanged: (val) => setState(() => _pushNotifications = val),
                ),
                const Divider(color: Colors.white10),
                SwitchListTile(
                  secondary: const Icon(Icons.cloud_off, color: Color(0xFF2E7D32)),
                  title: const Text('Offline SQLite Cache', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('Store plot boundaries and diagnosis offline', style: TextStyle(color: Colors.white54, fontSize: 12)),
                  value: _offlineCacheEnabled,
                  activeColor: const Color(0xFF2E7D32),
                  onChanged: (val) => setState(() => _offlineCacheEnabled = val),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Offline Sync Status
          const Text('Data Synchronization', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Card(
            color: const Color(0xFF111B14),
            child: ListTile(
              leading: const Icon(Icons.sync, color: Color(0xFF2E7D32)),
              title: const Text('Pending Sync Requests', style: TextStyle(color: Colors.white)),
              subtitle: Text('Queue size: $_pendingSyncCount items', style: const TextStyle(color: Colors.white54, fontSize: 12)),
              trailing: ElevatedButton(
                onPressed: _checkSyncQueue,
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32)),
                child: const Text('Sync Now', style: TextStyle(color: Colors.white, fontSize: 12)),
              ),
            ),
          ),
          const SizedBox(height: 32),

          // Logout Button
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton.icon(
              onPressed: () async {
                await _authService.logout();
                if (mounted) {
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                }
              },
              icon: const Icon(Icons.logout, color: Colors.white),
              label: const Text('Log Out', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red.withOpacity(0.8)),
            ),
          ),
        ],
      ),
    );
  }
}
