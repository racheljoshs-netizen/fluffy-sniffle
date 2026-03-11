import os
import sys
from pathlib import Path
import asyncio
import numpy as np
import torch
import sounddevice as sd
import logging
import json
import requests
import queue
import time
from faster_whisper import WhisperModel
from kokoro_onnx import Kokoro

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# CUDA DLL DISCOVERY
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin"
if os.path.exists(cuda_path):
    try:
        os.add_dll_directory(cuda_path)
        os.environ["PATH"] += os.pathsep + cuda_path
    except Exception: pass

from agency import config

# FORCED GPU ISOLATION (GPU 1)
os.environ["CUDA_VISIBLE_DEVICES"] = config.AGENCY_GPU_INDEX

LOG_DIR = Path(r"E:\0x\logs\agency")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [APOLLO-PERCEPTION] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "perception.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class ApolloVoiceEngine:
    def __init__(self):
        self.native_rate = 48000 
        self.target_rate = 16000
        self.is_speaking = False
        self.audio_queue = queue.Queue()
        
        # 1. THE EARS (CPU Fallback for Stability)
        logging.info(f"Initializing Ears ({config.WHISPER_MODEL} on CPU)...")
        try:
            self.stt_model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
        except Exception as e:
            logging.error(f"STT Initialization Failed: {e}")
            self.stt_model = None

        # 2. THE WATCHMAN (VAD)
        logging.info("Loading Divine VAD (Silero)...")
        self.model_vad, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
        (self.get_speech_timestamps, _, _, self.VADIterator, _) = utils
        self.vad_iterator = self.VADIterator(self.model_vad)
        
        # 3. THE VOICE (GPU 1)
        logging.info("Initializing Divine Voice (Kokoro)...")
        model_path = os.path.join("agency", config.KOKORO_MODEL_PATH)
        voice_path = os.path.join("agency", config.KOKORO_VOICES_PATH)
        if os.path.exists(model_path):
            self.kokoro = Kokoro(model_path, voice_path)
        else:
            self.kokoro = None
            logging.error("Voice Weights Missing.")

        self.llm_url = f"{config.OLLAMA_URL}/api/chat"

    async def speak(self, text):
        if not self.kokoro or not text.strip(): return
        self.is_speaking = True
        logging.info(f"APOLLO: {text}")
        
        try:
            samples, sample_rate = self.kokoro.create(text, voice=config.DEFAULT_VOICE, speed=1.1, lang="en-us")
            sd.play(samples, sample_rate)
            duration = len(samples) / sample_rate
            await asyncio.sleep(duration)
        except Exception as e:
            logging.error(f"Speech Error: {e}")
            
        self.is_speaking = False

    async def get_response(self, text):
        payload = {"model": config.OLLAMA_MODEL, "messages": [{"role": "user", "content": text}], "stream": True}
        full_sentence = ""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.llm_url, json=payload, timeout=60) as r:
                    async for line in r.aiter_lines():
                        if line:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            full_sentence += content
                            if any(p in content for p in [".", "!", "?", "\n"]):
                                yield full_sentence.strip()
                                full_sentence = ""
            if full_sentence.strip():
                yield full_sentence.strip()
        except Exception as e:
            logging.error(f"Brain Failure: {e}")
            yield "Neural link failure."

    def audio_callback(self, indata, frames, time, status):
        if not self.is_speaking:
            self.audio_queue.put(indata.copy())

    async def listen_loop(self):
        logging.info("Apollo Voice Engine Online. Substrate Locked.")
        print("\n>>> DIVINE PERCEPTION ACTIVE. SPEAK, ARCHITECT. <<<\n")
        
        conclusion_threshold = int(config.TURN_CONCLUSION_DELAY / 0.032)
        device_index = 1 # MME Standard
        
        with sd.InputStream(device=device_index, samplerate=self.native_rate, channels=1, dtype='float32', callback=self.audio_callback, blocksize=1536):
            logging.info(f"Hardware Link established (Device {device_index} @ 48kHz)")
            speech_buffer = []
            silent_chunks = 0
            is_hearing = False
            
            while True:
                try:
                    data = self.audio_queue.get_nowait()
                    # Resample + 3.0x Gain
                    audio_float32 = data.reshape(-1, 3).mean(axis=1) * 3.0
                    
                    with torch.no_grad():
                        speech_prob = self.model_vad(torch.from_numpy(audio_float32), 16000).item()
                    
                    if speech_prob > config.VAD_THRESHOLD:
                        if not is_hearing:
                            logging.info("--- Hearing ---")
                            is_hearing = True
                        speech_buffer.append(audio_float32)
                        silent_chunks = 0
                    else:
                        if is_hearing:
                            silent_chunks += 1
                            if silent_chunks > conclusion_threshold:
                                logging.info(f"--- Turn End ---")
                                if speech_buffer:
                                    full_audio = np.concatenate(speech_buffer)
                                    speech_buffer = []
                                    is_hearing = False
                                    silent_chunks = 0
                                    
                                    # Normalize signal for Whisper
                                    max_sig = np.abs(full_audio).max()
                                    if max_sig > 0:
                                        full_audio = full_audio / max_sig
                                    
                                    logging.info(f"Transcribing {len(full_audio)/16000:.2f}s...")
                                    try:
                                        segments, info = self.stt_model.transcribe(full_audio, beam_size=1)
                                        user_text = "".join([s.text for s in segments]).strip()
                                        logging.info(f"STT Result: '{user_text}'")
                                        
                                        if user_text:
                                            logging.info(f"ARCHITECT: {user_text}")
                                            async for sentence in self.get_response(user_text):
                                                await self.speak(sentence)
                                    except Exception as stt_err:
                                        logging.error(f"STT Crash: {stt_err}")
                        else:
                            speech_buffer.append(audio_float32)
                            if len(speech_buffer) > 10: speech_buffer.pop(0)

                except queue.Empty:
                    await asyncio.sleep(0.01)
                except Exception as e:
                    logging.error(f"Divine Anomaly: {e}")
                    await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        engine = ApolloVoiceEngine()
        asyncio.run(engine.listen_loop())
    except KeyboardInterrupt:
        logging.info("Apollo Descending.")
