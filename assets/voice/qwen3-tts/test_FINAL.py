"""
Qwen3-TTS using Transformers AutoModel
Final working approach - use transformers directly
"""

import torch
from transformers import AutoModel, AutoTokenizer
import soundfile as sf
import numpy as np

print("Loading Qwen3-TTS via transformers...")

model_id = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"

# Load with trust_remote_code
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="cuda"
)

print("✓ Model loaded on GPU")

# Generate speech
text = "Hello Captain. This is Qwen3 TTS working correctly with AutoModel. High quality, zero cost."
print(f"Generating: '{text}'")

# Use the model's built-in synthesis method
audio = model.synthesize(text, speaker="neutral")

# Save
output_file = "test_qwen3_FINAL.wav"
sf.write(output_file, audio.cpu().numpy(), 24000)

print(f"\n✓ SUCCESS: {output_file}")
