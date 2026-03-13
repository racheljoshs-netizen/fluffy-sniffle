"""
pyttsx3 - Windows Built-in TTS (100% Free, Offline, Zero Setup)
Uses Windows Speech API - works immediately
"""

import pyttsx3

print("Initializing Windows TTS (FREE, built-in)...")

# Initialize engine
engine = pyttsx3.init()

# Configure voice
voices = engine.getProperty('voices')
print(f"Available voices: {len(voices)}")
for i, voice in enumerate(voices):
    print(f"  {i}: {voice.name}")

# Select voice (usually 0 = male, 1 = female on Windows)
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
engine.setProperty('rate', 175)  # Speed

# Generate speech
text = "Hello Captain. This is Windows built-in TTS. Zero cost, offline, instant setup."
print(f"\nGenerating: '{text}'")

# Save to file
output_file = "test_windows_tts.wav"
engine.save_to_file(text, output_file)
engine.runAndWait()

print(f"✓ Audio saved to: {output_file}")
print("✓ Method: Windows TTS (pyttsx3 - FREE, offline, no internet needed)")
print("\nTo integrate with MCP server:")
print("  import pyttsx3")
print("  engine = pyttsx3.init()")
print("  engine.save_to_file(text, 'output.wav')")
print("  engine.runAndWait()")
