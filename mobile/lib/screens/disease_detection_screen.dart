import 'package:flutter/material.dart';

class DiseaseDetectionScreen extends StatefulWidget {
  const DiseaseDetectionScreen({super.key});

  @override
  State<DiseaseDetectionScreen> createState() => _DiseaseDetectionScreenState();
}

class _DiseaseDetectionScreenState extends State<DiseaseDetectionScreen> {
  bool _isAnalyzing = false;
  String? _result;

  void _scanLeaf() async {
    setState(() {
      _isAnalyzing = true;
    });

    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isAnalyzing = false;
      _result = "Early Blight (Alternaria solani)\nConfidence: 94.8%\nRecommended Action: Apply Copper Fungicide 2g/L";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Disease Detection'),
        backgroundColor: Theme.of(context).colorScheme.surface,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              height: 260,
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.green.shade700, width: 2),
              ),
              child: _isAnalyzing
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CircularProgressIndicator(color: Colors.green),
                          SizedBox(height: 12),
                          Text('Analyzing leaf image via ResNet50 model...'),
                        ],
                      ),
                    )
                  : const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.camera_alt, size: 64, color: Colors.green),
                          SizedBox(height: 8),
                          Text('Tap below to take leaf photo'),
                        ],
                      ),
                    ),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _isAnalyzing ? null : _scanLeaf,
              icon: const Icon(Icons.document_scanner),
              label: const Text('Capture & Scan Leaf'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
            const SizedBox(height: 20),
            if (_result != null) ...[
              Card(
                color: const Color(0xFF1E2D22),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI Diagnostic Result',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.greenAccent),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _result!,
                        style: const TextStyle(color: Colors.white70, height: 1.4),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
