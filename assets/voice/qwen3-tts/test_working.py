"""
Qwen3-TTS Working Example
Based on official GitHub documentation
"""

from qwen_tts.model import QwenTTS

# Initialize model
print("Loading Qwen3-TTS...")
model = QwenTTS()

# Basic synthesis
text = "Hello Captain. This is Qwen3 TTS running locally on your RTX 3060."
print(f"Synthesizing: {text}")

# Generate audio
audio = model.synthesize(
    text=text,
    speaker_id="speaker_1"  # Default speaker
)

# Save to file
import soundfile as sf
output_file = "test_qwen3.wav"
sf.write(output_file, audio, 24000)

print(f"✓ Audio saved to: {output_file}")
