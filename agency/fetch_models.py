import google.generativeai as genai
import os
import sys

# Setup
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try .env
    try:
        with open("E:/0x/.env", "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=")[1].strip()
                    break
    except:
        pass

if not api_key:
    print("NO API KEY FOUND.")
    sys.exit(1)

genai.configure(api_key=api_key)

print("--- AVAILABLE MODELS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods or 'embedContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
            print(f"  - Version: {m.version}")
            print(f"  - Methods: {m.supported_generation_methods}")
            print("-" * 20)
except Exception as e:
    print(f"Error listing models: {e}")
