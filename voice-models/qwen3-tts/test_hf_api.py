"""
Qwen3-TTS using Hugging Face Inference API (100% Free)
No local model needed - uses HF API
"""

from huggingface_hub import InferenceClient
import soundfile as sf
import numpy as np

print("Using Hugging Face Inference API (FREE)...")

# Initialize client
client = InferenceClient()

# Generate speech
text = "Hello Captain. This is Qwen3 TTS via Hugging Face Inference API. Zero cost, zero setup."
print(f"Generating: '{text}'")

# Call the model via API
audio_bytes = client.text_to_speech(
    text,
    model="Qwen/Qwen3-TTS-12Hz-1.7B-Base"
)

# Save audio
output_file = "test_qwen3_hf.wav"
with open(output_file, "wb") as f:
    f.write(audio_bytes)

print(f"✓ Audio saved to: {output_file}")
print("✓ Method: Hugging Face Inference API (FREE, no local model)")
