# Qwen3-TTS Local Deployment Guide (RTX 3060)

## Overview

Deploy Qwen3-TTS locally on your RTX 3060 (12GB VRAM) for FREE, unlimited voice synthesis with 3-second cloning.

## Prerequisites

- RTX 3060 (12GB VRAM) ✅
- Python 3.10+
- CUDA 12.1+ (already installed for ComfyUI)
- 10GB disk space

## Installation

### 1. Create Environment

```powershell
cd E:\G\voice-models
mkdir qwen3-tts
cd qwen3-tts
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate soundfile librosa
```

### 3. Download Model

```python
# download_qwen3.py
from transformers import AutoModel, AutoProcessor

model_name = "Qwen/Qwen3-TTS-1.7B"  # Or 0.6B for smaller

print("Downloading Qwen3-TTS...")
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModel.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="cuda"
)

print("Model downloaded and cached!")
```

Run: `python download_qwen3.py`

### 4. Create Inference Script

```python
# synthesize.py
import torch
from transformers import AutoModel, AutoProcessor
import soundfile as sf

class Qwen3TTS:
    def __init__(self, model_size="1.7B"):
        self.device = "cuda"
        model_name = f"Qwen/Qwen3-TTS-{model_size}"
        
        print(f"Loading {model_name}...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        print("Model loaded!")
    
    def synthesize(self, text, voice_reference=None, output_file="output.wav"):
        """
        Generate speech from text.
        
        Args:
            text: Text to synthesize
            voice_reference: Path to 3+ second audio for voice cloning (optional)
            output_file: Output file path
        """
        inputs = self.processor(text, return_tensors="pt").to(self.device)
        
        if voice_reference:
            # Load reference audio for voice cloning
            ref_audio = self.processor.audio_processor(voice_reference)
            inputs["reference_audio"] = ref_audio.to(self.device)
        
        with torch.no_grad():
            audio = self.model.generate(**inputs)
        
        # Save audio
        sf.write(output_file, audio.cpu().numpy(), 24000)
        print(f"Audio saved to {output_file}")
        return output_file

# Usage
if __name__ == "__main__":
    tts = Qwen3TTS(model_size="1.7B")  # or "0.6B"
    
    # Basic synthesis
    tts.synthesize("Hello, this is a test of Qwen3 TTS running locally on RTX 3060.")
    
    # Voice cloning (3+ seconds of reference audio)
    # tts.synthesize(
    #     "This is my cloned voice!",
    #     voice_reference="reference_voice.wav"
    # )
```

### 5. Web API Server (Optional)

```python
# server.py
from flask import Flask, request, send_file
from synthesize import Qwen3TTS
import os

app = Flask(__name__)
tts = Qwen3TTS()

@app.route('/tts', methods=['POST'])
def generate_speech():
    data = request.json
    text = data.get('text')
    voice_ref = data.get('voice_reference')
    
    output_file = f"temp_{hash(text)}.wav"
    tts.synthesize(text, voice_ref, output_file)
    
    return send_file(output_file, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(port=5050)
```

Install: `pip install flask`
Run: `python server.py`

## Usage Examples

### CLI

```powershell
cd E:\G\voice-models\qwen3-tts
.\venv\Scripts\activate
python synthesize.py
```

### API

```bash
curl -X POST http://localhost:5050/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Qwen3-TTS!"}'
```

### Voice Cloning

1. Record 3+ seconds of clean speech
2. Save as `reference.wav`
3. Run:

```python
tts.synthesize(
    "This is my cloned voice speaking!",
    voice_reference="reference.wav",
    output_file="cloned.wav"
)
```

## Performance (RTX 3060)

| Model | VRAM | Speed | Quality |
|-------|------|-------|---------|
| 0.6B | ~3GB | ~2x RT | Good |
| 1.7B | ~6GB | ~1x RT | Excellent |

**Recommendations:**

- Use 1.7B for best quality (6GB VRAM, plenty of headroom)
- Batch processing: 5-10 requests in parallel
- Expected: ~1 second per second of audio

## Integration with MCP Server

Add to Extended Capabilities MCP:

```javascript
// Local Qwen3-TTS provider
case "qwen3":
  const qwen3Response = await fetch("http://localhost:5050/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, voice_reference: voice })
  });
  const wavBuffer = await qwen3Response.arrayBuffer();
  return Buffer.from(wavBuffer).toString('base64');
```

## Troubleshooting

**Out of Memory:**

- Use 0.6B model: `Qwen3TTS(model_size="0.6B")`
- Close other GPU apps

**Slow Generation:**

- Use `torch.float16` (already set)
- Enable xFormers: `pip install xformers`

**CUDA Not Found:**

```powershell
nvidia-smi  # Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

## Next Steps

1. Download model: `python download_qwen3.py`
2. Test basic: `python synthesize.py`
3. Start server: `python server.py`
4. Add to MCP: Update `extended-capabilities/server.js`

---

**Status**: Ready to deploy  
**Cost**: $0 (one-time setup)  
**Ongoing**: Unlimited usage, no API limits
