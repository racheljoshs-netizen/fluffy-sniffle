import os
import urllib.request
import sys
from pathlib import Path

# G-FORGE: Fast Model Setup
# Uses Python's urllib for reliable downloads with progress

BASE_DIR = Path("e:/G/forge-backend/models")

MODELS = {
    # SDXL Base - Unrestricted, fast, widely compatible
    "sdxl_base": {
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
        "dest": "checkpoints",
        "filename": "sd_xl_base_1.0.safetensors"
    },
    # SDXL VAE
    "sdxl_vae": {
        "url": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors",
        "dest": "vae",
        "filename": "sdxl_vae.safetensors"
    }
}

def download_with_progress(url, dest_path):
    """Download with progress bar"""
    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 // total_size) if total_size > 0 else 0
        bar = '=' * (percent // 2) + '>' + ' ' * (50 - percent // 2)
        sys.stdout.write(f'\r[{bar}] {percent}% ({downloaded // 1024 // 1024}MB)')
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, dest_path, reporthook)
    print()  # newline after progress

def main():
    print("[GENESIS] Model Setup - Unrestricted Local Generation")
    print("=" * 60)
    
    for name, info in MODELS.items():
        dest_dir = BASE_DIR / info["dest"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / info["filename"]
        
        if dest_path.exists():
            print(f"[OK] {name} already exists")
            continue
            
        print(f"\n[GENESIS] Downloading {name}...")
        print(f"  URL: {info['url']}")
        
        try:
            download_with_progress(info["url"], str(dest_path))
            print(f"[OK] {name} saved to {dest_path}")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
    
    print("\n" + "=" * 60)
    print("[GENESIS] Setup complete!")
    print("Start ComfyUI: e:\\G\\forge\\start_forge.bat")

if __name__ == "__main__":
    main()
