import 'package:flutter/material';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../services/gps_service.dart';
import '../services/voice_service.dart';
import '../services/notification_service.dart';
import '../database/local_database.dart';
import 'login_screen.dart';
import 'weather_screen.dart';
import 'market_prices_screen.dart';
import 'advisory_screen.dart';
import 'settings_screen.dart';

class FarmerDashboard extends StatefulWidget {
  const FarmerDashboard({super.key});

  @override
  State<FarmerDashboard> createState() => _FarmerDashboardState();
}

class _FarmerDashboardState extends State<FarmerDashboard> {
  int _currentIndex = 0;
  final _gpsService = GpsService();
  final _voiceService = VoiceService();
  final _localDb = LocalDatabase.instance;

  // Local State
  List<Map<String, dynamic>> _plots = [];
  PositionData? _currentPosition;
  String _assistantSpeechResult = "Press the mic and say something...";
  bool _voiceListening = false;

  @override
  void initState() {
    super.initState();
    _loadLocalPlots();
    _voiceService.initialize();
    NotificationService.instance.initialize();
  }

  Future<void> _loadLocalPlots() async {
    final list = await _localDb.getPlots();
    setState(() => _plots = list);
  }

  Future<void> _captureLocation() async {
    try {
      final pos = await _gpsService.getCurrentLocation();
      setState(() {
        _currentPosition = PositionData(pos.latitude, pos.longitude);
      });
      NotificationService.instance.showNotification(
        id: 1,
        title: 'GPS Coordinates Captured',
        body: 'Latitude: ${pos.latitude.toStringAsFixed(4)}, Longitude: ${pos.longitude.toStringAsFixed(4)}',
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('GPS Error: ${e.toString()}')),
      );
    }
  }

  void _triggerVoiceAssistant() async {
    if (_voiceListening) {
      await _voiceService.stopListening();
      setState(() => _voiceListening = false);
    } else {
      setState(() => _voiceListening = true);
      await _voiceService.startListening((words) {
        setState(() => _assistantSpeechResult = words);
        if (words.toLowerCase().contains('irrigation')) {
          _voiceService.speak("Your Basmati rice field requires 15 millimeters of irrigation tomorrow.");
        } else if (words.toLowerCase().contains('weather')) {
          _voiceService.speak("Weather forecast indicates heavy rain shower at 4 PM.");
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final tabs = [
      _buildHomeTab(),
      _buildPlotsMapTab(),
      _buildVoiceTab(),
    ];

    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111B14),
        title: const Text('Farmer Advisor Portal', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        actions: [
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
      drawer: Drawer(
        backgroundColor: const Color(0xFF111B14),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const UserAccountsDrawerHeader(
              decoration: BoxDecoration(color: Color(0xFF16251C)),
              accountName: Text('Rajesh Kumar', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              accountEmail: Text('Farmer Account | +91 90000 00000'),
              currentAccountPicture: CircleAvatar(
                backgroundColor: Color(0xFF2E7D32),
                child: Icon(Icons.person, color: Colors.white, size: 36),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.home, color: Color(0xFF2E7D32)),
              title: const Text('Home Dashboard', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 0);
              },
            ),
            ListTile(
              leading: const Icon(Icons.wb_sunny, color: Colors.orange),
              title: const Text('Weather & ET₀', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(context, MaterialPageRoute(builder: (_) => const WeatherScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.store, color: Colors.amber),
              title: const Text('Mandi Commodity Prices', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(context, MaterialPageRoute(builder: (_) => const MarketPricesScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.eco, color: Colors.green),
              title: const Text('ML Crop Advisory', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(context, MaterialPageRoute(builder: (_) => const AdvisoryScreen()));
              },
            ),
            const Divider(color: Colors.white10),
            ListTile(
              leading: const Icon(Icons.settings, color: Colors.white70),
              title: const Text('Settings & Sync', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen()));
              },
            ),
          ],
        ),
      ),
      body: tabs[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: const Color(0xFF111B14),
        selectedItemColor: const Color(0xFF2E7D32),
        unselectedItemColor: Colors.white54,
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Plots Map'),
          BottomNavigationBarItem(icon: Icon(Icons.mic), label: 'AI Voice'),
        ],
      ),
    );
  }

  Widget _buildHomeTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Welcome Back, Rajesh!', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          
          // Weather summary widget
          Card(
            color: const Color(0xFF16251C),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Icon(Icons.wb_sunny, color: Colors.orange, size: 48),
                  SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Current Weather', style: TextStyle(color: Colors.white70, fontSize: 14)),
                      Text('32°C - Clear Sky', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                      Text('Humidity: 65% | Wind: 12 km/h', style: TextStyle(color: Colors.white54, fontSize: 12)),
                    ],
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          const Text('Your Plots', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),

          _plots.isEmpty
              ? Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(color: const Color(0xFF111B14), borderRadius: BorderRadius.circular(12)),
                  child: const Center(
                    child: Text('No plot boundaries stored offline. Tap Plots Map to create one.', style: TextStyle(color: Colors.white70)),
                  ),
                )
              : ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _plots.length,
                  itemBuilder: (context, idx) {
                    final p = _plots[idx];
                    return Card(
                      color: const Color(0xFF111B14),
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: const Icon(Icons.landscape, color: Color(0xFF2E7D32)),
                        title: Text(p['name'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        subtitle: Text('Area: ${p['total_area_ha']} Ha | Irrigation: ${p['irrigation_type']}', style: const TextStyle(color: Colors.white70)),
                      ),
                    );
                  },
                ),
        ],
      ),
    );
  }

  Widget _buildPlotsMapTab() {
    final initialCenter = _currentPosition != null
        ? LatLng(_currentPosition!.lat, _currentPosition!.lng)
        : const LatLng(21.1702, 72.8311);

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Draw Plot Boundaries', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
              ElevatedButton.icon(
                onPressed: _captureLocation,
                icon: const Icon(Icons.gps_fixed, size: 16),
                label: const Text('Capture GPS'),
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32)),
              ),
            ],
          ),
        ),
        Expanded(
          child: FlutterMap(
            options: MapOptions(
              initialCenter: initialCenter,
              initialZoom: 15.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.agridecision.app',
              ),
              if (_currentPosition != null)
                MarkerLayer(
                  markers: [
                    Marker(
                      point: LatLng(_currentPosition!.lat, _currentPosition!.lng),
                      width: 40,
                      height: 40,
                      child: const Icon(Icons.location_on, color: Colors.red, size: 40),
                    )
                  ],
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildVoiceTab() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.chat_bubble_outline, size: 80, color: Color(0xFF2E7D32)),
          const SizedBox(height: 24),
          const Text('Voice Assistant Guidance', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Ask questions regarding irrigation requirements, disease diagnosis, or weather forecasts.', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70)),
          const SizedBox(height: 32),
          Container(
            padding: const EdgeInsets.all(16),
            width: double.infinity,
            decoration: BoxDecoration(color: const Color(0xFF111B14), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0x332E7D32))),
            child: Text(
              _assistantSpeechResult,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white, fontSize: 16, fontStyle: FontStyle.italic),
            ),
          ),
          const SizedBox(height: 40),
          GestureDetector(
            onTap: _triggerVoiceAssistant,
            child: CircleAvatar(
              radius: 40,
              backgroundColor: _voiceListening ? Colors.redAccent : const Color(0xFF2E7D32),
              child: Icon(_voiceListening ? Icons.mic_off : Icons.mic, size: 36, color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }
}

class PositionData {
  final double lat;
  final double lng;
  PositionData(this.lat, this.lng);
}
