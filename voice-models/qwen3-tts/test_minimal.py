"""
Qwen3-TTS Minimal Working Example
Using correct API from package inspection
"""

from qwen_tts.core import Qwen3TTSModel, Qwen3TTSTokenizer

print("Initializing Qwen3-TTS...")

# Load tokenizer and model
tokenizer = Qwen3TTSTokenizer.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")

print("✓ Model loaded")

# Generate speech
text = "Hello Captain. This is Qwen3 TTS running locally."
print(f"Generating speech: '{text}'")

# Tokenize and generate
inputs = tokenizer(text, return_tensors="pt")
with model.no_grad():
    audio = model.generate(**inputs)

# Save audio
import soundfile as sf
output_file = "test_qwen3.wav"
sf.write(output_file, audio.cpu().numpy(), 24000)

print(f"✓ Audio saved to: {output_file}")
