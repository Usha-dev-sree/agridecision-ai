import 'package:flutter/material.dart';

class VoiceAssistantScreen extends StatefulWidget {
  const VoiceAssistantScreen({super.key});

  @override
  State<VoiceAssistantScreen> createState() => _VoiceAssistantScreenState();
}

class _VoiceAssistantScreenState extends State<VoiceAssistantScreen> {
  bool _isListening = false;
  String _transcript = "Tap the microphone to speak your question in Hindi, English, or Punjabi...";
  String? _response;

  void _toggleListening() async {
    setState(() {
      _isListening = true;
      _transcript = "Listening...";
    });

    await Future.delayed(const Duration(seconds: 3));

    setState(() {
      _isListening = false;
      _transcript = "How much nitrogen should I apply to my Basmati rice field today?";
      _response = "AI Recommendation: Your soil test shows N level is 180 kg/ha. Apply 45 kg/ha Urea before tomorrow's expected rain for maximum root absorption.";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice AI Assistant'),
        backgroundColor: Theme.of(context).colorScheme.surface,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF141F17),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Spoken Query:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 6),
                    Text(_transcript, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
                    if (_response != null) ...[
                      const Divider(height: 32, color: Colors.white24),
                      const Text('AgriDecision AI Response:', style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 6),
                      Text(_response!, style: const TextStyle(fontSize: 15, height: 1.4, color: Colors.white)),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 30),
            GestureDetector(
              onTap: _toggleListening,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _isListening ? Colors.redAccent : Theme.of(context).colorScheme.primary,
                  boxShadow: [
                    BoxShadow(
                      color: (_isListening ? Colors.redAccent : Colors.green).withOpacity(0.5),
                      blurRadius: 16,
                      spreadRadius: 4,
                    )
                  ],
                ),
                child: Icon(
                  _isListening ? Icons.stop : Icons.mic,
                  color: Colors.white,
                  size: 36,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _isListening ? 'Listening...' : 'Tap Mic to Speak',
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
