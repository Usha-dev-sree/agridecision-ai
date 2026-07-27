import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class MarketPricesScreen extends StatefulWidget {
  const MarketPricesScreen({super.key});

  @override
  State<MarketPricesScreen> createState() => _MarketPricesScreenState();
}

class _MarketPricesScreenState extends State<MarketPricesScreen> {
  String _selectedCommodity = 'Wheat';
  final TextEditingController _searchController = TextEditingController();

  final List<Map<String, dynamic>> _mandiRates = [
    {
      'mandi': 'Khanna Grain Market',
      'state': 'Punjab',
      'commodity': 'Wheat',
      'modal_price': 2183.0,
      'min_price': 2100.0,
      'max_price': 2250.0,
      'trend': 'UP'
    },
    {
      'mandi': 'Karnal Mandi',
      'state': 'Haryana',
      'commodity': 'Rice (Basmati 1121)',
      'modal_price': 4020.0,
      'min_price': 3800.0,
      'max_price': 4150.0,
      'trend': 'STABLE'
    },
    {
      'mandi': 'Indore Mandi',
      'state': 'Madhya Pradesh',
      'commodity': 'Soybean',
      'modal_price': 4650.0,
      'min_price': 4400.0,
      'max_price': 4800.0,
      'trend': 'UP'
    },
    {
      'mandi': 'Rajkot Mandi',
      'state': 'Gujarat',
      'commodity': 'Cotton',
      'modal_price': 6120.0,
      'min_price': 5900.0,
      'max_price': 6350.0,
      'trend': 'DOWN'
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0F0D),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111B14),
        title: const Text('Mandi Commodity Prices', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Search & Filter
          TextField(
            controller: _searchController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Search Mandi or Commodity...',
              hintStyle: const TextStyle(color: Colors.white38),
              prefixIcon: const Icon(Icons.search, color: Color(0xFF2E7D32)),
              filled: true,
              fillColor: const Color(0xFF111B14),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0x332E7D32))),
            ),
          ),
          const SizedBox(height: 20),

          // Price Forecast Chart
          Card(
            color: const Color(0xFF111B14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0x332E7D32))),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('14-Day AI Price Trend Forecast', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                      Chip(
                        label: const Text('BULLISH +4.2%'),
                        backgroundColor: Colors.green.withOpacity(0.2),
                        labelStyle: const TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold),
                      )
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text('Model: LSTM Time Series Predictor', style: TextStyle(color: Colors.white54, fontSize: 12)),
                  const SizedBox(height: 24),

                  // FL Chart LineChart
                  SizedBox(
                    height: 180,
                    child: LineChart(
                      LineChartData(
                        gridData: const FlGridData(show: false),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: false),
                        lineBarsData: [
                          LineChartBarData(
                            spots: const [
                              FlSpot(0, 2100),
                              FlSpot(1, 2120),
                              FlSpot(2, 2115),
                              FlSpot(3, 2145),
                              FlSpot(4, 2160),
                              FlSpot(5, 2183),
                              FlSpot(6, 2210),
                            ],
                            isCurved: true,
                            color: const Color(0xFF2E7D32),
                            barWidth: 3,
                            dotData: const FlDotData(show: true),
                            belowBarData: BarAreaData(show: true, color: const Color(0x332E7D32)),
                          )
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Mandi Price Cards
          const Text('Live Market Rates (₹/Quintal)', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),

          ..._mandiRates.map((rate) {
            return Card(
              color: const Color(0xFF111B14),
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: const BorderSide(color: Color(0x222E7D32))),
              child: ListTile(
                title: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(rate['commodity'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    Text('₹${rate['modal_price']}', style: const TextStyle(color: Color(0xFFA5D6A7), fontWeight: FontWeight.bold, fontSize: 18)),
                  ],
                ),
                subtitle: Padding(
                  padding: const EdgeInsets.only(top: 6.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('${rate['mandi']}, ${rate['state']}', style: const TextStyle(color: Colors.white54, fontSize: 12)),
                      Text('Range: ₹${rate['min_price']} - ₹${rate['max_price']}', style: const TextStyle(color: Colors.white38, fontSize: 11)),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }
}
