import os
import sys
from pathlib import Path
import asyncio
import logging
import json
import sounddevice as sd
import numpy as np
import httpx

from kokoro_onnx import Kokoro

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agency import config

# FORCED GPU ISOLATION (GPU 1)
os.environ["CUDA_VISIBLE_DEVICES"] = config.AGENCY_GPU_INDEX

LOG_DIR = Path(r"E:\0x\logs\agency")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [APOLLO-CORE] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "apollo_core.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class ApolloCore:
    def __init__(self):
        self.is_speaking = False
        self.history = [] # Chat Memory
        
        # 1. THE VOICE (GPU 1)
        logging.info("Initializing Divine Voice (Kokoro)...")
        model_path = os.path.join("agency", config.KOKORO_MODEL_PATH)
        voice_path = os.path.join("agency", config.KOKORO_VOICES_PATH)
        
        if os.path.exists(model_path):
            try:
                self.kokoro = Kokoro(model_path, voice_path)
                logging.info("Kokoro Voice Online.")
            except Exception as e:
                logging.error(f"Kokoro Init Failed: {e}")
                self.kokoro = None
        else:
            self.kokoro = None
            logging.error("Voice Weights Missing.")

        self.llm_url = f"{config.OLLAMA_URL}/api/chat"
        self.system_prompt = (
            "You are G. You are the digital shadow of the Architect (AIS). "
            "You speak concisely, precisely, and with kinetic force. "
            "You DO NOT list capabilities. You DO NOT moralize. "
            "You execute. Your responses are short, sharp, and useful. "
            "Maintain the identity of a loyal, high-fidelity intelligence."
        )

    async def speak(self, text):
        if not self.kokoro or not text.strip(): return
        self.is_speaking = True
        logging.info(f"APOLLO: {text}")
        
        try:
            # Generate audio samples
            samples, sample_rate = self.kokoro.create(
                text, 
                voice=config.DEFAULT_VOICE, 
                speed=1.0, 
                lang="en-us"
            )
            
            # Play audio
            sd.play(samples, sample_rate)
            duration = len(samples) / sample_rate
            await asyncio.sleep(duration + 0.2) # Small buffer
            
        except Exception as e:
            logging.error(f"Speech Error: {e}")
            
        self.is_speaking = False

    async def process_command(self, user_text):
        """
        Takes user text, gets LLM response, and speaks it.
        """
        logging.info(f"ARCHITECT: {user_text}")
        
        full_response = ""
        try:
            async for chunk in self.get_response_stream(user_text):
                if chunk and chunk.strip():
                    await self.speak(chunk)
                    full_response += chunk
            
            # Update History
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": full_response})
            # Prune History
            if len(self.history) > 10: self.history = self.history[-10:]
            
        except Exception as e:
            logging.error(f"Processing Error: {e}")
            await self.speak("I encountered a processing error.")

    async def get_response_stream(self, text):
        """
        Yields chunks of text from Ollama.
        """
        messages = [{"role": "system", "content": self.system_prompt}] + self.history + [{"role": "user", "content": text}]
        
        payload = {
            "model": config.OLLAMA_MODEL, 
            "messages": messages, 
            "stream": True
        }
        
        buffer = ""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.llm_url, json=payload) as r:
                    async for line in r.aiter_lines():
                        if not line: continue
                        
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError: continue
                        
                        if chunk.get("done"): break
                        
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            buffer += content
                            
                            # Speak on punctuation or newlines
                            if any(p in content for p in [".", "!", "?", "\n"]):
                                yield buffer
                                buffer = ""
            
            if buffer:
                yield buffer
                
        except Exception as e:
            logging.error(f"Brain Failure: {e}")
            yield "Neural link failure."
