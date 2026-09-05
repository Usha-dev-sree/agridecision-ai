import 'package:flutter/material.dart';

class FarmerProfileScreen extends StatelessWidget {
  const FarmerProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farmer Profile'),
        backgroundColor: Theme.of(context).colorScheme.surface,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const CircleAvatar(
              radius: 40,
              backgroundColor: Colors.green,
              child: Icon(Icons.person, size: 50, color: Colors.white),
            ),
            const SizedBox(height: 12),
            const Text('Ramesh Kumar', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const Text('+91 98765 43210 • Karnal, Haryana', style: TextStyle(color: Colors.white70)),
            const SizedBox(height: 20),
            Card(
              color: const Color(0xFF16241B),
              child: Column(
                children: const [
                  ListTile(leading: Icon(Icons.language, color: Colors.green), title: Text('Language'), trailing: Text('Hindi')),
                  Divider(height: 1),
                  ListTile(leading: Icon(Icons.cloud_sync, color: Colors.green), title: Text('Offline Sync Status'), trailing: Text('Synced')),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
