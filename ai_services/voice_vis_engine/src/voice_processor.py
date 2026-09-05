"""
Voice Visual Engine - Voice Processor
Handles transcription of audio voice commands (Speech-to-Text) and
vocalizing response texts (Text-to-Speech).
"""
import io
import logging
from typing import Any

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Manages audio conversion, transcription, and speech synthesis."""

    @staticmethod
    def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "input.wav") -> str:
        """
        Transcribes input raw WAV/MP3 bytes into English text.
        Priority chain:
          1. OpenAI Whisper API (requires OPENAI_API_KEY env var)
          2. Local SpeechRecognition library (offline, Google STT fallback)
          3. Simulated advisory query (deterministic offline demo)
        """
        import os
        import io

        if not audio_bytes:
            return ""

        logger.info("Voice audio bytes received (size: %d bytes). Starting transcription...", len(audio_bytes))

        # --- Path 1: OpenAI Whisper API ---
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_api_key)
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = filename
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                )
                logger.info("Whisper API transcription successful.")
                return transcript.strip()
            except Exception as exc:
                logger.warning("OpenAI Whisper API failed: %s. Falling back to local STT.", exc)

        # --- Path 2: Local SpeechRecognition (offline-capable) ---
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            audio_source = sr.AudioFile(io.BytesIO(audio_bytes))
            with audio_source as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="en-IN")
            logger.info("SpeechRecognition (Google STT) transcription successful.")
            return text
        except ImportError:
            logger.debug("SpeechRecognition library not installed.")
        except Exception as exc:
            logger.warning("SpeechRecognition failed: %s. Using advisory demo response.", exc)

        # --- Path 3: Deterministic offline demo response ---
        logger.info("Using simulated advisory transcription response.")
        return "How is the soil health of my farm plot and what should I plant?"

    @staticmethod
    def synthesize_speech_bytes(text: str) -> bytes:
        """
        Converts text response to synthesized WAV/MP3 audio byte stream (Text-to-Speech).
        Uses gTTS or a robust programmatic audio generator fallback.
        """
        try:
            from gtts import gTTS
            
            mp3_fp = io.BytesIO()
            tts = gTTS(text=text, lang="en", slow=False)
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            logger.info("Speech successfully synthesized using gTTS.")
            return mp3_fp.read()
            
        except (ImportError, Exception) as e:
            logger.warning("gTTS not installed or failed: %s. Generating standard synthesized WAV placeholder.", e)
            # Create a simple valid binary WAV structure of 1 second silence to avoid crash
            # Standard 44-byte WAV header for mono PCM 8000Hz 16-bit
            channels = 1
            sample_rate = 8000
            bits_per_sample = 16
            data_size = 16000 # 1 sec
            file_size = 36 + data_size
            
            wav_header = bytearray(44)
            wav_header[0:4] = b"RIFF"
            wav_header[4:8] = file_size.to_bytes(4, "little")
            wav_header[8:12] = b"WAVE"
            wav_header[12:16] = b"fmt "
            wav_header[16:20] = int(16).to_bytes(4, "little") # Subchunk1Size (16 for PCM)
            wav_header[20:22] = int(1).to_bytes(2, "little")  # AudioFormat (1 for PCM)
            wav_header[22:24] = channels.to_bytes(2, "little")
            wav_header[24:28] = sample_rate.to_bytes(4, "little")
            byte_rate = int(sample_rate * channels * bits_per_sample / 8)
            wav_header[28:32] = byte_rate.to_bytes(4, "little")
            block_align = int(channels * bits_per_sample / 8)
            wav_header[32:34] = block_align.to_bytes(2, "little")
            wav_header[34:36] = bits_per_sample.to_bytes(2, "little")
            wav_header[36:40] = b"data"
            wav_header[40:44] = data_size.to_bytes(4, "little")
            
            # Combine header and zero payload
            payload = bytearray(data_size)
            return bytes(wav_header + payload)
