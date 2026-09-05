import 'package:flutter/material.dart';

class LoansScreen extends StatelessWidget {
  const LoansScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farmer Microloans'),
        backgroundColor: Theme.of(context).colorScheme.surface,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              color: const Color(0xFF142E1F),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: const Padding(
                padding: EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Agri AI Credit Score', style: TextStyle(color: Colors.white70)),
                    SizedBox(height: 8),
                    Text('784 / 900', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.greenAccent)),
                    SizedBox(height: 8),
                    Text('Pre-approved Limit: ₹2,50,000', style: TextStyle(color: Colors.white)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text('Active Microloans', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Card(
              color: const Color(0xFF161F19),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: const ListTile(
                title: Text('LN-2026-001 • ₹75,000', style: TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text('Seeds & Fertilizer • 6 Months Tenure'),
                trailing: Chip(label: Text('DISBURSED'), backgroundColor: Colors.green),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
