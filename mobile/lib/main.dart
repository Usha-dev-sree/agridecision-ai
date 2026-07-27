import 'package:flutter/material';
import 'screens/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AgriDecisionApp());
}

class AgriDecisionApp extends StatelessWidget {
  const AgriDecisionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AgriDecision AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF2E7D32),
        scaffoldBackgroundColor: const Color(0xFF0A0F0D),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF2E7D32),
          secondary: Color(0xFFFFA000),
          background: Color(0xFF0A0F0D),
          surface: Color(0xFF111B14),
        ),
        textTheme: const TextTheme(
          titleLarge: TextStyle(fontFamily: 'Outfit', fontWeight: FontWeight.bold, color: Colors.white),
          bodyLarge: TextStyle(fontFamily: 'Inter', color: Colors.white),
          bodyMedium: TextStyle(fontFamily: 'Inter', color: Colors.white70),
        ),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}
