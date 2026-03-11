"""
Qwen3-TTS Synthesis Script
Simple interface for generating speech with Qwen3-TTS
"""

import torch
from transformers import AutoModel, AutoProcessor
import soundfile as sf
import argparse

class Qwen3TTS:
    def __init__(self, model_size="1.7B"):
        """Initialize Qwen3-TTS model"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = f"Qwen/Qwen3-TTS-{model_size}"
        
        print(f"Loading {model_name} on {self.device}...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map=self.device
        )
        print("✓ Model loaded!")
    
    def synthesize(self, text, voice_reference=None, output_file="output.wav"):
        """
        Generate speech from text
        
        Args:
            text: Text to synthesize
            voice_reference: Path to 3+ second audio for voice cloning (optional)
            output_file: Output WAV file path
        
        Returns:
            Path to generated audio file
        """
        print(f"Generating speech: '{text[:50]}...'")
        
        inputs = self.processor(text, return_tensors="pt").to(self.device)
        
        if voice_reference:
            print(f"Using voice reference: {voice_reference}")
            # Load and process reference audio
            import librosa
            ref_audio, sr = librosa.load(voice_reference, sr=24000)
            ref_tensor = torch.tensor(ref_audio).unsqueeze(0).to(self.device)
            inputs["reference_audio"] = ref_tensor
        
        with torch.no_grad():
            audio = self.model.generate(**inputs)
        
        # Convert to numpy and save
        audio_np = audio.cpu().numpy().squeeze()
        sf.write(output_file, audio_np, 24000)
        
        print(f"✓ Audio saved to {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Qwen3-TTS Speech Synthesis")
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument("--model", default="1.7B", choices=["0.6B", "1.7B"], 
                       help="Model size (default: 1.7B)")
    parser.add_argument("--voice", help="Path to reference audio for voice cloning (3+ seconds)")
    parser.add_argument("--output", default="output.wav", help="Output file path")
    
    args = parser.parse_args()
    
    tts = Qwen3TTS(model_size=args.model)
    tts.synthesize(args.text, voice_reference=args.voice, output_file=args.output)

if __name__ == "__main__":
    main()
