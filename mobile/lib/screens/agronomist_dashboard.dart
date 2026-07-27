import 'dart:io';
import 'package:flutter/material';
import 'package:camera/camera.dart';
import '../services/camera_service.dart';
import '../database/local_database.dart';
import 'login_screen.dart';

class AgronomistDashboard extends StatefulWidget {
  const AgronomistDashboard({super.key});

  @override
  State<AgronomistDashboard> createState() => _AgronomistDashboardState();
}

class _AgronomistDashboardState extends State<AgronomistDashboard> {
  int _currentIndex = 0;
  final _cameraService = CameraService();
  final _localDb = LocalDatabase.instance;

  // Local state
  bool _cameraInitialized = false;
  XFile? _capturedImage;
  bool _analyzingImage = false;
  Map<String, dynamic>? _analysisResult;
  List<Map<String, dynamic>> _diagnosticReports = [];
  int _syncQueueCount = 0;

  @override
  void initState() {
    super.initState();
    _loadDiagnosticReports();
    _checkSyncQueue();
  }

  Future<void> _loadDiagnosticReports() async {
    // Generate mock diagnostic history records for agronomist view
    setState(() {
      _diagnosticReports = [
        {'id': '1', 'crop': 'Rice', 'disease': 'Leaf Blast', 'severity': 'HIGH', 'date': '2026-07-23'},
        {'id': '2', 'crop': 'Wheat', 'disease': 'Brown Rust', 'severity': 'MEDIUM', 'date': '2026-07-22'},
      ];
    });
  }

  Future<void> _checkSyncQueue() async {
    final queued = await _localDb.getQueuedRequests();
    setState(() => _syncQueueCount = queued.length);
  }

  Future<void> _initCamera() async {
    await _cameraService.initialize();
    setState(() => _cameraInitialized = true);
  }

  Future<void> _captureAndAnalyze() async {
    final file = await _cameraService.takePicture();
    if (file != null) {
      setState(() {
        _capturedImage = file;
        _analyzingImage = true;
      });

      // Simulate CNN model inference locally
      await Future.delayed(const Duration(seconds: 2));

      setState(() {
        _analyzingImage = false;
        _analysisResult = {
          'class': 'Bacterial Leaf Blight',
          'confidence': 0.92,
          'remedy': 'Apply Copper Oxychloride (0.3%) along with Streptocycline (100 ppm) at 15-day intervals.'
        };
      });

      // Queue diagnostic update to SQLite offline sync queue
      await _localDb.queueRequest(
        '/v1/advisory/diagnosis',
        'POST',
        '{"crop": "Rice", "disease": "Bacterial Leaf Blight", "confidence": 0.92}',
      );
      _checkSyncQueue();
    }
  }

  @override
  void dispose() {
    _cameraService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tabs = [
      _buildDiagnosticFeedTab(),
      _buildCameraCaptureTab(),
    ];

    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111B14),
        title: const Text('Agronomist Portal', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 12.0),
              child: Chip(
                label: Text('Sync Queue: $_syncQueueCount'),
                backgroundColor: const Color(0xFF2E7D32),
                labelStyle: const TextStyle(color: Colors.white, fontSize: 11),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
          )
        ],
      ),
      body: tabs[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: const Color(0xFF111B14),
        selectedItemColor: const Color(0xFF2E7D32),
        unselectedItemColor: Colors.white54,
        currentIndex: _currentIndex,
        onTap: (idx) {
          setState(() => _currentIndex = idx);
          if (idx == 1 && !_cameraInitialized) {
            _initCamera();
          }
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.feed), label: 'Diagnostics Feed'),
          BottomNavigationBarItem(icon: Icon(Icons.camera_alt), label: 'Leaf Capture'),
        ],
      ),
    );
  }

  Widget _buildDiagnosticFeedTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16.0),
      itemCount: _diagnosticReports.length,
      itemBuilder: (context, idx) {
        final rep = _diagnosticReports[idx];
        return Card(
          color: const Color(0xFF111B14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0x222E7D32)),
          ),
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      rep['crop'] as String,
                      style: const TextStyle(color: Color(0xFFA5D6A7), fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    Chip(
                      label: Text(rep['severity'] as String),
                      backgroundColor: rep['severity'] == 'HIGH' ? Colors.red.withOpacity(0.2) : Colors.orange.withOpacity(0.2),
                      labelStyle: TextStyle(
                        color: rep['severity'] == 'HIGH' ? Colors.redAccent : Colors.orangeAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    )
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Detected: ${rep['disease']}',
                  style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Date Reported: ${rep['date']}',
                  style: const TextStyle(color: Colors.white38, fontSize: 12),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCameraCaptureTab() {
    if (!_cameraInitialized) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)));
    }

    final controller = _cameraService.controller;

    return SingleChildScrollView(
      child: Column(
        children: [
          if (_capturedImage == null && controller != null && controller.value.isInitialized)
            AspectRatio(
              aspectRatio: controller.value.aspectRatio,
              child: CameraPreview(controller),
            ),
          if (_capturedImage != null)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Image.file(
                File(_capturedImage!.path),
                height: 300,
                fit: BoxFit.cover,
              ),
            ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _captureAndAnalyze,
                    icon: const Icon(Icons.camera),
                    label: const Text('Capture & Run Inference'),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32)),
                  ),
                ),
                if (_capturedImage != null) ...[
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.refresh, color: Colors.white),
                    onPressed: () {
                      setState(() {
                        _capturedImage = null;
                        _analysisResult = null;
                      });
                    },
                  )
                ]
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (_analyzingImage)
            const Padding(
              padding: EdgeInsets.all(24.0),
              child: Column(
                children: [
                  CircularProgressIndicator(color: Color(0xFF2E7D32)),
                  SizedBox(height: 12),
                  Text('Processing CNN Leaf Blight classifications...', style: TextStyle(color: Colors.white70)),
                ],
              ),
            ),
          if (_analysisResult != null)
            Card(
              color: const Color(0xFF111B14),
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _analysisResult!['class'] as String,
                          style: const TextStyle(color: Colors.redAccent, fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        Chip(
                          label: Text('${((_analysisResult!['confidence'] as double) * 100).toStringAsFixed(0)}% Match'),
                          backgroundColor: Colors.red.withOpacity(0.1),
                          labelStyle: const TextStyle(color: Colors.redAccent),
                        )
                      ],
                    ),
                    const Divider(color: Colors.white12, height: 24),
                    const Text('Remedy Instructions:', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Text(
                      _analysisResult!['remedy'] as String,
                      style: const TextStyle(color: Colors.white70, fontSize: 14),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
