"""
Qwen3-TTS Simple Test
Using the official qwen-tts package
"""

from qwen_tts import QwenTTS

# Initialize TTS model
print("Loading Qwen3-TTS 1.7B...")
tts = QwenTTS(model_size="1.7B")

# Generate speech
text = "Hello Captain. This is Qwen3 TTS running locally on your RTX 3060. Zero cost, unlimited usage."
print(f"Synthesizing: '{text}'")

output_file = "test_qwen3.wav"
tts.synthesize(text, output_file=output_file)

print(f"✓ Audio generated: {output_file}")
print("Play with: vlc test_qwen3.wav")
