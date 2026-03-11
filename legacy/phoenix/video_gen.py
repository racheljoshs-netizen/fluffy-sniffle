import os
import time
import mimetypes
from pathlib import Path
from google import genai
from google.genai import types as gtypes

# Configuration
KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    "AIzaSyDrS4domFdJ6glQpJzgjO4ZcwZuCcbCodA", "AIzaSyC4S4qAHamQIbGTF2HKtTZyuO2pbnpnsDs",
    "AIzaSyCMLp-K-VmU5mkbgmvl9VAynt9BPXKF0uI", "AIzaSyArLAAc1l7gJ8QLzCYLAveOUyii-uRZzHM",
    "AIzaSyANIs0FTi1lSuw5GWqXAIw7iOxIh-vpniU", "AIzaSyCA_EnKtSZrUaDBai-ksMUIVEUyJ5TfHIE",
    "AIzaSyAETN8xZun1DgzccRarhF5YM1oZoAAs7nU", "AIzaSyBcSPhVD-GczK1VUBztL7SJl5vgNhaDWXs"
]
KEYS = [k for k in KEYS if k]

DOWNLOADS_DIR = os.path.join(os.path.expanduser('~'), '.gemini', 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

class NeuralCockpit:
    def __init__(self):
        self.key_index = 0
        self.client = genai.Client(api_key=KEYS[self.key_index])
        self.output_dir = Path(DOWNLOADS_DIR)

    def rotate_key(self):
        self.key_index += 1
        if self.key_index < len(KEYS):
            print(f"[Cockpit] Quota hit. Rotating to key #{self.key_index}...")
            self.client = genai.Client(api_key=KEYS[self.key_index])
            return True
        return False

    def generate(self, prompt, image_path=None, aspect_ratio="16:9", resolution="1080p"):
        """
        Generates a video using Veo 3.0.
        """
        print(f"[Cockpit] Engaging Veo 3.0...")
        print(f"[Cockpit] Prompt: {prompt}")
        
        image_obj = None
        if image_path:
            print(f"[Cockpit] Conditioning on image: {image_path}")
            with open(image_path, "rb") as f:
                data = f.read()
            mt, _ = mimetypes.guess_type(image_path)
            image_obj = gtypes.Image(image_bytes=data, mime_type=mt or "image/png")

        config = gtypes.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution if aspect_ratio == "16:9" else None
        )

        try:
            # Start Generation
            operation = self.client.models.generate_videos(
                model="veo-3.0-generate-001",
                prompt=prompt,
                image=image_obj,
                config=config
            )
            
            print("[Cockpit] Generation started. Polling (this may take minutes)...")
            
            # Polling
            while not operation.done:
                time.sleep(10)
                operation = self.client.operations.get(operation)
                print(".", end="", flush=True)
            
            print("\n[Cockpit] Generation Complete.")
            
            # Download
            videos = getattr(operation.response, "generated_videos", [])
            if not videos:
                print("[Cockpit] Error: No video in response.")
                return None
            
            saved_paths = []
            for i, gv in enumerate(videos):
                # Ensure the file is downloaded
                self.client.files.download(file=gv.video)
                
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = f"veo_{ts}_{i}.mp4"
                fpath = self.output_dir / fname
                gv.video.save(str(fpath))
                print(f"[Cockpit] Saved: {fpath}")
                saved_paths.append(str(fpath))
            
            return saved_paths

        except Exception as e:
            if "429" in str(e) and self.rotate_key():
                return self.generate(prompt, image_path, aspect_ratio, resolution)
            print(f"[Cockpit] FATAL: {e}")
            return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python video_gen.py \"your prompt\"")
        sys.exit(1)
    
    prompt_text = sys.argv[1]
    cockpit = NeuralCockpit()
    cockpit.generate(prompt_text)
