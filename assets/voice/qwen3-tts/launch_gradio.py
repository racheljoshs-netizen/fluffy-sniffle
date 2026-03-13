"""
Qwen3-TTS via Gradio Demo (Proven Working)
Using the same method as HuggingFace Spaces
"""

from qwen_tts import app

# Start the Gradio interface
# This is the EXACT same code that works on HuggingFace
print("Starting Qwen3-TTS Gradio Interface...")
print("This will open in your browser at http://127.0.0.1:7860")
print("You can generate speech there and download the audio files.")

app.launch(
    server_name="127.0.0.1",
    server_port=7860,
    share=False  # Local only
)
