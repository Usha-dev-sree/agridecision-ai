import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:agridecision_mobile/main.dart';
import 'package:agridecision_mobile/screens/login_screen.dart';

void main() {
  testWidgets('AgriDecision App renders LoginScreen', (WidgetTester tester) async {
    await tester.pumpWidget(const AgriDecisionApp());
    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.text('AgriDecision AI'), findsOneWidget);
    expect(find.text('Log In'), findsOneWidget);
  });
}
