"""
Piper TTS - Fast, Free, CPU-only
No CUDA needed, runs anywhere
"""

from piper import PiperVoice
import wave

print("Loading Piper TTS (CPU-only, FREE)...")

# Initialize voice (downloads model automatically)
voice = PiperVoice.load("en_US-lessac-medium")

print("✓ Voice loaded")

# Generate speech
text = "Hello Captain. This is Piper TTS running on CPU. Zero cost, instant setup, unlimited usage."
print(f"Generating: '{text}'")

# Synthesize
audio = voice.synthesize(text)

# Save as WAV
output_file = "test_piper.wav"
with wave.open(output_file, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(22050)
    wav_file.writeframes(audio)

print(f"✓ Audio saved to: {output_file}")
print("✓ Method: Piper TTS (CPU-only, no GPU needed)")
