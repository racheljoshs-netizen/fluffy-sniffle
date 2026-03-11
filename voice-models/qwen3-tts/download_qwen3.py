"""
Qwen3-TTS Download Script
Downloads Qwen3-TTS model weights from Hugging Face
"""

from transformers import AutoModel, AutoProcessor
import torch

def download_qwen3(model_size="1.7B"):
    """
    Download Qwen3-TTS model
    
    Args:
        model_size: "0.6B" or "1.7B"
    """
    # Correct model names from Hugging Face
    model_names = {
        "0.6B": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        "1.7B": "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    }
    model_name = model_names.get(model_size, model_names["1.7B"])
    
    print(f"Downloading {model_name}...")
    print("This may take several minutes depending on your connection.")
    
    try:
        processor = AutoProcessor.from_pretrained(model_name)
        print("✓ Processor downloaded")
        
        model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cpu"  # Download to CPU, will move to GPU at runtime
        )
        print("✓ Model downloaded")
        
        print(f"\nSuccess! {model_name} is ready to use.")
        print(f"Model cached to: ~/.cache/huggingface/hub/")
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Ensure transformers is installed: pip install transformers")
        print("3. Check Hugging Face Hub status: https://status.huggingface.co/")

if __name__ == "__main__":
    import sys
    
    model_size = "1.7B"  # Default to high quality
    if len(sys.argv) > 1:
        model_size = sys.argv[1]
    
    print(f"RTX 3060 detected - using {model_size} model")
    download_qwen3(model_size)
