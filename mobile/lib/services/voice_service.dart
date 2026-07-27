import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';

class VoiceService {
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  bool _isListening = false;

  Future<void> initialize() async {
    await _speechToText.initialize();
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setSpeechRate(0.5);
  }

  Future<void> speak(String text) async {
    await _flutterTts.speak(text);
  }

  Future<void> stopSpeaking() async {
    await _flutterTts.stop();
  }

  Future<void> startListening(Function(String) onResult) async {
    if (!_isListening) {
      bool available = await _speechToText.initialize();
      if (available) {
        _isListening = true;
        await _speechToText.listen(
          onResult: (result) {
            onResult(result.recognizedWords);
          },
        );
      }
    }
  }

  Future<void> stopListening() async {
    if (_isListening) {
      await _speechToText.stop();
      _isListening = false;
    }
  }

  bool get isListening => _isListening;
}
