import 'package:flutter/material.dart';

class AdvisoryScreen extends StatefulWidget {
  const AdvisoryScreen({super.key});

  @override
  State<AdvisoryScreen> createState() => _AdvisoryScreenState();
}

class _AdvisoryScreenState extends State<AdvisoryScreen> {
  String _selectedSeason = 'KHARIF';
  final _phController = TextEditingController(text: '6.5');
  final _rainfallController = TextEditingController(text: '120');

  List<Map<String, dynamic>> _recommendations = [
    {
      'crop_name': 'Rice (Basmati 1121)',
      'confidence': 0.91,
      'season': 'KHARIF',
      'reason': 'pH 6.5 and high monsoon rainfall optimal for Basmati cultivation.',
      'expected_yield': '4,800 kg/ha'
    },
    {
      'crop_name': 'Maize (Hybrid)',
      'confidence': 0.84,
      'season': 'KHARIF',
      'reason': 'Moderate nitrogen requirement and well-drained loamy soil.',
      'expected_yield': '5,200 kg/ha'
    },
    {
      'crop_name': 'Soybean (JS-335)',
      'confidence': 0.78,
      'season': 'KHARIF',
      'reason': 'Fixes atmospheric nitrogen, ideal for crop rotation after wheat.',
      'expected_yield': '2,400 kg/ha'
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111B14),
        title: const Text('ML Crop Advisory', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Filter Form
          Card(
            color: const Color(0xFF111B14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0x332E7D32))),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Plot Parameters & Season', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _phController,
                          keyboardType: TextInputType.number,
                          style: const TextStyle(color: Colors.white),
                          decoration: InputDecoration(
                            labelText: 'Soil pH',
                            labelStyle: const TextStyle(color: Color(0xFFA5D6A7)),
                            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0x332E7D32))),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextField(
                          controller: _rainfallController,
                          keyboardType: TextInputType.number,
                          style: const TextStyle(color: Colors.white),
                          decoration: InputDecoration(
                            labelText: 'Rainfall (mm)',
                            labelStyle: const TextStyle(color: Color(0xFFA5D6A7)),
                            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0x332E7D32))),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: ['KHARIF', 'RABI', 'ZAID'].map((season) {
                      final isSelected = _selectedSeason == season;
                      return ChoiceChip(
                        label: Text(season),
                        selected: isSelected,
                        selectedColor: const Color(0xFF2E7D32),
                        backgroundColor: const Color(0xFF16251C),
                        labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.white70, fontWeight: FontWeight.bold),
                        onSelected: (val) {
                          if (val) setState(() => _selectedSeason = season);
                        },
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          const Text('Recommended Crop Candidates', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),

          ..._recommendations.map((rec) {
            final confidencePct = ((rec['confidence'] as double) * 100).toStringAsFixed(0);
            return Card(
              color: const Color(0xFF111B14),
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0x222E7D32))),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(rec['crop_name'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 17)),
                        Chip(
                          label: Text('$confidencePct% Match'),
                          backgroundColor: const Color(0x222E7D32),
                          labelStyle: const TextStyle(color: Color(0xFFA5D6A7), fontWeight: FontWeight.bold, fontSize: 12),
                        )
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(rec['reason'] as String, style: const TextStyle(color: Colors.white70, fontSize: 13)),
                    const Divider(color: Colors.white10, height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Estimated Yield: ${rec['expected_yield']}', style: const TextStyle(color: Colors.orangeAccent, fontSize: 13, fontWeight: FontWeight.bold)),
                        const Icon(Icons.arrow_forward_ios, color: Colors.white38, size: 14),
                      ],
                    )
                  ],
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}
