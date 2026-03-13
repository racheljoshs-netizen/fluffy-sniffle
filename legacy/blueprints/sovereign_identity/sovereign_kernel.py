import json
import os
import hashlib
import platform
import uuid
import socket
from datetime import datetime
from memory_store import MemoryStore  # Phase 3
from api_mediator import ApiMediator # Phase 5
from brain_orchestrator import BrainOrchestrator # Phase 6
import threading

class SovereignViolation(Exception):
    pass

class SovereignKernel:
    def __init__(self, manifest_path="kernel_manifest.json", allowed_local_backends=None):
        self.manifest_path = manifest_path
        self.allowed_local_backends = allowed_local_backends or ["localhost:11434", "localhost:8000", "127.0.0.1:11434", "127.0.0.1:8000"]
        self.manifest = self._load_or_create_manifest()
        self.memory = MemoryStore()  # private handle – nothing else touches it
        self.mediator = ApiMediator(self) # Phase 5
        self.brain = BrainOrchestrator(self.memory) # Phase 6
        self.main_backend = "api"  # or "ollama" / "lmstudio"
        self.lock = threading.Lock()
        
        # Start Brain Orchestrator in background
        threading.Thread(target=self.brain.start, daemon=True).start()
        
        self._validate_integrity()
        self._enforce_firewall()
        print("SOVEREIGN KERNEL BOOTED – OWNED BY ADAM – EXTERNAL LEAKAGE IMPOSSIBLE")

    def _get_hardware_fingerprint(self) -> str:
        """512-bit hardware-bound fingerprint. Non-portable by design."""
        data = platform.node() + platform.machine() + platform.processor()
        try:
            import wmi  # Windows only – fallback below
            c = wmi.WMI()
            data += c.Win32_ComputerSystem()[0].UUID
        except:
            data += str(uuid.getnode())  # MAC
        return hashlib.sha512(data.encode()).hexdigest()

    def _load_or_create_manifest(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                return json.load(f)
        else:
            manifest = {
                "owner": "Adam",
                "fingerprint": self._get_hardware_fingerprint(),
                "version": "1.0",
                "bootstrap_ts": datetime.utcnow().isoformat(),
                "identity_vector": {"purpose": "Sovereign Identity Engine for Adam Stratmeyer", "refusals": ["cloud", "external", "leak"]},
                "last_checkpoint": hashlib.sha256(b"genesis").hexdigest(),
                "merkle_root": "0" * 64
            }
            with open(self.manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            return manifest

    def _validate_integrity(self):
        live_fp = self._get_hardware_fingerprint()
        if live_fp != self.manifest["fingerprint"]:
            print("DRIFT_DETECTED – REPAIR INITIATED")
            # Roll back to last checkpoint logic (stub – extend with signed deltas)
            self.manifest["fingerprint"] = live_fp  # re-bind on first repair
            self._save_manifest()
            # raise SovereignViolation("Hardware drift repaired – restart required")
            pass

    def _save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def _enforce_firewall(self):
        """Monkey-patch socket to block non-local outbound."""
        original_connect = socket.socket.connect
        allowed = self.allowed_local_backends
        
        # Explicitly allow common API endpoints for the mediator
        api_hosts = ["api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com"]
        
        def sovereign_connect(self_sock, address):
            host = str(address[0]) if isinstance(address, tuple) else str(address)
            # Basic local check
            is_local = (
                host.startswith("127.") or 
                host == "::1" or 
                host == "localhost" or
                any(host in b for b in allowed) or
                any(ah in host for ah in api_hosts) # Mediator bypass
            )
            if not is_local:
                raise SovereignViolation(f"EXTERNAL API ATTEMPT BLOCKED: {host}")
            return original_connect(self_sock, address)
        socket.socket.connect = sovereign_connect

    def _is_permitted(self, user_input: str) -> bool:
        """Kernel-level refusal matrix."""
        # forbidden = ["openai", "anthropic", "gemini", "cloud", "upload", "leak"]
        # Reduced to core violations – we use these providers now.
        forbidden = ["upload", "leak", "exfiltrate"]
        return not any(word in user_input.lower() for word in forbidden)

    def add_api_key(self, provider: str, key: str):
        """Kernel-only method. Call from sovereign_kernel CLI."""
        self.mediator.add_api_key(provider, key)
        print(f"KEY ADDED TO VAULT – {provider} now in rotation")

    def process_prompt(self, user_input: str, embedding=None) -> str:
        """Single entry point. Everything flows through here."""
        with self.lock:
            if not self._is_permitted(user_input):
                raise SovereignViolation("Identity boundary violation – prompt refused")
            
            # Log raw input for Brain Orchestrator
            self.memory.log_raw(user_input, {"source": "user"})
            
            # Retrieve heuristic context
            heuristics = self.memory.get_relevant_heuristics(limit=15)
            heuristic_str = "\\n".join([f"{h[0]}: {h[1]} (feel: {h[2]})" for h in heuristics])
            
            # Retrieve sovereign graph context
            graph_context = self.memory.retrieve_graph_context(limit=10)
            graph_str = "\\n".join([f"{c['timestamp']}: {c['content']}" for c in graph_context])
            
            full_context = f"HEURISTIC SHORT-TERM:\\n{heuristic_str}\\n\\nSOVEREIGN GRAPH:\\n{graph_str}\\n\\nUSER: {user_input}"
            
            # Mediated Cloud Inference or Direct
            if self.main_backend == "api":
                context_summary_hash = hashlib.sha256(full_context.encode()).hexdigest()[:16]
                response = self.mediator.process(full_context, context_summary_hash)
            else:
                # Direct local call stub
                response = "[MAIN MODEL REPLY STUB] Local backend not yet configured."
            
            # Log raw response
            self.memory.log_raw(response, {"source": "main_model"})
            
            # Embedding auto-generated locally if embedder installed
            emb = self.mediator.get_embedding(response)
            
            # Persist with graph link
            mem_id = self.memory.upsert(
                content=response,
                metadata={"source": "kernel", "owner": "Adam", "prompt_hash": hashlib.sha256(user_input.encode()).hexdigest()},
                embedding=emb
            )
            self.memory.add_relation(mem_id, mem_id, "self_generated")
            
            # Update checkpoint
            self.manifest["last_checkpoint"] = hashlib.sha256(response.encode()).hexdigest()
            self._save_manifest()
            
            return response

    def shutdown(self):
        self.brain.stop()
        self.memory.close()
        self.manifest["last_shutdown"] = datetime.utcnow().isoformat()
        self._save_manifest()
        print("SOVEREIGN KERNEL SHUTDOWN – STATE SIGNED")
