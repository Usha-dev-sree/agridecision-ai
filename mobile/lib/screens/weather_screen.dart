import 'package:flutter/material.dart';

class WeatherScreen extends StatelessWidget {
  const WeatherScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final forecastList = [
      {'day': 'Today', 'temp': '32°C / 22°C', 'condition': 'Sunny', 'rain': '0 mm', 'icon': Icons.wb_sunny, 'color': Colors.orange},
      {'day': 'Tomorrow', 'temp': '30°C / 21°C', 'condition': 'Partly Cloudy', 'rain': '2 mm', 'icon': Icons.cloud, 'color': Colors.lightBlue},
      {'day': 'Wed, Jul 29', 'temp': '27°C / 20°C', 'condition': 'Heavy Rain', 'rain': '45 mm', 'icon': Icons.thunderstorm, 'color': Colors.indigo},
      {'day': 'Thu, Jul 30', 'temp': '28°C / 21°C', 'condition': 'Moderate Rain', 'rain': '18 mm', 'icon': Icons.water_drop, 'color': Colors.blue},
      {'day': 'Fri, Jul 31', 'temp': '31°C / 22°C', 'condition': 'Clear Sky', 'rain': '0 mm', 'icon': Icons.wb_sunny, 'color': Colors.orange},
    ];

    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111B14),
        title: const Text('Weather & Evapotranspiration', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Weather Alert Warning Box
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.orange.withOpacity(0.15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.orange.withOpacity(0.4)),
            ),
            child: const Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Colors.orangeAccent, size: 36),
                SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Monsoon Heavy Rainfall Alert', style: TextStyle(color: Colors.orangeAccent, fontWeight: FontWeight.bold, fontSize: 15)),
                      SizedBox(height: 4),
                      Text('45mm rainfall expected on Wednesday. Ensure drainage channels are clear.', style: TextStyle(color: Colors.white70, fontSize: 12)),
                    ],
                  ),
                )
              ],
            ),
          ),
          const SizedBox(height: 24),

          // FAO Penman-Monteith ET0 Gauge Card
          Card(
            color: const Color(0xFF111B14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0x332E7D32))),
            child: const Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('FAO-56 Evapotranspiration (ET₀)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  SizedBox(height: 4),
                  Text('Reference crop water loss rate', style: TextStyle(color: Colors.white54, fontSize: 12)),
                  SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Column(
                        children: [
                          Text('4.8 mm/day', style: TextStyle(color: Color(0xFFA5D6A7), fontSize: 24, fontWeight: FontWeight.bold)),
                          Text('Calculated ET₀ Rate', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                      Column(
                        children: [
                          Text('15.2 mm', style: TextStyle(color: Colors.cyanAccent, fontSize: 24, fontWeight: FontWeight.bold)),
                          Text('Recommended Irrigation', style: TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                    ],
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          const Text('7-Day Forecast', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),

          ...forecastList.map((f) {
            return Card(
              color: const Color(0xFF111B14),
              margin: const EdgeInsets.only(bottom: 10),
              child: ListTile(
                leading: Icon(f['icon'] as IconData, color: f['color'] as Color, size: 32),
                title: Text(f['day'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                subtitle: Text('${f['condition']} | Rain: ${f['rain']}', style: const TextStyle(color: Colors.white54, fontSize: 12)),
                trailing: Text(f['temp'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}
