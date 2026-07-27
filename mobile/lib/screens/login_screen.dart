import 'package:flutter/material';
import '../services/auth_service.dart';
import 'farmer_dashboard.dart';
import 'agronomist_dashboard.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();
  bool _offlineMode = false;
  bool _loading = false;
  String? _errorMessage;

  Future<void> _handleLogin() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
    });

    final success = await _authService.login(
      _phoneController.text.trim(),
      _passwordController.text.trim(),
      offlineMode: _offlineMode,
    );

    setState(() => _loading = false);

    if (success) {
      final role = await _authService.getRole();
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => role == 'AGRONOMIST'
                ? const AgronomistDashboard()
                : const FarmerDashboard(),
          ),
        );
      }
    } else {
      setState(() {
        _errorMessage = 'Invalid login credentials. Note: Use "9000000000" for Farmer and "9190000000" for Agronomist.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Card(
            color: const Color(0xFF111B14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: const BorderSide(color: Color(0x332E7D32), width: 1.5),
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 32.0, horizontal: 24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Logo Icon
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF2E7D32), Color(0xFF1B5E20)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.agriculture, color: Colors.white, size: 36),
                  ),
                  const SizedBox(height: 16),
                  const TypographyHeader(text: 'AgriDecision AI'),
                  const SizedBox(height: 8),
                  Text(
                    'Intelligent Agriculture System',
                    style: theme.textTheme.bodyMedium?.copyWith(color: const Color(0xFFA5D6A7)),
                  ),
                  const SizedBox(height: 32),

                  if (_errorMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.solid(color: Colors.red.withOpacity(0.3)),
                      ),
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  TextField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      prefixIcon: const Icon(Icons.phone, color: Color(0xFFA5D6A7)),
                      labelText: 'Phone Number',
                      labelStyle: const TextStyle(color: Color(0xFFA5D6A7)),
                      enabledBorder: OutlineInputBorder(
                        borderSide: const BorderSide(color: Color(0x332E7D32)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: const BorderSide(color: Color(0xFF2E7D32)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      prefixIcon: const Icon(Icons.lock, color: Color(0xFFA5D6A7)),
                      labelText: 'Password',
                      labelStyle: const TextStyle(color: Color(0xFFA5D6A7)),
                      enabledBorder: OutlineInputBorder(
                        borderSide: const BorderSide(color: Color(0x332E7D32)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: const BorderSide(color: Color(0xFF2E7D32)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Offline Mode Selector Toggle
                  Row(
                    children: [
                      Checkbox(
                        value: _offlineMode,
                        activeColor: const Color(0xFF2E7D32),
                        onChanged: (val) {
                          setState(() => _offlineMode = val ?? false);
                        },
                      ),
                      const Text(
                        'Enable Offline Cache Mode',
                        style: TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _handleLogin,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2E7D32),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: _loading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Log In', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class TypographyHeader extends StatelessWidget {
  final String text;
  const TypographyHeader({required this.text, super.key});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.w800,
        color: Colors.white,
        fontFamily: 'Outfit',
      ),
    );
  }
}
